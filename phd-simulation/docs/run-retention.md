# Run retention guard — 2026-10-20

Actual execution: 14 standard-library workflow tests passed on Python 3.12.14;
see results/2026-10-20-retention-audit.json. Zero SDK circuits or quantum search
evaluations ran today. Synthetic callbacks exercise storage, not solver accuracy.

## Contract and usage

The CLI in src/run_pilot_v1.py now calls evidence_store.execute before SDK imports.
An existing output, symlink or adjacent `<output>.run` reservation refuses the
launch. The run directory is reserved using exclusive directory creation. No
overwrite switch, automatic cleanup or silent retry is provided. The numerical
grid, objective, selection rule and frozen v1 protocol are unchanged.

When a future run is explicitly justified, from phd-simulation:

```bash
python src/run_pilot_v1.py --output results/NEW-UNIQUE-RUN.json --parent-commit ACTUAL_PARENT_SHA
```

This is a usage example, NOT a request or evidence that this new grid ran.
The parent SHA is caller-declared metadata; the caller must verify it against
GitHub. The recorded argv and runner SHA replace the old hardcoded invocation.
The runner hashes local source/input bytes as before. Verify those against the
parent before execution; a guard does not repair incorrect materialization.

Each reserved directory contains a STARTED manifest, exclusive numbered event
files and, if finalization succeeds, a terminal record with the result SHA-256.
Candidate-attempt events precede circuit construction; completion events contain
the full probability vector and metrics. Winner validation has a separate
attempt event. Final output uses exclusive creation even if an unrelated writer
creates the pathname after reservation. Errors and caught interruptions leave
an abort event; a hard kill can leave only a manifest or partial file. Keep these
artifacts rather than making the run disappear.

`inventory(parent)` scans retained run directories, sums persisted attempt,
completion and winner-validation events, and flags absent terminal records.
These are conservative workflow counters, not proof a circuit executed: a
process can stop between recording intent and performing work. A malformed or
partial event raises rather than being silently skipped. The inventory does NOT
enforce a global budget, discover runs elsewhere or import historical counts.

Historical ledger remains results/2026-10-19-run-ledger.json: 512 search
evaluations and two winner validations. Today's new quantum count is zero.
Never add synthetic test callback counts to scientific experiment counts.
Future accounting must retain and reconcile both the historical ledger and all
new per-run directories before any aggregate budget claim.

## Executed checks and limits

Tests cover existing evidence, abandoned reservations, digest verification, raw
event retention, callback exceptions, KeyboardInterrupt, late output collisions,
event-sequence collisions, two-run counting, eight concurrent thread launches,
the real CLI refusal path, failed numerical-result retention, symlinks and
nonfinite JSON rejection. Test fixtures are temporary and intentionally synthetic;
the retained report stores every test name, timing and source hash.

This is local application-level append-only behavior, not immutable storage.
Files can still be edited manually. Python's exclusive `x` mode refuses an
existing file; unlike `w`, it does not truncate it. File flushing uses flush then
fsync, but there is no directory fsync, power-cut guarantee, disk-full recovery,
distributed-filesystem test or adversarial-path security claim. Primary API
sources checked October 20:

- https://docs.python.org/3/library/functions.html#open
- https://docs.python.org/3.11/library/os.html#os.fsync

R15's original procedural failure remains NOT MET. The new guarded runner has
not yet completed an SDK integration check. Next gate: one fixed candidate and
an injected failure through the real callback boundary, with unique paths and
all artifacts preserved; not another 256-candidate grid.
