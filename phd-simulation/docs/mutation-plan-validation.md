# Prospective mutation-plan validation

Status: **PLAN VALIDATED / M01–M12 UNEXECUTED — 2026-10-27**.

The machine-readable plan in `mutation-pilot-plan-v1.json` binds each frozen
record to its deciding test layer, expected outcome and resource claim. It is a
control document, not a mutation result. `execution_authorized` remains false.

## Allocation proved by execution

The local standard-library validator computed the allocation from the thirteen
records rather than trusting the declared totals.

| Resource | Computed total | Protocol cap |
|---|---:|---:|
| formulation passes | 2 | 2 |
| SDK statevectors | 15 | 15 |
| baseline bundles | 1 | 1 |
| mutant attempts | 12 | 12 |
| searches, shots, optimizers, transpilers, cloud calls, hardware jobs | 0 | 0 |

The three unmutated baseline statevectors and the twelve statevectors declared
for M03–M06 exhaust the SDK cap. M01–M02 exhaust the two formulation passes.
M07–M12 claim only in-memory use of retained baseline data. Every mutant claims
exactly one attempt.

All 22 plan checks passed. A second executed test suite passed seven cases,
including six malformed controls: missing M12, a nonzero search request, moving
SDK work to M07, changing the M02 split-oracle prediction, setting execution
authorization true and duplicating an identity. During that work, the validator
was hardened so a missing control record produces failed checks instead of an
uncaught lookup exception.

## Scientific boundary

No plan entry was submitted to `PilotHarness.execute`. The validator did not
import Qiskit, construct a circuit, transform an amplitude, enumerate mutant
energies or classify a fault. Therefore:

- the executed plan counters remain zero;
- the 15-statevector pilot allowance remains unused;
- M01–M12 remain `PLANNED/UNEXECUTED`;
- no mutation score exists.

The resource manifest reduces discretion before execution, but it cannot prove
that a future callback reports its work honestly. The next gate is a dry-run
aggregate builder using synthetic retained records. It must regenerate totals
and statuses from append-only evidence and reject missing terminals, digest
mismatches and undeclared identities. Only then should the scientific callbacks
be wired to the harness.

