# Research charter — fictional program, real methods
## Motivation and scope
A low numerical objective is insufficient if a dispatch violates capacity or if a benchmark silently compares different tasks.
The research contribution sought is a verification framework for the chain from engineering requirement to binary formulation to circuit to decoded decision.
The power-system case study is a vehicle for evaluating the verification method; it is not a claim that three loads represent a real grid.

## Questions
RQ1: Which formulation and decoding faults escape ordinary objective-value checks?
RQ2: Can metamorphic tests and independent feasibility checks detect those faults at acceptable overhead?
RQ3: How do penalty choices, noise and finite measurement budgets affect feasibility and the credibility of comparisons?
RQ4: Which conclusions survive stronger classical baselines and independent reproduction?

## Provisional hypotheses (not findings)
H1: Feasibility-aware tests detect fault classes missed by objective-only tests.
H2: Poor penalty scaling can make an optimizer prefer infeasible schedules even when it minimizes its mathematical objective correctly.
H3: Apparent solver improvements shrink when feasibility, optimization effort and end-to-end costs are included.
Novelty remains unestablished until the literature review. If an identical method exists, reproduce it and narrow the contribution.

## Progressive model ladder
1. Three-load service selection: enumerate eight decisions and validate conventions.
2. QUBO with explicit slack variables and checked binary encoding; prove equivalence on tiny cases.
3. Small multi-period scheduling including battery energy balance, bounds and ramping where relevant.
4. Broader synthetic instance families; realistic public test cases only after provenance and license checks.
5. Ideal and noisy simulated circuits; real hardware only if separately authorized and available.
Power-flow physics, protection, dynamic stability, network topology, load uncertainty and reserve requirements are absent at step 1. Do not call step 1 deployable dispatch.

## Experimental protocol v0.1
Store a schema, source revision/hash, environment versions, seeds, instance definition, solver settings and raw outputs for every run.
Begin with exhaustive enumeration as an independent oracle. Later add a verified classical MILP baseline, a greedy policy and equal-budget random search.
QAOA comparisons must include parameter optimization evaluations, compilation, measurement shots, decoding and repair. Report queue time separately.
Use training instances for parameter selection and held-out instances for evaluation; never tune on the reported test set.
At the substantive benchmark stage, target at least 30 independent seeds per stochastic configuration, then revisit precision and computational budget after a pilot.
Experimental units are independent instances/runs, not individual correlated shots. Use paired per-instance comparisons and bootstrap intervals over independent instances where appropriate.
Report feasibility rate, objective conditional on feasibility, unserved energy or proxy cost, optimum gap where known, runtime, shots, circuit depth and test overhead.
Infeasible outputs remain visible. Do not silently discard or repair them; label repaired and unrepaired metrics separately.
Freeze the main analysis before examining held-out outcomes. Exploratory changes go in a deviation log.

## Fault and test catalog
Faults: wrong penalty sign, insufficient penalty, bit-order reversal, missing capacity constraint, bad slack range, decoding mismatch, off-by-one time index and invalid probability normalization.
Properties: relabeling equivalent loads preserves the optimum; relaxing capacity cannot worsen the true optimum; zero-demand loads do not consume capacity; independently recomputed constraints agree with decoded output.
Symmetry tests require correspondingly permuting all demand/priority data. Scale-invariance claims require scaling every relevant objective term and optimizer settings appropriately.
Mutation score alone is not evidence of realistic fault detection; inspect equivalent mutants and record the representativeness of faults.

## Stop and pivot criteria
If the formulation is wrong, suspend performance plots. If classical baselines dominate, study reliability and explain limits instead of escalating qubit counts for appearance.
Reserve approximately 20% of normal capacity for failed experiments, reading and rework.
Limit simulation size before exponential statevector cost becomes impractical. No paid services or indefinite background jobs.

## Planned research outputs
Paper A: *A Verification Protocol for Hybrid Quantum Microgrid Optimization* — workshop-style draft by February; fictional submission milestone, no actual venue commitment.
Paper B: *Penalty Scaling and Feasibility in Small Quantum Scheduling Benchmarks* — conditional draft by June; only if enough defensible evidence exists.
September: first-year report, reproducibility package and proposed year-two direction. Acceptance and positive outcomes are never guaranteed.
