"""Aggregate separated application verdicts under an explicit distribution."""

import math


class DistributionInputError(ValueError):
    pass


CATEGORIES = (
    "PHYSICAL_AND_AUXILIARY_VALID",
    "PHYSICAL_ONLY",
    "AUXILIARY_ONLY",
    "NEITHER",
)


def _expected_category(physical, auxiliary):
    if physical and auxiliary:
        return "PHYSICAL_AND_AUXILIARY_VALID"
    if physical:
        return "PHYSICAL_ONLY"
    if auxiliary:
        return "AUXILIARY_ONLY"
    return "NEITHER"


def aggregate(state_reports, probabilities, tolerance=1e-12):
    """Return physical, auxiliary, joint and category masses.

    The caller must supply a complete ordered support with explicit normalized
    probabilities.  No distribution is inferred from the reports.
    """
    if not isinstance(state_reports, (list, tuple)) or not state_reports:
        raise DistributionInputError("state_reports must be nonempty")
    if not isinstance(probabilities, (list, tuple)) or len(probabilities) != len(state_reports):
        raise DistributionInputError("probabilities must match support length")
    if not isinstance(tolerance, (int, float)) or isinstance(tolerance, bool) or not math.isfinite(tolerance) or tolerance <= 0:
        raise DistributionInputError("tolerance must be positive and finite")

    checked_probabilities = []
    checked_reports = []
    seen = set()
    for expected_index, (report, probability) in enumerate(zip(state_reports, probabilities)):
        if not isinstance(report, dict) or report.get("index") != expected_index or expected_index in seen:
            raise DistributionInputError("support indices must be unique, complete and ordered")
        seen.add(expected_index)
        physical = report.get("physical_feasible")
        auxiliary = report.get("auxiliary_consistent")
        category = report.get("category")
        if not isinstance(physical, bool) or not isinstance(auxiliary, bool):
            raise DistributionInputError("verdicts must be Booleans")
        if category not in CATEGORIES or category != _expected_category(physical, auxiliary):
            raise DistributionInputError("category must agree with source verdicts")
        if not isinstance(probability, (int, float)) or isinstance(probability, bool) or not math.isfinite(probability) or probability < 0:
            raise DistributionInputError("probabilities must be finite and nonnegative")
        checked_reports.append((physical, auxiliary, category))
        checked_probabilities.append(float(probability))

    total = math.fsum(checked_probabilities)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=tolerance):
        raise DistributionInputError("probabilities must sum to one")

    physical_mass = math.fsum(p for p, (physical, _, _) in zip(checked_probabilities, checked_reports) if physical)
    auxiliary_mass = math.fsum(p for p, (_, auxiliary, _) in zip(checked_probabilities, checked_reports) if auxiliary)
    joint_mass = math.fsum(p for p, (physical, auxiliary, _) in zip(checked_probabilities, checked_reports) if physical and auxiliary)
    category_mass = {
        category: math.fsum(p for p, (_, _, observed) in zip(checked_probabilities, checked_reports) if observed == category)
        for category in CATEGORIES
    }
    return {
        "support_size": len(checked_reports),
        "probability_sum": total,
        "physical_feasible_mass": physical_mass,
        "auxiliary_consistent_mass": auxiliary_mass,
        "joint_valid_mass": joint_mass,
        "category_mass": category_mass,
    }
