"""Frozen R15 v1: deterministic bounded exact-statevector development pilot.

Run from phd-simulation: python src/run_pilot_v1.py --output results/2026-10-19-pilot-v1.json
Writes evidence even on regression/search/validation failure; no silent retries.
"""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
import math
import platform
import signal
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import qiskit
from qiskit.quantum_info import Statevector
from verify_qiskit_mixer import qaoa_circuit, independent_state, apply_independent_mixer
from verify_readout import summarize, fixture, LOADS, LOSSES
from verify_baseline_references import decision

TOL = 1e-11
ROOT = Path(__file__).resolve().parent.parent
GATES = ['verify_formulation', 'verify_ising', 'verify_phase_evolution',
         'verify_statevector_interface', 'verify_qiskit_cost_circuit',
         'verify_qiskit_mixer', 'verify_readout', 'verify_baseline_references']


def select(rows):
    minimum = min(r['metrics']['mean_energy'] for r in rows)
    tied = [r['ordinal'] for r in rows if abs(r['metrics']['mean_energy']-minimum) <= TOL]
    return min(tied), tied, minimum


def metrics(p):
    report = summarize(p)  # Rejects nonfinite, negative or unnormalized inputs.
    physical = report['physical_feasibility']
    loss = math.fsum(float(p[i])*LOSSES[i % 8] for i in range(64) if LOADS[i % 8] <= 5)
    return dict(mean_energy=report['expected_energy'],
                energy_excess=report['expected_energy']-6,
                physical_feasibility=physical,
                encoding_consistency=report['encoding_consistency'],
                optimal_load_probability=math.fsum(float(p[i]) for i in range(64) if i % 8 == 3),
                ground_state_probability=float(p[3]),
                conditional_service_loss=loss/physical if physical > TOL else None)


def independent_metrics(p):
    # Separate bit-derived calculation, not the hand table/readout implementation.
    rows = []
    for i in range(64):
        demand, loss = decision(i % 8)
        residual = demand+i//8-5
        rows.append((loss+2*residual**2, demand <= 5, residual == 0, loss))
    ground = min(r[0] for r in rows)
    optimum = min(r[3] for r in rows if r[1])
    safe_mass = sum(float(p[i]) for i, r in enumerate(rows) if r[1])
    energy = sum(float(p[i])*r[0] for i, r in enumerate(rows))
    return dict(mean_energy=energy, energy_excess=energy-ground,
                physical_feasibility=safe_mass,
                encoding_consistency=sum(float(p[i]) for i, r in enumerate(rows) if r[2]),
                optimal_load_probability=sum(float(p[i]) for i, r in enumerate(rows) if r[1] and r[3] == optimum),
                ground_state_probability=sum(float(p[i]) for i, r in enumerate(rows) if r[0] == ground),
                conditional_service_loss=sum(float(p[i])*r[3] for i, r in enumerate(rows) if r[1])/safe_mass if safe_mass > TOL else None)


def timeout_handler(signum, frame):
    raise TimeoutError('Frozen 30-second search safety limit reached')


