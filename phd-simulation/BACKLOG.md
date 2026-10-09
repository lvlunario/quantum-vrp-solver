# Research backlog
| ID | Work | Status | Acceptance evidence |
|---|---|---|---|
| R01 | Charter and year calendar | Done | README, charter and 365 calendar rows |
| R02 | Three-qubit toy and independent checks | Done | Source, three passing tests and raw JSON |
| R03 | Derive a sufficient penalty bound on the toy | Done | docs/penalty-bound.md; exact all-minimizer audit |
| R04 | QUBO with slack-variable encoding | Done (toy formulation only) | docs/qubo-equivalence.md; all 64 energies and eight reduced decisions verified |
| R05 | Read original QAOA paper beyond abstract | Done (foundational source only) | docs/qaoa-reading-notes.md; equation-grounded conventions and limitations |
| R06 | Literature map of quantum testing | Planned | Verified papers and explicit novelty assessment |
| R07 | Fault catalog and metamorphic tests | Planned | Independent test oracle and faulty cases |
| R08 | Benchmark protocol and classical solvers | Planned | Fair budget and held-out instance plan |
| R09 | Paper A complete educational draft | In progress | v0.3 evidence traceability and limits; broader review still open |
| R10 | First-year review | Planned | Report, slides and year-two decision |

R11: Done for the toy — docs/ising-mapping.md and results/2026-10-05-ising-audit.json; all 64 energies and eight checks pass.

R12: Done for the ideal cost-layer statevector boundary — Qiskit 2.5.2 executed a six-qubit circuit in a pinned environment; nine checks passed across three angles. Sign, reversed-order and omitted-interaction faults were rejected. See docs/qiskit-cost-circuit.md and results/2026-10-08-qiskit-cost-circuit.json. Transpilation, sampling, noise and hardware remain unverified.

Next R13: implement the one-layer mixer against the acceptance contract in docs/qaoa-reading-notes.md. Required checks include beta-zero identity, gamma-zero uniform probabilities, norm, independent tensor-product agreement, `RX(2*beta)`, circuit order, and deliberate sign/factor/order mutations. **PLANNED/UNEXECUTED.**

Blocker: no current execution blocker. The next evidence boundary is mixer correctness, not parameter optimization.
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
