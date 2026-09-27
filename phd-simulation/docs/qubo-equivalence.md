# Six-variable QUBO equivalence — reconstructed 24 September episode
Created 2026-09-27. Original toy derivation, checked by actual exhaustive enumeration.

Introduce nonnegative integer slack s=y0+2y1+4y2, with each y binary. Define z=(x0,x1,x2,y0,y1,y2) and a=(2,3,4,1,2,4). Use

E(z)=14-3x0-5x1-6x2 + lambda (a dot z-5)^2.

Because z_i^2=z_i, the expanded expression is c+sum h_i z_i+sum_{i<j} q_ij z_i z_j, where c=14+25lambda, h_i=lambda(a_i^2-10a_i)-p_i, p=(3,5,6,0,0,0), and q_ij=2lambda a_i a_j. Cross terms are stored once, using an upper-triangular convention; a symmetric matrix convention would divide off-diagonal coefficients by two.

For lambda=2, c=64 and h=(-35,-47,-54,-18,-32,-48). All 15 cross coefficients are stored in the JSON audit.

For a feasible x, required slack 5-D lies in 0..5 and is representable. The minimum penalty is zero. For an infeasible x, every nonnegative slack increases the positive residual, so s=0 minimizes it. Therefore minimizing E over slack reproduces the original hinge-squared penalty for every x. Slack values 6 and 7 cannot create a new lower minimum: they are nonnegative and unnecessary to satisfy the equality. This argument is specific to nonnegative demand and the chosen capacity/range.

## Executed checks
The polynomial and residual expressions agree on all 64 assignments at lambda=2. After minimizing over slack, all eight decision energies equal the original penalty expression. The unique six-bit minimizer is (1,1,0,0,0,0), energy 6.

Two deliberately injected faults were tested:
- Insufficient slack weights (1,2) cover only 0..3. At x=000 the minimum energy becomes 22 rather than 14. This violates full equivalence even though the optimal service decision is unchanged.
- Omitting all quadratic cross terms causes 57 of the 64 energies to disagree with the residual expression.

These are demonstrations of fault sensitivity, not a measured detection rate over representative defects. No accidental historical bug is claimed.

## What remains open
Six binary variables are a QUBO formulation, not an executed six-qubit circuit. Ground-state equivalence does not establish equal QAOA sampling distributions, angle landscapes, or resource costs relative to the three-variable oracle. Circuit mapping, basis ordering, decoding and independent statevector verification remain planned.

Reproduce from phd-simulation with `python src/verify_formulation.py`. Standard library only. See [raw results and provenance](../results/week01-formulation-audit.json).
