#!/usr/bin/env python3
"""Project-specific structural contract; no scientific callbacks or evidence IO."""
import re


def validate_record(record, schema):
    errors = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    if set(record) != set(schema["required_fields"]):
        errors.append("exact record fields required")
    if not isinstance(record.get("id"), str) or not re.fullmatch(r"SYN[0-9]{2}", record["id"]):
        errors.append("synthetic-only identity required")
    cls = record.get("fault_class")
    detector = record.get("minimum_detecting_layer")
    if not isinstance(cls, str) or cls not in schema["fault_classes"]:
        errors.append("unknown fault class")
    elif detector not in schema["class_detectors"][cls]:
        errors.append("detector incompatible with fault class")
    if detector not in schema["layers"]:
        errors.append("unknown detector")
    for name in ("precondition", "blindness_reason"):
        if not isinstance(record.get(name), str) or not record[name].strip():
            errors.append(name + " must explain the claim")
    blind = record.get("known_blind_layers")
    if not isinstance(blind, list) or not blind:
        errors.append("explicit nonempty blind-layer list required")
    elif any(not isinstance(x, str) or x not in schema["layers"] for x in blind):
        errors.append("unknown blind layer")
    elif len(set(blind)) != len(blind) or detector in blind:
        errors.append("duplicate or contradictory blind layer")
    status = record.get("evidence_status")
    evidence = record.get("evidence")
    if status not in schema["evidence_statuses"]:
        errors.append("unsupported evidence status")
    elif status == "PROSPECTIVE_UNEXECUTED":
        if evidence is not None:
            errors.append("prospective record must not claim evidence")
    else:
        if not isinstance(evidence, dict) or set(evidence) != {"path", "sha256"}:
            errors.append("reference needs path and digest")
        else:
            path, digest = evidence["path"], evidence["sha256"]
            if not isinstance(path, str) or not re.fullmatch(r"results/synthetic-[a-z0-9-]+\.json", path):
                errors.append("synthetic local reference required")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                errors.append("invalid reference digest")
    if record.get("pilot_mutant") is not False:
        errors.append("pilot overlap prohibited")
    resources = record.get("resource_boundary")
    keys = set(schema["resource_counters"]) | {schema["baseline_flag"]}
    if not isinstance(resources, dict) or set(resources) != keys:
        errors.append("complete exact resource boundary required")
    else:
        for key in schema["resource_counters"]:
            if type(resources[key]) is not int or resources[key] != 0:
                errors.append(key + " must be integer zero")
        if resources[schema["baseline_flag"]] is not False:
            errors.append("baseline reservation prohibited")
    return errors
