"""Bounded synthetic verification for explicit distribution aggregation."""

import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path

from application_metrics import evaluate_state
from distribution_metrics import DistributionInputError, aggregate
from independent_feasibility import bits_q0_first


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "distribution_metrics.py"
OUTPUT = ROOT / "results" / "2026-11-13-distribution-metrics.json"


def build_support():
    rows = []
    for index in range(64):
        report = evaluate_state(
            bits_q0_first(index % 8, 3),
            bits_q0_first(index // 8, 3),
            [2, 3, 4],
            5,
            [1, 2, 4],
        )
        rows.append({
            "index": index,
            "physical_feasible": report["physical"]["feasible"],
            "auxiliary_consistent": report["auxiliary"]["consistent"],
            "category": report["category"],
        })
    return rows


def check(name, passed, detail=None):
    row = {"name": name, "passed": bool(passed)}
    if detail is not None:
        row["detail"] = detail
    return row


def close(actual, expected):
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12)


def main():
    support = build_support()
    uniform = aggregate(support, [1 / 64] * 64)
    joint_delta_weights = [0.0] * 64
    joint_delta_weights[3] = 1.0
    joint_delta = aggregate(support, joint_delta_weights)
    physical_only_weights = [0.0] * 64
    physical_only_weights[0] = 1.0
    physical_only = aggregate(support, physical_only_weights)
    mixture_weights = [0.0] * 64
    mixture_weights[3] = 0.25
    mixture_weights[0] = 0.50
    mixture_weights[5] = 0.25
    mixture = aggregate(support, mixture_weights)

    checks = [
        check("uniform distribution reproduces physical mass 40/64", close(uniform["physical_feasible_mass"], 40 / 64), uniform),
        check("uniform distribution reproduces auxiliary and joint mass 5/64", close(uniform["auxiliary_consistent_mass"], 5 / 64) and close(uniform["joint_valid_mass"], 5 / 64)),
        check("joint-valid point mass reports all three masses as one", all(close(joint_delta[key], 1.0) for key in ("physical_feasible_mass", "auxiliary_consistent_mass", "joint_valid_mass"))),
        check("physical-only point mass keeps auxiliary and joint at zero", close(physical_only["physical_feasible_mass"], 1.0) and close(physical_only["auxiliary_consistent_mass"], 0.0) and close(physical_only["joint_valid_mass"], 0.0)),
        check("three-point analytic mixture preserves separate masses", close(mixture["physical_feasible_mass"], 0.75) and close(mixture["auxiliary_consistent_mass"], 0.25) and close(mixture["joint_valid_mass"], 0.25), mixture),
        check("category masses partition every tested distribution", all(close(math.fsum(result["category_mass"].values()), 1.0) for result in (uniform, joint_delta, physical_only, mixture))),
    ]

    malformed = []
    malformed.append((support, [1 / 64] * 63))
    malformed.append((support, [1 / 64] * 63 + [-1 / 64]))
    malformed.append((support, [1 / 64] * 63 + [float("nan")]))
    malformed.append((support, [1 / 64] * 63 + [True]))
    malformed.append((support, [1 / 128] * 64))
    duplicate = [dict(row) for row in support]
    duplicate[10]["index"] = 9
    malformed.append((duplicate, [1 / 64] * 64))
    tampered = [dict(row) for row in support]
    tampered[0]["category"] = "NEITHER"
    malformed.append((tampered, [1 / 64] * 64))
    rejected = 0
    for reports, probabilities in malformed:
        try:
            aggregate(reports, probabilities)
        except DistributionInputError:
            rejected += 1
    checks.append(check("seven malformed distributions and supports fail closed", rejected == len(malformed), {"rejected": rejected}))
    checks.append(check("all tested masses remain within probability bounds", all(0.0 <= result[key] <= 1.0 for result in (uniform, joint_delta, physical_only, mixture) for key in ("physical_feasible_mass", "auxiliary_consistent_mass", "joint_valid_mass"))))

    payload = {
        "schema_version": 1,
        "status": "EXECUTED_DEVELOPMENT_DISTRIBUTION_METRIC_AUDIT",
        "scope": "DEVELOPMENT_TEST_OUTSIDE_FROZEN_MUTATION_PILOT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/verify_distribution_metrics.py",
        "python": platform.python_version(),
        "data": "Four explicit synthetic distributions over the fixed 64-state fixture; no external dataset",
        "randomness": "None; deterministic distributions and exhaustive support",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "checks": checks,
        "distributions": {"uniform": uniform, "joint_point_mass": joint_delta, "physical_only_point_mass": physical_only, "three_point_mixture": mixture},
        "summary": {
            "checks_passed": sum(item["passed"] for item in checks),
            "checks_total": len(checks),
            "support_size": len(support),
            "synthetic_distributions_tested": 4,
            "malformed_cases_rejected": rejected,
            "protocol_formulation_passes_executed": 0,
            "protocol_mutants_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
            "pilot_baseline_reserved": False,
        },
        "limitations": [
            "Weights are constructed synthetic distributions, not circuit outputs or measurements.",
            "Only one static capacity fixture is represented.",
            "No objective quality, uncertainty, resilience physics, optimizer, or quantum advantage is evaluated.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(item["passed"] for item in checks):
        raise SystemExit("distribution metric audit failed")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
