# A Verification Protocol for Hybrid Quantum Microgrid Optimization
**Educational working manuscript v0.1. Unsubmitted. Personal project; no institutional affiliation or coauthors claimed.**

## Abstract — preliminary, not a finished research result
Hybrid quantum optimization pipelines can produce low objective values while violating the engineering requirements their formulations were intended to encode. This working paper proposes a verification protocol separating model equivalence, circuit correctness, decoding and physical feasibility. A three-load synthetic example illustrates why a penalty objective must be checked against an independent constrained oracle. The current evidence consists of exhaustive enumeration and an ideal three-qubit statevector experiment. General fault-detection effectiveness, realistic grid applicability and quantum computational advantage have not been established.

## 1. Introduction
Engineering validation asks whether a returned decision satisfies the original requirement. Optimization of a transformed objective alone cannot answer that question. A pipeline can correctly minimize an incorrectly weighted objective, faithfully returning an operationally unacceptable answer. We investigate test methods intended to reveal such failures before comparative solver results are interpreted.

The planned contribution is a protocol and executable verification suite, supported by fault-injection experiments and independent reproduction. This initial draft establishes the small example and the evidence requirements. Novelty claims await a structured review of prior work.

## 2. Background
QAOA is a parameterized quantum algorithm for approximate combinatorial optimization [1]. Here the state is prepared uniformly, evolved under a diagonal objective, then mixed with single-qubit X rotations at depth one. A classical grid search chooses parameters. This implements the educational statevector model directly; it does not demonstrate an efficient hardware compilation.

## 3. Toy problem and protocol
Three binary decisions x_i indicate whether loads are served. Demands are (2,3,4), priorities (3,5,6), and available capacity is 5 synthetic units. Minimize U(x)=sum_i priority_i(1-x_i), subject to sum_i demand_i x_i <= 5.
The toy penalty objective is E(x)=U(x)+lambda*max(0, demand(x)-5)^2. This piecewise expression is evaluated as a diagonal oracle. It has not yet been reduced to a QUBO; a later slack-variable encoding must be independently verified.
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
