# Mutation-pilot preflight gate

Status: **BLOCKED BEFORE BASELINE RESERVATION — 2026-11-05**.

The gate implements a conjunction:

```text
READY = frozen_schema AND immutable_parent AND exact_source_inventory
        AND valid_blob_identities AND exact_python AND exact_packages
        AND explicit_execution_authorization
```

Failure of any term returns `BLOCKED_BEFORE_BASELINE_RESERVATION`. The
preflight imports no scientific SDK API, creates no pilot run directory, and
consumes no protocol resource.

## Inputs and evidence boundary

`docs/mutation-preflight-manifest-v1.json` records the immutable parent commit,
the exact locked environment, and eight source objects resolved from GitHub
before execution. Each source has its content-addressed Git blob identity. The
inventory covers the lock, frozen plan and protocol, retention harness,
stub-only adapter boundary, and the formulation, mixer and readout reference
implementations.

The executed report hashes both the manifest and the preflight implementation
with SHA-256. Package versions are read through Python distribution metadata;
Qiskit and NumPy scientific APIs are not imported.

## Actual result

Python 3.12.14 matched. The environment did not match the frozen lock:

| Distribution | Required | Observed |
|---|---:|---:|
| qiskit | 2.5.2 | missing |
| numpy | 2.5.3 | 2.3.5 |
| scipy | 1.18.1 | 1.17.0 |
| dill | 0.4.1 | missing |
| rustworkx | 0.18.1 | missing |
| stevedore | 5.9.1 | missing |
| typing_extensions | 4.16.0 | 4.16.0 |

Independently, the frozen plan still has `execution_authorized: false`.
Therefore the baseline was not reserved. This is the intended fail-closed
outcome, not an infrastructure failure and not a scientific result.

Seven bounded controls passed. A synthetic exact environment plus explicit
authorization reached `READY_FOR_BASELINE_ONLY`. Package mismatch, malformed
source identity, missing source, extra source, mutable parent reference, and
false authorization each blocked. The READY control is a dictionary-level
logic test; it did not install packages or execute a baseline.

## Decision

Do not edit the frozen plan merely to make the gate pass. First recreate the
published lock in an isolated local environment, or version and justify a
replacement lock if exact recreation is impossible. Then rerun this preflight.
Only after a verified READY result may a separately reviewed change set
authorize the one baseline bundle. READY never authorizes M01–M12
automatically.

Limitations: Git blob identities establish exact repository objects but are not
a substitute for re-reading those objects at the future execution commit.
Installed-package metadata does not prove runtime numerical behavior. Those
properties require the later baseline oracle checks.
