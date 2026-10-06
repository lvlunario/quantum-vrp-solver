# Research backlog
| ID | Work | Status | Acceptance evidence |
|---|---|---|---|
| R01 | Charter and year calendar | Done | README, charter and 365 calendar rows |
| R02 | Three-qubit toy and independent checks | Done | Source, three passing tests and raw JSON |
| R03 | Derive a sufficient penalty bound on the toy | Done | docs/penalty-bound.md; exact all-minimizer audit |
| R04 | QUBO with slack-variable encoding | Done (toy formulation only) | docs/qubo-equivalence.md; all 64 energies and eight reduced decisions verified |
| R05 | Read QAOA paper beyond abstract | Planned | Page/section-grounded notes and limitations |
| R06 | Literature map of quantum testing | Planned | Verified papers and explicit novelty assessment |
| R07 | Fault catalog and metamorphic tests | Planned | Independent test oracle and faulty cases |
| R08 | Benchmark protocol and classical solvers | Planned | Fair budget and held-out instance plan |
| R09 | Paper A complete educational draft | Planned | Evidence traceability, limitations, source checks |
| R10 | First-year review | Planned | Report, slides and year-two decision |

R11: Done for the toy — docs/ising-mapping.md and results/2026-10-05-ising-audit.json; all 64 energies and eight checks pass.

R12: In progress — plain-Python diagonal phase audit completed; nine checks pass over 64 states and four angles. See docs/phase-evolution.md and results/2026-10-06-phase-audit.json. SDK statevector, layout and circuit synthesis remain unverified.

Next R12: compare a six-qubit SDK statevector with the oracle up to global phase, then add a mixer only after the interface passes.

Blocker: algebraic QUBO/Ising mapping and a plain-Python bit-order contract are verified. SDK integration, circuit decomposition and six-qubit execution remain unverified.
Risk: a toy feasibility result may be obvious rather than novel; usefulness must come from a generalizable verification method.

## Catch-up evidence — 2026-09-27
Story dates September 23–25 reconstructed at the user's explicit request. All new experiments ran September 27; see results/week01-formulation-audit.json. Nine exact checks passed. Two intentional fault injections are pilot examples only; R07 remains planned for a general catalog. R05 remains planned: only records/abstracts checked this session. Day 1's lambda=1 single-argmin interpretation is corrected in docs/penalty-bound.md. No workday existed before the September 22 project start.

## Recovery — 2026-10-05
September 30 code, raw output and draft survived locally without publication. Re-execution today reproduced all raw states and source hashes; eight checks pass. First publication is October 5. September 28–29 and October 1–2 remain incomplete; no meetings or experiments are claimed for those dates. See docs/recovery-2026-10-05.md. R05 remains planned.

## Phase audit — 2026-10-06
Executed `src/verify_phase_evolution.py` with the Python standard library on the existing synthetic toy. Nine checks passed. Direct and decomposed phases agree across 256 state-angle pairs; exponent-sign and missing-factor-two faults were detected. The cost layer preserved every basis probability. No SDK circuit, mixer, sampler, optimizer or hardware was executed. R05 remains planned.
