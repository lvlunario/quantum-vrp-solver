"""Dry-run the mutation-pilot harness with synthetic callbacks only."""
import hashlib
import json
import platform
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from mutation_harness import CAPS, PilotHarness, ProtocolViolation


def provenance():
    return {
        "parent_commit": "41ce4232a3ecd9ab146f59a86335a4be0b74b53f",
        "source_sha256": "dry-run-placeholder-replaced-in-report",
        "lock_sha256": "dry-run-standard-library-only",
        "python": platform.python_version(),
        "command": "python src/verify_mutation_harness.py",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "thresholds": {"statevector": 1e-12, "readout": 1e-11},
        "fixture": "synthetic stub callbacks; no circuit or mutant execution",
    }


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def harness(self):
        return PilotHarness(self.root / "pilot.run", provenance())

    def pass_baseline(self, harness):
        return harness.execute("baseline", "baseline", {
            "baseline_bundles": 1, "sdk_statevectors": 3,
        }, lambda: {"baseline_passed": True, "synthetic": True})

    def test_missing_provenance_refused_before_reservation(self):
        bad = provenance(); del bad["parent_commit"]
        with self.assertRaises(ProtocolViolation):
            PilotHarness(self.root / "pilot.run", bad)
        self.assertFalse((self.root / "pilot.run").exists())

    def test_duplicate_pilot_directory_refused(self):
        self.harness()
        with self.assertRaises(FileExistsError): self.harness()

    def test_mutant_before_baseline_refused_without_callback(self):
        harness = self.harness(); calls = []
        with self.assertRaises(ProtocolViolation):
            harness.execute("M01", "mutant", {"mutant_attempts": 1},
                            lambda: calls.append(True))
        self.assertEqual(calls, [])

    def test_failed_baseline_aborts_and_blocks_mutants(self):
        harness = self.harness()
        with self.assertRaises(ProtocolViolation):
            harness.execute("baseline", "baseline", {"baseline_bundles": 1},
                            lambda: {"baseline_passed": False})
        self.assertTrue((harness.records / "baseline" / "aborted.json").exists())
        self.assertFalse((harness.records / "baseline" / "terminal.json").exists())

    def test_baseline_terminal_has_digest(self):
        harness = self.harness(); self.pass_baseline(harness)
        terminal = json.loads((harness.records / "baseline" / "terminal.json").read_text())
        expected = hashlib.sha256((harness.records / "baseline" / "result.json").read_bytes()).hexdigest()
        self.assertEqual(terminal["result_sha256"], expected)

    def test_budget_counts_attempts_not_completions(self):
        harness = self.harness(); self.pass_baseline(harness)
        with self.assertRaises(RuntimeError):
            harness.execute("M01", "mutant", {"mutant_attempts": 1,
                            "formulation_passes": 1},
                            lambda: (_ for _ in ()).throw(RuntimeError("injected")))
        self.assertEqual(harness.counts()["mutant_attempts"], 1)
        self.assertEqual(harness.counts()["formulation_passes"], 1)

    def test_sdk_overflow_refused_before_callback(self):
        harness = self.harness(); self.pass_baseline(harness); calls = []
        with self.assertRaises(ProtocolViolation):
            harness.execute("M03", "mutant", {"mutant_attempts": 1,
                            "sdk_statevectors": 13}, lambda: calls.append(True))
        self.assertEqual(calls, [])

    def test_zero_search_budget_is_enforced(self):
        harness = self.harness(); self.pass_baseline(harness)
        with self.assertRaises(ProtocolViolation):
            harness.execute("M01", "mutant", {"mutant_attempts": 1,
                            "search_evaluations": 1}, lambda: {})

    def test_unknown_mutant_refused(self):
        harness = self.harness(); self.pass_baseline(harness)
        with self.assertRaises(ProtocolViolation):
            harness.execute("M13", "mutant", {"mutant_attempts": 1}, lambda: {})

    def test_duplicate_mutant_id_preserves_first_record(self):
        harness = self.harness(); self.pass_baseline(harness)
        harness.execute("M01", "mutant", {"mutant_attempts": 1}, lambda: {"status": "DRY"})
        before = (harness.records / "M01" / "result.json").read_bytes()
        with self.assertRaises(FileExistsError):
            harness.execute("M01", "mutant", {"mutant_attempts": 1}, lambda: {})
        self.assertEqual((harness.records / "M01" / "result.json").read_bytes(), before)

    def test_all_forbidden_resource_caps_are_zero(self):
        for name in ("search_evaluations", "shots", "optimizer_calls",
                     "transpiler_runs", "cloud_calls", "hardware_jobs"):
            self.assertEqual(CAPS[name], 0)

    def test_dry_run_uses_no_protocol_budget(self):
        harness = self.harness()
        self.assertEqual(harness.counts(), {name: 0 for name in CAPS})


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.passed = []
    def addSuccess(self, test):
        super().addSuccess(test); self.passed.append(test.id())


if __name__ == "__main__":
    started = datetime.now(timezone.utc).isoformat()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HarnessTests)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    root = Path(__file__).resolve().parent
    report = {
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "evidence_label": "EXECUTED LOCAL DRY-RUN TESTS",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "command": "python src/verify_mutation_harness.py",
        "parent_commit": "41ce4232a3ecd9ab146f59a86335a4be0b74b53f",
        "test_count": result.testsRun,
        "passed": result.passed,
        "failures": [(t.id(), msg) for t, msg in result.failures + result.errors],
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (root / "mutation_harness.py", Path(__file__))},
        "data": "Synthetic temporary-directory fixtures and stub callbacks only",
        "protocol_mutants_executed": 0,
        "sdk_statevectors_executed": 0,
        "search_evaluations": 0,
        "shots": 0,
        "hardware_jobs": 0,
        "limitations": [
            "Tests orchestration and retention logic, not scientific mutant oracles",
            "Local filesystem behavior only; no power-loss or distributed-filesystem test",
            "The prospective M01-M12 pilot remains unexecuted",
        ],
    }
    output = root.parent / "results" / "2026-10-26-mutation-harness-dry-run.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(not result.wasSuccessful())