def run():
    started = time.perf_counter()
    result = dict(status='RUNNING', executed_at_utc=datetime.now(timezone.utc).isoformat(),
                  command='python src/run_pilot_v1.py --output results/2026-10-19-pilot-v1.json',
                  parent_commit='71b7fa40abf03abe5d8dd0677d2bfd0b685b9ac8',
                  data='Fixed synthetic six-qubit development fixture; no holdout or external dataset',
                  versions=dict(python=platform.python_version(), numpy=np.__version__, qiskit=qiskit.__version__),
                  dependencies={name: importlib.metadata.version(name) for name in
                      ('dill', 'numpy', 'qiskit', 'rustworkx', 'scipy', 'stevedore', 'typing_extensions')},
                  platform=platform.platform(), randomness='None',
                  config=dict(protocol='docs/baseline-protocol-v1.md', grid=16, max_candidates=256,
                              gamma='2*pi*j/16', beta='pi*k/16', order='j outer, k inner',
                              tolerance=TOL, wall_limit_seconds=30, demands=[2,3,4],
                              priorities=[3,5,6], capacity=5, penalty=2),
                  sampling_used=False, hardware_used=False, noise_used=False, transpilation_used=False,
                  adaptive_optimizer_used=False, regression_gates=[], candidates=[], checks=[],
                  counts=dict(search_attempted=0, search_completed=0, winner_oracle_validations=0),
                  timings_seconds=dict(construction=0., sdk_evolution=0., oracle=0., readout_checks=0.))
    paths = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'src').glob('*.py'))]
    paths += ['requirements-sdk.txt', 'docs/baseline-protocol-v1.md', 'results/2026-10-15-readout.json']
    result['source_sha256'] = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    def check(name, ok):
        result['checks'].append(dict(name=name, passed=bool(ok)))
        if not ok:
            raise AssertionError(name)
    try:
        regression_start = time.perf_counter()
        for name in GATES:
            t = time.perf_counter()
            raw = importlib.import_module(name).run()
            result['regression_gates'].append(dict(module=name, duration_seconds=time.perf_counter()-t,
                invocation=f'{name}.run() imported by run_pilot_v1.py; nested command fields describe legacy standalone entrypoints',
                evidence=raw))
            check(name+' regression gate passes', bool(raw['checks']) and all(c['passed'] for c in raw['checks']))
        result['timings_seconds']['regressions'] = time.perf_counter()-regression_start
        fake = [dict(ordinal=1,metrics=dict(mean_energy=2.0)),
                dict(ordinal=0,metrics=dict(mean_energy=2.0+TOL/2))]
        check('selection uses absolute tolerance then lowest ordinal', select(fake)[0] == 0)
        uniform = metrics(np.full(64, 1/64))
        greedy = np.zeros(64); greedy[3] = 1
        canonical = np.zeros(64)
        for x in range(8):
            demand, _ = decision(x)
            canonical[x+8*max(0,5-demand)] += 1/8
        result['baselines'] = dict(uniform_encoded=uniform,
            greedy=dict(order=[1,0,2], inspected_decisions=3, index=3, metrics=metrics(greedy)),
            representation_adjusted_uniform_load_canonical_slack=metrics(canonical))
        search_start = time.perf_counter()
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, 30)
        cached_states = []
        try:
            for j in range(16):
                for k in range(16):
                    gamma, beta = 2*math.pi*j/16, math.pi*k/16
                    row = dict(ordinal=16*j+k, j=j, k=k, gamma=gamma, beta=beta, status='ATTEMPTED')
                    result['candidates'].append(row)
                    result['counts']['search_attempted'] += 1
                    t = time.perf_counter(); circuit = qaoa_circuit(gamma,beta)
                    result['timings_seconds']['construction'] += time.perf_counter()-t
                    t = time.perf_counter(); sdk = Statevector.from_instruction(circuit).data
                    result['timings_seconds']['sdk_evolution'] += time.perf_counter()-t
                    t = time.perf_counter(); oracle = independent_state(gamma,beta)
                    result['timings_seconds']['oracle'] += time.perf_counter()-t
                    t = time.perf_counter()
                    error = float(np.max(np.abs(sdk-oracle)))
                    norm_error = abs(float(np.vdot(sdk,sdk).real)-1)
                    row.update(max_component_error=error, norm_error=norm_error)
                    if not np.isfinite(sdk).all() or not np.isfinite(oracle).all() or error > TOL or norm_error > TOL:
                        row['status'] = 'FAILED'; raise ValueError('SDK/oracle or norm gate')
                    p = np.abs(sdk)**2
                    row.update(metrics=metrics(p), probabilities_qiskit_index=p.tolist(), status='PASSED')
                    result['timings_seconds']['readout_checks'] += time.perf_counter()-t
                    cached_states.append(sdk)
                    result['counts']['search_completed'] += 1
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)
            result['timings_seconds']['search'] = time.perf_counter()-search_start
        check('all 256 candidates completed with no retries', result['counts']['search_completed'] == 256)
        ordinal, tied, minimum = select(result['candidates'])
        winner = result['candidates'][ordinal]
        result['selection'] = dict(primary='minimum mean energy; absolute tie tolerance then smallest ordinal',
                                   ordinal=ordinal, tied_ordinals=tied, numerical_minimum=minimum)
        validation_start = time.perf_counter()
        result['counts']['winner_oracle_validations'] += 1
        independent_energies = np.array([decision(i%8)[1]+2*(decision(i%8)[0]+i//8-5)**2 for i in range(64)])
        reference = apply_independent_mixer(np.exp(-1j*winner['gamma']*independent_energies)/8, winner['beta'])
        independent = independent_metrics(np.abs(reference)**2)
        state_error = float(np.max(abs(reference-cached_states[ordinal])))
        metric_error = max(abs(independent[key]-winner['metrics'][key]) for key in independent)
        result['winner_validation'] = dict(state_error=state_error, metric_error=metric_error,
                                          metrics=independent, probabilities_qiskit_index=(np.abs(reference)**2).tolist())
        check('winner independently validates state and all metrics', state_error < TOL and metric_error < TOL)
        result['timings_seconds']['winner_validation'] = time.perf_counter()-validation_start
        result['winner'] = winner
        result['difference_from_uniform'] = {key:winner['metrics'][key]-uniform[key] for key in uniform}
        check('selected mean cannot exceed included zero-angle uniform candidate', winner['metrics']['mean_energy'] <= uniform['mean_energy']+TOL)
        check('all candidates retain energy lower bound and probability subset', all(
            r['metrics']['mean_energy'] >= 6-TOL and
            r['metrics']['encoding_consistency'] <= r['metrics']['physical_feasibility']+TOL
            for r in result['candidates']))
        result['primary_improved'] = uniform['mean_energy']-winner['metrics']['mean_energy'] > TOL
        result['secondary_deteriorations'] = [key for key in ('physical_feasibility','encoding_consistency',
            'optimal_load_probability','ground_state_probability') if result['difference_from_uniform'][key] < -TOL]
        if result['difference_from_uniform']['conditional_service_loss'] > TOL:
            result['secondary_deteriorations'].append('conditional_service_loss')
        result['status'] = 'EXECUTED_COMPLETE'
    except Exception as exc:
        result['status'] = 'FAILED'
        result['failure'] = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
    finally:
        result['timings_seconds']['total'] = time.perf_counter()-started
        result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['limitations'] = ['One development fixture; no holdout or generalization evidence',
        'Finite coarse grid, not a continuous optimum', 'Ideal exact local simulation; no speedup or quantum advantage claim',
        'Greedy already solves the physical and encoded toy exactly',
        'No network, storage dynamics, disturbances or realistic resilient-control evidence']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','counts','selection','winner_validation','difference_from_uniform','timings_seconds','failure') if k in result}, indent=2))
    sys.exit(0 if result['status'] == 'EXECUTED_COMPLETE' else 1)
