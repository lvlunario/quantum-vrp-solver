# R14 — Exact readout semantics on the six-bit toy

Created 2026-10-15. Numerical evidence: [executed JSON](../results/2026-10-15-readout.json). Reproduce from `phd-simulation`:

```sh
python -m venv /tmp/readout-env
/tmp/readout-env/bin/pip install -r requirements-sdk.txt
/tmp/readout-env/bin/python src/verify_readout.py > results/2026-10-15-readout.json
```

## Definitions and independence

For logical bits x0,x1,x2 and slack s=b3+2b4+4b5, let L=2x0+3x1+4x2, U=3(1-x0)+5(1-x1)+6(1-x2).
The energy is E=U+2(L+s-5)^2. For state amplitudes a_j, p_j=|a_j|^2, and the readouts are:

- Expected energy: sum_j p_j E_j, including the constant identity offset.
- Physical feasibility: sum_j p_j 1[L_j<=5].
- Encoding consistency: sum_j p_j 1[L_j+s_j=5].
- Load marginal: P(x)=sum_s p(x,s).

Encoding consistency implies physical feasibility for this nonnegative slack encoding. It does not follow that their probabilities are equal. No postselection, repair, renormalization or conditional success rate is used.

The reference uses hand-enumerated load/loss tables and integer index decoding; the SDK observable uses the existing Ising coefficients. These paths share the mathematical fixture but not the energy evaluation or bit decoder. Every observable diagonal is checked against the independent table, and every one-hot summary is checked. This reduces common implementation dependence; it cannot prove the underlying microgrid model represents reality.

## Executed findings

Python 3.12.14, Qiskit 2.5.2, NumPy 2.5.3; exact six-qubit local statevectors; 26 passing checks at tolerance 1e-11.

| gamma | beta | Expected E | Physical probability | Encoding probability |
|---|---|---|---|---|
| 0.2 | 0.31 | 49.26741508546327 | 0.6330953684437471 | 0.01604168028438998 |
| pi/17 | 0.63 | 60.485315965857325 | 0.609154080389986 | 0.05113288100140919 |
| 0.7 | 0.19 | 50.02915563399305 | 0.6092891798595818 | 0.07488547323021144 |

The uniform distribution has physical mass 5/8, encoding mass 5/64 and mean energy 50.
Its residual mean is 3 and variance is (2^2+3^2+4^2+1^2+2^2+4^2)/4=12.5.
The mean loss is 7, so mean energy is 7+2(3^2+12.5)=50.
An initial test mistakenly expected 62 and failed; the derivation corrected the test before the final recorded run.

The unique encoded minimizer is index 3 (logical bits 110000 in q0-first order), energy 6. The existing fixed angles are not optimized. One primary energy is slightly below the uniform mean, while the other two exceed it; this is no evidence of general optimization quality.

## Faults and invariants

On the first fixed state, reversed decoding yields energy 52.64243820211661; magnitude rather than squared-magnitude weighting yields 358.5162757745817; dropping the identity term yields -0.7325849145366465. The correct mean is 49.26741508546327 and the identity offset is 50.

Global phase leaves every readout unchanged. Positive affine transformations preserve argmin but transform the expectation. Slack marginalization agrees with direct physical event summation. Bad shape, negative entries, nonfinite entries and missing normalization are rejected.

## Sources and boundaries

Primary source checked 2026-10-15: [IBM Qiskit bit-ordering guide](https://quantum.cloud.ibm.com/docs/en/guides/bit-ordering), sections Integers, Strings and Statevector matrices. This supports the index/string contract, not project performance claims. Qiskit's installed `Statevector.expectation_value`, `probabilities` and `probabilities_dict` implementations are directly exercised. The energy and event formulas above are project derivations with exhaustive fixture checks.

The result JSON retains all 64 state energies, three full probability vectors, configuration, dependency versions, UTC execution time, source/dependency-file hashes and limitations. No random draws, search, optimizer, shots, hardware, noise or transpilation were used. This verifies a reporting boundary on one synthetic toy; it is not a resilient-grid benchmark, novelty assessment, or quantum-advantage result.

Next R15: specify the classical baseline, fixed search budget, metrics, and claim limits before any search. PLANNED/UNEXECUTED.
