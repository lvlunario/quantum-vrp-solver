# P01 nonnegative-demand monotonicity — development result

Status: **EXECUTED ON THE FIXED SYNTHETIC DEVELOPMENT FIXTURE**. This is not
execution of the frozen mutation pilot.

## Frozen property

The November 16 contract fixed demands `(2, 3, 4)`, capacity `5`, and exactly
27 binary pairs satisfying `x_i <= y_i`. P01 required:

- `load(y) >= load(x)`;
- `overload(y) >= overload(x)`;
- if `y` is feasible, `x` is feasible.

Auxiliary consistency, objective energy, negative demands and changing
capacity were excluded before execution.

## Executed result

Run from `phd-simulation/`:

```bash
python src/verify_monotonicity_p01.py
```

Eight checks passed. All 27 ordered pairs were retained: 8 identity pairs and
19 nonidentity pairs with strict load increases. Every pair satisfied all
three P01 relations, so the in-scope counterexample count is zero on this
fixture.

Two controls failed closed before scientific evaluation:

1. a negative demand violates the nonnegative-demand precondition;
2. different capacities for `x` and `y` violate the fixed-capacity
   precondition.

Calling either a counterexample would overstate the property's domain.

The JSON evidence stores every pair, source and contract hashes, Python
version, UTC execution time, exact fixture and limitations. The result
supports P01 only for one exhaustive three-bit synthetic fixture. It says
nothing about auxiliary consistency, objective quality, restoration, power
flow, uncertainty or quantum advantage.

No protocol formulation pass, M01–M12 mutant, SDK statevector, search, shot,
hardware job or baseline reservation occurred.
