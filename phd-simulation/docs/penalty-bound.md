# Exact penalty bound — reconstructed 23 September episode
Created 2026-09-27. Original derivation and executed synthetic enumeration; no novelty claim.

Let x=(x0,x1,x2), with one meaning served. Demand D=2x0+3x1+4x2; unserved priority U=14-3x0-5x1-6x2. Capacity is 5. We minimize E=U+lambda max(0,D-5)^2 for lambda >= 0.

| x | D | U | Feasible |
|---|---:|---:|---|
| 000 | 0 | 14 | Yes |
| 001 | 4 | 8 | Yes |
| 010 | 3 | 9 | Yes |
| 011 | 7 | 3 | No |
| 100 | 2 | 11 | Yes |
| 101 | 6 | 5 | No |
| 110 | 5 | 6 | Yes |
| 111 | 9 | 0 | No |

The constrained optimum is U*=6 at x=110. Every infeasible assignment must have E>6 to guarantee that **all** global minimizers are feasible. For each infeasible x, this requires lambda > (6-U)/(D-5)^2. The three thresholds are 3/4, 1, and 3/8. Their maximum is 1. Consequently lambda>1 is necessary and sufficient for this particular instance to exclude every infeasible global minimizer. At lambda=1, x=101 and x=110 both have energy 6. At lambda=0.1, x=111 has energy 1.6.

A simpler sufficient bound uses any known feasible incumbent Ubar and a positive lower bound delta on violation. If U>=0 everywhere and every infeasible point has D-5>=delta, then lambda>Ubar/delta^2 makes every infeasible energy exceed the incumbent. Here Ubar=6 and delta=1 give lambda>6. This is conservative and depends on assumptions; for continuous or differently scaled data delta may change or not exist. The exact bound above uses enumeration and is not a scalable recipe.

## Acceptance rule and correction
Never use just `argmin` followed by a feasibility check. Enumerate the entire minimum-energy set on small instances. Day 1's lambda=1 row reports one argmin, not a guarantee over all minimizers. Its recorded numbers are retained as historical evidence; their interpretation is corrected here. For floating-point problems a documented tie tolerance is needed. This audit uses exact rational arithmetic, so the equality is exact.

## Evidence
[Executed audit](../results/week01-formulation-audit.json), [source](../src/verify_formulation.py). Six penalty settings are evaluated. Lambda=1.01, 2 and 7 have only feasible minimizers for this toy. This establishes nothing about a heuristic solver's probability of returning those minimizers.
