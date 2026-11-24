# P02 simultaneous permutation development result

**Status:** `EXECUTED_DEVELOPMENT_FIXTURE_PASSED` on November 24, 2026.

This document reports an executed bounded development audit on deterministic
synthetic data. It is outside the frozen mutation pilot. It is not evidence of
quantum advantage, real-microgrid performance or general invariance of an
encoded quantum formulation.

## Frozen question

For fixed capacity, does applying the same coordinate permutation to a binary
decision vector and its matching demand vector preserve physical load,
overload and feasibility?

The audit used the contract frozen November 23:

- demands `(2, 3, 4)` and capacity `5`;
- all eight three-bit binary decisions;
- all six permutations of three coordinates;
- exactly 48 decision-permutation cases;
- the convention `transformed[j] = original[permutation[j]]` for both vectors.

## Executed result

All 48 retained rows preserved load, overload and physical feasibility. The
surface contained eight identity cases and 40 nonidentity cases. Eight checks
passed: exact count, identity partition, unique complete surface, equality of
each of the three physical metrics, rejection of two one-sided controls, and
confirmation that both rejected controls would materially change load if
naively admitted. No in-scope counterexample was observed.

The one-sided controls used decision `(1,0,0)`, demands `(2,3,4)` and a swap of
coordinates 0 and 2. Permuting only the decision or only the demands would
change load from 2 to 4. The pair-boundary validator rejected both before they
could be recorded as P02 cases because the two permutation descriptors were
not identical.

## Provenance

The retained JSON records all 48 rows, both rejected controls, the exact check
outcomes, the Python version, UTC execution time, the command, deterministic
fixture description and SHA-256 hashes for the source, contract and independent
physical oracle. A separate post-run parse confirmed the 48 unique keys, all
property flags, zero in-scope counterexamples and both material control loads.

Resource counters remain zero for protocol formulation passes, mutation-pilot
mutants, SDK statevectors, parameter searches, shots and hardware jobs. No
baseline was reserved.

## Interpretation boundary

P02 is a coordinate-relabeling check for a physical dot product. It does not
show that auxiliary slack-bit meanings survive a permutation, that a QUBO
matrix or circuit statevector may be arbitrarily reindexed, or that an
optimizer produces equivalent output after representation changes. Those
claims require separate mappings and tests.

The result is exhaustive only for the fixed three-item fixture. It does not
cover power flow, restoration, contingencies, uncertainty or a real resilient
microgrid.
