# A Verification Protocol for Hybrid Quantum Microgrid Optimization
**Educational working manuscript v0.5. Unsubmitted. Personal project; no institutional affiliation or coauthors claimed.**

## Abstract — preliminary, not a finished research result
Hybrid quantum optimization pipelines can produce low objective values while violating the engineering requirements their formulations were intended to encode. This working paper proposes a verification protocol separating model equivalence, circuit correctness, decoding and physical feasibility. A three-load synthetic example illustrates why a penalty objective must be checked against an independent constrained oracle. Current evidence consists of exhaustive six-variable formulation audits, ideal six-qubit Qiskit cost-plus-mixer checks, independent exact readout checks, and one exploratory 256-candidate parameter grid whose execution violated its aggregate-budget and retention protocol. Physical feasibility, auxiliary encoding consistency and optimal-load probability are distinguished. A twelve-mutant layered pilot is prospectively specified but unexecuted. Realistic grid applicability and quantum computational advantage have not been verified.

## 1. Introduction
Engineering validation asks whether a returned decision satisfies the original requirement. Optimization of a transformed objective alone cannot answer that question. A pipeline can correctly minimize an incorrectly weighted objective, faithfully returning an operationally unacceptable answer. We investigate test methods intended to reveal such failures before comparative solver results are interpreted.

The planned contribution is a protocol and executable verification suite, supported by fault-injection experiments and independent reproduction. This draft establishes the small example and the evidence requirements. Novelty claims await a structured review of prior work.

## 2. Background and conventions
QAOA is a parameterized quantum algorithm for approximate combinatorial optimization [1]. Equations (2)–(6) of the original paper define a uniform initial state, a diagonal cost unitary (U(C,\gamma)=\exp(-i\gamma C)), and a mixer (U(B,\beta)=\prod_j\exp(-i\beta X_j)), alternated for (p) layers. The paper writes (C) as an objective to maximize. This project instead keeps its engineering penalty (E) as an energy to minimize, implements (\exp(-i\gamma E)), and will minimize expected energy. These are consistent conventions only if the direction is stated and tested.

Qiskit's `RX(theta)` is (\exp(-i\theta X/2)) [2]. Implementing the paper's mixer therefore requires `RX(2*beta)` on every qubit. The ideal mixer and its factor-of-two acceptance test were executed on 12 October; finite-shot and hardware behavior remain unverified. Ideal statevector execution does not demonstrate efficient hardware compilation or advantage.

## 3. Toy problem and protocol
Three binary decisions (x_i) indicate whether loads are served. Demands are (2,3,4), priorities (3,5,6), and available capacity is 5 synthetic units. Minimize (U(x)=\sum_i p_i(1-x_i)), subject to (\sum_i d_i x_i\leq5).

The initial toy penalty objective was (E(x)=U(x)+\lambda\max(0,D(x)-5)^2), evaluated as a diagonal oracle over eight assignments. The 27 September catch-up introduced slack (s=y_0+2y_1+4y_2) and verified the six-variable QUBO (E=U+\lambda(D+s-5)^2) algebraically and exhaustively. The QUBO-to-Ising map and bit-order contract were subsequently verified over all 64 states.

The original three-qubit educational sweep used 41 gamma values in ([0,2\pi)) and 41 beta values in ([0,\pi)) for lambda values 0.1, 1 and 4. It reports exact statevector probabilities, not shot estimates. That sweep is distinct from the later six-qubit cost-layer circuit, which was followed by a verified mixer on 12 October and independent readout checks on 15 October, but no six-qubit parameter search.

## 4. Preliminary executed observations
Serving loads 0 and 1 uses all five capacity units and leaves priority cost 6. At lambda=0.1, serving all loads gives penalty energy 1.6 while exceeding capacity by four units. Thus minimizing the penalty objective can prefer an infeasible decision. At lambda=1, a feasible and an infeasible decision tie at energy 6, so the sufficient strict threshold for all minimizers on this instance is lambda greater than 1.

