# Stub-only L1–L4 scientific-adapter interface

Status: **INTERFACE TESTED; SCIENTIFIC ADAPTERS UNEXECUTED — 2026-11-04**.

This boundary connects the frozen mutation plan to future scientific callbacks
without allowing an interface test to masquerade as experiment evidence.
`src/scientific_adapters.py` routes all thirteen plan records to L1–L4,
retains each record's declared *future* resource allocation, and requires
actual consumption to remain zero in `STUB_INTERFACE_TEST` mode.

## Contract

| Layer | Future scientific payload | Stub-only requirement |
|---|---|---|
| L1 | exact labeled-state and reduced-decision comparisons | zero states and decisions examined |
| L2 | phase-aligned complex-state errors at frozen angles | zero angle cases and null numerical metrics |
| L3 | normalization, energy, and readout invariants | zero probabilities and null numerical metrics |
| L4 | physical feasibility and auxiliary consistency | two separately named null metrics |

The baseline routes to all four layers in order. Each mutant routes only to the
layer frozen in `docs/mutation-pilot-plan-v1.json`. A stub record is rejected
if it changes identity, layer, declared allocation, or schema; consumes any
protocol resource; performs an enumeration; populates a numerical observation;
conflates L4 metrics; or emits a scientific verdict.

## Executed verification

Command:

```text
python src/verify_scientific_adapters.py
```

The standard-library test routed the baseline and M01–M12 and passed eleven
checks: one complete valid-plan check plus ten deliberately invalid fixtures
that were all rejected. The retained report includes the Python version,
canonical plan digest, adapter-source digest, UTC timestamp, check details and
explicit zero counters.

No Qiskit module was imported. No formulation pass, statevector, probability
vector, baseline bundle or mutant was executed. Therefore the report contains
no scientific verdict and consumes none of the frozen pilot budget.

## Remaining gate

The concrete scientific functions still need to be connected and independently
tested. Before any real baseline bundle, perform an environment/source-hash
preflight against the frozen lock and exact published sources. A failed
preflight must stop before reserving or executing M01.

Limitations: this verifies local Python object contracts only. It does not prove
scientific correctness, numerical stability, crash safety, or compatibility
with the eventual Qiskit environment.
