# R15 pilot comparison protocol v1 — frozen 2026-10-16

**Prospective local protocol, not an external preregistration.** Independent educational personal project; no affiliation or submission. Search is **PLANNED/UNEXECUTED**. This document is frozen before the new six-qubit angle grid is evaluated. Prior three-qubit sweeps and three fixed six-qubit settings are development evidence, not held-out evaluation.

## Question and scope
On the existing synthetic fixture only, does a bounded p=1 parameter grid lower expected penalized energy relative to the analytic uniform distribution, and what happens to physically optimal load probability? A result answers neither scalability nor quantum advantage. Larger-instance benchmarking (R08) remains open.

Fixture: demands (2,3,4), priorities (3,5,6), capacity 5, penalty 2; load index x=x0+2*x1+4*x2, slack s=y0+2*y1+4*y2; basis index i=x+8*s. Energy E=U+2*(D+s-5)^2 is minimized. U=sum priorities of unserved loads. Use the audited ideal six-qubit circuit: uniform initial state, cost exp(-i*gamma*E), then RX(2*beta) on each qubit. No shots, noise or hardware.

## Frozen candidate budget and selection
- Exactly 256 candidates: gamma=2*pi*j/16 and beta=pi*k/16, j,k in 0..15; iterate j outermost, k innermost. Include zero; exclude duplicate endpoint.
- Select smallest expected E. Values within absolute 1e-11 of the minimum are tied; choose lowest candidate ordinal among them. Do not select by secondary metrics.
- Record all 256 candidates, full 64-state probabilities, metrics and checks, not just the winner.
- No random restart, adaptive optimizer, post-hoc refinement, rescaled energy, repair or penalty retuning. Any change requires v2 with rationale and a separate result, retaining v1.
- A candidate evaluation counts even if it fails. No silent retry or omission. Abort on invalid normalization, nonfinite output or SDK/oracle discrepancy above 1e-11; persist partial results as FAILED.
- Maximum 256 search circuit evaluations plus at most one separately counted independent winner validation. No sampling. Thirty-second wall-clock safety limit for search; persist actual evaluated count on timeout. Report construction, oracle, validation and total wall time separately if available. Timing is descriptive, not a speedup measure.
- Run the existing mixer/readout regression gates before search and keep their costs separate from the 256-evaluation budget. Independently validate the winner with the amplitude-pairing oracle. Retain source/dependency hashes, Python/NumPy/Qiskit versions, UTC timestamp and command.

Integer diagonal energies give the cost a 2*pi period. RX(2*beta) has a pi beta period up to global phase for each qubit. This is a bounded grid, not a proof of the continuous optimum.

## Metrics (all required; no combined “feasibility” score)
For normalized probabilities p_i:
| Metric | Definition / reporting rule |
|---|---|
| Primary mean energy | sum p_i E_i, including identity offset |
| Physical feasibility | sum p_i over D(x)<=5, ignoring slack |
| Encoding consistency | sum p_i over D(x)+s=5 |
| Physical optimal-load probability | sum p_i for feasible x with U(x)=U*, including all slack encodings |
| Encoded ground-state probability | sum p_i for E_i=E* |
| Conditional service loss | sum of p_i U(x) over physically feasible states divided by physical mass; null if mass<=1e-11 |

Report mean-energy excess above E* (not an approximation ratio dependent on offsets). Also report differences from uniform in every metric. No significance test or confidence interval is appropriate for these deterministic exact calculations. Success on the primary outcome means mean-energy improvement >1e-11, not merely nonzero optimal-load probability. Report a primary improvement with a secondary deterioration as mixed, not uniformly better.

## Classical references and representation fairness
1. Enumerate all eight original load decisions, filter capacity, retain **all** minimizing decisions. Independently enumerate all 64 encoded states, retain **all** energy minimizers. These are exact truth references with different search spaces, not budget-matched algorithms.
2. Uniform over all 64 encoded states is the representation-matched analytic distribution baseline. No random shots are drawn.
3. A transparent feasible priority/demand greedy rule sorts decreasing priority/demand, ties by ascending load index, and accepts each load if capacity permits. Give it canonical residual slack. Report its inspected decisions, construction rule and deterministic metrics. This is an engineering baseline, not a tuned competitor or a general guarantee.
4. Uniform over the eight load decisions with canonical slack max(0,5-D) is an optional **representation-adjusted** baseline, clearly labeled. It must not be confused with uniform six-bit output.
No equal wall-time or speedup claim: exact statevector calculations and classical enumeration use different work units. A later true performance comparison needs prespecified common resources and appropriate classical solvers.

## Data split and release gate
This is a development/pilot instance; no holdout exists. Never rename this fixture a test set. R08 must later freeze independent training/validation/held-out instance generation, penalties and seed manifest before broader claims.
Before executing R15 search: protocol committed; all prior regression gates pass; baseline reference audit passes. After execution: publish every candidate, winner validation, failures and provenance. If expected energy improves but physical optimal-load probability worsens, report both. No claim of useful power-system control: the fixture has no network flows, storage dynamics, resilience disturbances or realistic uncertainty.

## Source checks — 2026-10-16
- Farhi, Goldstone and Gutmann (2014), *A Quantum Approximate Optimization Algorithm*: https://arxiv.org/abs/1411.4028. Foundational QAOA source; not evidence for this toy's performance.
- IBM RXGate documentation: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RXGate. Rechecked matrix convention exp(-i*theta*X/2).
- Primary conventions were derived in docs/qaoa-reading-notes.md. Budget, metrics and acceptance rules above are project design choices, not prescriptions attributed to those sources.

