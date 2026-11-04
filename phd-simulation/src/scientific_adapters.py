"""Fail-closed L1--L4 adapter contracts for mutation-pilot callbacks.

This module is intentionally scientific-computation free.  It constructs and
validates STUB_INTERFACE_TEST records only: no mutant classification, circuit,
statevector, exhaustive formulation pass, or probability calculation occurs.
"""
import math

from mutation_harness import CAPS, ProtocolViolation


LAYER_PREFIXES = ("L1", "L2", "L3", "L4")
ZERO_CONSUMPTION = {name: 0 for name in CAPS}


def layer_code(description):
    """Return the protocol layer prefix, rejecting unknown descriptions."""
    matches = [code for code in LAYER_PREFIXES if description.startswith(code)]
    if len(matches) != 1:
        raise ProtocolViolation(f"unsupported scientific layer: {description}")
    return matches[0]


def _stub_observation(layer):
    common = {"status": "STUB_ONLY", "measurements_performed": 0}
    if layer == "L1":
        return {**common, "oracle_family": "exact_enumeration",
                "encoded_states_examined": 0, "reduced_decisions_examined": 0}
    if layer == "L2":
        return {**common, "oracle_family": "phase_aligned_statevector",
                "angle_cases_examined": 0, "max_component_error": None,
                "norm_squared_error": None, "phase_alignment": None}
    if layer == "L3":
        return {**common, "oracle_family": "probability_readout",
                "probabilities_examined": 0, "normalization_error": None,
                "expected_energy_error": None}
    if layer == "L4":
        return {**common, "oracle_family": "application_invariants",
                "physical_feasibility": None, "auxiliary_consistency": None,
                "separate_metrics": True}
    raise ProtocolViolation(f"unsupported scientific layer: {layer}")


def build_stub_record(plan_record):
    """Build a no-science interface fixture for one frozen plan record."""
    if plan_record["id"] == "baseline":
        layers = list(LAYER_PREFIXES)
    else:
        layers = [layer_code(plan_record["layer"])]
    return {
        "schema_version": 1,
        "mode": "STUB_INTERFACE_TEST",
        "record_id": plan_record["id"],
        "record_kind": plan_record["kind"],
        "layers": layers,
        "declared_future_consumption": plan_record["consumption"],
        "actual_consumption": dict(ZERO_CONSUMPTION),
        "scientific_verdict": None,
        "observations": {layer: _stub_observation(layer) for layer in layers},
    }


def _finite_or_none(value):
    return value is None or (
        isinstance(value, (int, float)) and not isinstance(value, bool)
        and math.isfinite(value)
    )


def validate_stub_record(plan_record, result):
    """Validate a stub record and return it; raise on any scope escape."""
    required = {
        "schema_version", "mode", "record_id", "record_kind", "layers",
        "declared_future_consumption", "actual_consumption",
        "scientific_verdict", "observations",
    }
    if set(result) != required:
        raise ProtocolViolation("stub record fields do not exactly match schema")
    if result["schema_version"] != 1 or result["mode"] != "STUB_INTERFACE_TEST":
        raise ProtocolViolation("record is not schema-v1 STUB_INTERFACE_TEST")
    if result["record_id"] != plan_record["id"] or result["record_kind"] != plan_record["kind"]:
        raise ProtocolViolation("record identity does not match frozen plan")
    expected_layers = list(LAYER_PREFIXES) if plan_record["id"] == "baseline" else [
        layer_code(plan_record["layer"])]
    if result["layers"] != expected_layers or list(result["observations"]) != expected_layers:
        raise ProtocolViolation("adapter layers/order do not match frozen plan")
    if result["declared_future_consumption"] != plan_record["consumption"]:
        raise ProtocolViolation("future consumption does not match frozen plan")
    if result["actual_consumption"] != ZERO_CONSUMPTION:
        raise ProtocolViolation("stub interface test consumed protocol resources")
    if result["scientific_verdict"] is not None:
        raise ProtocolViolation("stub interface test cannot emit a scientific verdict")

    for layer in expected_layers:
        observation = result["observations"][layer]
        if observation.get("status") != "STUB_ONLY" or observation.get("measurements_performed") != 0:
            raise ProtocolViolation(f"{layer} observation is not empty stub evidence")
        expected_fields = set(_stub_observation(layer))
        if set(observation) != expected_fields:
            raise ProtocolViolation(f"{layer} observation fields do not match schema")
        for key, value in observation.items():
            if key.endswith("error") and not _finite_or_none(value):
                raise ProtocolViolation(f"{layer} contains a non-finite metric")
        if layer == "L1" and (observation["encoded_states_examined"] != 0 or
                              observation["reduced_decisions_examined"] != 0):
            raise ProtocolViolation("L1 stub performed enumeration")
        if layer == "L2" and (observation["angle_cases_examined"] != 0 or
                              any(observation[name] is not None for name in
                                  ("max_component_error", "norm_squared_error", "phase_alignment"))):
            raise ProtocolViolation("L2 stub contains statevector evidence")
        if layer == "L3" and (observation["probabilities_examined"] != 0 or
                              observation["normalization_error"] is not None or
                              observation["expected_energy_error"] is not None):
            raise ProtocolViolation("L3 stub contains readout evidence")
        if layer == "L4" and (observation["physical_feasibility"] is not None or
                              observation["auxiliary_consistency"] is not None or
                              observation["separate_metrics"] is not True):
            raise ProtocolViolation("L4 stub conflates or populates application metrics")
    return result
