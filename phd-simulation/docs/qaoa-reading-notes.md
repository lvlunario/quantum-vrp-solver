# QAOA source reading: conventions that constrain this project

**Status:** source-checked reading note, 2026-10-09. This is not a literature review and makes no novelty claim.

## Source and scope

Primary source: E. Farhi, J. Goldstone, and S. Gutmann, *A Quantum Approximate Optimization Algorithm*, arXiv:1411.4028 (2014), https://arxiv.org/abs/1411.4028. The notes below were checked against the paper's full text, not only its abstract. Gate semantics were cross-checked against IBM Quantum's current `RXGate` API documentation: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RXGate.

## Equation-grounded reading

1. **Cost unitary.** Equations (1)–(2) define a classical objective (C(z)), promote it to a diagonal operator (C), and use (U(C,\gamma)=\exp(-i\gamma C)). The clause terms commute because they are diagonal. This is the exact convention already exercised by the project's phase and cost-circuit oracles.

2. **Mixer.** Equations (3)–(4) define (B=\sum_j X_j) and (U(B,\beta)=\exp(-i\beta B)=\prod_j\exp(-i\beta X_j)), with (0\leq\beta\leq\pi). IBM defines `RX(theta)` as (\exp(-i\theta X/2)). Therefore an implementation of the paper's mixer must call `rx(2*beta)` on every qubit. A missing factor of two is a testable defect.

3. **Initial state and ordering.** Equations (5)–(6) start from the uniform superposition |+>^{\otimes n} and alternate cost and mixer operators for (p) layers. For (p=1), the state is (U(B,\beta)U(C,\gamma)|s>): cost first, then mixer. The project must test this order directly.

4. **Objective direction.** Equation (7) evaluates (F_p=\langle\gamma,\beta|C|\gamma,\beta\rangle), and the paper searches for large values because its combinatorial objective is written as a maximization. This project writes a microgrid penalty energy (E) to be minimized. Two consistent choices exist: set (C=-E) and maximize, or keep (C=E) and minimize the expectation. Mixing these conventions silently reverses optimization direction. The implementation will keep (C=E), use (\exp(-i\gamma E)), and minimize expected energy; reports must say so.

5. **Depth claims.** Equations (8)–(10) establish monotonicity of the best variational value with increasing (p) under the paper's definitions and connect the (p\to\infty) limit to the optimum. These statements do not imply that a finite-depth implementation will outperform a classical method, nor that angle selection is cheap. The paper explicitly identifies angle selection as a central practical issue.

6. **Sampling and locality.** The algorithm repeatedly measures bit strings and uses their objective values. For fixed (p), the paper analyzes bounded neighborhoods to compute contributions for bounded-degree problems. That analysis is problem-structure specific; it does not validate this project's slack-QUBO embedding or its decoder.

7. **Evidence boundaries.** The paper gives analytic examples, including a (p=1) result for 3-regular MaxCut, and explicitly notes that the cited approximation ratio is worse than known classical algorithms. It motivates possible usefulness but does not establish generic quantum advantage. The present project therefore treats QAOA as an object to verify, not as a presumed superior solver.

## Project decisions

- Use the six-qubit ordering and endianness contract already verified by the cost-layer harness.
- Implement one layer as Hadamards, the verified cost circuit, then one `RX(2*beta)` per qubit.
- Keep the energy-minimization convention explicit in source, result metadata, and manuscript.
- Compare statevectors only after removing a predicted global phase when the constant energy offset is intentionally omitted.
- Do not interpret ideal-statevector agreement as evidence about shots, transpilation, noise, hardware, optimizer performance, or advantage.

## R13 acceptance criteria — PLANNED/UNEXECUTED

1. At `beta = 0`, the mixer is the identity and the post-mixer state matches the cost-layer state.
2. At `gamma = 0`, the uniform input is an eigenstate of (B); the mixer changes only global phase and measurement probabilities remain uniform.
3. Norm is preserved for every tested ((\gamma,\beta)).
4. Qiskit's product of `RX(2*beta)` gates matches an independent tensor-product mixer oracle.
5. Deliberate `RX(beta)` and `RX(-2*beta)` mutations are rejected on at least one phase-rich cost state.
6. Circuit order is cost then mixer; a reversed-order mutant is rejected.
7. The cost layer alone preserves basis probabilities. A nonzero mixer may redistribute them, but no improvement claim is permitted without an executed parameter search and classical baseline.

These criteria define the next implementation boundary. No mixer circuit or new numerical experiment was executed for this reading note.
