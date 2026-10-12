# Six-qubit Qiskit mixer audit

**Executed:** 2026-10-12 on the existing synthetic six-variable microgrid toy.  
**Boundary:** local exact statevector simulation only; no optimizer, shots, transpilation, noise model, cloud service, or quantum hardware.

## Question

Does a one-layer QAOA circuit implement the intended product mixer without changing the established cost-phase sign, qubit order, or layer order?

For this project the energy (E(z)) is minimized and the cost phase is

\[
U_E(\gamma)=e^{-i\gamma E}.
\]

The mixer from the foundational QAOA convention is

\[
U_B(\beta)=e^{-i\beta\sum_j X_j}=\prod_j e^{-i\beta X_j}.
\]

IBM's current Qiskit documentation defines `RX(theta)` as (e^{-i\theta X/2}), so each mixer gate must be `RX(2*beta)`: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RXGate. Qiskit's `Statevector` can be constructed from a circuit initialized in the all-zero state, which is the exact local execution path used here: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector.

## Independent oracle

The Qiskit circuit is not used as its own reference. Starting from the 64 equal amplitudes, the oracle:

1. multiplies basis index (z) by (e^{-i\gamma E(z)});
2. applies each single-qubit mixer by explicit amplitude pairs,

\[
\begin{bmatrix}a'_0\\a'_1\end{bmatrix}=
\begin{bmatrix}\cos\beta&-i\sin\beta\\-i\sin\beta&\cos\beta\end{bmatrix}
\begin{bmatrix}a_0\\a_1\end{bmatrix};
\]

3. repeats that pairing for qubits 0 through 5 under the existing q0-first index contract.

The SDK implementation independently builds six Hadamards, the previously verified six-RZ/fifteen-RZZ cost layer, and six `RX(2*beta)` gates.

## Executed configuration

- Python 3.12.14
- Qiskit 2.5.2
- NumPy 2.5.3
- Predetermined angle pairs: `(0.2, 0.31)`, `(pi/17, 0.63)`, `(0.7, 0.19)`
- Absolute tolerance: `1e-12`
- Data: fixed synthetic toy; no external dataset and no randomness

## Results

All ten assertions passed. The largest componentwise difference between Qiskit and the independent oracle was `1.360182507175779e-15`. The largest normalization error was `1.5543122344752192e-15`.

The beta-zero circuit matched the cost-only oracle. With gamma zero, the maximum departure from uniform measurement probability was `1.734723475976807e-17`. On the phase-rich primary fixture, adding the mixer changed at least one basis probability by `0.03787431109323938`.

Three deliberate faults were rejected by `Statevector.equiv` at zero relative tolerance and `1e-12` absolute tolerance:

- `RX(beta)`, which omits the required factor of two;
- `RX(-2*beta)`, which reverses the mixer sign;
- mixer-before-cost layer ordering.

The expected-energy values stored in the raw JSON are reproduction observables for the three predetermined angle pairs. They are not optimized values and are not evidence of improved solution quality.

## Decision and limits

R13 is complete for this exact ideal boundary. The next boundary is readout semantics: independently verify expected energy and feasible probability from the final state before any angle search.

The evidence covers one synthetic instance, three fixed angle pairs, and selected mutations. It does not estimate general fault-detection effectiveness and says nothing about finite shots, compilation, noise, hardware performance, runtime advantage, or novelty.
