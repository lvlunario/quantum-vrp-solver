"""Validate the frozen mutation plan without importing Qiskit or running mutants."""
import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from mutation_harness import CAPS


EXPECTED_IDS = ["baseline"] + [f"M{i:02d}" for i in range(1, 13)]
SDK_IDS = {"baseline", "M03", "M04", "M05", "M06"}
FORMULATION_IDS = {"M01", "M02"}
EXPECTED_LAYERS = {
    "M01": "L1 formulation", "M02": "L1 labeled-state formulation",
    "M03": "L2 exact statevector", "M04": "L2 exact statevector",
    "M05": "L2 exact statevector", "M06": "L2 exact statevector",
    "M07": "L3 readout", "M08": "L3 readout", "M09": "L3 readout",
    "M10": "L4 application", "M11": "L2 exact statevector",
    "M12": "L2 exact statevector",
}


def validate(plan):
    checks = []

    def check(name, condition, detail=None):
        row = {"name": name, "passed": bool(condition)}
        if detail is not None: row["detail"] = detail
        checks.append(row)

    records = plan.get("records", [])
    ids = [row.get("id") for row in records]
    check("plan is explicitly unexecuted", plan.get("status") == "PLANNED_UNEXECUTED")
    check("execution is not authorized", plan.get("execution_authorized") is False)
    check("record identities and order are exact", ids == EXPECTED_IDS, {"ids": ids})
    check("record identities are unique", len(ids) == len(set(ids)))
    check("one baseline plus twelve mutants", len(records) == 13 and
          sum(r.get("kind") == "baseline" for r in records) == 1 and
          sum(r.get("kind") == "mutant" for r in records) == 12)
    check("all mutant layers match the frozen routing",
          all(r.get("layer") == EXPECTED_LAYERS[r["id"]]
              for r in records if r.get("kind") == "mutant"))
    check("every record names an oracle and expected outcome",
          all(r.get("oracle") and r.get("expected") for r in records))
    check("only baseline and M03-M06 claim SDK statevectors",
          {r["id"] for r in records if r.get("consumption", {}).get("sdk_statevectors", 0)} == SDK_IDS)
    check("only M01-M02 claim formulation passes",
          {r["id"] for r in records if r.get("consumption", {}).get("formulation_passes", 0)} == FORMULATION_IDS)
    check("M07-M12 claim no SDK statevectors",
          all(r.get("consumption", {}).get("sdk_statevectors", 0) == 0
              for r in records if r.get("id") in {f"M{i:02d}" for i in range(7, 13)}))
    check("each mutant claims exactly one attempt",
          all(r.get("consumption", {}).get("mutant_attempts") == 1
              for r in records if r.get("kind") == "mutant"))
    check("baseline claims one bundle and no mutant attempt",
          records and records[0].get("consumption") == {"baseline_bundles": 1, "sdk_statevectors": 3})
    check("all consumption values are nonnegative integers",
          all(isinstance(v, int) and v >= 0 for r in records
              for v in r.get("consumption", {}).values()))
    check("all consumption keys are protocol counters",
          all(k in CAPS for r in records for k in r.get("consumption", {})))

    totals = {name: 0 for name in CAPS}
    for record in records:
        for name, amount in record.get("consumption", {}).items(): totals[name] += amount
    check("computed totals equal declared totals", totals == plan.get("declared_totals"), totals)
    check("computed totals exactly equal frozen caps", totals == CAPS, totals)
    check("all prohibited-resource totals remain zero",
          all(totals[name] == 0 for name in ("search_evaluations", "shots",
              "optimizer_calls", "transpiler_runs", "cloud_calls", "hardware_jobs")))
    check("three fixed angle pairs are present", len(plan.get("angle_pairs", [])) == 3)
    check("thresholds remain frozen",
          plan.get("thresholds") == {"statevector": 1e-12, "readout": 1e-11})
    by_id = {r.get("id"): r for r in records}
    check("M02 split-oracle control remains explicit",
          by_id.get("M02", {}).get("expected") ==
          "KILLED_WITH_REDUCED_ORACLE_SURVIVAL_CONTROL")
    check("M11 is the equivalent survivor",
          by_id.get("M11", {}).get("expected") ==
          "SURVIVED_EQUIVALENT_CONTROL")
    check("M12 probability blind control remains explicit",
          by_id.get("M12", {}).get("expected") ==
          "KILLED_WITH_PROBABILITY_SURVIVAL_CONTROL")
    return checks, totals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    checks, totals = validate(plan)
    passed = all(row["passed"] for row in checks)
    source = Path(__file__)
    result = {
        "status": "PASSED" if passed else "FAILED",
        "evidence_label": "EXECUTED LOCAL PLAN VALIDATION",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "command": "python src/validate_mutation_plan.py --plan docs/mutation-pilot-plan-v1.json --output results/2026-10-27-mutation-plan-validation.json",
        "parent_commit": plan.get("parent_commit"),
        "plan_sha256": hashlib.sha256(args.plan.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "protocol_git_blob_sha": plan.get("protocol", {}).get("git_blob_sha"),
        "check_count": len(checks), "checks": checks, "computed_totals": totals,
        "protocol_mutants_executed": 0, "sdk_statevectors_executed": 0,
        "search_evaluations": 0, "shots": 0, "hardware_jobs": 0,
        "data": "Static prospective manifest for the fixed synthetic fixture",
        "limitations": [
            "Validates plan structure and declared budgets, not mutant behavior",
            "Does not import Qiskit or invoke scientific callbacks",
            "Future execution must reconcile declared counters with append-only attempt records"
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "check_count": len(checks),
                      "computed_totals": totals}, indent=2))
    raise SystemExit(not passed)


if __name__ == "__main__": main()
