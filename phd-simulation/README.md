# Personal Quantum Research Project
**FICTIONAL PhD career simulation, 22 September 2026–21 September 2027.**
No employment, enrollment, collaboration, funding, peer review, or institutional endorsement is claimed.
This is an independent personal project using a fictional PhD-style research routine; no host institution is assigned.
This is a first-year research experience, not a PhD completed in one year.

## Your research question
**Can verification methods detect when hybrid quantum optimization produces misleading or infeasible microgrid decisions?**
The working theme is *Verification and reproducible benchmarking of quantum optimization for resilient microgrids*.
It combines power-system intuition, test engineering, Python and quantum computing. Research success can be a useful test method or a carefully explained negative result; quantum advantage is not promised.

## Start here
- [Latest: October 7 — defining global-phase-aware statevector acceptance](logs/2026-10-07.md)
- [Statevector acceptance contract and SDK blocker](docs/statevector-acceptance.md)
- [October 6 — auditing diagonal phase evolution](logs/2026-10-06.md)
- [Phase-evolution convention, nine checks and fault injections](docs/phase-evolution.md)
- [October 5 — recovering evidence and fixing the decoding contract](logs/2026-10-05.md)
- [Recovered September 30 episode, first published October 5](logs/2026-09-30.md)
- [Ising mapping and eight-check audit](docs/ising-mapping.md)
- [Publication gap and recovery record](docs/recovery-2026-10-05.md)
- [Week 1 catch-up summary, September 22–25](docs/week01-summary.md)
- Daily journals: [Sep 22](logs/2026-09-22.md), [Sep 23](logs/2026-09-23.md), [Sep 24](logs/2026-09-24.md), [Sep 25](logs/2026-09-25.md)
- [Important Day 1 correction: a feasible argmin can hide an infeasible tie](docs/penalty-bound.md)
- [Research charter and experimental protocol](docs/charter.md)
- [365-day planned calendar](calendar.csv), including weekends and simulated leave
- [Weekly goals](docs/weekly-plan.md)
- [Fictional international research network](docs/collaborators.md)
- [How each daily episode must run](RUNBOOK.md)
- [Research state](state.json) and [open work](BACKLOG.md)
- [First manuscript draft](papers/01-verification-protocol.md)
- [Executed toy experiment](results/day001-toy.json) and [source](src/toy_qaoa.py)
- [Initial lab talk outline](slides/01-kickoff.md)

## What an ordinary week feels like
Monday: literature and supervisor decisions. Tuesday: implementation and debugging.
Wednesday: experiments and a rotating collaborator discussion. Thursday: derivations, coursework and analysis.
Friday: write up evidence, group seminar and plan the next week. These are defaults, not a rigid daily ritual.
Normal simulated work: roughly 37.5 hours/week, including breaks, admin and seminars; ordinary day 08:30–16:30 with lunch.
Some days produce only a failed run, a corrected assumption or two paragraphs. A rejected hypothesis counts as progress.
Deadline weeks can reach 42–48 hours, with 2–4 hours on an occasional weekend. This is a scenario choice, not a claim about any institution's employment terms.
Leave entries produce short status logs rather than pretend experiments. July is deliberately quieter.

## Evidence labels
- **SIMULATED NARRATIVE:** invented meetings, reviewer feedback, travel and day-to-day events.
- **EXECUTED LOCAL EXPERIMENT:** real code run on explicitly synthetic toy data, with stored outputs.
- **PLANNED:** unexecuted experiment or future work. No invented numerical findings.
- **VERIFIED SOURCE:** real citation with a checked source URL.

The year is planned in advance; future daily logs are generated only as their dates arrive.
No external messages, invitations, hardware purchases or actual paper submissions are part of this simulation.
All project history belongs here in GitHub. No extra plugin is required for Markdown, Python, CSV, JSON or manuscript drafts.
Presentations can be produced later using the available presentation capability, with editable source and exports committed here when feasible.

## Reproduce Day 1
Use an isolated Python environment with NumPy 2.3.5 (the version used for the stored run).
From this folder run `python src/test_toy.py` and `python src/toy_qaoa.py`.
The result is an exact statevector simulation of a 3-qubit educational model, not execution on a quantum processor.

## Week 1 catch-up — created 27 September 2026
September 23–25 episodes were reconstructed on request, not completed on their story dates. New executed evidence: [formulation audit](results/week01-formulation-audit.json), nine passing checks, exhaustive six-variable QUBO equivalence, and two deliberate fault injections. Run `python src/verify_formulation.py` from this folder (Python standard library only). The source hash and actual UTC execution timestamp are retained in the output. No six-qubit circuit has been executed.
