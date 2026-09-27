# A Verification Protocol for Hybrid Quantum Microgrid Optimization
**Educational working manuscript v0.2. Unsubmitted. Personal project; no institutional affiliation or coauthors claimed.**

## Abstract — preliminary, not a finished research result
Hybrid quantum optimization pipelines can produce low objective values while violating the engineering requirements their formulations were intended to encode. This working paper proposes a verification protocol separating model equivalence, circuit correctness, decoding and physical feasibility. A three-load synthetic example illustrates why a penalty objective must be checked against an independent constrained oracle. The current evidence consists of exhaustive enumeration and an ideal three-qubit statevector experiment. General fault-detection effectiveness, realistic grid applicability and quantum computational advantage have not been established.

## 1. Introduction
Engineering validation asks whether a returned decision satisfies the original requirement. Optimization of a transformed objective alone cannot answer that question. A pipeline can correctly minimize an incorrectly weighted objective, faithfully returning an operationally unacceptable answer. We investigate test methods intended to reveal such failures before comparative solver results are interpreted.

The planned contribution is a protocol and executable verification suite, supported by fault-injection experiments and independent reproduction. This initial draft establishes the small example and the evidence requirements. Novelty claims await a structured review of prior work.

## 2. Background
QAOA is a parameterized quantum algorithm for approximate combinatorial optimization [1]. Here the state is prepared uniformly, evolved under a diagonal objective, then mixed with single-qubit X rotations at depth one. A classical grid search chooses parameters. This implements the educational statevector model directly; it does not demonstrate an efficient hardware compilation.

## 3. Toy problem and protocol
Three binary decisions x_i indicate whether loads are served. Demands are (2,3,4), priorities (3,5,6), and available capacity is 5 synthetic units. Minimize U(x)=sum_i priority_i(1-x_i), subject to sum_i demand_i x_i <= 5.
The toy penalty objective is E(x)=U(x)+lambda*max(0, demand(x)-5)^2. This piecewise expression is evaluated as a diagonal oracle. The initial experiment did not reduce this expression to a QUBO. The 27 September catch-up now verifies a six-variable slack QUBO algebraically and exhaustively, without executing its circuit.
Enumerate all eight assignments. Validate the constrained optimum separately from the penalized optimum. Evaluate QAOA at 41 gamma values in [0,2pi) and 41 beta values in [0,pi), reporting feasibility probabilities alongside expected energy. Repeat the deterministic sweep for lambda values 0.1, 1 and 4. No sampling uncertainty applies to exact statevector probabilities, but finite-grid optimization error remains.

## 4. Preliminary executed observation
Serving loads 0 and 1 uses all five capacity units and leaves priority cost 6. At lambda=0.1, serving all loads instead gives penalty energy 1.6 while exceeding capacity by four units. Thus minimizing the penalty objective can prefer an infeasible decision. This is a diagnostic example, not a novel theorem or empirical validation of the proposed full protocol.
The stored run reports all three penalty settings and QAOA probability vectors in `results/day001-toy.json`. Use those values directly rather than inventing or rounding a favorable summary. The test suite checks a manually enumerated feasible objective set, normalization and an independent one-qubit analytic formula.

## 5. Planned evaluation
Compare objective-only tests against feasibility checks and metamorphic tests on a documented fault catalog. Measure detection, false alarms, equivalent-mutant handling and overhead. Add classical exact and heuristic baselines before making performance comparisons. Hold out test instances and preserve failed cases.

## 6. Threats to validity
The instance is extremely small and artificial. It omits grid physics, dynamics and realistic uncertainty. Statevector simulation is classical and scales exponentially. The angle search may miss better parameters. A weak penalty failure is unsurprising and establishes neither novelty nor advantage. Noise and hardware effects have not been measured. The single example cannot support general detection-rate claims.

## 7. Current conclusion
The first example demonstrates the need to separate a penalized numerical objective from engineering feasibility. Whether the proposed protocol offers a useful research contribution remains open.

## References
[1] E. Farhi, J. Goldstone, S. Gutmann, *A Quantum Approximate Optimization Algorithm*, 2014. https://arxiv.org/abs/1411.4028

## 8. Week 1 correction and formulation audit — added 2026-09-27
These results were executed during the actual 27 September catch-up, linked to reconstructed story dates 23–25 September. They were not obtained on those earlier dates.

At lambda=1 the feasible decision (1,1,0) and infeasible decision (1,0,1) both minimize energy at 6. The original single-argmin report is therefore insufficient to guarantee feasibility of all minimizers. Exact enumeration yields the strict threshold lambda>1 for this instance. The inequality follows by comparing each infeasible decision's energy with the constrained optimum; see the [derivation](../docs/penalty-bound.md).

Introducing slack s=y0+2y1+4y2 gives E=U+lambda(D+s-5)^2. At lambda=2, all 64 expanded polynomial energies match the direct residual expression. Minimizing over slack reproduces the original hinge penalty on all eight decisions. The unique ground state is (1,1,0,0,0,0). The [QUBO note](../docs/qubo-equivalence.md) gives the proof and coefficient convention.

Deliberately limiting slack to weights (1,2) changes the all-off reduced energy from 14 to 22, despite preserving the best service choice. Deliberately dropping all quadratic cross terms produces 57 disagreements out of 64 states. These targeted fault injections demonstrate test sensitivity to selected defects, not general effectiveness or statistical detection rates.

| Claim | Evidence | Limit |
|---|---|---|
| Strict toy threshold lambda>1 | penalty-bound.md; exact rational sweep | Requires this finite instance; no sampler guarantee |
| Slack reduction preserves all decision energies | qubo-equivalence.md; 64 raw states and eight reduced states | Integer toy inputs, tested at lambda=2 |
| Tests detect two seeded faults | week01-formulation-audit.json | Selected known defects, not representative fault population |
| Nine checks pass | src/verify_formulation.py; audit checks array | No quantum circuit or hardware execution |

All execution provenance is in [week01-formulation-audit.json](../results/week01-formulation-audit.json). The standard-library script uses no random sampling. Ground-state equivalence does not imply equivalent QAOA distributions. A six-qubit implementation and independent circuit tests remain planned.

Updated conclusion: the project now has an explicit, verified toy QUBO and a documented correction to its acceptance criterion. General verification utility and novelty remain unestablished. The manuscript remains educational and unsubmitted.

