# R06 fault-to-oracle matrix — 2026-10-21

Status: **IN PROGRESS**. This is a bounded comparison of verified sources and
project evidence, not a systematic review, completed novelty assessment, or
general mutation-score study. The project-specific mappings below are our
interpretation. No cited tool was reproduced today.

## Why one oracle is not enough

A quantum optimization workflow crosses several contracts: physical objective,
binary encoding, circuit phases, SDK semantics, measurement decoding,
application metrics, and evidence retention. A check that is strong at one
boundary can be blind at another. In particular, computational-basis
probabilities cannot reveal a pure relative-phase error before a mixer, while an
exact statevector oracle says nothing by itself about whether the decoded load
schedule is physically meaningful.

| Fault class | Minimum useful oracle in this project | Evidence or source | Known blind spot |
|---|---|---|---|
| Wrong penalty, missing cross term, or insufficient slack range | Exhaustive classical enumeration of all encoded states and reduction back to the original constrained problem | Project R01–R04 exact audits | A matching ground state does not prove equal excited-state dynamics or correct SDK construction. |
| Global phase only | State equivalence after explicit global-phase alignment | Project R11; Qiskit `Statevector.equiv` supplies the relevant SDK concept | A strict component comparison without alignment can reject physically equivalent states. |
| Exponent sign, missing factor two, reversed layer order, or wrong relative phase | Exact statevector comparison against an independently implemented amplitude oracle at predetermined points | Project R12–R13 and today's fixed-point check | Exact simulation does not cover sampling noise, transpilation, hardware, or broad input diversity. |
| Wrong qubit/bit order, amplitudes used as probabilities, omitted identity offset | Hand-enumerated diagonal observable plus independent probability-weighted readout | Project R14 | Correct expected energy can still hide poor physical feasibility or poor optimal-load probability. |
| Weak or unrepresentative test inputs | Coverage-guided or search-based generation, followed by a specified pass/fail oracle | Quito studies input/output coverage; QuSBT uses search-based test generation | Coverage or diversity is not correctness and can scale poorly. We have not compared these generators. |
| Platform/compiler/backend inconsistency without a full expected output | Differential or metamorphic relation across equivalent programs or implementations | QDiff compares quantum software stacks; MorphQ applies quantum-specific program transformations | Agreement can be common-mode wrong; transformations must genuinely preserve the intended semantics. |
| Lost or overwritten run evidence | Pre-execution reservation, append-only attempt/completion events, terminal digest, and explicit incomplete status | Project R15 retention guard and today's success/failure integration | Workflow retention is not a scientific oracle, immutable storage, or a global budget enforcer. |

## Source-checked method notes

- Huang and Martonosi's *Statistical Assertions for Validating Patterns and
  Finding Bugs in Quantum Programs* uses measurement-based statistical
  assertions and reference checks. It supports the general need for explicit
  expected properties; it does not make our exact phase oracle novel.
  https://arxiv.org/abs/1905.09721
- Wang, Arcaini, Yue and Ali's *QuSBT* uses search-based test-suite generation
  to seek failing cases in Qiskit simulation. We have verified metadata and the
  abstract only; no effectiveness comparison is claimed.
  https://arxiv.org/abs/2204.08561
- Ali, Arcaini, Wang and Yue evaluate quantum input, output and input-output
  coverage criteria (Quito). The DOI and publication metadata are verified;
  full method extraction remains open.
  https://doi.org/10.1109/ICST49551.2021.00014
- Wang et al.'s *QDiff* is a differential-testing approach for quantum software
  stacks. Today it is included as a platform-level oracle family, not as
  evidence about our QAOA circuit.
  https://doi.org/10.1109/ASE51524.2021.9678792
- Paltenghi and Pradel's *MorphQ* generates valid quantum programs and applies
  quantum-specific metamorphic transformations to address the oracle problem.
  https://arxiv.org/abs/2206.01111

## Decision for the next experiments

Use a layered acceptance record rather than a single pass/fail flag:

1. formulation equivalence;
2. phase-sensitive circuit equivalence;
3. probability/readout correctness;
4. physical and service metrics;
5. retained provenance and failure status.

The current six-qubit fixture can demonstrate the chain but cannot establish
generality or novelty. Before a new grid, R06 needs direct full-text extraction
for Quito and QDiff, backward/forward citation chaining, and a prospective
mutant table that states which layer should kill each mutant. The fault set must
not be selected after observing which checks pass.
