# Mutation-pilot harness implementation contract

Status: **DRY-RUN VERIFIED / SCIENTIFIC PILOT UNEXECUTED — 2026-10-26**.

This document maps the frozen `mutation-pilot-protocol-v1.md` rules to the
first implementation of `src/mutation_harness.py`. The associated tests use
temporary directories and synthetic stub callbacks only. They execute no
mutant, Qiskit circuit, statevector, search, shot, optimizer, transpiler, cloud
call or hardware job.

## Decision from the Monday review

The harness is deliberately an orchestration boundary rather than a scientific
oracle. Mutant implementations and the independent formulation/statevector/
readout checks remain separate. This prevents a bookkeeping layer from quietly
becoming the authority on whether a scientific result is correct.

The implementation applies four fail-closed gates in this order:

1. **Provenance before reservation.** Parent commit, source and lock hashes,
   Python version, command, creation time, thresholds and fixture description
   are mandatory. A missing field creates no pilot directory.
2. **Baseline before mutants.** Exactly one record named `baseline` must
   complete with `baseline_passed: true`. Until its terminal record exists, all
   M01–M12 attempts are refused before their callback can run.
3. **Attempt-counted budget.** Proposed consumption is checked against the
   frozen caps, then persisted in an attempt event before the callback. Failed
   computations therefore still consume budget. A retry cannot disappear from
   the count merely because it produced no result.
4. **Append-only identity.** The pilot directory and every record directory are
   created with collision refusal. Duplicate mutant IDs cannot replace prior
   evidence. Successful records receive a SHA-256 terminal digest; exceptions
   retain an abort record and have no success terminal.

## Frozen counters represented in code

| Counter | Cap | Intended future use |
|---|---:|---|
| formulation passes | 2 | M01 and M02, 64 labeled states each |
| SDK statevectors | 15 | 3 baselines plus 3 cases for each M03–M06 |
| baseline bundles | 1 | shared retained reference data |
| mutant attempts | 12 | one each for M01–M12 |
| search evaluations | 0 | prohibited |
| shots | 0 | prohibited |
| optimizer calls | 0 | prohibited |
| transpiler runs | 0 | prohibited |
| cloud calls | 0 | prohibited |
| hardware jobs | 0 | prohibited |

M07–M12 must be in-memory transformations of the retained baseline and must not
increment the SDK counter. The harness can enforce the declared counter but
cannot prove that a callback truthfully described hidden work. The future
scientific runner must therefore expose operation counts in its result and the
aggregate checker must reconcile those counts independently.

## Executed dry-run evidence

`src/verify_mutation_harness.py` executed twelve standard-library tests. They
verify missing-provenance refusal, unique pilot reservation, baseline gating,
failed-baseline retention, terminal hashing, attempt-based counting, SDK budget
overflow refusal, the zero search cap, mutant-ID validation, duplicate-record
preservation and the zero caps for all prohibited resources.

The result file records source SHA-256 values, the parent commit, Python
version, timestamps, command and explicit zero scientific execution counts.
Because the callbacks are stubs, this result is evidence about workflow
control only. It is not evidence that any of the twelve faults are killed or
survive. The protocol remains `FROZEN/UNEXECUTED`.

## Known limitation and next gate

This version reconstructs budget totals from append-only local attempt events.
It does not defend against a malicious callback, disk failure, power loss,
manual file deletion, or distributed writers outside the reservation boundary.
It also does not yet regenerate a mutation summary from twelve retained
records.

Before the pilot runs, the next implementation must connect the frozen oracle
functions to this boundary and add a **plan-only manifest check**. That check
should enumerate the baseline and M01–M12 resource claims and prove their total
is exactly two formulation passes, fifteen SDK statevectors, one baseline and
twelve attempts—with every forbidden counter remaining zero. It may inspect
and validate the plan but must still not execute the mutants. Only after that
artifact is versioned should the scientific pilot be authorized.

