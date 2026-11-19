# Auxiliary consistency is not decision-monotone

Status: **EXECUTED DEVELOPMENT COUNTEREXAMPLE AUDIT OUTSIDE THE FROZEN
MUTATION PILOT**.

## Question

P01 showed that, with fixed nonnegative demands and capacity, increasing a
binary decision componentwise cannot reduce load or overload. This audit asks
whether the auxiliary equality indicator behaves the same way when slack bits
are held fixed.

For the fixture, `auxiliary_consistent = (load + slack == 5)`.

That indicator is equality to one target, not an inequality ordering.

## Minimal witnesses

Use `x=(0,0,0)`, `y=(1,0,0)`, demands `(2,3,4)`, capacity `5`:

- Fixed slack `5`: `x` has residual `0` and is consistent; `y` has residual
  `2` and is inconsistent. This is true→false.
- Fixed slack `3`: `x` has residual `-2` and is inconsistent; `y` has residual
  `0` and is consistent. This is false→true.

Both decisions are physically feasible in both witnesses. The change is only
in representation consistency.

## Exhaustive bounded audit

Run:

```bash
python src/verify_auxiliary_nonmonotonicity.py
```

The program combines the 27 componentwise ordered decision pairs with all 8
fixed slack assignments, retaining 216 rows. Eight checks passed. Transition
counts were:

| Auxiliary transition | Count |
|---|---:|
| false→false | 188 |
| false→true | 6 |
| true→false | 17 |
| true→true | 5 |

All 64 identity cases preserved consistency, as expected. The physical P01
relations still held on every projected ordered pair; auxiliary
nonmonotonicity therefore does not refute P01.

## Interpretation

Auxiliary consistency should be treated as an encoding diagnostic, not as a
monotone safety score. A decision can move into or out of the equality surface
as load rises. The result is exact for one synthetic equality encoding and
does not establish behavior for other encodings.

No protocol formulation pass, mutant, statevector, search, shot, hardware job
or baseline reservation occurred. No objective quality, resilience physics,
uncertainty or quantum advantage was evaluated.
