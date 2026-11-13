# Explicit distribution metric aggregation

Status: **EXECUTED DEVELOPMENT TEST OUTSIDE THE FROZEN MUTATION PILOT**

## Purpose

`distribution_metrics.aggregate` turns per-state application verdicts into
distribution-level masses without inventing a distribution. The caller must
supply a complete ordered support and an explicit finite, nonnegative,
normalized probability vector.

The returned quantities remain separate:

- physical-feasibility mass;
- auxiliary-consistency mass;
- joint-valid mass;
- the four-category partition.

The aggregator validates each category against its two source Booleans. It
also rejects incomplete support, duplicate or reordered indices, negative or
nonfinite weights, Boolean weights, mismatched lengths and weights that do not
sum to one within a fixed absolute tolerance of `1e-12`.

## Executed development audit

From `phd-simulation/`:

```bash
python src/verify_distribution_metrics.py
```

Eight checks passed over four explicit synthetic distributions on the fixed
64-state capacity fixture:

| Distribution | Physical mass | Auxiliary mass | Joint mass |
|---|---:|---:|---:|
| Uniform | 0.625 | 0.078125 | 0.078125 |
| Joint-valid point mass | 1.0 | 1.0 | 1.0 |
| Physical-only point mass | 1.0 | 0.0 | 0.0 |
| Three-point mixture | 0.75 | 0.25 | 0.25 |

Seven malformed inputs were rejected. The result file stores the exact
distributions, category masses, source hash, Python version, execution time,
resource counters and limitations.

## Interpretation boundary

These are deterministic calculations on constructed weights. They are not
statevector probabilities, shots, hardware measurements or optimizer output.
The uniform case reproduces November 11's counting fractions only because its
weights are explicitly `1/64`; the implementation never assumes uniformity.

This work does not reserve the mutation-pilot baseline or consume formulation,
mutant or circuit budgets. The preflight remains blocked. One static capacity
constraint is not evidence of resilient microgrid operation or quantum
advantage.
