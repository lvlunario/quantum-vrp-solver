"""Executed regression tests for the stub-only scientific adapter boundary."""
import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from mutation_harness import ProtocolViolation
from scientific_adapters import build_stub_record, validate_stub_record


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs" / "mutation-pilot-plan-v1.json"
SOURCE_PATH = ROOT / "src" / "scientific_adapters.py"
OUTPUT_PATH = ROOT / "results" / "2026-11-04-scientific-adapter-interface-tests.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_sha256(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def expect_rejected(name, plan_record, result, checks):
    try:
        validate_stub_record(plan_record, result)
    except ProtocolViolation as exc:
        checks.append({"name": name, "passed": True, "reason": str(exc)})
    else:
        checks.append({"name": name, "passed": False,
                       "reason": "invalid fixture was accepted"})


def main():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    checks = []
    fixtures = {}
    for row in plan["records"]:
        fixture = build_stub_record(row)
        validate_stub_record(row, fixture)
        fixtures[row["id"]] = fixture
    checks.append({"name": "all_13_plan_records_route_to_exact_stub_layers",
                   "passed": len(fixtures) == 13})

    by_id = {row["id"]: row for row in plan["records"]}
    cases = []
    wrong = copy.deepcopy(fixtures["M03"]); wrong["record_id"] = "M04"
    cases.append(("identity_mismatch", by_id["M03"], wrong))
    wrong = copy.deepcopy(fixtures["M07"]); wrong["layers"] = ["L4"]
    cases.append(("layer_mismatch", by_id["M07"], wrong))
    wrong = copy.deepcopy(fixtures["M01"]); wrong["scientific_verdict"] = "KILLED"
    cases.append(("stub_verdict_refused", by_id["M01"], wrong))
    wrong = copy.deepcopy(fixtures["M04"]); wrong["actual_consumption"]["sdk_statevectors"] = 1
    cases.append(("stub_sdk_consumption_refused", by_id["M04"], wrong))
    wrong = copy.deepcopy(fixtures["M01"]); wrong["observations"]["L1"]["encoded_states_examined"] = 64
    cases.append(("stub_enumeration_refused", by_id["M01"], wrong))
    wrong = copy.deepcopy(fixtures["M05"]); wrong["observations"]["L2"]["max_component_error"] = 0.0
    cases.append(("stub_statevector_metric_refused", by_id["M05"], wrong))
    wrong = copy.deepcopy(fixtures["M08"]); wrong["observations"]["L3"]["probabilities_examined"] = 64
    cases.append(("stub_readout_metric_refused", by_id["M08"], wrong))
    wrong = copy.deepcopy(fixtures["M10"]); wrong["observations"]["L4"]["separate_metrics"] = False
    cases.append(("conflated_application_metrics_refused", by_id["M10"], wrong))
    wrong = copy.deepcopy(fixtures["M12"]); wrong["declared_future_consumption"] = {}
    cases.append(("changed_future_budget_refused", by_id["M12"], wrong))
    wrong = copy.deepcopy(fixtures["baseline"]); del wrong["observations"]["L3"]
    cases.append(("incomplete_baseline_bundle_refused", by_id["baseline"], wrong))
    for name, row, fixture in cases:
        expect_rejected(name, row, fixture, checks)

    passed = sum(item["passed"] for item in checks)
    report = {
        "schema_version": 1,
        "status": "PASSED" if passed == len(checks) else "FAILED",
        "mode": "STUB_INTERFACE_TEST",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_scientific_adapters.py",
        "python": platform.python_version(),
        "provenance": {
            "plan_canonical_json_sha256": canonical_json_sha256(PLAN_PATH),
            "adapter_source_sha256": sha256(SOURCE_PATH),
        },
        "summary": {
            "checks_passed": passed,
            "checks_total": len(checks),
            "valid_plan_records_routed": len(fixtures),
            "negative_controls_rejected": sum(item["passed"] for item in checks[1:]),
            "protocol_mutants_executed": 0,
            "formulation_passes_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
        },
        "checks": checks,
        "limitations": [
            "These tests verify interface shape and fail-closed stub behavior only.",
            "No formulation, statevector, probability, application metric, mutant, or baseline was evaluated.",
            "Scientific adapters and the final environment/source-hash preflight remain unexecuted.",
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["status"] != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
