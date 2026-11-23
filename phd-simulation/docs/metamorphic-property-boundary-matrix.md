# Metamorphic property boundary matrix

**SIMULATED NARRATIVE:** this is documentation for an independent personal
project in a Norway setting, without a host institution. The supervisor-role
decision below is fictional. No real meeting, affiliation, collaboration,
review or submission occurred.

## Why the boundary matters

The synthetic capacity model contains several related but non-interchangeable
objects. A decision-level physical oracle asks whether selected demand fits a
capacity. An auxiliary-consistency oracle asks whether a particular slack
assignment satisfies an exact equality. Distribution metrics aggregate
explicit probabilities over those verdicts. A transformation safe for one
layer must not be silently promoted to another.

| Property | Transformation | Preserved claim | Required preconditions | Explicitly not claimed | Evidence status |
|---|---|---|---|---|---|
| P01 nonnegative-demand monotonicity | Replace binary decision `x` with componentwise larger `y`; keep demands and capacity fixed | Load and overload do not decrease; feasibility is downward closed | Equal vector length, binary decisions, `x <= y`, fixed nonnegative integer demands, fixed nonnegative integer capacity | Auxiliary equality, objective monotonicity, changing capacity, negative demands | **EXECUTED_DEVELOPMENT_FIXTURE_PASSED** on 27 ordered pairs, November 18 |
| Auxiliary equality nonmonotonicity | Increase the decision while holding the same slack assignment | No Boolean ordering is promised | Same three-item fixture and fixed slack per comparison | “True” means safer, or true→false means graded degradation | **EXECUTED_DEVELOPMENT_COUNTEREXAMPLE_CONFIRMED** on 216 cases, November 19 |
| P02 simultaneous permutation invariance | Apply the same coordinate permutation to decision and matching demands; keep capacity fixed | Load, overload and physical feasibility should be identical | Matching positive lengths, binary decisions, nonnegative integer demands, fixed capacity, one shared bijection | Auxiliary-bit semantics, QUBO coefficient order, statevector indexing, optimizer output, one-sided permutation | **PLANNED_UNEXECUTED**; contract frozen November 23 |

## P01 and the auxiliary counterexample are compatible

P01 follows from the order of a weighted sum with nonnegative coefficients.
If `x_i <= y_i` and `d_i >= 0`, then each term `d_i x_i <= d_i y_i`, so the
total load cannot fall. The capacity comparison then makes overload
nondecreasing and gives downward-closed feasibility.

Auxiliary consistency is the Boolean equality `load + slack = capacity`.
An increasing load can approach, hit, or pass that equality. Consequently its
truth value can change in either direction even while the physical inequality
behaves exactly as P01 predicts. The November 19 audit observed both directions
and zero physical P01 violations; this is a boundary result, not a conflict.

## P02 derivation and frozen audit size

For a permutation `p`, define `x'_j = x_{p(j)}` and `d'_j = d_{p(j)}`. Then

`sum_j d'_j x'_j = sum_j d_{p(j)} x_{p(j)} = sum_i d_i x_i`,

because a bijection merely reorders the same paired products. Fixed capacity
therefore implies equal overload and equal physical feasibility. On the frozen
fixture there are eight binary decisions and six coordinate permutations, so
the future audit contains exactly 48 cases: eight identity and 40 nonidentity.

The case count is a prospective cap, not an executed result. The contract
validator checks the frozen schema, fixture, count, metric boundary and zero
resource authorization. It does not enumerate or evaluate any P02 case.

## Fictional supervisor-role decision

**SIMULATED NARRATIVE:** the weekly supervisor role accepted P02 as the next
small, interpretable metamorphic property because its mathematical mechanism
is exact paired relabeling. The decision was to freeze the shared-permutation
convention before implementation, retain all 48 future rows, include one-sided
permutations only as rejected controls, and keep the blocked mutation pilot
untouched. No real person participated.

## Limitations

This matrix concerns a static three-item synthetic capacity inequality. It
does not cover power flow, islanding, restoration, contingencies, uncertainty,
QUBO equivalence under variable remapping, circuit layouts, sampling, hardware
or optimization quality. Nothing here supports a quantum-advantage claim.
