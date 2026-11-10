"""Execute the bounded independent-feasibility audit on the synthetic fixture."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

from independent_feasibility import (
    FeasibilityInputError,
    bits_q0_first,
    evaluate,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "independent_feasibility.py"
OUTPUT = ROOT / "results" / "2026-11-10-independent-feasibility.json"
DEMANDS = (2, 3, 4)
CAPACITY = 5


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []

    def check(name, passed, detail=None):
        row = {"name": name, "passed": bool(passed)}
        if detail is not None:
            row["detail"] = detail
        checks.append(row)
        if not passed:
            raise AssertionError(name)

    expected_loads = [0, 2, 3, 5, 4, 6, 7, 9]
    expected_feasible = [True, True, True, True, True, False, False, False]
    decision_rows = [
        {"index": index, **evaluate(bits_q0_first(index, 3), DEMANDS, CAPACITY)}
        for index in range(8)
    ]
    check("hand-enumerated eight-load table matches",
          [row["load"] for row in decision_rows] == expected_loads,
          {"loads": [row["load"] for row in decision_rows]})
    check("physical feasibility matches the direct capacity requirement",
          [row["feasible"] for row in decision_rows] == expected_feasible)
    check("capacity boundary is feasible with zero headroom",
          decision_rows[3]["load"] == 5 and decision_rows[3]["feasible"] and
          decision_rows[3]["headroom"] == 0)
    check("overload margins are exact for all infeasible decisions",
          [decision_rows[i]["overload"] for i in (5, 6, 7)] == [1, 2, 4])

    encoded_rows = []
    proxy_disagreements = []
    for index in range(64):
        bits = bits_q0_first(index, 6)
        decision = bits[:3]
        slack = bits[3] + 2 * bits[4] + 4 * bits[5]
        physical = evaluate(decision, DEMANDS, CAPACITY)
        encoded_consistent = physical["load"] + slack == CAPACITY
        row = {
            "index": index,
            "decision_bits": list(decision),
            "auxiliary_bits": list(bits[3:]),
            "slack": slack,
            "physical_feasible": physical["feasible"],
            "encoding_consistent": encoded_consistent,
        }
        encoded_rows.append(row)
        if physical["feasible"] != encoded_consistent:
            proxy_disagreements.append(index)
    check("physical verdict is invariant across all eight auxiliary encodings",
          all(len({row["physical_feasible"] for row in encoded_rows
                   if row["decision_bits"] == list(bits_q0_first(i, 3))}) == 1
              for i in range(8)))
    check("encoding consistency is not a physical-feasibility proxy",
          len(proxy_disagreements) > 0,
          {"disagreement_count": len(proxy_disagreements),
           "first_indices": proxy_disagreements[:8]})

    invalid_decisions = [(), (0, 1), (0, 1, 2), (True, 0, 1)]
    rejected = 0
    for decisions in invalid_decisions:
        try:
            evaluate(decisions, DEMANDS, CAPACITY)
        except FeasibilityInputError:
            rejected += 1
    check("empty, wrong-length, nonbinary and Boolean decisions are rejected",
          rejected == len(invalid_decisions), {"rejected": rejected})

    invalid_models = [
        ((0, 1, 0), (2, -3, 4), 5),
        ((0, 1, 0), (2, 3, 4), -1),
        ((0, 1, 0), (2.0, 3, 4), 5),
    ]
    rejected = 0
    for decisions, demands, capacity in invalid_models:
        try:
            evaluate(decisions, demands, capacity)
        except FeasibilityInputError:
            rejected += 1
    check("negative and noninteger model data are rejected",
          rejected == len(invalid_models), {"rejected": rejected})

    result = {
        "schema_version": 1,
        "status": "EXECUTED_DEVELOPMENT_FEASIBILITY_AUDIT",
        "scope": "DEVELOPMENT_TEST_OUTSIDE_FROZEN_MUTATION_PILOT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_independent_feasibility.py",
        "python": platform.python_version(),
        "source_sha256": sha256(SOURCE),
        "data": "Fixed synthetic three-load fixture; no external dataset",
        "randomness": "None; exhaustive deterministic enumeration",
        "config": {"demands": list(DEMANDS), "capacity": CAPACITY},
        "decision_rows": decision_rows,
        "encoded_rows": encoded_rows,
        "checks": checks,
        "summary": {
            "checks_passed": sum(row["passed"] for row in checks),
            "checks_total": len(checks),
            "load_decisions_examined": 8,
            "encoded_states_examined_for_auxiliary_invariance": 64,
            "physical_feasible_decisions": sum(expected_feasible),
            "encoding_proxy_disagreements": len(proxy_disagreements),
            "pilot_baseline_reserved": False,
            "protocol_mutants_executed": 0,
            "protocol_formulation_passes_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0
        },
        "limitations": [
            "One deterministic synthetic capacity constraint only.",
            "The 64-state auxiliary-invariance audit is development evidence, not M01 or M02 execution.",
            "No objective quality, resilience physics, uncertainty, circuit, solver, or quantum advantage is tested."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
