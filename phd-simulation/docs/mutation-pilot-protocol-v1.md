# Bounded mutation pilot protocol v1

Status: **FROZEN/UNEXECUTED — 2026-10-23**. This is a prospective protocol for
the twelve mutations declared on October 22. It authorizes no parameter search,
sampling, transpilation, noise model, cloud service or quantum hardware. No
mutation result or mutation score exists yet.

## Purpose and scope

The pilot asks whether the project's layered checks behave as predicted on one
fixed six-variable synthetic microgrid fixture. It tests formulation,
phase-sensitive circuit construction, readout, application metrics and evidence
retention separately. It does not estimate real-world defect prevalence,
generalize to larger instances or compare quantum and classical performance.

The scientific unit is one predeclared mutant, M01–M12. Each mutant is applied
alone to the October 22 reference implementation. Compound faults are excluded.
M06 must be rerun under this protocol; its earlier demonstration is regression
context and will not be counted as prospective evidence.

## Frozen fixture and environment

- Loads: demands `(2,3,4)`, priorities `(3,5,6)`, capacity `5`.
- Reference penalty: lambda `2`; slack weights `(1,2,4)`.
- Basis convention: `index=sum(bits_q0_first[i]*2**i)`.
- Circuit cases: `(gamma,beta)=(0.2,0.31), (pi/17,0.63), (0.7,0.19)`.
- SDK lock: Python 3.12, Qiskit 2.5.2 and NumPy 2.5.3, or an explicitly
  recorded replacement lock if recreation is impossible. A replacement lock
  invalidates comparison with historical timings but not exact-oracle checks.
- Data: the fixed synthetic fixture only; no external dataset or randomness.

The harness must record the parent commit, source and lock SHA-256 values,
versions, command, UTC creation time and all configured thresholds.

## October 23 amendment to M02

Review found that “reverse one slack-bit binary weight” was underspecified.
Merely swapping weights 1 and 4 preserves the representable slack set
`{0,...,7}`; therefore minimization over slack can remain correct even though
the named bit-to-weight contract is wrong.

M02 is now frozen as: **swap the declared q3 and q5 weights from (1,2,4) to
(4,2,1), while the external bit labels remain unchanged.** It is expected to be
killed by the labeled 64-state energy table and to survive the reduced
eight-decision minimum-over-slack oracle. This is a planned split-oracle control,
not an equivalent mutant. The amendment occurred before pilot execution.

## Oracles and fixed thresholds

| Layer | Decision rule |
|---|---|
| L1 formulation | Integer/rational equality over all 64 labeled encoded states and all eight reduced decisions; minimizer feasibility is exact, with no floating tolerance. |
| L2 statevector | Align one global phase, then kill if maximum component error is at least `1e-12`; also require norm-squared error below `1e-12`. |
| L3 readout | Require 64 finite nonnegative probabilities, normalization within `1e-11`, and expected-energy/fixture agreement within `1e-11`. A fault is killed when its predeclared invariant fails. |
| L4 application | Physical feasibility and auxiliary consistency must remain separately named, each in `[0,1]`, with auxiliary consistency no larger than physical feasibility within `1e-11`. |
| L5 retention | Before computation, reserve a unique run directory and append an attempt event. Preserve fault and abort events; write a terminal digest only for a complete success. |

No threshold may be relaxed after a mutant is observed. A numerical value
exactly on a rejection boundary is rejected.

## Exact mutant observations

- **M01:** set lambda to `1`. Kill if any global minimizer is infeasible or
  tied with an infeasible state.
- **M02:** use `(4,2,1)`. Kill at the labeled-state oracle; require survival at
  the reduced-decision oracle.
- **M03–M06:** evaluate all three fixed angle pairs against the independent
  complex-amplitude oracle. A mutant is killed if any fixed case crosses the L2
  threshold. Record all three cases even after the first kill.
- **M07–M10:** apply each readout/application fault to the unmutated probability
  vector at `(0.2,0.31)`; use the fixed L3/L4 invariants.
- **M11:** multiply the state at each fixed angle pair by `exp(0.73i)`.
  It must survive global-phase-aligned equivalence. Naive strict component
  comparison is recorded only as a negative control.
- **M12:** after the cost layer, multiply basis-state index 3 by `-1`, leaving
  all other amplitudes unchanged. Pre-mixer computational-basis probabilities
  must survive within `1e-12`; the complex state must be rejected by L2.
  Continue through the reference mixer and record whether output probabilities
  change, but do not make that secondary observation the primary kill rule.

## Hard budget

The entire prospective pilot is capped at:

- two exhaustive formulation mutation passes, each covering 64 encoded states;
- fifteen SDK statevector circuit constructions: three unmutated baselines plus
  three cases for each of M03–M06;
- in-memory transformations for M07–M12, with no additional SDK circuits;
- twelve mutant attempts and one baseline bundle in the retention ledger;
- zero parameter-search evaluations, shots, optimizer calls, transpiler runs,
  noise simulations, cloud calls or hardware jobs.

Reusing a statevector within the same retained baseline bundle is required.
A rerun caused by infrastructure failure is permitted only under a new run ID
and counts against the budget. If the cap would be exceeded, stop and report an
incomplete pilot rather than silently extending it.

## Scoring and reporting

Report each mutant as `KILLED`, `SURVIVED`, `INVALID RUN` or
`NOT EXECUTED`, plus the deciding layer and retained evidence path.

The kill-rate denominator contains the eleven predeclared killable mutants
M01–M10 and M12. M11 is an expected-equivalent survivor and is excluded from
that denominator. Report three control predictions separately: M02 must survive
the reduced-decision oracle, M11 must survive phase-aligned equivalence, and M12
must survive the pre-mixer probability-only oracle. Do not combine those
controls into the kill rate.

An unexpected survivor is a scientific result, not permission to change its
oracle. Post-result mutant reclassification is prohibited. Any proposed
interpretive change belongs in a versioned v2 protocol and cannot alter v1.

## Abort and acceptance rules

Abort the whole pilot if the unmutated baseline fails, provenance fields are
missing, output reservation collides, or the retention/budget counter is
unreliable. Preserve the partial record. An individual mutant exception is an
`INVALID RUN`; do not call it killed. An unexpected killed/survived result does
not abort other mutants when the infrastructure remains valid.

The pilot is complete only when all twelve attempt records exist, the hard
budget reconciles, every success has a terminal digest, every failure remains
auditable, and the aggregate report is independently regenerated from the
retained per-mutant records.

## Limitations

This is one hand-designed mutant set on one six-qubit exact-statevector fixture.
The mutants are not sampled from a population, so the kill rate is descriptive,
not an estimate of general effectiveness. No power analysis, finite-shot
statistics, hardware noise, compiler diversity, realistic microgrid physics,
speedup, novelty or quantum advantage is tested.
