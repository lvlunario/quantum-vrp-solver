# Research backlog
## October 20 retention update
14 workflow tests passed; results/2026-10-20-retention-audit.json. New source: src/evidence_store.py and src/verify_evidence_store.py; pilot CLI instrumented. Existing-output refusal precedes SDK imports. Event files retain full completed-candidate rows; inventory counts retained attempts and missing terminal records, not unknown past runs. Zero new SDK circuits or quantum search evaluations. Historical 512 evaluations and NOT MET R15 acceptance are unchanged. See docs/run-retention.md. R06 seed map started, not completed. Next: one fixed SDK point and injected failure, not another grid.

| ID | Work | Status | Acceptance evidence |
|---|---|---|---|
| R01 | Charter and year calendar | Done | README, charter and 365 calendar rows |
| R02 | Three-qubit toy and independent checks | Done | Source, three passing tests and raw JSON |
| R03 | Derive a sufficient penalty bound on the toy | Done | docs/penalty-bound.md; exact all-minimizer audit |
| R04 | QUBO with slack-variable encoding | Done (toy formulation only) | docs/qubo-equivalence.md; all 64 energies and eight reduced decisions verified |
| R05 | Read original QAOA paper beyond abstract | Done (foundational source only) | docs/qaoa-reading-notes.md; equation-grounded conventions and limitations |
| R06 | Literature map of quantum testing | In progress | docs/quantum-testing-literature-map.md: three verified seeds; targeted reading versus abstract screening explicit. Citation chaining and novelty comparison remain open. |
| R07 | Fault catalog and metamorphic tests | Planned | Independent test oracle and faulty cases |
| R08 | Benchmark protocol and classical solvers | Planned | Fair budget and held-out instance plan |
| R09 | Paper A complete educational draft | In progress | v0.4 mixer/readout reconciliation and baseline references; broader review still open |
| R10 | First-year review | Planned | Report, slides and year-two decision |

R11: Done for the toy — docs/ising-mapping.md and results/2026-10-05-ising-audit.json; all 64 energies and eight checks pass.

R12: Done for the ideal cost-layer statevector boundary — Qiskit 2.5.2 executed a six-qubit circuit in a pinned environment; nine checks passed across three angles. Sign, reversed-order and omitted-interaction faults were rejected. See docs/qiskit-cost-circuit.md and results/2026-10-08-qiskit-cost-circuit.json. Transpilation, sampling, noise and hardware remain unverified.

R13: Done for the ideal one-layer mixer boundary — Qiskit 2.5.2 matched an independent amplitude-pairing oracle across three predetermined angle pairs; all ten checks passed. Beta-zero identity and gamma-zero uniform probabilities passed, and factor-two, mixer-sign, and layer-order mutations were rejected. See docs/qiskit-mixer-audit.md and results/2026-10-12-qiskit-mixer.json. No optimizer, shots, transpilation, noise or hardware was used.

R14: Done for the fixed synthetic exact-statevector fixture — 26 checks pass; docs/readout-audit.md and results/2026-10-15-readout.json. Physical feasibility and encoding consistency are separately reported; no optimization or shot-based readout verified.

R15: Numerical pilot executed October 19, **WITH PROTOCOL DEVIATION**; see docs/pilot-v1-results.md and results/2026-10-19-run-ledger.json. Two unchanged full grids were run (512 search evaluations aggregate); provenance repair replay overwrote the first raw JSON. The second complete grid, all 256 probability vectors and independent winner validation are retained. Numerical checks pass, but strict aggregate budget and complete run-retention acceptance are NOT met. Do not mark unqualified Done.

Blocker update October 20: collision refusal, per-candidate append-only events and retained-directory inventory implemented; 14 synthetic workflow tests pass. Real SDK callback integration remains untested after instrumentation; no new parameter search until a bounded fixed-point/failure integration check and ledger reconciliation. No SDK availability blocker. The fixed pilot is exploratory evidence, not a compliant benchmark or held-out result.
Risk: a toy feasibility result may be obvious rather than novel; usefulness must come from a generalizable verification method.

## Catch-up evidence — 2026-09-27
Story dates September 23–25 reconstructed at the user's explicit request. All new experiments ran September 27; see results/week01-formulation-audit.json. Nine exact checks passed. Two intentional fault injections are pilot examples only; R07 remains planned for a general catalog. Day 1's lambda=1 single-argmin interpretation is corrected in docs/penalty-bound.md. No workday existed before the September 22 project start.

