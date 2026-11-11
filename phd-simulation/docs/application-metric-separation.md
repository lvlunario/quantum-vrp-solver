# Application metric separation

Status: **EXECUTED DEVELOPMENT TEST OUTSIDE THE FROZEN MUTATION PILOT**

## Contract

`application_metrics.evaluate_state` returns two named reports rather than one
ambiguous validity flag:

- `physical.feasible` evaluates the original capacity inequality from the load
  decisions only;
- `auxiliary.consistent` evaluates whether the encoded nonnegative slack makes
  `load + slack = capacity`.

The category is descriptive and never replaces those fields. For the fixed
synthetic fixture, an auxiliary-consistent state must be physically feasible,
but many physically feasible states have deliberately incorrect auxiliary
bits. That implication follows from this exact equality and nonnegative slack;
it is not assumed as a universal property of other encodings.

## Executed audit

Run from `phd-simulation/`:

```bash
python src/verify_application_metrics.py
```

The deterministic program enumerates all 64 combinations of three load bits
and three slack bits with demands `(2, 3, 4)`, capacity `5`, and slack weights
`(1, 2, 4)`. Eight checks passed. The partition is:

| Category | States |
|---|---:|
| physical and auxiliary valid | 5 |
| physical only | 35 |
| auxiliary only | 0 |
| neither | 24 |

Under a uniform counting measure, physical feasibility is `40/64 = 0.625`,
whereas auxiliary consistency is `5/64 = 0.078125`. These are enumeration
diagnostics, not observed circuit probabilities.

Each feasible load decision has exactly one consistent slack assignment; each
overloaded decision has none. Five malformed auxiliary definitions were also
rejected. Raw rows, exact configuration, runtime version, source hash and
limitations are retained in
`results/2026-11-11-application-metrics.json`.

## Boundary

This adapter imports the independent capacity checker but does not evaluate
energy, construct a circuit, reserve a baseline, or touch an M01–M12 record.
The preflight remains blocked and scientific execution remains unauthorized.
The fixture contains one static capacity constraint: it does not establish
microgrid resilience, optimality, uncertainty handling, or quantum advantage.
