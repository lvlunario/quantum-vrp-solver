# A Verification Protocol for Hybrid Quantum Microgrid Optimization
**Educational working manuscript v0.3. Unsubmitted. Personal project; no institutional affiliation or coauthors claimed.**

## Abstract — preliminary, not a finished research result
Hybrid quantum optimization pipelines can produce low objective values while violating the engineering requirements their formulations were intended to encode. This working paper proposes a verification protocol separating model equivalence, circuit correctness, decoding and physical feasibility. A three-load synthetic example illustrates why a penalty objective must be checked against an independent constrained oracle. Current evidence consists of exhaustive six-variable formulation audits and an ideal six-qubit Qiskit 2.5.2 cost-layer statevector experiment. A QAOA mixer, parameter optimization, realistic grid applicability and quantum computational advantage have not been verified.

## 1. Introduction
Engineering validation asks whether a returned decision satisfies the original requirement. Optimization of a transformed objective alone cannot answer that question. A pipeline can correctly minimize an incorrectly weighted objective, faithfully returning an operationally unacceptable answer. We investigate test methods intended to reveal such failures before comparative solver results are interpreted.

The planned contribution is a protocol and executable verification suite, supported by fault-injection experiments and independent reproduction. This draft establishes the small example and the evidence requirements. Novelty claims await a structured review of prior work.

## 2. Background and conventions
QAOA is a parameterized quantum algorithm for approximate combinatorial optimization [1]. Equations (2)–(6) of the original paper define a uniform initial state, a diagonal cost unitary (U(C,\gamma)=\exp(-i\gamma C)), and a mixer (U(B,\beta)=\prod_j\exp(-i\beta X_j)), alternated for (p) layers. The paper writes (C) as an objective to maximize. This project instead keeps its engineering penalty (E) as an energy to minimize, implements (\exp(-i\gamma E)), and will minimize expected energy. These are consistent conventions only if the direction is stated and tested.

Qiskit's `RX(theta)` is (\exp(-i\theta X/2)) [2]. Implementing the paper's mixer therefore requires `RX(2*beta)` on every qubit. The mixer and its factor-of-two acceptance test remain planned. Ideal statevector execution does not demonstrate efficient hardware compilation or advantage.

## 3. Toy problem and protocol
Three binary decisions (x_i) indicate whether loads are served. Demands are (2,3,4), priorities (3,5,6), and available capacity is 5 synthetic units. Minimize (U(x)=\sum_i p_i(1-x_i)), subject to (\sum_i d_i x_i\leq5).

The initial toy penalty objective was (E(x)=U(x)+\lambda\max(0,D(x)-5)^2), evaluated as a diagonal oracle over eight assignments. The 27 September catch-up introduced slack (s=y_0+2y_1+4y_2) and verified the six-variable QUBO (E=U+\lambda(D+s-5)^2) algebraically and exhaustively. The QUBO-to-Ising map and bit-order contract were subsequently verified over all 64 states.

The original three-qubit educational sweep used 41 gamma values in ([0,2\pi)) and 41 beta values in ([0,\pi)) for lambda values 0.1, 1 and 4. It reports exact statevector probabilities, not shot estimates. That sweep is distinct from the later six-qubit cost-layer circuit, which has not yet been followed by a mixer or parameter search.

## 4. Preliminary executed observations
Serving loads 0 and 1 uses all five capacity units and leaves priority cost 6. At lambda=0.1, serving all loads gives penalty energy 1.6 while exceeding capacity by four units. Thus minimizing the penalty objective can prefer an infeasible decision. At lambda=1, a feasible and an infeasible decision tie at energy 6, so the sufficient strict threshold for all minimizers on this instance is lambda greater than 1.

The 8 October execution built the six-qubit ideal cost layer with six RZ and fifteen RZZ gates in Qiskit 2.5.2. Across three angles, nine checks passed and the SDK statevector agreed with an independent oracle to maximum strict error (1.53\times10^{-15}). Sign, reversed-order and omitted-interaction mutations were rejected. These selected faults demonstrate sensitivity, not a general detection rate.

