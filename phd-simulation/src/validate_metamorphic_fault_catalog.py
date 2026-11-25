#!/usr/bin/env python3
"""Validate fault routing and existing evidence without executing mutants."""

from __future__ import annotations

import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "docs" / "metamorphic-fault-catalog-v1.json"
OUTPUT_PATH = ROOT / "results" / "2026-11-25-metamorphic-fault-routing.json"

EXPECTED_IDS = [f"MF{i:02d}" for i in range(1, 9)]
EXPECTED_SOURCES = {"P01": 3, "P02": 4, "APPLICATION_BOUNDARY": 1}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evidence(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate_structure(catalog: dict) -> list[str]:
    errors: list[str] = []
    faults = catalog.get("faults", [])
    ids = [fault.get("id", "") for fault in faults]
    prefixes = [item.split("_", 1)[0] for item in ids]
    if catalog.get("schema_version") != 1:
        errors.append("schema version mismatch")
    if catalog.get("status") != "ROUTING_VALIDATED_NO_MUTANTS_EXECUTED":
        errors.append("catalog status changed")
    if prefixes != EXPECTED_IDS or len(set(ids)) != 8:
        errors.append("fault identities are incomplete, reordered, or duplicated")
    counts = {key: sum(f.get("source_property") == key for f in faults) for key in EXPECTED_SOURCES}
    if counts != EXPECTED_SOURCES:
        errors.append("P01/P02/application coverage mismatch")
    allowed = set(catalog.get("allowed_layers", []))
    if not allowed or any(f.get("minimum_detecting_layer") not in allowed for f in faults):
        errors.append("unknown detecting layer")
    if any(f.get("pilot_mutant") is not False for f in faults):
        errors.append("catalog entry overlaps the frozen mutation pilot")
    if any(f.get("id", "").startswith("M0") and not f.get("id", "").startswith("MF") for f in faults):
        errors.append("pilot mutant identifier reused")
    resource = catalog.get("resource_boundary", {})
    if any(value not in (0, False) for value in resource.values()):
        errors.append("resource boundary is nonzero")
    confirmed = [f for f in faults if f.get("evidence_status") == "CONFIRMED_EXISTING_DEVELOPMENT_EVIDENCE"]
    prospective = [f for f in faults if f.get("evidence_status") == "ROUTED_PROSPECTIVE_NOT_EXECUTED_AS_FAULT"]
    if len(confirmed) != 6 or len(prospective) != 2:
        errors.append("evidence-status partition mismatch")
    if any(not f.get("evidence") for f in confirmed) or any(f.get("evidence") is not None for f in prospective):
        errors.append("evidence path does not match evidence status")
    return errors


def evidence_assertions(catalog: dict) -> tuple[list[dict], dict[str, str]]:
    paths = sorted({f["evidence"] for f in catalog["faults"] if f["evidence"]})
    evidence = {path: load_evidence(path) for path in paths}
    p01 = evidence["results/2026-11-18-p01-monotonicity.json"]
    auxiliary = evidence["results/2026-11-19-auxiliary-nonmonotonicity.json"]
    p02 = evidence["results/2026-11-24-p02-permutation.json"]
    metrics = evidence["results/2026-11-11-application-metrics.json"]
    checks = [
        {"name": "p01_two_controls_rejected", "passed": p01["summary"]["out_of_precondition_controls_rejected"] == 2 and all(c["rejected"] for c in p01["out_of_precondition_controls"])},
        {"name": "auxiliary_bidirectional_counterexamples", "passed": auxiliary["summary"]["transition_counts"]["false_to_true"] > 0 and auxiliary["summary"]["transition_counts"]["true_to_false"] > 0 and auxiliary["summary"]["physical_p01_violations"] == 0},
        {"name": "p02_one_sided_controls_rejected", "passed": p02["summary"]["out_of_precondition_controls_rejected"] == 2 and all(c["rejected"] for c in p02["rejected_controls"])},
        {"name": "p02_controls_material", "passed": all(c["original_load"] != c["naive_transformed_load"] for c in p02["rejected_controls"])},
        {"name": "application_metrics_separated", "passed": metrics["summary"]["physical_feasible_states"] == 40 and metrics["summary"]["auxiliary_consistent_states"] == 5 and metrics["summary"]["category_counts"]["PHYSICAL_ONLY"] == 35},
    ]
    return checks, {path: digest(ROOT / path) for path in paths}


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    structure_errors = validate_structure(catalog)
    evidence_checks, evidence_digests = evidence_assertions(catalog)
    structure_checks = [
        {"name": "catalog_structure", "passed": not structure_errors, "errors": structure_errors},
        {"name": "eight_unique_faults", "passed": len(catalog["faults"]) == len({f["id"] for f in catalog["faults"]}) == 8},
        {"name": "no_pilot_overlap", "passed": all(not f["pilot_mutant"] for f in catalog["faults"])},
        {"name": "zero_resource_boundary", "passed": all(v in (0, False) for v in catalog["resource_boundary"].values())},
    ]

    mutations = [
        ("duplicate_id", lambda c: c["faults"][1].__setitem__("id", c["faults"][0]["id"])),
        ("unknown_layer", lambda c: c["faults"][0].__setitem__("minimum_detecting_layer", "L9_UNKNOWN")),
        ("pilot_overlap", lambda c: c["faults"][0].__setitem__("pilot_mutant", True)),
        ("resource_consumption", lambda c: c["resource_boundary"].__setitem__("protocol_mutants", 1)),
        ("missing_evidence", lambda c: c["faults"][0].__setitem__("evidence", None)),
        ("false_execution_claim", lambda c: c["faults"][5].__setitem__("evidence_status", "CONFIRMED_EXISTING_DEVELOPMENT_EVIDENCE")),
    ]
    mutation_results = []
    for name, mutate in mutations:
        changed = copy.deepcopy(catalog)
        mutate(changed)
        mutation_results.append({"name": name, "rejected": bool(validate_structure(changed))})

    all_checks = structure_checks + evidence_checks
    if not all(c["passed"] for c in all_checks) or not all(m["rejected"] for m in mutation_results):
        raise SystemExit("metamorphic fault catalog validation failed")

    output = {
        "story_date": "2026-11-25",
        "status": "ROUTING_VALIDATED_NO_MUTANTS_EXECUTED",
        "execution": {
            "executed_at_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": platform.python_version(),
            "command": "python3 phd-simulation/src/validate_metamorphic_fault_catalog.py",
            "source_sha256": digest(Path(__file__)),
            "catalog_sha256": digest(CATALOG_PATH),
            "evidence_sha256": evidence_digests,
        },
        "summary": {
            "faults_routed": len(catalog["faults"]),
            "existing_evidence_confirmed": 6,
            "prospective_routes_unexecuted": 2,
            "checks_passed": len(all_checks),
            "invalid_catalog_mutations_rejected": sum(m["rejected"] for m in mutation_results),
            "catalog_fault_executions": 0,
        },
        "checks": all_checks,
        "invalid_catalog_mutations": mutation_results,
        "routes": catalog["faults"],
        "resource_counters": catalog["resource_boundary"],
        "limitations": catalog["limitations"],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