The 8 October execution built the six-qubit ideal cost layer with six RZ and fifteen RZZ gates in Qiskit 2.5.2. Across three angles, nine checks passed and the SDK statevector agreed with an independent oracle to maximum strict error (1.53\times10^{-15}). Sign, reversed-order and omitted-interaction mutations were rejected. These selected faults demonstrate sensitivity, not a general detection rate.

## 5. Exploratory search and planned evaluation
The ideal mixer and fixed-state readout gates passed (Section 10). The local search contract in docs/baseline-protocol-v1.md froze a 16-by-16 grid, energy-only selection, deterministic ties and independent winner validation. On 19 October the retained run evaluated all 256 candidates, but a provenance-repair workflow repeated the full grid and overwrote the first raw result. Aggregate execution was therefore 512 candidate evaluations, and strict protocol acceptance is **NOT MET**.

The retained candidate reduced mean energy from the uniform value 50 to 26.756841 and raised physical-feasibility mass from 0.625 to 0.977671, but reduced optimal-load probability from 0.125 to 0.083381. This mixed result is exploratory, not held out, and the simple greedy rule already solves the fixture exactly. Broader solver comparison remains R08.

The next study is not another parameter grid. docs/mutation-pilot-protocol-v1.md prospectively fixes twelve single mutants, their deciding layers, three circuit cases, numerical tolerances, a hard execution budget, equivalent/blind controls and fail-closed retention rules. All twelve remain **PLANNED/UNEXECUTED**.

## 6. Threats to validity
The instance is extremely small and synthetic. It omits grid physics, dynamics and realistic uncertainty. Exact statevector simulation is classical and scales exponentially. Selected mutations cannot estimate general fault-detection power, and the prospective set was hand-designed on one development fixture. The ideal mixer has been checked at three fixed parameter pairs, but finite-shot sampling, transpilation, noise models and hardware have not been verified. The October 19 grid was repeated and incompletely retained, so its procedural acceptance failed. The angle grid may miss better parameters. A weak-penalty failure is unsurprising and establishes neither novelty nor advantage.

## 7. Current conclusion
The evidence supports a narrow engineering claim: formulation, diagonal-phase, ideal SDK cost-plus-mixer, readout, application metrics and evidence retention can be separated and audited on this toy. The exploratory search lowered mean encoded energy without improving every engineering metric, and its workflow violated the frozen aggregate budget. The evidence does not show improvement over classical methods. Whether the layered protocol detects the prospectively declared mutants or generalizes usefully remains open.

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
| Statevector interface | `results/2026-10-07-statevector-acceptance.json` | Nine checks; predicted global phase handled | NumPy oracle |
| Qiskit cost circuit | `results/2026-10-08-qiskit-cost-circuit.json` | Three angles; nine checks; max error (1.53\times10^{-15}) | Ideal cost layer only |

The staged checks intentionally avoid using the SDK circuit as its own oracle. The mixer acceptance contract is source-grounded in `docs/qaoa-reading-notes.md` and was executed on 12 October (Section 10). Six-qubit parameter search remains **PLANNED/UNEXECUTED**. The manuscript remains educational and unsubmitted.

## 10. Mixer, readout and baseline reconciliation — 2026-10-16

### Executed methods and results
The 12 October ideal six-qubit p=1 experiment compared three prespecified angle pairs against an independent amplitude-pairing oracle. Ten checks passed, with maximum component error 1.36e-15; factor-two, sign and layer-order mutations were rejected. Evidence: results/2026-10-12-qiskit-mixer.json and src/verify_qiskit_mixer.py. These are historical results, not a new execution on 16 October.

The 15 October readout audit independently enumerated all 64 states and compared expected energy with an SDK observable at the same three pairs. Twenty-six checks passed. At gamma=0.2, beta=0.31, mean energy was 49.26741508546327, physical-feasibility mass 0.6330953684437471 and encoding-consistency mass 0.01604168028438998. The latter event requires D+s=5; the former only D<=5. No angle was selected by its outcome. Evidence: results/2026-10-15-readout.json. The unpublished 13–14 October package was not recovered; those dates remain incomplete and are not counted as executions.

