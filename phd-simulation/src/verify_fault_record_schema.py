#!/usr/bin/env python3
"""Bounded synthetic structural checks, not catalog-fault executions."""
import copy
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from validate_fault_record_schema import validate_record

ROOT = Path(__file__).resolve().parents[1]


def run():
    schema_path = ROOT / "docs/fault-record-schema-v1.json"
    schema = json.loads(schema_path.read_text())
    base = {
        "id": "SYN01", "fault_class": "PRECONDITION",
        "precondition": "Both sides use the same fixed capacity.",
        "minimum_detecting_layer": "G0_TRANSFORM_PRECONDITION",
        "known_blind_layers": ["L4_PHYSICAL_APPLICATION_ORACLE"],
        "blindness_reason": "Independent single-state reports do not establish a shared pair precondition.",
        "evidence_status": "PROSPECTIVE_UNEXECUTED", "evidence": None,
        "pilot_mutant": False,
        "resource_boundary": {**dict.fromkeys(schema["resource_counters"], 0), "pilot_baseline_reserved": False}
    }
    positives = [base]
    for idx, cls, layer in [(2, "CROSS_LAYER_INFERENCE", "G0_SCOPE_CONTRACT"), (3, "METRIC_COLLAPSE", "L4_METRIC_SEPARATION_ORACLE")]:
        row = copy.deepcopy(base)
        row.update(id=f"SYN{idx:02}", fault_class=cls, minimum_detecting_layer=layer)
        positives.append(row)
    reference = copy.deepcopy(base)
    reference.update(id="SYN04", evidence_status="REFERENCE_DECLARED_NOT_VERIFIED",
                     evidence={"path": "results/synthetic-reference.json", "sha256": "0" * 64})
    positives.append(reference)
    # Intentionally fabricated reference bytes: syntax accepted, existence/truth not asserted.
    mutations = [
        ("missing_precondition", lambda r: r.pop("precondition")),
        ("blank_precondition", lambda r: r.update(precondition=" ")),
        ("unknown_field", lambda r: r.update(verdict="KILLED")),
        ("real_catalog_id", lambda r: r.update(id="MF06")),
        ("unknown_class", lambda r: r.update(fault_class="OTHER")),
        ("unknown_detector", lambda r: r.update(minimum_detecting_layer="L9")),
        ("wrong_class_detector", lambda r: r.update(minimum_detecting_layer="G0_SCOPE_CONTRACT")),
        ("missing_blind_list", lambda r: r.pop("known_blind_layers")),
        ("empty_blind_list", lambda r: r.update(known_blind_layers=[])),
        ("unknown_blind_layer", lambda r: r.update(known_blind_layers=["L9"])),
        ("duplicate_blind_layer", lambda r: r.update(known_blind_layers=r["known_blind_layers"] * 2)),
        ("detector_also_blind", lambda r: r.update(known_blind_layers=[r["minimum_detecting_layer"]])),
        ("blank_blind_reason", lambda r: r.update(blindness_reason="")),
        ("false_confirmation", lambda r: r.update(evidence_status="CONFIRMED")),
        ("prospective_with_evidence", lambda r: r.update(evidence=reference["evidence"])),
        ("declared_without_reference", lambda r: r.update(evidence_status="REFERENCE_DECLARED_NOT_VERIFIED")),
        ("pilot_overlap", lambda r: r.update(pilot_mutant=True)),
        ("empty_resources", lambda r: r.update(resource_boundary={})),
        ("missing_counter", lambda r: r["resource_boundary"].pop("shots")),
        ("unknown_counter", lambda r: r["resource_boundary"].update(other=0)),
        ("boolean_counter", lambda r: r["resource_boundary"].update(shots=False)),
        ("float_counter", lambda r: r["resource_boundary"].update(shots=0.0)),
        ("nonzero_counter", lambda r: r["resource_boundary"].update(shots=1)),
        ("baseline_integer_zero", lambda r: r["resource_boundary"].update(pilot_baseline_reserved=0))
    ]
    trials = []
    for name, mutate in mutations:
        row = copy.deepcopy(base)
        mutate(row)
        trials.append((name, row))
    for name, value in [("path_traversal", "../secret.json"), ("absolute_path", "/tmp/file.json")]:
        row = copy.deepcopy(reference)
        row["evidence"]["path"] = value
        trials.append((name, row))
    row = copy.deepcopy(reference)
    row["evidence"]["sha256"] = "bad"
    trials.append(("bad_digest", row))
    trials.append(("nonobject", []))
    good = [{"record": r, "errors": validate_record(r, schema)} for r in positives]
    bad = [{"name": n, "record": r, "errors": validate_record(r, schema)} for n, r in trials]
    assert all(not x["errors"] for x in good)
    assert all(x["errors"] for x in bad)
    paths = [schema_path, Path(__file__), ROOT / "src/validate_fault_record_schema.py"]
    output = {
        "story_date": "2026-11-26", "status": "EXECUTED_SYNTHETIC_SCHEMA_CHECKS_ONLY",
        "execution": {"executed_at_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
                      "command": "python3 phd-simulation/src/verify_fault_record_schema.py",
                      "input_data": "Deterministic synthetic records embedded in verifier; no real evidence references resolved.",
                      "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}},
        "summary": {"accepted_synthetic_records": len(good), "rejected_synthetic_records": len(bad), "checks_passed": len(good) + len(bad)},
        "accepted": good, "rejected": bad, "resource_counters": base["resource_boundary"],
        "limitations": schema["limitations"]
    }
    dest = ROOT / "results/2026-11-26-fault-record-schema.json"
    with dest.open("x") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    print(json.dumps(output["summary"]))


if __name__ == "__main__":
    run()
