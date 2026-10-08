# Six-qubit Qiskit cost-circuit verification

**EXECUTED LOCAL SDK EXPERIMENT — 8 October 2026.** This experiment used Qiskit 2.5.2 exact statevector evolution on the existing synthetic six-variable microgrid toy. It did not use sampling, transpilation, a noise model, an optimizer, cloud services or quantum hardware.

## Source and environment check

The latest official Qiskit GitHub release checked on 8 October 2026 was [Qiskit 2.5.2](https://github.com/Qiskit/qiskit/releases/tag/2.5.2), published 13 August 2026. Its tagged [project metadata](https://github.com/Qiskit/qiskit/blob/2.5.2/pyproject.toml) supports Python 3.12, and its [runtime requirements](https://github.com/Qiskit/qiskit/blob/2.5.2/requirements.txt) specify NumPy 2.x among the dependencies. A clean temporary Python 3.12.14 environment resolved the exact package set stored in [`requirements-sdk.txt`](../requirements-sdk.txt).

IBM's API documentation defines `Statevector.equiv` as equivalence up to global phase and `Statevector.evolve` as evolution by an operator or circuit:

- [IBM Quantum: Statevector](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector)
- [IBM Quantum: RZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZGate)
- [IBM Quantum: RZZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RZZGate)

## Mathematical construction

The previously verified cost Hamiltonian is

\[
H_C=cI+\sum_{i=0}^{5}h_iZ_i+\sum_{i<j}J_{ij}Z_iZ_j,
\]

with constant offset \(c=50\), six local fields and fifteen pair couplings. Because every term is diagonal in the computational basis, the terms commute. Under the documented gate definitions, the ideal circuit implements

\[
e^{-i\gamma H_C}=e^{-i\gamma c}
\prod_i RZ_i(2\gamma h_i)
\prod_{i<j}RZZ_{ij}(2\gamma J_{ij}).
\]

The code places the constant in `QuantumCircuit.global_phase`. A second circuit intentionally omits it, which should remain equivalent up to the common factor \(e^{+i\gamma c}\) relative to the full circuit.

## Reproduce

From `phd-simulation`, create an isolated environment using the pinned dependencies, then run:

```bash
python src/verify_qiskit_cost_circuit.py
```

The script prepares a deterministic normalized 64-amplitude state, evolves it at \(\gamma=\pi/17,0.2,0.7\), and compares the SDK result with phases calculated from the independent capacity-residual oracle. Statevector index \(j\) is decoded as \(b_i=(j\mathbin{\gg}i)\&1\), so index 3 is pinned to logical tuple `(1,1,0,0,0,0)`.

## Executed result

All nine checks passed. With the offset included, the maximum component error against the oracle was \(1.52\times10^{-15}\) over the three angles. Without the offset, Qiskit's global-phase-aware comparison accepted all three circuits. A naive strict comparison rejected all three, with maximum component distances between 0.2902 and 0.3014.

Each complete circuit contained exactly six RZ and fifteen RZZ gates. At \(\gamma=0.2\), `Statevector.equiv` rejected three deliberate mutations: reversed exponent sign, reversed logical-qubit placement, and removal of the \(J_{01}=6\) RZZ interaction. The reference norm squared remained 1.0 at reported precision.

These are detection observations for one deterministic input and selected angles, not general fault-detection rates.

## What this closes—and what it does not

R12 is complete only at the ideal cost-layer statevector boundary. The algebraic energy oracle, gate angles, qubit indexing and global phase now agree with one pinned Qiskit execution. The result does not establish correct transpilation, measurement decoding, shot-based statistics, mixer behavior, parameter optimization, noisy performance or hardware behavior. It provides the reference those later layers must match.

No quantum speedup, advantage or novelty is claimed.

