# Diagonal cost-evolution audit

**EXECUTED LOCAL EXPERIMENT — 6 October 2026.** This note covers a standard-library calculation on the existing synthetic six-variable toy. It is not an SDK circuit, transpilation test, sampler run, optimizer run or hardware experiment.

## Convention under test

For a diagonal cost Hamiltonian

\[
H_C=cI+\sum_i h_iZ_i+\sum_{i<j}J_{ij}Z_iZ_j,
\]

the tested basis-state action is

\[
U_C(\gamma)|z\rangle=e^{-i\gamma E(z)}|z\rangle.
\]

IBM's `PauliEvolutionGate` documentation defines the evolution as \(e^{-itH}\). The IBM `RZGate` and `RZZGate` documentation defines the rotation exponent with a one-half factor. Consequently, a term \(h_i Z_i\) requires an RZ angle \(2\gamma h_i\), and \(J_{ij} Z_iZ_j\) requires an RZZ angle \(2\gamma J_{ij}\), under these conventions.

Verified primary documentation, accessed 6 October 2026:

- [IBM Quantum: PauliEvolutionGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.PauliEvolutionGate)
- [IBM Quantum: RZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.3/qiskit.circuit.library.RZGate)
- [IBM Quantum: RZZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/2.2/qiskit.circuit.library.RZZGate)

These sources establish the interface convention. The numerical evidence below comes from the committed local script, not from documentation examples.

## Reproducible method

From `phd-simulation`, run:

```bash
python src/verify_phase_evolution.py
```

The script uses Python 3's standard library, no randomness and no external data. It reconstructs the already-audited Ising coefficients, checks them against the independent capacity-residual oracle, and evaluates 64 computational-basis states at four angles: 0, \(\pi/17\), 0.2 and 0.7. It then compares three routes:

1. direct \(e^{-i\gamma E(z)}\) from the residual oracle;
2. direct evolution from the mapped Ising energy;
3. the product of the constant, RZ-like and RZZ-like term phases using the required factor of two.

The script also drops the constant offset and checks the exact predicted common factor \(e^{+i\gamma c}\). Finally, it applies the phase to a deterministic normalized 64-amplitude fixture and measures norm and probability drift.

## Executed result

All nine checks passed. The exact oracle and mapped energies agreed on all 64 states. Direct phases agreed for all 256 state-angle pairs with zero reported difference; the decomposed gate-angle calculation had maximum absolute error \(1.05\times10^{-14}\). Removing the offset of 50 produced only the predicted global phase, with maximum residual \(1.42\times10^{-14}\).

At \(\gamma=0.2\), reversing the exponent sign mismatched all 64 states. Deliberately omitting the factor of two in rotation angles mismatched 63 states. These counts are fault-injection observations for this fixture, not general detection rates.

The deterministic statevector retained unit norm exactly at the reported precision. Its maximum basis-probability drift was \(1.04\times10^{-17}\), while all 64 complex amplitudes changed at the chosen nonzero angle. This is expected: a diagonal cost unitary alone changes phases, not computational-basis probabilities. A mixer or other interference-producing operation is required before those phases can affect sampled probabilities.

## Boundary of the claim

This result verifies an algebraic phase convention on one synthetic instance and four selected angles. It does not verify an SDK's qubit layout, circuit synthesis, transpilation, sampler output, noisy execution or QAOA optimization. No quantum advantage, speedup or methodological novelty is claimed. The next interface test should construct the six-qubit SDK circuit and compare its statevector up to global phase before any sampling or optimization.

