#!/usr/bin/env python3
"""Validate the frozen P02 contract without executing P02 cases."""

from __future__ import annotations

import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "p02-permutation-contract-v1.json"
OUTPUT = ROOT / "results" / "2026-11-23-p02-contract-validation.json"

EXPECTED_PROPERTY = "P02_SIMULTANEOUS_DECISION_DEMAND_PERMUTATION_INVARIANCE"
EXPECTED_METRICS = ["load", "overload", "physical_feasibility"]
REQUIRED_EXCLUSION_FRAGMENTS = [
    "auxiliary consistency",
    "QUBO energy",
    "statevector",
    "optimizer output",
    "only decisions or only demands",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fixture = contract.get("development_fixture", {})
    resource = contract.get("resource_boundary", {})

    if contract.get("schema_version") != 1 or contract.get("property_id") != EXPECTED_PROPERTY:
        errors.append("identity/schema mismatch")
    if contract.get("status") != "PLANNED_UNEXECUTED":
        errors.append("status must remain PLANNED_UNEXECUTED")
    if fixture.get("demands") != [2, 3, 4] or fixture.get("capacity") != 5:
        errors.append("fixture changed")
    if fixture.get("planned_case_count") != 48:
        errors.append("planned count must equal 8 decisions times 6 permutations")
    if fixture.get("identity_cases") != 8 or fixture.get("nonidentity_cases") != 40:
        errors.append("identity partition mismatch")
    if contract.get("preserved_metrics") != EXPECTED_METRICS:
        errors.append("preserved metrics changed")
    exclusions = "\n".join(contract.get("excluded_claims", []))
    if any(fragment not in exclusions for fragment in REQUIRED_EXCLUSION_FRAGMENTS):
        errors.append("required boundary exclusion missing")
    if resource != {
        "property_cases_authorized_by_freeze": 0,
        "protocol_formulation_passes_authorized": 0,
        "protocol_mutants_authorized": 0,
        "sdk_statevectors_authorized": 0,
        "search_evaluations_authorized": 0,
        "shots_authorized": 0,
        "hardware_jobs_authorized": 0,
        "pilot_baseline_reservation_authorized": False,
    }:
        errors.append("resource boundary is not zero/false")
    return errors


def main() -> None:
    contract_bytes = CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)
    checks = [
        ("identity_and_schema", contract.get("schema_version") == 1 and contract.get("property_id") == EXPECTED_PROPERTY),
        ("planned_status", contract.get("status") == "PLANNED_UNEXECUTED"),
        ("fixed_fixture", contract.get("development_fixture", {}).get("demands") == [2, 3, 4] and contract.get("development_fixture", {}).get("capacity") == 5),
        ("planned_case_count", contract.get("development_fixture", {}).get("planned_case_count") == 48),
        ("identity_partition", contract.get("development_fixture", {}).get("identity_cases") == 8 and contract.get("development_fixture", {}).get("nonidentity_cases") == 40),
        ("preserved_metrics", contract.get("preserved_metrics") == EXPECTED_METRICS),
        ("boundary_exclusions", all(f in "\n".join(contract.get("excluded_claims", [])) for f in REQUIRED_EXCLUSION_FRAGMENTS)),
        ("zero_resource_authorization", not validate(contract)),
    ]
    if not all(passed for _, passed in checks):
        raise SystemExit("frozen contract failed validation")

    mutations: list[tuple[str, Any]] = [
        ("executed_status", lambda c: c.__setitem__("status", "EXECUTED")),
        ("wrong_case_count", lambda c: c["development_fixture"].__setitem__("planned_case_count", 47)),
        ("missing_auxiliary_exclusion", lambda c: c.__setitem__("excluded_claims", c["excluded_claims"][1:])),
        ("changed_metric", lambda c: c.__setitem__("preserved_metrics", ["load", "physical_feasibility"])),
        ("authorized_property_cases", lambda c: c["resource_boundary"].__setitem__("property_cases_authorized_by_freeze", 48)),
    ]
    mutation_results = []
    for name, mutate in mutations:
        changed = copy.deepcopy(contract)
        mutate(changed)
        errors = validate(changed)
        mutation_results.append({"name": name, "rejected": bool(errors), "errors": errors})
    if not all(item["rejected"] for item in mutation_results):
        raise SystemExit("contract mutation escaped validation")

    source_bytes = Path(__file__).read_bytes()
    result = {
        "story_date": "2026-11-23",
        "execution": {
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": platform.python_version(),
            "source_sha256": sha256_bytes(source_bytes),
            "contract_sha256": sha256_bytes(contract_bytes),
            "command": "python3 phd-simulation/src/validate_p02_permutation_contract.py",
        },
        "status": "CONTRACT_VALIDATED_PROPERTY_PLANNED_UNEXECUTED",
        "checks": [{"name": name, "passed": passed} for name, passed in checks],
        "checks_passed": sum(passed for _, passed in checks),
        "contract_mutations": mutation_results,
        "contract_mutations_rejected": sum(item["rejected"] for item in mutation_results),
        "property_execution": {
            "p02_cases_executed": 0,
            "identity_cases_executed": 0,
            "nonidentity_cases_executed": 0,
            "counterexamples_observed": None,
        },
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
            "This execution validates only the P02 contract structure and fail-closed boundary.",
            "No P02 decision-permutation case was generated or evaluated.",
            "No claim is made about quantum advantage or a real microgrid.",
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "checks_passed": result["checks_passed"], "contract_mutations_rejected": result["contract_mutations_rejected"], "p02_cases_executed": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
