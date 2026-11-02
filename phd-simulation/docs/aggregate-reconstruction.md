# Aggregate evidence reconstruction gate

Status: **SYNTHETIC DRY-RUN PASSED — SCIENTIFIC PILOT UNEXECUTED — 2026-11-02**.

`aggregate_mutation_evidence.py` rebuilds bookkeeping from retained bytes. It
does not import Qiskit or invoke a formulation, circuit, readout or application
oracle. The reader checks:

- exact baseline and M01–M12 record-directory identities;
- contiguous append-only event numbering;
- attempt and completion identities in plan order;
- counters recomputed from attempt events;
- equality with both the declared plan and frozen protocol caps;
- presence and parseability of every result and terminal;
- `COMPLETE` terminal status; and
- SHA-256 agreement between every result file and its terminal record.

Seven executed standard-library tests used temporary synthetic records. The
complete 13-record fixture reconstructed the future allocation of two
formulation passes, fifteen SDK statevectors, one baseline bundle and twelve
mutant attempts. Six injected evidence faults were rejected: a missing
terminal, modified result bytes, undeclared M13 directory, ledger counter
mismatch, missing attempt event and incorrect fixture mode.

The fixture records say `SYNTHETIC_RECORD_ONLY` and contain no scientific
verdict. The future counters represented in their event files are test data,
not actual protocol consumption. Actual execution remains zero mutants, zero
SDK statevectors and zero searches, shots or hardware jobs.

## Remaining gate

The orchestration boundary, prospective resource plan and aggregate reader are
now independently tested. The next step is to define thin scientific adapters
for L1–L4 and test their interfaces with stub data. A final preflight should
verify the pinned environment and source hashes immediately before the first
baseline bundle. The pilot must abort if that baseline fails.

