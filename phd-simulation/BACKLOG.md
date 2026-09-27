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

Next R11: map the verified six-variable QUBO to an Ising expression and check all basis energies independently; circuit implementation remains PLANNED.

Blocker: algebraic QUBO is verified, but circuit decomposition, bit-order conventions and a six-qubit execution are not yet verified.
Risk: a toy feasibility result may be obvious rather than novel; usefulness must come from a generalizable verification method.

## Catch-up evidence — 2026-09-27
Story dates September 23–25 reconstructed at the user's explicit request. All new experiments ran September 27; see results/week01-formulation-audit.json. Nine exact checks passed. Two intentional fault injections are pilot examples only; R07 remains planned for a general catalog. R05 remains planned: only records/abstracts checked this session. Day 1's lambda=1 single-argmin interpretation is corrected in docs/penalty-bound.md. No workday existed before the September 22 project start.

