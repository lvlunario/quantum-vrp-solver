"""Validate the frozen application-oracle contract without executing P01."""

import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "application-oracle-contract-v1.json"
SOURCE = ROOT / "src" / "validate_application_oracle_contract.py"
OUTPUT = ROOT / "results" / "2026-11-16-application-oracle-contract-validation.json"
EXPECTED_LAYERS = ["decision_physical", "encoded_state", "distribution"]
EXPECTED_IMPLEMENTATIONS = [
    "src/independent_feasibility.py:evaluate",
    "src/application_metrics.py:evaluate_state",
    "src/distribution_metrics.py:aggregate",
]


class ContractError(ValueError):
    pass


def validate(contract):
    if contract.get("schema_version") != 1 or contract.get("contract_id") != "application-oracle-v1":
        raise ContractError("unexpected schema or contract id")
    if contract.get("status") != "FROZEN_FOR_DEVELOPMENT_TESTS":
        raise ContractError("contract must be frozen before testing")
    layers = contract.get("layers")
    if not isinstance(layers, list) or [layer.get("id") for layer in layers] != EXPECTED_LAYERS:
        raise ContractError("layer order and identifiers are fixed")
    if [layer.get("implementation") for layer in layers] != EXPECTED_IMPLEMENTATIONS:
        raise ContractError("layer implementations changed")
    for relative in [item.split(":", 1)[0] for item in EXPECTED_IMPLEMENTATIONS]:
        if not (ROOT / relative).is_file():
            raise ContractError(f"missing implementation: {relative}")

    prop = contract.get("preregistered_property", {})
    if prop.get("id") != "P01_NONNEGATIVE_DEMAND_MONOTONICITY" or prop.get("status") != "PLANNED_UNEXECUTED":
        raise ContractError("P01 must remain preregistered and unexecuted")
    fixture = prop.get("development_fixture", {})
    if fixture.get("demands") != [2, 3, 4] or fixture.get("capacity") != 5 or fixture.get("ordered_pairs_max") != 27:
        raise ContractError("development fixture or bound changed")
    if len(prop.get("preconditions", [])) != 4 or len(prop.get("excluded_claims", [])) != 4 or len(prop.get("planned_checks", [])) != 6:
        raise ContractError("P01 preconditions, exclusions and checks must be explicit")

    boundary = contract.get("resource_boundary", {})
    numeric = [value for key, value in boundary.items() if key.endswith("_authorized") and key != "pilot_baseline_reservation_authorized"]
    if len(numeric) != 6 or any(value != 0 or isinstance(value, bool) for value in numeric):
        raise ContractError("all numerical pilot authorizations must be integer zero")
    if boundary.get("pilot_baseline_reservation_authorized") is not False:
        raise ContractError("baseline reservation must remain false")
    return {
        "layer_ids": EXPECTED_LAYERS,
        "ordered_pairs_max": fixture["ordered_pairs_max"],
        "property_status": prop["status"],
        "resource_boundary": boundary,
    }


def check(name, passed, detail=None):
    row = {"name": name, "passed": bool(passed)}
    if detail is not None:
        row["detail"] = detail
    return row


def main():
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    summary = validate(contract)
    checks = [
        check("schema, identifier and frozen status are exact", True),
        check("three layers are ordered and separately named", summary["layer_ids"] == EXPECTED_LAYERS, {"layers": summary["layer_ids"]}),
        check("all referenced implementations exist", True),
        check("P01 remains explicitly planned and unexecuted", summary["property_status"] == "PLANNED_UNEXECUTED"),
        check("synthetic fixture and 27-pair bound are frozen", summary["ordered_pairs_max"] == 27),
        check("preconditions, excluded claims and planned checks are complete", True),
        check("all scientific execution authorizations remain zero or false", all(value in (0, False) for value in summary["resource_boundary"].values())),
    ]

    mutations = []
    changed = copy.deepcopy(contract); changed["layers"][1]["id"] = "physical_proxy"; mutations.append(changed)
    changed = copy.deepcopy(contract); changed["preregistered_property"]["status"] = "EXECUTED"; mutations.append(changed)
    changed = copy.deepcopy(contract); changed["preregistered_property"]["development_fixture"]["ordered_pairs_max"] = 28; mutations.append(changed)
    changed = copy.deepcopy(contract); changed["resource_boundary"]["sdk_statevectors_authorized"] = 1; mutations.append(changed)
    changed = copy.deepcopy(contract); changed["resource_boundary"]["pilot_baseline_reservation_authorized"] = True; mutations.append(changed)
    rejected = 0
    for mutation in mutations:
        try:
            validate(mutation)
        except ContractError:
            rejected += 1
    checks.append(check("five contract mutations fail closed", rejected == 5, {"rejected": rejected}))

    payload = {
        "schema_version": 1,
        "status": "EXECUTED_CONTRACT_VALIDATION_PROPERTY_UNEXECUTED",
        "scope": "DEVELOPMENT_ONLY_OUTSIDE_FROZEN_MUTATION_PILOT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python src/validate_application_oracle_contract.py",
        "python": platform.python_version(),
        "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "checks": checks,
        "validated_contract": summary,
        "summary": {
            "checks_passed": sum(item["passed"] for item in checks),
            "checks_total": len(checks),
            "contract_mutations_rejected": rejected,
            "preregistered_property_status": "PLANNED_UNEXECUTED",
            "monotonicity_pairs_executed": 0,
            "protocol_formulation_passes_executed": 0,
            "protocol_mutants_executed": 0,
            "sdk_statevectors_executed": 0,
            "search_evaluations": 0,
            "shots": 0,
            "hardware_jobs": 0,
            "pilot_baseline_reserved": False
        },
        "limitations": [
            "This validates a contract and its fail-closed boundary; it does not execute P01.",
            "Implementation existence is checked, not full semantic equivalence across layers.",
            "No scientific or quantum execution is authorized by a passing validation."
        ]
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(item["passed"] for item in checks):
        raise SystemExit("contract validation failed")
    print(json.dumps(payload["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