On 16 October a new standard-library exact-rational reference audit enumerated eight original decisions and 64 encoded states. Eleven checks passed, including row-by-row agreement with all 64 earlier readout labels and energies. The unique constrained optimum is x=3 (serve loads 0 and 1), with unserved priority 6. The encoded minimum is index 3 with energy 6. A deterministic priority/demand greedy construction also finds that solution on this fixture; this does not establish greedy optimality generally. No Qiskit circuit or parameter search ran in this new audit.

| Reference distribution | Mean E | Physical mass | Consistent encoding | Optimal load mass | Encoded ground mass |
|---|---:|---:|---:|---:|---:|
| Uniform 64 encoded states | 50 | 5/8 | 5/64 | 1/8 | 1/64 |
| Uniform 8 load choices, canonical nonnegative slack | 49/4 | 5/8 | 5/8 | 1/8 | 1/8 |
| Greedy decision with canonical slack | 6 | 1 | 1 | 1 | 1 |

Canonical slack is max(0,5-D), and does not repair overloaded load choices. These distributions differ in representation and cannot be presented as interchangeable baselines. Exact enumeration supplies truth, not a budget-matched QAOA competitor. New evidence: results/2026-10-16-baseline-references.json and src/verify_baseline_references.py.

### Interpretation and prospective boundary
The fixture is already solved by a transparent classical rule, limiting its value as a solver-performance demonstration. Its present value is a tractable verification fixture. In particular, uniformly distributed load choices have identical physical success whether slack is random or canonical, while encoded success differs by a factor of eight. Reporting only an unnamed “success rate” would confound representation with decision quality.

The next pilot will minimize mean E with fixed budget and report physical optimal-load probability and encoded ground-state probability separately. The local protocol is not an external preregistration or independent evaluation: earlier development outputs were already observed. There is no held-out instance and no novelty, realistic resilience, speedup or advantage claim. All research-routine scenes are SIMULATED NARRATIVE; this manuscript is educational and unsubmitted.

### Revision record
v0.4 removes stale statements that the mixer was unexecuted, incorporates R13/R14 with dated evidence, corrects the October 7 evidence filename and adds the prospective pilot boundary. No historical evidence file is overwritten.


## 11. Oracle boundary and mutation protocol — 2026-10-23

Targeted full-text reading of Quito and QDiff sharpened the protocol boundary.
Quito assumes a user-supplied specification of valid inputs and output
probabilities. Its wrong-output oracle can reject specified-zero outcomes, while
its statistical probability oracle treats non-rejection as inconclusive. QDiff
compares supposedly equivalent variants against a collective empirical
reference; divergence supports inconsistency, but common-mode agreement is not
independent ground truth. These methods inform future sampled and stack-level
work but do not replace the exact fixture oracles used here.

The project therefore predeclares five layers: exact formulation enumeration,
global-phase-aligned complex-state comparison, readout invariants, separately
named physical/application metrics, and evidence retention. Retention makes a
decision auditable but cannot establish scientific correctness.

The October 22 table declared twelve mutants. Review on October 23 corrected M02
before execution: swapping slack weights 1 and 4 preserves the representable
slack set and may survive reduction over slack, while violating the labeled
bit-to-weight contract. Protocol v1 now fixes this as a split-oracle control.
Eleven mutants are predeclared killable; M11 is an expected global-phase
survivor. M02's reduced oracle, M11's phase-aligned comparison and M12's
pre-mixer probability check are reported as separate expected survivals.

The hard budget is two exhaustive 64-state formulation passes and fifteen SDK
statevector constructions, with in-memory postprocessing for the remaining
mutants. No search, shots, optimizer, transpilation, noise, cloud service or
hardware is authorized. An exception is an invalid run rather than a kill;
baseline or provenance failure aborts the whole pilot. All results remain
**PLANNED/UNEXECUTED**.

### Revision record

v0.5 reconciles the manuscript with the October 19 exploratory pilot and its
protocol deviation, incorporates the Quito/QDiff oracle assumptions, and links
the frozen bounded mutation protocol. No numerical experiment ran for this
revision, and no mutation outcome or score is claimed.
