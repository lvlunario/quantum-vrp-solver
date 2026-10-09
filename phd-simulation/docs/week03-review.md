# Week 3 evidence review and next acceptance boundary

**Story week:** 2026-10-05 to 2026-10-09  
**Scope:** independent personal simulation; no host institution.  
**Evidence status:** writing and synthesis today; numerical values below are carried from versioned, previously executed artifacts.

## Traceability table

| Claim | Versioned evidence | What was actually checked | Explicit limit |
|---|---|---|---|
| Six-variable Ising mapping preserves the QUBO | `docs/ising-mapping.md`; `results/2026-10-05-ising-audit.json` | All 64 states and eight acceptance checks | Synthetic toy only; no circuit |
| Cost-unitary phase decomposition is correct | `docs/cost-phase-conventions.md`; `results/2026-10-06-phase-audit.json` | 256 state-angle pairs; sign and factor-two faults rejected | Plain Python; no SDK |
| Statevector comparison handles known global phase | `docs/statevector-acceptance.md`; `results/2026-10-07-statevector-interface.json` | Nine checks; strict comparison corrected by predicted phase | NumPy oracle; Qiskit unavailable that day |
| Qiskit implements the intended ideal cost layer | `docs/qiskit-cost-circuit.md`; `results/2026-10-08-qiskit-cost-circuit.json` | Qiskit 2.5.2, three angles, six RZ + fifteen RZZ gates, nine checks, maximum strict error (1.53\times10^{-15}) | Exact statevector only; no mixer, sampling, transpilation, noise or hardware |
| Foundational QAOA conventions are source-grounded | `docs/qaoa-reading-notes.md` | Original paper equations and IBM RX definition checked | One foundational source, not a systematic review |

## Weekly interpretation

The week converted an algebraically verified synthetic penalty model into an independently checked ideal Qiskit cost circuit. Each stage has a separate oracle and fault probes, reducing the chance that one shared convention silently validates itself. The strongest current claim is narrow: under the pinned Qiskit 2.5.2 environment, the six-qubit ideal statevector produced by the implemented diagonal cost circuit agrees with the independent oracle for the tested angles.

This is not evidence that QAOA finds good schedules, that a mixer is correct, that finite-shot decoding works, or that a quantum method beats classical optimization. No new numerical experiment was run on 9 October; today consolidated evidence and set the next test contract.

## Next boundary: R13 mixer invariants

Implement the one-layer mixer only after encoding the acceptance criteria in `docs/qaoa-reading-notes.md`. The first executable should test identity at (\beta=0), uniform probabilities at (\gamma=0), norm preservation, analytical agreement with (\prod_j e^{-i\beta X_j}), correct Qiskit angle `2*beta`, and rejection of sign, factor-two, and order mutations. Preserve the current six-qubit bit-order contract and reuse the pinned environment.

## Simulated lab seminar — SIMULATED NARRATIVE

Leo presented the traceability table as a short internal-style seminar exercise. The fictional roles from Finland and Japan challenged whether global-phase tolerance might hide a wrong objective sign; the Denmark and Spain roles asked for a hard separation between circuit fidelity and solution quality. The recorded decision is to keep strict and phase-aligned comparisons side by side and to add the objective-direction mutation to the mixer/expectation tests. No real meeting, affiliation, message, or external collaboration occurred.

## Retrospective

- Good: algebra, phase, interface and SDK checks are now distinct evidence layers.
- Corrective action: manuscript language that still described the six-qubit circuit as planned has been updated.
- Open risk: the evidence remains a very small synthetic example and selected mutants do not estimate general fault-detection power.
- Next workday: implement and execute R13 without an optimizer; parameter search and classical baselines stay separate.
