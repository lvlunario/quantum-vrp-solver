# Oracle assumptions and prospective mutant-to-layer plan

Status: **FROZEN/UNEXECUTED — 2026-10-22**. Evidence creation occurred on
October 22, 2026. This document records source-grounded assumptions and
predeclared hypotheses; it reports no new circuit, sample, parameter search,
hardware run, or mutation score.

## Primary sources read directly

1. Shaukat Ali, Paolo Arcaini, Xinyi Wang, and Tao Yue, “Assessing the
   Effectiveness of Input and Output Coverage Criteria for Testing Quantum
   Programs,” ICST 2021, pp. 13–23.
   DOI: https://doi.org/10.1109/ICST49551.2021.00014
   Author full text: https://cms.simula.no/sites/default/files/publications/files/quito.pdf
2. Xinyi Wang, Paolo Arcaini, Tao Yue, and Shaukat Ali, “Quito: a
   Coverage-Guided Test Generator for Quantum Programs,” ASE 2021 tool
   demonstration.
   DOI: https://doi.org/10.1109/ASE51524.2021.9678798
   Author full text: https://cms.simula.no/sites/default/files/publications/files/quito_tool.pdf
3. Jiyuan Wang, Qian Zhang, Guoqing Harry Xu, and Miryung Kim, “QDiff:
   Differential Testing of Quantum Software Stacks,” ASE 2021, pp. 692–704.
   DOI: https://doi.org/10.1109/ASE51524.2021.9678792
   Author full text: https://www.cs.tulane.edu/~wjiyuan/research/ASE2021_QDiff.pdf

## Quito: what its oracles assume

Quito models a program as valid classical inputs mapped to probability
distributions over measured classical outputs. Correctness assessment requires
a program specification identifying valid inputs and expected output
probabilities. Coverage alone is not an oracle.

- **WOO (Wrong Output Oracle):** an observed input-output pair is a definite
  failure when the specification assigns that output probability zero.
- **OPO (Output Probability Oracle):** repeated suites yield observed
  input-output proportions. A one-sample Wilcoxon signed-rank test compares
  those proportions with the specified probability. Rejection indicates a
  likely failure at the selected significance level; non-rejection is
  explicitly inconclusive, not a correctness certificate.
- Input, output, and input-output coverage describe which measured cases were
  exercised. They do not establish phase coverage.
- Budgets, the number and grouping of repeated suites, and significance choices
  influence cost and conclusions. The original study used five small programs,
  single seeded one-qubit mutations, ideal simulator qubits, and no modeled
  hardware error. The authors explicitly identify phase blindness and
  scalability as limitations.

For this project, Quito-like WOO/OPO reasoning belongs at the sampled readout
boundary. It cannot replace the exact complex-amplitude oracle used to catch
pre-mixer relative-phase faults.

## QDiff: what differential evidence assumes

QDiff creates syntactically different variants using gate transformations
intended to preserve the unitary matrix. It executes variants through different
stack configurations and compares empirical output distributions.

- The first oracle assumption is **transformation validity**: variants are
  supposed to represent the same unitary behavior.
- QDiff forms a reference by averaging the observed distributions of the
  equivalent-variant group. It then uses a distribution distance such as a
  Kolmogorov–Smirnov test or cross entropy and reports divergence beyond a
  threshold.
- Measurement budgets depend on a distance threshold, confidence target,
  outcome-space size, and empirically calibrated platform constant.
- Varying frontend and backend choices helps label a *potential* source of
  divergence. It does not prove which implementation is correct.
- Because the reference is collective rather than independently derived,
  common-mode error can survive. Filtering noise-dominated circuits also
  changes which cases reach the differential oracle.

For this project, differential testing is useful later for SDK/compiler/backend
consistency. It is weaker than the independent exact oracle for the current
six-qubit ideal circuit, but covers stack interactions the exact local oracle
does not.

## Frozen mutant-to-layer table

“Killed” means the named layer is expected to reject the mutant under a future
separately approved protocol. “Survives” is also a prospective prediction. No
entry below has been executed as part of this plan.

| ID | Predeclared mutation | Primary layer expected to decide | Expected observation |
|---|---|---|---|
| M01 | Reduce the capacity-penalty coefficient below the sufficient bound | L1 formulation enumeration | Killed: at least one invalid state becomes an unintended minimizer or tie |
| M02 | Reverse one slack-bit binary weight | L1 formulation enumeration | Killed: reduced encoded energy disagrees with the constrained objective |
| M03 | Reverse the cost-layer exponent sign | L2 exact statevector | Killed: relative complex amplitudes disagree after global-phase alignment |
| M04 | Omit the factor of two in one RZZ angle | L2 exact statevector | Killed: component error exceeds the frozen tolerance |
| M05 | Apply mixer before cost | L2 exact statevector | Killed at nontrivial predetermined angles |
| M06 | Use RX(beta) instead of RX(2*beta) | L2 exact statevector | Killed; this is a regression control already observed elsewhere, but unexecuted in the future mutation study |
| M07 | Decode Qiskit bits in forward rather than little-endian order | L3 readout | Killed: hand-enumerated energy or load mapping disagrees |
| M08 | Weight metrics by amplitudes rather than squared magnitudes | L3 readout | Killed: normalization and expectation checks fail |
| M09 | Omit the Ising identity offset only in reporting | L3 readout | Killed: selected state may remain unchanged while reported energy shifts |
| M10 | Collapse physical feasibility and auxiliary consistency into one label | L4 application metrics | Killed: separate denominators and fixture invariants disagree |
| M11 | Multiply the entire state by one global phase | L2 phase-aligned physical equivalence | Survives the correct equivalence check; a naive componentwise comparator would falsely kill it |
| M12 | Introduce a probability-preserving relative-phase error before the mixer | L2 exact statevector, with L3 as a documented blind control | Killed by L2; survives a pre-mixer computational-basis probability-only check |

Every future attempt must also pass **L5 retention**: reserve output before
execution, append the attempt, preserve failures, and emit a terminal digest
only for success. L5 cannot establish scientific correctness; it establishes
whether the scientific evidence remains auditable.

## Execution gate and limitations

The table freezes mutant identities, expected deciding layers, and blind
controls before any observation. A later protocol must still freeze angle/input
cases, tolerances, total executions, treatment of equivalent mutants, and
failure handling. R15's historical procedural acceptance remains **NOT MET**.
No new grid is authorized by this document.

This is a targeted reading, not a systematic review. Backward/forward citation
chaining, tool reproduction, stack-level differential execution, sampling,
noise, transpilation, and hardware remain outside today's evidence.
