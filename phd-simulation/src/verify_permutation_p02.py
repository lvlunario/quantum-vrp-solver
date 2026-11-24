#!/usr/bin/env python3
"""Execute frozen P02 on the bounded synthetic development fixture."""

from __future__ import annotations

import hashlib
import itertools
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from independent_feasibility import evaluate

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "p02-permutation-contract-v1.json"
ORACLE_PATH = ROOT / "src" / "independent_feasibility.py"
OUTPUT_PATH = ROOT / "results" / "2026-11-24-p02-permutation.json"


class PermutationPreconditionError(ValueError):
    """Raised when a proposed comparison is not a simultaneous permutation."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_permutation(permutation: Sequence[int], width: int) -> tuple[int, ...]:
    if not isinstance(permutation, (list, tuple)):
        raise PermutationPreconditionError("permutation must be a list or tuple")
    if len(permutation) != width or tuple(sorted(permutation)) != tuple(range(width)):
        raise PermutationPreconditionError("permutation must be a bijection over all coordinates")
    return tuple(permutation)


def permute(values: Sequence[int], permutation: Sequence[int]) -> tuple[int, ...]:
    p = validate_permutation(permutation, len(values))
    return tuple(values[index] for index in p)


def evaluate_simultaneous(
    decision: Sequence[int],
    demands: Sequence[int],
    capacity: int,
    decision_permutation: Sequence[int],
    demand_permutation: Sequence[int],
) -> dict:
    """Compare only when decision and demand use the identical bijection."""
    dp = validate_permutation(decision_permutation, len(decision))
    mp = validate_permutation(demand_permutation, len(demands))
    if dp != mp:
        raise PermutationPreconditionError(
            "P02 requires the same permutation for decision and matching demand"
        )
    if len(decision) != len(demands):
        raise PermutationPreconditionError("decision and demand lengths must match")

    before = evaluate(decision, demands, capacity)
    transformed_decision = permute(decision, dp)
    transformed_demands = permute(demands, mp)
    after = evaluate(transformed_decision, transformed_demands, capacity)
    return {
        "decision": list(decision),
        "demands": list(demands),
        "capacity": capacity,
        "permutation": list(dp),
        "transformed_decision": list(transformed_decision),
        "transformed_demands": list(transformed_demands),
        "before": {
            "load": before["load"],
            "overload": before["overload"],
            "physical_feasibility": before["feasible"],
        },
        "after": {
            "load": after["load"],
            "overload": after["overload"],
            "physical_feasibility": after["feasible"],
        },
        "properties": {
            "load_equal": before["load"] == after["load"],
            "overload_equal": before["overload"] == after["overload"],
            "physical_feasibility_equal": before["feasible"] == after["feasible"],
        },
    }


def rejected_control(
    name: str,
    decision_permutation: Sequence[int],
    demand_permutation: Sequence[int],
) -> dict:
    decision = (1, 0, 0)
    demands = (2, 3, 4)
    try:
        evaluate_simultaneous(
            decision,
            demands,
            5,
            decision_permutation,
            demand_permutation,
        )
    except PermutationPreconditionError as error:
        naive_decision = permute(decision, decision_permutation)
        naive_demands = permute(demands, demand_permutation)
        return {
            "name": name,
            "rejected": True,
            "reason": str(error),
            "attempted_decision_permutation": list(decision_permutation),
            "attempted_demand_permutation": list(demand_permutation),
            "original_load": evaluate(decision, demands, 5)["load"],
            "naive_transformed_load": evaluate(naive_decision, naive_demands, 5)["load"],
        }
    return {"name": name, "rejected": False}


def decisions(width: int) -> Iterable[tuple[int, ...]]:
    return itertools.product((0, 1), repeat=width)


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract["status"] != "PLANNED_UNEXECUTED":
        raise SystemExit("P02 contract status changed before execution")

    fixture = contract["development_fixture"]
    demands = tuple(fixture["demands"])
    capacity = fixture["capacity"]
    permutations = list(itertools.permutations(range(len(demands))))
    rows = [
        evaluate_simultaneous(decision, demands, capacity, permutation, permutation)
        for decision in decisions(len(demands))
        for permutation in permutations
    ]

    identity = tuple(range(len(demands)))
    identity_count = sum(tuple(row["permutation"]) == identity for row in rows)
    unique_keys = {
        (tuple(row["decision"]), tuple(row["permutation"])) for row in rows
    }
    controls = [
        rejected_control("decision_only_swap_0_2", (2, 1, 0), (0, 1, 2)),
        rejected_control("demand_only_swap_0_2", (0, 1, 2), (2, 1, 0)),
    ]

    checks = [
        ("exact_case_count", len(rows) == fixture["planned_case_count"] == 48),
        ("identity_partition", identity_count == 8 and len(rows) - identity_count == 40),
        ("complete_unique_surface", len(unique_keys) == len(rows)),
        ("load_invariance", all(row["properties"]["load_equal"] for row in rows)),
        ("overload_invariance", all(row["properties"]["overload_equal"] for row in rows)),
        ("physical_feasibility_invariance", all(row["properties"]["physical_feasibility_equal"] for row in rows)),
        ("one_sided_controls_rejected", all(control["rejected"] for control in controls)),
        ("one_sided_controls_are_material", all(control["original_load"] != control["naive_transformed_load"] for control in controls)),
    ]
    if not all(passed for _, passed in checks):
        raise SystemExit("P02 development audit failed")

    result = {
        "story_date": "2026-11-24",
        "status": "EXECUTED_DEVELOPMENT_FIXTURE_PASSED",
        "execution": {
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": platform.python_version(),
            "command": "python3 phd-simulation/src/verify_permutation_p02.py",
            "source_sha256": sha256(Path(__file__)),
            "contract_sha256": sha256(CONTRACT_PATH),
            "independent_oracle_sha256": sha256(ORACLE_PATH),
            "data_provenance": "Deterministic synthetic fixture frozen in p02-permutation-contract-v1.json; no external data.",
        },
        "fixture": {
            "demands": list(demands),
            "capacity": capacity,
            "decision_generation": "itertools.product((0,1), repeat=3)",
            "permutation_generation": "itertools.permutations(range(3))",
        },
        "summary": {
            "cases_executed": len(rows),
            "identity_cases": identity_count,
            "nonidentity_cases": len(rows) - identity_count,
            "in_scope_counterexamples": sum(
                not all(row["properties"].values()) for row in rows
            ),
            "out_of_precondition_controls_rejected": sum(
                control["rejected"] for control in controls
            ),
            "checks_passed": sum(passed for _, passed in checks),
        },
        "checks": [{"name": name, "passed": passed} for name, passed in checks],
        "rejected_controls": controls,
        "rows": rows,
        "resource_counters": {
            "protocol_formulation_passes": 0,
            "protocol_mutants": 0,
            "sdk_statevectors": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
            "pilot_baseline_reserved": False,
        },
        "limitations": [
            "Development evidence for one three-item deterministic synthetic fixture.",
            "The result checks a physical dot-product relabeling only; it does not cover auxiliary-bit, QUBO-variable, circuit-index or optimizer invariance.",
            "No power flow, restoration, uncertainty, real microgrid or quantum advantage is addressed.",
        ],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
