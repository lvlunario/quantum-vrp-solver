# R15 v1 pilot — mixed metrics and a procedural deviation

Actual local execution on 2026-10-19; synthetic six-qubit development fixture only.
No hardware, shots, noise, transpilation, adaptive optimization or holdout data.
The Norway research routine is **SIMULATED NARRATIVE**, without a host institution.

## Release status: qualified exploratory evidence

The numerical implementation completed the frozen 16-by-16 grid and independent
winner validation. However, the whole grid was executed twice during provenance
repair, and the first full JSON was overwritten. Therefore today's total is **512
search circuit evaluations**, not 256, plus two independent winner-oracle checks
and two separately counted regression suites. The prospective aggregate budget
and complete evidence-retention gate are **not met**. Do not describe R15 as an
unqualified protocol-compliant completion.

First-run materialization appended one newline to repository inputs. This did not
change Python behavior, but input hashes were not byte-identical to GitHub. The
files were restored exactly and the search replayed using the same grid, objective,
selection rule and source. The archived second execution retains every candidate;
the first execution retains only its observed summary, source hashes and full-file
digest in [the run ledger](../results/2026-10-19-run-ledger.json). Agreement of the
recorded winner summaries is not proof that all first-run candidate vectors match.
No failed candidates were retried or omitted within either grid.

This is a real workflow failure: the new CLI permits an existing output pathname
to be overwritten. Before any later experiment, add collision refusal and unique
run identifiers. Do not repair the missing evidence by inventing it or silently
changing the frozen protocol. The original v1 document remains unchanged, including
its prospective PLANNED/UNEXECUTED wording; this note records subsequent status.

## Archived execution

- Python 3.12.14, NumPy 2.5.3, Qiskit 2.5.2; full seven-package lock unchanged.
- Eight regression modules passed 91 underlying checks before the grid; thirteen
  runner-level gates also passed. These overlap and are not 104 independent findings.
- All 256 candidates have full 64-state probabilities, metrics, norm and oracle errors.
- Maximum candidate SDK/oracle component error: 1.3109010445264553e-14, below 1e-11.
- Energy ties at ordinals 99 and 173; the prespecified rule chooses ordinal 99.
- Chosen j=6, k=3: gamma=3*pi/4, beta=3*pi/16.
- Independent winner state error: 3.1312988881233425e-15; maximum metric error:
  7.815970093361102e-14. This check reuses the independent amplitude-pairing routine
  but derives its energies and readout directly from bits rather than the hand table.
- Second search: 0.85998 seconds, total runner: 1.09861 seconds, excluding dependency
  installation and imports. These are descriptive timings, not speedup evidence.

## Same candidate, different success measures

| Metric | Uniform six-bit output | Selected grid candidate | Feasible greedy construction |
|---|---:|---:|---:|
| Mean penalized energy, lower is better | 50 | 26.756841 | 6 |
| Excess above exact minimum, lower is better | 44 | 20.756841 | 0 |
| Physical feasibility | 62.5% | 97.767084% | 100% |
| Correct auxiliary encoding | 7.8125% | 19.596842% | 100% |
| Physically optimal load probability | 12.5% | 8.338058% | 100% |
| Encoded ground-state probability | 1.5625% | 1.671315% | 100% |
| Conditional service loss, lower is better | 9.6 | 10.931974 | 6 |

The primary energy outcome improves by 23.243159, and physical-feasibility mass
increases by 35.267084 percentage points. But optimal-load probability decreases
by 4.161942 points and conditional service loss increases by 1.331974. The result is
**mixed**, not uniformly better. Energy selection rewards the penalized objective;
it was not designed to maximize the probability of serving the best feasible loads.
No secondary metric was used to choose a more flattering candidate.

The optional representation-adjusted uniform-load baseline has mean energy 12.25,
physical mass 0.625, encoding mass 0.625 and optimal-load probability 0.125. Its
canonical slack assignment changes the representation distribution; do not label
it uniform six-bit output. The greedy construction inspects three load decisions
in order 1,0,2 and already finds the exact optimum. Neither it nor enumeration is a
budget-matched speed competitor. This toy does not support an advantage claim.

## Reproduction and evidence boundaries

From phd-simulation, install requirements-sdk.txt in an isolated free environment,
then run `python src/run_pilot_v1.py --output results/UNIQUE-run-name.json`.
**Use a new pathname: this version does not guard against overwriting.** The script
hardcodes the canonical publication command in provenance; the actual output
argument must be retained by the caller for differently named reproduction runs.
All input/source hashes and full nested regression outputs are archived in
[the second-run JSON](../results/2026-10-19-pilot-v1.json).

The source checks were refreshed on October 19 using IBM's primary documentation:
[RXGate](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.RXGate)
defines RX(theta)=exp(-i*theta*X/2), and
[Statevector](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector)
documents from_instruction and computational-basis probabilities. These sources
support API conventions, not today's numerical outcomes, which come from execution.
The 2*pi gamma period follows from integer energies; the pi beta period is up to
global phase. The coarse grid does not establish a continuous optimum.

Tomorrow: harden evidence retention before any further runs, then start R06's
source-verified testing literature map. R08's realistic baseline/resource and
held-out-instance design remains open. No manuscript submission or real meeting occurred.
