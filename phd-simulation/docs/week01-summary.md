# Week 1 — September 22–25, 2026
**Personal Quantum Research Project.** Independent educational project; Norway is a fictional setting, not an affiliation.

## What was actually completed
September 22's existing episode and outputs are retained. September 23–25 were missing from GitHub and were reconstructed on **September 27, 2026**, following Leo's request. The new experiment actually ran on September 27; no earlier execution or unattended background work is claimed. The project began Tuesday, so Monday September 21 is outside its window. The weekend remains rest in the story.

| Story day | Work and result | Evidence |
|---|---|---|
| Tue Sep 22 | Existing three-load experiment: a weak penalty favors overload | [Journal](../logs/2026-09-22.md) |
| Wed Sep 23 | Derive strict penalty bound; expose an infeasible tie at lambda=1 | [Journal](../logs/2026-09-23.md), [proof](penalty-bound.md) |
| Thu Sep 24 | Build six-variable QUBO; verify every energy; inject two faults | [Journal](../logs/2026-09-24.md), [formulation](qubo-equivalence.md) |
| Fri Sep 25 | Correct manuscript interpretation, audit claims and plan next week | [Journal](../logs/2026-09-25.md), [manuscript v0.2](../papers/01-verification-protocol.md) |

## Main finding
At penalty 1, a safe schedule and an overloaded schedule tie at score 6. Finding the safe one first does not certify the model. For this specific instance, penalty **strictly greater than 1** excludes every infeasible global minimizer. This says nothing about whether an approximate solver finds a global minimum.

## Actual execution
[Source](../src/verify_formulation.py) and [full raw output](../results/week01-formulation-audit.json).
- Nine checks passed using exact arithmetic and Python's standard library.
- All 64 QUBO state energies match the direct residual expression at penalty 2.
- All eight decisions retain their original best energy after minimizing over slack.
- Deliberately insufficient slack changes the all-off score from 14 to 22.
- Deliberately omitted cross terms cause 57 energy mismatches out of 64.
- Synthetic fixed inputs; no random shots, external data, hardware or new QAOA execution.

Reproduce from `phd-simulation`: `python src/verify_formulation.py`. The recorded output contains the actual execution time, Python version, source hash, configuration, full energy table and limitations. A new run changes the timestamp, not the deterministic scientific result.

## Why this resembles research work
The week makes progress by correcting a claim, exposing a boundary case, proving a small equivalence and documenting limits. The fictional Finland-setting methods exchange and seminar questions are labeled SIMULATED NARRATIVE. They are educational scenarios, not real collaboration or peer review. No paper was submitted.

## Continuation
The daily task was confirmed enabled on September 27, with its last recorded run on September 26. The ordinary Saturday rest policy explains no Saturday episode; the available task metadata does not explain the missing September 23–25 publications. No schedule change is claimed.

Next planned workday is Monday September 28: derive an Ising mapping, independently verify its basis-state energies and decide the circuit convention. R05 full-text QAOA reading remains open. The rest of the week returns to foundations in complex amplitudes, qubits and measurement. Actual circuit execution and broader benchmark claims remain gated on evidence.

**Ten-minute exercise:** for decisions 101 and 110, compute demand, unserved priority and total energy at penalties 1 and 2. Then explain why checking only the best returned answer can miss a tie.
