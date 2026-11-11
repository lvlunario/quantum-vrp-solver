"""Separate application feasibility from auxiliary encoding consistency.

This development-only adapter composes the independent capacity oracle with a
separately named slack-bit report.  It does not evaluate QUBO energy or run the
frozen mutation pilot.
"""

from independent_feasibility import FeasibilityInputError, evaluate


def _validate_weights(auxiliary_bits, weights):
    if not isinstance(auxiliary_bits, (list, tuple)) or not auxiliary_bits:
        raise FeasibilityInputError("auxiliary_bits must be a nonempty list or tuple")
    if not isinstance(weights, (list, tuple)) or len(weights) != len(auxiliary_bits):
        raise FeasibilityInputError("weights must match auxiliary bit length")
    if any(bit not in (0, 1) or isinstance(bit, bool) for bit in auxiliary_bits):
        raise FeasibilityInputError("auxiliary_bits must contain integer bits")
    if any(not isinstance(weight, int) or isinstance(weight, bool) or weight <= 0 for weight in weights):
        raise FeasibilityInputError("weights must be positive integers")


def evaluate_state(decisions, auxiliary_bits, demands, capacity, weights):
    """Return independent physical and auxiliary reports for one encoded state."""
    physical = evaluate(decisions, demands, capacity)
    _validate_weights(auxiliary_bits, weights)
    slack = sum(bit * weight for bit, weight in zip(auxiliary_bits, weights))
    residual = physical["load"] + slack - capacity
    consistent = residual == 0

    if physical["feasible"] and consistent:
        category = "PHYSICAL_AND_AUXILIARY_VALID"
    elif physical["feasible"]:
        category = "PHYSICAL_ONLY"
    elif consistent:
        category = "AUXILIARY_ONLY"
    else:
        category = "NEITHER"

    return {
        "physical": physical,
        "auxiliary": {
            "bits": list(auxiliary_bits),
            "weights": list(weights),
            "slack": slack,
            "residual": residual,
            "consistent": consistent,
        },
        "category": category,
    }
