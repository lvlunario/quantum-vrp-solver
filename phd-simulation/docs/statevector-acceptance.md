# Statevector acceptance contract before SDK integration

**EXECUTED LOCAL NUMPY EXPERIMENT — 7 October 2026.** The committed calculation uses NumPy 2.3.5 on the existing synthetic six-variable microgrid toy. Qiskit was not available, so no SDK circuit was created or executed.

## Why an acceptance contract comes first

Yesterday's phase audit showed that omitting the Ising constant changes a state only by a global phase. A raw element-by-element comparison will therefore reject two physically equivalent statevectors whenever that global phase is not one. The future SDK test needs to distinguish this valid difference from a relative-phase, sign or indexing error.

IBM's current `Statevector.equiv` documentation explicitly defines equivalence up to global phase. The local harness mirrors that acceptance concept without claiming it reproduces Qiskit's implementation:

- [IBM Quantum: Statevector](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector), checked 7 October 2026.

Given normalized reference vector \(a\) and candidate \(b\), the harness selects the largest-magnitude reference amplitude, infers \(\alpha=b_k/a_k\), and checks every component of \(b-\alpha a\). For unitary outputs, \(|\alpha|\) should be one within tolerance. Choosing the largest reference component avoids dividing by a small amplitude in this deterministic fixture.

## Basis contract

The vector index uses

\[
j=\sum_{i=0}^{5} b_i2^i,
\]

where the stored logical tuple is `(q0, q1, ..., q5)`. Thus index 3 must decode to `(1,1,0,0,0,0)`. This asymmetric fixture is checked before any phase comparison. It prevents a reversed ordering from passing merely because an encoder and decoder share the same mistake.

## Executed method and result

Run from `phd-simulation`:

```bash
python src/verify_statevector_interface.py
```

The deterministic 64-amplitude input has no zero components and is normalized before evolution. At \(\gamma\in\{\pi/17,0.2,0.7\}\), the script compares:

1. the independent residual-oracle evolution;
2. the mapped Ising evolution with its offset;
3. the offset-free Ising evolution;
4. deliberate exponent-sign and reversed-qubit-order faults.

All nine checks passed. With the offset included, the strict comparison had zero maximum component error. Without it, the strict component distances were 0.3014, 0.2902 and 0.2953, so an unadjusted assertion would reject all three valid cases. After inferring one common phase, the largest residual was \(1.84\times10^{-15}\); the recovered phase agreed with \(e^{+i\gamma 50}\) within \(1.84\times10^{-15}\).

At \(\gamma=0.2\), the global-phase-aware comparator rejected the exponent-sign fault with residual 0.2909. It also rejected the reversed-qubit-order fault with residual 0.2928; that mutation changed 56 of the 64 basis energies. The reference vector retained norm squared 1.0 at reported precision.

These values are observations for one synthetic input and chosen angles, not general detection rates.

## SIMULATED NARRATIVE decision record

A fictional Netherlands circuit-mapping role reviews the acceptance boundary. No real person or institution participated. The simulated decisions are:

- require the index-3 asymmetric fixture before comparing statevectors;
- require strict equality when both implementations retain the constant offset;
- allow equivalence up to a single unit-modulus global phase when an implementation intentionally drops the offset;
- reject sign, relative-phase and order faults even if measurement probabilities happen to match;
- do not describe the acceptance harness as an SDK or circuit result.

## Remaining blocker

`qiskit_available` is false in the recorded environment. The next SDK milestone remains **PLANNED/UNEXECUTED**. It requires a documented, version-locked environment; construction of the six-qubit cost circuit; and comparison of the SDK statevector against this committed oracle before adding a mixer, transpilation study, sampler or optimizer.

