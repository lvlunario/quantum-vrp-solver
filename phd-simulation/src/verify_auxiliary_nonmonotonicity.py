"""Show that fixed-slack auxiliary consistency is not monotone in decisions."""

import hashlib
import itertools
import json
import platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from application_metrics import evaluate_state
from independent_feasibility import bits_q0_first


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "verify_auxiliary_nonmonotonicity.py"
OUTPUT = ROOT / "results" / "2026-11-19-auxiliary-nonmonotonicity.json"
DEMANDS = [2, 3, 4]
CAPACITY = 5
WEIGHTS = [1, 2, 4]


def check(name, passed, detail=None):
    row = {"name": name, "passed": bool(passed)}
    if detail is not None:
        row["detail"] = detail
    return row


def row_for(x, y, auxiliary):
    left = evaluate_state(x, auxiliary, DEMANDS, CAPACITY, WEIGHTS)
    right = evaluate_state(y, auxiliary, DEMANDS, CAPACITY, WEIGHTS)
    return {
        "x": list(x),
        "y": list(y),
        "auxiliary_bits": list(auxiliary),
        "slack": left["auxiliary"]["slack"],
        "load_x": left["physical"]["load"],
        "load_y": right["physical"]["load"],
        "physical_feasible_x": left["physical"]["feasible"],
        "physical_feasible_y": right["physical"]["feasible"],
        "overload_x": left["physical"]["overload"],
        "overload_y": right["physical"]["overload"],
        "auxiliary_consistent_x": left["auxiliary"]["consistent"],
        "auxiliary_consistent_y": right["auxiliary"]["consistent"],
        "residual_x": left["auxiliary"]["residual"],
        "residual_y": right["auxiliary"]["residual"],
    }


def main():
    component_options = ((0, 0), (0, 1), (1, 1))
    rows = []
    ordinal = 0
    for slack_index in range(8):
        auxiliary = bits_q0_first(slack_index, 3)
        for components in itertools.product(component_options, repeat=3):
            x = tuple(item[0] for item in components)
            y = tuple(item[1] for item in components)
            row = row_for(x, y, auxiliary)
            row["ordinal"] = ordinal
            rows.append(row)
            ordinal += 1

    transitions = Counter(
        f"{str(row['auxiliary_consistent_x']).lower()}_to_{str(row['auxiliary_consistent_y']).lower()}"
        for row in rows
    )
    destroy = row_for((0, 0, 0), (1, 0, 0), (1, 0, 1))
    create = row_for((0, 0, 0), (1, 0, 0), (1, 1, 0))
    identity_rows = [row for row in rows if row["x"] == row["y"]]
    physical_p01 = all(
        row["load_y"] >= row["load_x"]
        and row["overload_y"] >= row["overload_x"]
        and ((not row["physical_feasible_y"]) or row["physical_feasible_x"])
        for row in rows
    )

    checks = [
        check("exactly 216 ordered-decision fixed-slack cases are enumerated", len(rows) == 27 * 8),
        check("slack-five witness changes auxiliary consistency true to false", destroy["slack"] == 5 and destroy["auxiliary_consistent_x"] is True and destroy["auxiliary_consistent_y"] is False, destroy),
        check("slack-three witness changes auxiliary consistency false to true", create["slack"] == 3 and create["auxiliary_consistent_x"] is False and create["auxiliary_consistent_y"] is True, create),
        check("both witnesses keep x and y physically feasible", all(item["physical_feasible_x"] and item["physical_feasible_y"] for item in (destroy, create))),
        check("both directions of auxiliary-consistency transition occur exhaustively", transitions["true_to_false"] > 0 and transitions["false_to_true"] > 0, dict(sorted(transitions.items()))),
        check("all 64 identity cases preserve auxiliary consistency", len(identity_rows) == 64 and all(row["auxiliary_consistent_x"] == row["auxiliary_consistent_y"] for row in identity_rows)),
        check("physical P01 remains valid on every projected pair", physical_p01),
        check("transition counts partition all 216 cases", sum(transitions.values()) == len(rows)),
    ]

    payload = {
        "schema_version": 1,
        "status": "EXECUTED_DEVELOPMENT_AUXILIARY_NONMONOTONICITY_CONFIRMED",
        "scope": "DEVELOPMENT_TEST_OUTSIDE_FROZEN_MUTATION_PILOT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_auxiliary_nonmonotonicity.py",
        "python": platform.python_version(),
        "data": "Fixed synthetic three-load fixture; no external dataset",
        "randomness": "None; exhaustive deterministic enumeration",
        "config": {"demands": DEMANDS, "capacity": CAPACITY, "auxiliary_weights": WEIGHTS},
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "claim_boundary": {
            "physical_p01": "PASSED_ON_PROJECTED_27_ORDERED_DECISION_PAIRS",
            "auxiliary_monotonicity": "REFUTED_IN_BOTH_DIRECTIONS_UNDER_FIXED_SLACK",
            "interpretation": "The auxiliary equality indicator is not an order-preserving proxy for physical feasibility."
        },
        "minimal_witnesses": {"true_to_false": destroy, "false_to_true": create},
        "checks": checks,
        "rows": rows,
        "summary": {
            "checks_passed": sum(item["passed"] for item in checks),
            "checks_total": len(checks),
            "cases_executed": len(rows),
            "ordered_decision_pairs": 27,
            "fixed_slack_assignments": 8,
            "identity_cases": len(identity_rows),
            "transition_counts": dict(sorted(transitions.items())),
            "physical_p01_violations": 0 if physical_p01 else None,
            "protocol_formulation_passes_executed": 0,
            "protocol_mutants_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
            "pilot_baseline_reserved": False
        },
        "limitations": [
            "The result concerns one fixed synthetic equality encoding only.",
            "Auxiliary nonmonotonicity does not refute physical P01.",
            "No objective, uncertainty, resilience physics, circuit, optimizer, hardware or quantum advantage is evaluated."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(item["passed"] for item in checks):
        raise SystemExit("auxiliary nonmonotonicity audit failed")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
