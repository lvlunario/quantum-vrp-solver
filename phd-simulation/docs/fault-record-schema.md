# Fault-record contract: explicit blind layers

Status: executed structural validation on synthetic records only, November 26, 2026.
This is a project-specific machine-readable contract, not a JSON Schema standard implementation.
The frozen November 25 catalog is preserved unchanged; migration remains planned.

## Meaning and acceptance rule

A record is a tuple of identity, fault class, precondition, minimum detecting
layer, known blind layers, blindness reason, evidence status/reference and
resource boundary. Acceptance requires all structural predicates, not a vote
among them. The detector must not appear in the blind-layer set.
Each blind-layer assertion is scoped by its precondition and explanation.
“Blind” means that layer alone does not establish this particular claim; it
does not assert that the layer could never detect the fault on any input.

Two separate physical feasibility reports cannot by themselves establish that
both members of a monotonicity comparison used the same capacity. Both reports
might be internally correct while the pair violates its contract. The transform
precondition is therefore the earliest specified detector for that class.
This is a local design decision, not a proof of global minimality.

| Evidence state | Required reference | Acceptance means |
|---|---|---|
| PROSPECTIVE_UNEXECUTED | null | No evidence claim recorded |
| REFERENCE_DECLARED_NOT_VERIFIED | synthetic path and 64-character hex digest | Reference syntax only; no bytes loaded or claim checked |

The synthetic reference fixture intentionally uses an all-zero digest and a
nonexistent file. Its acceptance demonstrates the boundary: structural validity
cannot establish provenance or scientific validity. The November 25 catalog's
six existing-evidence confirmations are neither repeated nor downgraded here.
Their separate evidence checker remains the relevant earlier artifact.

## Failure risks addressed

The old catalog validator checks values present in a resource dictionary.
An empty dictionary makes an all-values-zero predicate vacuously true.
Python equality also equates False and 0. The new contract requires the exact
counter key set, integer type (excluding Boolean and float) and value zero,
plus an explicitly Boolean false baseline flag.

It rejects missing or unknown fields, unspecified blind layers, contradictory
detector/blind assignments, class/detector mismatches, unsupported evidence
claims, malformed references, pilot overlap and incomplete resource reports.
Synthetic IDs are mandatory, preventing accidental application to MF06/MF08
or M01–M12. It has no evidence loader or scientific callback.

## Executed evidence and reproduction

Run from a repository checkout:

    python3 phd-simulation/src/verify_fault_record_schema.py

Use a clean copy without the dated output, or move that output to a retained
archive before reproduction: the writer uses exclusive creation and refuses
to overwrite evidence. Only the Python standard library is needed.

The retained JSON includes all four accepted and 28 rejected input records,
diagnostics, real UTC time, Python version, command and SHA-256 hashes of the
contract, validator and verifier. All 32 checks passed. These are schema checks,
not 32 scientific mutants. Catalog fault executions, formulation passes,
protocol mutants, statevectors, searches, shots, hardware jobs and baseline
reservations are zero for this episode.

## Handover

Friday: write an educational manuscript subsection connecting P01/P02 results,
fault routing and the evidence-status boundary; include unresolved semantic
migration and SDK preflight blockers. Before later migration, map the eight
real records to explicit scoped blind-layer claims and independently resolve
referenced bytes. Structural validation alone must never promote MF06 or MF08
to executed status. No new literature or novelty claim is made here.

Primary project evidence: [November 25 catalog](metamorphic-fault-catalog-v1.json),
[schema contract](fault-record-schema-v1.json),
[executed synthetic checks](../results/2026-11-26-fault-record-schema.json).
