# Independent physical-feasibility checker

Status: **EXECUTED DEVELOPMENT AUDIT — 2026-11-10**.

The checker evaluates the original engineering requirement directly:

```text
load(x) = sum(d[i] * x[i])
physical_feasible(x) = load(x) <= capacity
overload(x) = max(0, load(x) - capacity)
```

It does not accept QUBO energy, slack bits, statevectors, probabilities or an
optimizer verdict as inputs. This keeps physical capacity compliance
independent from encoding consistency and objective quality.

## Executed evidence

The standard-library audit exhaustively evaluated all eight three-load
decisions for demands `(2,3,4)` and capacity `5`, then repeated each physical
decision across all eight auxiliary-bit encodings (64 encoded states). Eight
checks passed:

- the hand-enumerated loads are `(0,2,3,5,4,6,7,9)`;
- five decisions are physically feasible;
- load 5 is feasible with zero headroom;
- infeasible overload margins are exactly 1, 2 and 4;
- auxiliary bits never change the physical verdict;
- encoding consistency disagrees with physical feasibility on deliberately
  exposed states, so it cannot serve as a proxy;
- malformed decision vectors and invalid model data fail closed.

This is actual deterministic execution on a synthetic fixture. It is labeled
`DEVELOPMENT_TEST_OUTSIDE_FROZEN_MUTATION_PILOT`: no baseline directory was
reserved, no M01/M02 formulation pass was consumed, and no Qiskit dependency
was imported.

## Interpretation

A load choice can be physically feasible while paired with incorrect slack
bits. Conversely, the equation `load + slack = capacity` cannot rescue an
overloaded decision with nonnegative slack. Physical feasibility and auxiliary
consistency therefore answer different questions and must remain separate
metrics.

Limitations: this checks one static synthetic capacity inequality. It does not
represent power flow, ramping, contingencies, uncertainty, restoration, or
resilience. It provides an independent oracle boundary, not evidence of solver
performance or quantum advantage.
