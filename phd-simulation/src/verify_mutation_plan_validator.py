"""Negative-control tests for the plan validator; no scientific execution."""
import copy
import hashlib
import json
import platform
import unittest
from datetime import datetime, timezone
from pathlib import Path

from validate_mutation_plan import validate


ROOT = Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / "docs/mutation-pilot-plan-v1.json").read_text())


def passes(plan):
    checks, _ = validate(plan)
    return all(row["passed"] for row in checks)


class ValidatorTests(unittest.TestCase):
    def test_frozen_plan_passes(self):
        self.assertTrue(passes(copy.deepcopy(PLAN)))

    def test_missing_control_record_fails_without_exception(self):
        plan = copy.deepcopy(PLAN)
        plan["records"] = [r for r in plan["records"] if r["id"] != "M12"]
        self.assertFalse(passes(plan))

    def test_nonzero_search_claim_fails(self):
        plan = copy.deepcopy(PLAN)
        plan["records"][1]["consumption"]["search_evaluations"] = 1
        self.assertFalse(passes(plan))

    def test_sdk_work_moved_to_in_memory_mutant_fails(self):
        plan = copy.deepcopy(PLAN)
        row = next(r for r in plan["records"] if r["id"] == "M07")
        row["consumption"]["sdk_statevectors"] = 1
        self.assertFalse(passes(plan))

    def test_changed_split_oracle_prediction_fails(self):
        plan = copy.deepcopy(PLAN)
        next(r for r in plan["records"] if r["id"] == "M02")["expected"] = "KILLED"
        self.assertFalse(passes(plan))

    def test_execution_authorization_fails(self):
        plan = copy.deepcopy(PLAN); plan["execution_authorized"] = True
        self.assertFalse(passes(plan))

    def test_duplicate_identity_fails(self):
        plan = copy.deepcopy(PLAN); plan["records"][2]["id"] = "M01"
        self.assertFalse(passes(plan))


class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.passed = []
    def addSuccess(self, test):
        super().addSuccess(test); self.passed.append(test.id())


if __name__ == "__main__":
    started = datetime.now(timezone.utc).isoformat()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests)
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordingResult).run(suite)
    source = Path(__file__)
    validator = source.with_name("validate_mutation_plan.py")
    report = {
        "status": "PASSED" if result.wasSuccessful() else "FAILED",
        "evidence_label": "EXECUTED LOCAL VALIDATOR NEGATIVE-CONTROL TESTS",
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "command": "python src/verify_mutation_plan_validator.py",
        "test_count": result.testsRun, "passed": result.passed,
        "failures": [(t.id(), msg) for t, msg in result.failures + result.errors],
        "source_sha256": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest(),
            validator.name: hashlib.sha256(validator.read_bytes()).hexdigest()
        },
        "protocol_mutants_executed": 0, "sdk_statevectors_executed": 0,
        "search_evaluations": 0, "shots": 0, "hardware_jobs": 0,
        "data": "Deep-copied malformed variants of the static prospective manifest",
        "limitations": ["Tests validator rejection behavior, not scientific oracles"]
    }
    output = ROOT / "results/2026-10-27-plan-validator-tests.json"
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(not result.wasSuccessful())
