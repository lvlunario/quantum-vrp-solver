# Application-oracle contract v1

Status: **FROZEN FOR DEVELOPMENT TESTS**. The P01 monotonicity property is
**PLANNED/UNEXECUTED**.

The machine-readable contract is
`docs/application-oracle-contract-v1.json`. It consolidates three already
executed development layers without merging their meanings:

| Layer | Question | Implementation |
|---|---|---|
| Decision physical | Does the selected load fit capacity? | `independent_feasibility.evaluate` |
| Encoded state | Are physical and auxiliary verdicts separately correct? | `application_metrics.evaluate_state` |
| Distribution | What explicit probability mass belongs to each verdict? | `distribution_metrics.aggregate` |

## Frozen P01 property

For fixed nonnegative demands and fixed capacity, let binary decisions satisfy
`x_i <= y_i` componentwise. P01 predicts:

1. `load(y) >= load(x)`;
2. `overload(y) >= overload(x)`;
3. if `y` is feasible, then `x` is feasible.

The converse feasibility implication is not claimed. Auxiliary consistency
and objective energy are outside P01. Negative demands or a changing capacity
violate its preconditions rather than refute it.

For the three-bit fixture, each component permits `(0,0)`, `(0,1)`, or `(1,1)`,
so Tuesday's exhaustive development test is capped at `3^3 = 27` ordered
pairs, including identities. This derivation is frozen before execution.

## Executed contract validation

Run:

```bash
python src/validate_application_oracle_contract.py
```

Eight checks passed and five altered contracts were rejected. The validator
checks identifiers, layer order, referenced implementation paths, P01's
unexecuted status, the fixture and pair bound, explicit exclusions, and the
zero/false execution boundary.

This validation does **not** execute any of the 27 pairs and does not establish
P01. It authorizes no formulation pass, mutant, statevector, search, shot,
hardware job or pilot baseline reservation. Passing means the pre-registered
test contract is internally consistent, not that the scientific property has
passed.
