"""Independent physical-feasibility contract for binary load decisions.

This standard-library module knows nothing about QUBO energy, slack variables,
statevectors, or optimization outcomes.  It checks the original capacity
requirement directly.
"""


class FeasibilityInputError(ValueError):
    pass


def _nonnegative_integer(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def evaluate(decisions, demands, capacity):
    """Return a decision-level capacity verdict with an exact overload margin."""
    if not isinstance(decisions, (list, tuple)) or not decisions:
        raise FeasibilityInputError("decisions must be a nonempty list or tuple")
    if not isinstance(demands, (list, tuple)) or len(demands) != len(decisions):
        raise FeasibilityInputError("demands must match decision length")
    if any(bit not in (0, 1) or isinstance(bit, bool) for bit in decisions):
        raise FeasibilityInputError("decisions must contain integer bits")
    if any(not _nonnegative_integer(value) for value in demands):
        raise FeasibilityInputError("demands must be nonnegative integers")
    if not _nonnegative_integer(capacity):
        raise FeasibilityInputError("capacity must be a nonnegative integer")

    load = sum(bit * demand for bit, demand in zip(decisions, demands))
    overload = max(0, load - capacity)
    return {
        "decisions": list(decisions),
        "load": load,
        "capacity": capacity,
        "feasible": load <= capacity,
        "overload": overload,
        "headroom": max(0, capacity - load),
    }


def bits_q0_first(index, width):
    if not _nonnegative_integer(index) or not _nonnegative_integer(width) or width == 0:
        raise FeasibilityInputError("index and positive width must be integers")
    if index >= 2 ** width:
        raise FeasibilityInputError("index does not fit width")
    return tuple((index >> offset) & 1 for offset in range(width))
