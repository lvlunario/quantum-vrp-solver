"""Execute preregistered P01 on exactly 27 development-fixture pairs."""

import hashlib
import itertools
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from independent_feasibility import FeasibilityInputError, evaluate


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "application-oracle-contract-v1.json"
SOURCE = ROOT / "src" / "verify_monotonicity_p01.py"
OUTPUT = ROOT / "results" / "2026-11-18-p01-monotonicity.json"


class PreconditionError(ValueError):
    pass


def validate_pair(x, y, demands_x, demands_y, capacity_x, capacity_y):
    """Fail closed before evaluating a pair outside P01's frozen domain."""
    if not isinstance(x, (list, tuple)) or not x or not isinstance(y, (list, tuple)) or len(x) != len(y):
        raise PreconditionError("x and y must have the same positive length")
    if any(bit not in (0, 1) or isinstance(bit, bool) for bit in (*x, *y)):
        raise PreconditionError("x and y must contain integer bits")
    if any(left > right for left, right in zip(x, y)):
        raise PreconditionError("x must be componentwise no greater than y")
    if demands_x != demands_y:
        raise PreconditionError("demand vector must remain fixed")
    if capacity_x != capacity_y:
        raise PreconditionError("capacity must remain fixed")
    try:
        left = evaluate(x, demands_x, capacity_x)
        right = evaluate(y, demands_y, capacity_y)
    except FeasibilityInputError as exc:
        raise PreconditionError(str(exc)) from exc
    return left, right


def check(name, passed, detail=None):
    row = {"name": name, "passed": bool(passed)}
    if detail is not None:
        row["detail"] = detail
    return row


def main():
    contract_bytes = CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)
    prop = contract["preregistered_property"]
    fixture = prop["development_fixture"]
    if prop["id"] != "P01_NONNEGATIVE_DEMAND_MONOTONICITY" or prop["status"] != "PLANNED_UNEXECUTED":
        raise SystemExit("frozen P01 contract is not executable as planned")

    demands = fixture["demands"]
    capacity = fixture["capacity"]
    rows = []
    component_options = ((0, 0), (0, 1), (1, 1))
    for ordinal, components in enumerate(itertools.product(component_options, repeat=3)):
        x = tuple(item[0] for item in components)
        y = tuple(item[1] for item in components)
        left, right = validate_pair(x, y, demands, demands, capacity, capacity)
        row = {
            "ordinal": ordinal,
            "x": list(x),
            "y": list(y),
            "load_x": left["load"],
            "load_y": right["load"],
            "overload_x": left["overload"],
            "overload_y": right["overload"],
            "feasible_x": left["feasible"],
            "feasible_y": right["feasible"],
            "load_nondecreasing": right["load"] >= left["load"],
            "overload_nondecreasing": right["overload"] >= left["overload"],
            "downward_feasibility": (not right["feasible"]) or left["feasible"],
        }
        rows.append(row)

    rejected_controls = []
    controls = [
        {
            "name": "negative demand violates the nonnegative-demand precondition",
            "args": ((0, 0, 0), (1, 0, 0), [2, 3, -4], [2, 3, -4], 5, 5),
        },
        {
            "name": "changing capacity violates the fixed-capacity precondition",
            "args": ((1, 0, 0), (1, 1, 0), demands, demands, 1, 10),
        },
    ]
    for control in controls:
        try:
            validate_pair(*control["args"])
        except PreconditionError as exc:
            rejected_controls.append({"name": control["name"], "rejected": True, "reason": str(exc)})

    identity_count = sum(row["x"] == row["y"] for row in rows)
    strict_count = sum(row["load_y"] > row["load_x"] for row in rows)
    checks = [
        check("frozen contract identifies P01 as planned and unexecuted before this run", prop["status"] == "PLANNED_UNEXECUTED"),
        check("exactly 27 componentwise ordered pairs are enumerated", len(rows) == fixture["ordered_pairs_max"] == 27),
        check("the enumeration contains exactly eight identity pairs", identity_count == 8, {"identity_pairs": identity_count}),
        check("load is nondecreasing for every ordered pair", all(row["load_nondecreasing"] for row in rows)),
        check("overload is nondecreasing for every ordered pair", all(row["overload_nondecreasing"] for row in rows)),
        check("feasibility is downward closed for every ordered pair", all(row["downward_feasibility"] for row in rows)),
        check("all nineteen nonidentity pairs strictly increase load", strict_count == 19, {"strict_load_increases": strict_count}),
        check("both out-of-precondition controls fail closed", len(rejected_controls) == 2, {"rejected": len(rejected_controls)}),
    ]

    payload = {
        "schema_version": 1,
        "status": "EXECUTED_DEVELOPMENT_P01_PASSED",
        "scope": "DEVELOPMENT_TEST_OUTSIDE_FROZEN_MUTATION_PILOT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_monotonicity_p01.py",
        "python": platform.python_version(),
        "data": "Fixed synthetic three-load fixture; no external dataset",
        "randomness": "None; exhaustive deterministic enumeration",
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "property": {
            "id": prop["id"],
            "contract_status_before_execution": prop["status"],
            "execution_outcome": "PASSED_ON_FIXED_DEVELOPMENT_FIXTURE",
            "demands": demands,
            "capacity": capacity,
        },
        "checks": checks,
        "rows": rows,
        "out_of_precondition_controls": rejected_controls,
        "summary": {
            "checks_passed": sum(item["passed"] for item in checks),
            "checks_total": len(checks),
            "ordered_pairs_executed": len(rows),
            "identity_pairs": identity_count,
            "strict_load_increases": strict_count,
            "in_scope_counterexamples": sum(not (row["load_nondecreasing"] and row["overload_nondecreasing"] and row["downward_feasibility"]) for row in rows),
            "out_of_precondition_controls_rejected": len(rejected_controls),
            "protocol_formulation_passes_executed": 0,
            "protocol_mutants_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
            "pilot_baseline_reserved": False
        },
        "limitations": [
            "P01 passed one exhaustive three-bit synthetic fixture only.",
            "The result does not cover auxiliary consistency, objective energy or negative demands.",
            "No resilience physics, uncertainty, optimizer, circuit, hardware or quantum advantage is evaluated."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(item["passed"] for item in checks):
        raise SystemExit("P01 development audit failed")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
