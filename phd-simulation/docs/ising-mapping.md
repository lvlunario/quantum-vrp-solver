# Exact mapping and bit-order contract
Created 30 September 2026. **EXECUTED LOCAL EXPERIMENT** on the existing synthetic toy. This note contains original algebra, not a claim of a new research method.

## Derivation
Write the upper-triangular binary polynomial as

\[
E(b)=c+\sum_i a_i b_i+\sum_{i<j}q_{ij}b_i b_j.
\]

Use spins \(s_i=1-2b_i\), hence \(b_i=(1-s_i)/2\). Substitution gives

\[
E(s)=k+\sum_i h_i s_i+\sum_{i<j}J_{ij}s_i s_j,
\quad J_{ij}=q_{ij}/4,
\]
\[
h_i=-a_i/2-\frac14\sum_{j\ne i}q_{\min(i,j),\max(i,j)},
\quad k=c+\frac12\sum_i a_i+\frac14\sum_{i<j}q_{ij}.
\]

For the existing penalty-two instance, the executed calculation gives k=50 and
h=(-21/2, -31/2, -21, -6, -12, -24). All 15 pair coefficients are in the raw JSON.
Replacing each spin by a Pauli Z operator gives a diagonal operator with these same computational-basis energies, since Z has eigenvalues +1 on zero and -1 on one. This is an operator specification; no circuit is claimed to have run.

## Decoding contract
Logical list order is [x0,x1,x2,slack1,slack2,slack4]. Assign list element i to qubit i, and eventually measure qubit i into classical bit i in one register. Integer index is sum(b_i * 2**i); a displayed string is q5 through q0. Reverse that string to obtain this project's logical list. Multiple registers or a different measurement mapping require a new decoder.

The unique minimum is logical [1,1,0,0,0,0], index 3, display `000011`, energy 6. This is an exact enumerated ground state, not a sampled result.

## Executed evidence and deliberate failures
Run `python src/verify_ising.py` from `phd-simulation`. The script uses exact fractions and the existing coefficient builder, but checks against a separate residual expression using demands, priorities and slack. [Raw output](../results/2026-09-30-ising-audit.json) includes all 64 states, configuration, UTC timestamp, Python version and hashes of both source files.

- All 64 Ising energies equal the independent residual oracle.
- All 64 display strings decode correctly; indices cover 0 through 63.
- The unique minimum agrees with the explicit fixture above.
- Deliberately reversing the fields' signs causes 64 energy mismatches.
- Deliberately reading the display as q0-first causes 56 energy mismatches. Example: display `100000` means slack4 is set, energy 16; the wrong interpretation sets x0, energy 29.
- Removing the offset shifts every energy down by exactly 50 but preserves the entire minimizer set.

Eight checks pass. These simple deliberate faults are examples, not a measured general fault-detection rate. In particular, a round-trip check alone could share a convention error with its encoder, so the asymmetric hand fixture matters.

## Offset and phase: derivation, not execution
For H=kI+H', exp(-i gamma H)=exp(-i gamma k) exp(-i gamma H'). The common phase has unit magnitude and cancels from measurement probabilities. Thus a future isolated cost evolution may omit the constant if energy reporting restores it. Controlled evolution needs separate treatment: a formerly global phase can become relative. No phase-evolution test was executed today.

## Sources checked 30 September 2026
- [IBM Quantum: Bit-ordering](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering), sections Integers, Strings and Statevector matrices: primary documentation for the external SDK convention. We implemented a plain-Python contract; we did not execute Qiskit.
- [IBM Quantum: ZGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.ZGate), matrix definition: basis eigenvalues used above.
- [Andrew Lucas, Ising formulations of many NP problems (2014)](https://arxiv.org/abs/1302.5843): bibliographic record/abstract checked as background only. No full-text reading or novelty assessment is claimed.

## Remaining limits
One synthetic integer instance; no network physics, noise, hardware, optimizer, six-qubit circuit or speed comparison. The proof preserves basis energies; it does not establish sampling performance. Next: verify the diagonal cost evolution and global-phase handling, then add a mixer. R05 full-text QAOA reading remains open.

## Recovery and recheck — 5 October 2026
First published October 5 from the surviving September 30 draft. [Fresh execution](../results/2026-10-05-ising-audit.json) reproduces all raw states and both source hashes. IBM bit-ordering and ZGate documentation rechecked October 5. The bit-ordering page also distinguishes primitive output conventions: this decoder must not be applied blindly to an arbitrary primitive result. Select the adapter for its documented output type and test an asymmetric known state. No SDK was executed.
