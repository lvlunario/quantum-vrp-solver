"""Execute the bounded development audit for separated application metrics."""

import hashlib
import json
import platform
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from application_metrics import evaluate_state
from independent_feasibility import FeasibilityInputError, bits_q0_first


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "application_metrics.py"
OUTPUT = ROOT / "results" / "2026-11-11-application-metrics.json"
DEMANDS = [2, 3, 4]
CAPACITY = 5
WEIGHTS = [1, 2, 4]


def check(name, passed, detail=None):
    row = {"name": name, "passed": bool(passed)}
    if detail is not None:
        row["detail"] = detail
    return row


def main():
    rows = []
    per_decision = defaultdict(list)
    for index in range(64):
        decision = bits_q0_first(index % 8, 3)
        auxiliary = bits_q0_first(index // 8, 3)
        report = evaluate_state(decision, auxiliary, DEMANDS, CAPACITY, WEIGHTS)
        row = {
            "index": index,
            "decision_bits": list(decision),
            "auxiliary_bits": list(auxiliary),
            "load": report["physical"]["load"],
            "physical_feasible": report["physical"]["feasible"],
            "slack": report["auxiliary"]["slack"],
            "auxiliary_residual": report["auxiliary"]["residual"],
            "auxiliary_consistent": report["auxiliary"]["consistent"],
            "category": report["category"],
        }
        rows.append(row)
        per_decision[index % 8].append(row)

    counts = Counter(row["category"] for row in rows)
    physical_count = sum(row["physical_feasible"] for row in rows)
    auxiliary_count = sum(row["auxiliary_consistent"] for row in rows)
    consistent_per_decision = [
        sum(row["auxiliary_consistent"] for row in per_decision[index])
        for index in range(8)
    ]
    checks = [
        check("all 64 encoded states are enumerated exactly once", len(rows) == 64 and [r["index"] for r in rows] == list(range(64))),
        check("category partition matches the hand-derived fixture", counts == Counter({"PHYSICAL_ONLY": 35, "NEITHER": 24, "PHYSICAL_AND_AUXILIARY_VALID": 5}), dict(sorted(counts.items()))),
        check("uniform physical-feasibility mass is 40/64", physical_count == 40, {"count": physical_count, "mass": physical_count / 64}),
        check("uniform auxiliary-consistency mass is 5/64", auxiliary_count == 5, {"count": auxiliary_count, "mass": auxiliary_count / 64}),
        check("auxiliary consistency is a strict subset of physical feasibility", all(not r["auxiliary_consistent"] or r["physical_feasible"] for r in rows) and auxiliary_count < physical_count),
        check("each feasible decision has one consistent slack and each overloaded decision has none", consistent_per_decision == [1, 1, 1, 1, 1, 0, 0, 0], {"counts": consistent_per_decision}),
        check("report fields preserve separate names and exact residuals", all(r["auxiliary_residual"] == r["load"] + r["slack"] - CAPACITY for r in rows)),
    ]

    rejected = 0
    invalid = [
        ([0, 0, 0], [], DEMANDS, CAPACITY, WEIGHTS),
        ([0, 0, 0], [0, 1], DEMANDS, CAPACITY, WEIGHTS),
        ([0, 0, 0], [0, True, 0], DEMANDS, CAPACITY, WEIGHTS),
        ([0, 0, 0], [0, 1, 0], DEMANDS, CAPACITY, [1, 0, 4]),
        ([0, 0, 0], [0, 1, 0], DEMANDS, CAPACITY, [1, 2.0, 4]),
    ]
    for args in invalid:
        try:
            evaluate_state(*args)
        except FeasibilityInputError:
            rejected += 1
    checks.append(check("malformed auxiliary definitions fail closed", rejected == len(invalid), {"rejected": rejected}))

    payload = {
        "schema_version": 1,
        "status": "EXECUTED_DEVELOPMENT_APPLICATION_METRIC_AUDIT",
        "scope": "DEVELOPMENT_TEST_OUTSIDE_FROZEN_MUTATION_PILOT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_application_metrics.py",
        "python": platform.python_version(),
        "data": "Fixed synthetic three-load fixture; no external dataset",
        "randomness": "None; exhaustive deterministic enumeration",
        "config": {"demands": DEMANDS, "capacity": CAPACITY, "auxiliary_weights": WEIGHTS},
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "checks": checks,
        "summary": {
            "checks_passed": sum(item["passed"] for item in checks),
            "checks_total": len(checks),
            "encoded_states_examined": len(rows),
            "physical_feasible_states": physical_count,
            "auxiliary_consistent_states": auxiliary_count,
            "category_counts": dict(sorted(counts.items())),
            "protocol_formulation_passes_executed": 0,
            "protocol_mutants_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
            "pilot_baseline_reserved": False,
        },
        "rows": rows,
        "limitations": [
            "One deterministic synthetic capacity constraint only.",
            "Uniform mass is a counting diagnostic, not a circuit or optimizer result.",
            "No resilience physics, uncertainty, objective quality, quantum execution, or advantage is tested.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(item["passed"] for item in checks):
        raise SystemExit("application metric audit failed")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