## 5. Planned evaluation
Before optimization, implement one mixer layer and test identity at beta zero, uniform probabilities at gamma zero, norm preservation, agreement with an independent tensor-product oracle, the Qiskit factor of two, and rejection of sign, factor and order mutations. Then compare objective-only tests against feasibility checks and metamorphic tests on a documented fault catalog. Add classical exact and heuristic baselines, held-out instances and a fair computational budget before performance comparisons.

## 6. Threats to validity
The instance is extremely small and synthetic. It omits grid physics, dynamics and realistic uncertainty. Exact statevector simulation is classical and scales exponentially. Selected mutation tests cannot estimate general fault-detection power. No mixer, finite-shot sampling, transpilation, noise model or hardware has been verified. The original angle grid may miss better parameters. A weak-penalty failure is unsurprising and establishes neither novelty nor advantage.

## 7. Current conclusion
The evidence supports a narrow engineering claim: formulation, diagonal-phase and ideal SDK cost-circuit checks can be separated and independently audited on this toy. It does not yet show that a QAOA circuit finds good schedules or improves on classical methods. Whether the protocol generalizes usefully remains open.

## References
[1] E. Farhi, J. Goldstone, S. Gutmann, *A Quantum Approximate Optimization Algorithm*, 2014. https://arxiv.org/abs/1411.4028

[2] IBM Quantum Documentation, `RXGate`, accessed 2026-10-09. https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RXGate

## 8. Week 1 correction and formulation audit — added 2026-09-27
These results were executed during the actual 27 September catch-up, linked to reconstructed story dates 23–25 September. They were not obtained on those earlier dates.

At lambda=1 the feasible decision (1,1,0) and infeasible decision (1,0,1) both minimize energy at 6. Exact enumeration yields the strict threshold lambda greater than 1 for this instance. Introducing slack (s=y_0+2y_1+4y_2) gives (E=U+\lambda(D+s-5)^2). At lambda=2, all 64 expanded polynomial energies match the direct residual expression; minimizing over slack reproduces the hinge penalty on all eight decisions. The unique ground state is (1,1,0,0,0,0).

Deliberately limiting slack to weights (1,2) changes the all-off reduced energy from 14 to 22, despite preserving the best service choice. Dropping all quadratic cross terms produces 57 disagreements out of 64 states. These are targeted fault injections, not representative effectiveness measurements.

| Claim | Evidence | Limit |
|---|---|---|
| Strict toy threshold lambda greater than 1 | `docs/penalty-bound.md`; exact rational sweep | This finite instance only |
| Slack reduction preserves decision energies | `docs/qubo-equivalence.md`; 64 raw and eight reduced states | Integer toy, lambda=2 |
| Tests detect two seeded faults | `results/week01-formulation-audit.json` | Selected known defects |
| Nine formulation checks pass | `src/verify_formulation.py` | No quantum circuit in that run |

## 9. Cost-layer verification — 2026-10-05 to 2026-10-08

| Boundary | Evidence | Executed result | Remaining limit |
|---|---|---|---|
| QUBO to Ising | `results/2026-10-05-ising-audit.json` | All 64 energies and eight checks pass | Algebra only |
| Diagonal phases | `results/2026-10-06-phase-audit.json` | 256 state-angle pairs; nine checks pass | Plain Python |
| Statevector interface | `results/2026-10-07-statevector-interface.json` | Nine checks; predicted global phase handled | NumPy oracle |
| Qiskit cost circuit | `results/2026-10-08-qiskit-cost-circuit.json` | Three angles; nine checks; max error (1.53\times10^{-15}) | Ideal cost layer only |

The staged checks intentionally avoid using the SDK circuit as its own oracle. The mixer acceptance contract is source-grounded in `docs/qaoa-reading-notes.md` and remains **PLANNED/UNEXECUTED**. The manuscript remains educational and unsubmitted.