## Recovery — 2026-10-05
September 30 code, raw output and draft survived locally without publication. Re-execution October 5 reproduced all raw states and source hashes; eight checks pass. First publication is October 5. September 28–29 and October 1–2 remain incomplete; no meetings or experiments are claimed for those dates. See docs/recovery-2026-10-05.md.

## Phase audit — 2026-10-06
Executed `src/verify_phase_evolution.py` with the Python standard library on the existing synthetic toy. Nine checks passed. Direct and decomposed phases agree across 256 state-angle pairs; exponent-sign and missing-factor-two faults were detected. No SDK circuit, mixer, sampler, optimizer or hardware was executed.

## Statevector acceptance — 2026-10-07
Executed `src/verify_statevector_interface.py` with NumPy 2.3.5. Nine checks passed. Three offset-free statevectors fail naive strict comparison but agree after removing the predicted global phase; exponent-sign and reversed-order faults remain rejected. This was an acceptance harness, not an SDK circuit result.

## Qiskit cost circuit — 2026-10-08
Created a clean Python 3.12 environment and executed Qiskit 2.5.2 exact statevector evolution. Nine checks passed for a circuit with six RZ and fifteen RZZ gates across three angles. The SDK statevector matched the independent oracle within `1.53e-15`; three deliberate circuit mutations were rejected. No mixer, shots, transpilation, noise model or hardware was used.

## Friday synthesis — 2026-10-09
Closed R05 for the original QAOA paper with full-text, equation-grounded notes and an IBM `RXGate` cross-check. Updated the working manuscript to v0.3 and added a weekly evidence table. No numerical experiment ran today. R13 is defined but remains planned; R06 remains open because a single foundational paper is not a literature map.

## Qiskit mixer audit — 2026-10-12
Executed `src/verify_qiskit_mixer.py` in a fresh pinned Python 3.12 environment. All ten checks passed across three predetermined angle pairs; the maximum SDK/oracle component error was `1.36e-15`. Missing factor-two, reversed mixer sign and mixer-before-cost faults were rejected. R13 is complete only for local exact statevectors. No parameter search, sampling, transpilation, noise model or hardware was used.

## Readout audit — 2026-10-15
New local execution in pinned Qiskit environment; 26 checks pass over all 64 one-hot states and three fixed circuit settings. An initial uniform-mean test expectation of 62 failed and was corrected by derivation to 50. The primary setting has physical mass 0.6330953684437471 and encoding mass 0.01604168028438998. Bit-order, amplitude-weighting and identity-offset reporting faults are detected. October 13–14 local files were not recovered; interruption logs record both days as incomplete. No historical results or meetings were reconstructed. See docs/gap-2026-10-13-14.md.

## Friday synthesis — 2026-10-16
Manuscript v0.4 reconciles R13/R14 and corrects a broken October 7 evidence filename. Prospective local R15 protocol fixes 256 candidate evaluations, deterministic energy selection, failure handling and separate physical/encoded metrics. A new exact-rational classical reference audit passes 11 checks across eight load decisions and 64 encoded states; the simple greedy rule finds the toy optimum. No QAOA search or new SDK execution occurred. Broader R08 benchmarking and R06 novelty review remain open; there is no held-out evidence. Weekend October 17–18 is rest; next active story date October 19.

## Monday pilot — 2026-10-19
Eight regression modules pass 91 underlying checks per run; thirteen runner gates pass. The retained grid completed 256 candidates with no failed evaluations; maximum SDK/oracle error 1.31e-14. Energy-only selection chooses ordinal 99 (tie with 173): mean energy 26.756841 versus uniform 50; physical feasibility 0.977671 versus 0.625, but optimal-load probability 0.083381 versus 0.125 and conditional service loss 10.931974 versus 9.6. Mixed outcome; greedy already gives the exact optimum. Actual aggregate execution was TWO grids plus two winner validations; initial materialization appended newlines, and repair/replay overwrote first full evidence. Only its observed summary and hashes survive. Frozen v1 remains unchanged; R15 procedural acceptance is not met. Next: refuse output collisions and retain run ledgers before further experiments, then start R06. No hardware, shots, noise, adaptive optimization, real meeting or submission occurred.

