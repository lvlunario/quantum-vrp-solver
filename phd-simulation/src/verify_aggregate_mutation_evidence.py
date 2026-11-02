"""Negative-control tests for aggregate evidence reconstruction."""
import copy
import hashlib
import json
import platform
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from aggregate_mutation_evidence import aggregate


ROOT = Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "docs/mutation-pilot-plan-v1.json").read_text())


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_fixture(root, plan=PLAN):
    write_json(root / "manifest.json", {"mode": "SYNTHETIC_DRY_RUN", "scientific_execution": False})
    sequence = 0
    for record in plan["records"]:
        record_id = record["id"]
        write_json(root / "events" / f"{sequence:06d}.json", {
            "kind": "attempt", "record_id": record_id,
            "consumption": record["consumption"]})
        sequence += 1
        result_path = root / "records" / record_id / "result.json"
        write_json(result_path, {"record_id": record_id,
            "status": "SYNTHETIC_RECORD_ONLY", "scientific_verdict": None})
        write_json(root / "records" / record_id / "terminal.json", {
            "status": "COMPLETE",
            "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest()})
        write_json(root / "events" / f"{sequence:06d}.json", {
            "kind": "complete", "record_id": record_id})
        sequence += 1


class AggregateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "pilot.run"; build_fixture(self.root)

    def test_complete_fixture_reconstructs_exact_totals(self):
        report = aggregate(self.root, PLAN)
        self.assertEqual(report["status"], "VALID")
        self.assertEqual(report["computed_totals"], PLAN["declared_totals"])
        self.assertEqual(report["record_count"], 13)

    def test_missing_terminal_is_rejected(self):
        (self.root / "records/M04/terminal.json").unlink()
        self.assertEqual(aggregate(self.root, PLAN)["status"], "INVALID")

    def test_changed_result_bytes_are_rejected(self):
        path = self.root / "records/M07/result.json"
        path.write_text(path.read_text() + " ", encoding="utf-8")
        report = aggregate(self.root, PLAN)
        self.assertIn("M07: result digest mismatch", report["issues"])

    def test_undeclared_record_directory_is_rejected(self):
        write_json(self.root / "records/M13/result.json", {"record_id": "M13"})
        self.assertEqual(aggregate(self.root, PLAN)["status"], "INVALID")

    def test_counter_mismatch_is_rejected(self):
        path = self.root / "events/000000.json"
        row = json.loads(path.read_text()); row["consumption"]["sdk_statevectors"] = 4
        write_json(path, row)
        report = aggregate(self.root, PLAN)
        self.assertIn("ledger totals do not equal protocol caps", report["issues"])

    def test_missing_attempt_is_rejected(self):
        (self.root / "events/000002.json").unlink()
        self.assertEqual(aggregate(self.root, PLAN)["status"], "INVALID")

    def test_wrong_fixture_mode_is_rejected(self):
        write_json(self.root / "manifest.json", {"mode": "SCIENTIFIC_EXECUTION"})
        self.assertEqual(aggregate(self.root, PLAN)["status"], "INVALID")


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.passed = []
    def addSuccess(self, test):
        super().addSuccess(test); self.passed.append(test.id())


if __name__ == "__main__":
    started = datetime.now(timezone.utc).isoformat()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AggregateTests)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    source = Path(__file__); aggregate_source = source.with_name("aggregate_mutation_evidence.py")
    report = {
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "evidence_label": "EXECUTED LOCAL SYNTHETIC AGGREGATE TESTS",
        "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "command": "python src/verify_aggregate_mutation_evidence.py",
        "parent_commit": "e856cc902e0a4038d105e9bc27071494465427d5",
        "test_count": result.testsRun, "passed": result.passed,
        "failures": [(t.id(), msg) for t, msg in result.failures + result.errors],
        "source_sha256": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest(),
            aggregate_source.name: hashlib.sha256(aggregate_source.read_bytes()).hexdigest()},
        "data": "Temporary synthetic retained records; no external dataset",
        "protocol_mutants_executed": 0, "sdk_statevectors_executed": 0,
        "search_evaluations": 0, "shots": 0, "hardware_jobs": 0,
        "limitations": ["Local filesystem only", "No scientific oracle or mutation verdict tested"]}
    output = ROOT / "results/2026-11-02-aggregate-reconstruction-tests.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(not result.wasSuccessful())
