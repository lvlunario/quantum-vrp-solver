# R06 seed map — 2026-10-20

Status: IN PROGRESS. A bounded initial search and targeted reading, not a
systematic review, exhaustive bibliography or established novelty claim.
No tools or published experiment results from these papers were reproduced.

## Search record and scope

Concept blocks: quantum programs/software; testing/assertions/faults;
oracles/coverage/reproducibility. Boolean expansion for the next pass:
`("quantum program" OR "quantum software") AND (test* OR assertion* OR fault*) AND (oracle OR coverage OR reproducib*)`.
Use arXiv for author manuscripts and ACM/IEEE for publication metadata.
Include directly relevant method papers and surveys, English, through October
20, 2026. Exclude hardware-only calibration and unsupported solver marketing.
Backward and forward citation chaining remain planned, not completed.

Today's searches included `site.arxiv.org quantum software testing Quito
assertion statistical testing Huang Martonosi` and `site.arxiv.org Quito quantum
input output coverage testing quantum programs Wang 2021`. The latter returned
substantial irrelevant material; it is NOT proof of a complete Quito search.
Direct primary pages below were opened and metadata checked October 20.

| Verified reference | Reading depth and source-supported method | Project implication (our interpretation) |
|---|---|---|
| Yipeng Huang and Margaret Martonosi (2019), *Statistical Assertions for Validating Patterns and Finding Bugs in Quantum Programs*. ISCA; DOI 10.1145/3307650.3322213. https://arxiv.org/abs/1905.09721 | Abstract and targeted full-text sections 3.3, 4.1–4.3. Measurement-based statistical assertions and cross-checking with closed-form/reference implementations. The paper warns that simple constraints alone do not validate a QFT. | Assertions and independent checks are established, not our invention. Our exact phase-sensitive comparison is distinct from a sampled distribution check, but distinction alone is not novelty. |
| Xinyi Wang, Paolo Arcaini, Tao Yue and Shaukat Ali (2022), *QuSBT: Search-Based Testing of Quantum Programs*. https://arxiv.org/abs/2204.08561 | Metadata and abstract only. Genetic-algorithm test-suite generation targeting failing cases; Qiskit simulation. | Future fault catalogs should address test-generation strategy, not only handpicked passing demonstrations. Do not claim a coverage or effectiveness comparison yet. |
| Matteo Paltenghi and Michael Pradel (2024), *A Survey on Testing and Analysis of Quantum Software*. https://arxiv.org/abs/2410.00650 | Metadata and abstract only; author preprint, not independently verified journal status. Broad testing, analysis and benchmark taxonomy. | Use for navigation, then inspect original methods. It is not primary experimental evidence that our approach works. |

## Decisions and open evidence

The candidate contribution is an auditable chain from physical objective to
encoding, circuit and reported application events, with explicit failure
retention. This is a research direction, NOT a demonstrated original method.
Today's retention tests establish selected classical workflow behaviors only.
The distinction between physical feasibility, auxiliary consistency and useful
service remains project evidence from the synthetic fixture, not a result of
the cited papers.

Next: read the statistical-assertion method in detail, verify Quito's original
source, inspect mutation/metamorphic testing and differential-testing papers,
then create a fault-to-oracle matrix. Record oracle assumptions, phase blindness,
sampling budgets, mutant selection and limitations before claiming any gap.
Keep R06 open until citation chaining and a direct novelty comparison exist.

## 2026-10-21 extension: fault-to-oracle routing

Added [fault-to-oracle-matrix.md](fault-to-oracle-matrix.md). The map separates formulation enumeration, phase-sensitive exact-state comparison, readout/application checks, input-generation/coverage approaches, differential/metamorphic platform checks, and evidence retention. MorphQ (https://arxiv.org/abs/2206.01111), QDiff (https://doi.org/10.1109/ASE51524.2021.9678792), and Quito (https://doi.org/10.1109/ICST49551.2021.00014) were added as verified primary publication records. Their placement is a project interpretation, not a reproduced comparison. Quito and QDiff full-text method extraction plus backward/forward citation chaining remain open. Today's half-angle fault is one predetermined acceptance case, not a mutation-score experiment.


## 2026-10-22 direct full-text extraction

Reading depth was upgraded from metadata/abstract screening to targeted full-text
extraction for the original Quito ICST paper, its ASE tool paper, and QDiff.
The detailed assumptions and frozen prospective routing table are recorded in
[oracle-assumptions-and-mutant-plan.md](oracle-assumptions-and-mutant-plan.md).

The key boundary is now explicit. Quito's correctness assessment depends on a
user-supplied program specification: WOO rejects an observed output assigned
zero probability, while OPO statistically compares repeated observed
frequencies with specified probabilities. Failure to reject is inconclusive,
not proof of correctness. The published study is black-box, measurement-output
focused and explicitly does not cover phase; its reported experiment used
ideal simulator qubits without hardware errors.

QDiff uses no independent expected distribution. It first assumes its gate
rewrites preserve the unitary, then treats the average empirical distribution
of the variant group as a reference and reports members that diverge beyond a
chosen threshold. K-S and cross-entropy comparisons require a distance
threshold, confidence target, and platform-calibrated measurement estimate.
This can expose stack inconsistency but remains vulnerable to common-mode error.

R06 is still **IN PROGRESS**. Backward and forward citation chaining, a broader
novelty comparison, and reproduction of any cited tool remain uncompleted.
No numerical result or mutation score was produced on October 22.
