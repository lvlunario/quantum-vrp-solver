"""One fixed Qiskit point through the retention guard; no parameter search."""
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import qiskit
from qiskit.quantum_info import Statevector

from evidence_store import execute, now
from verify_qiskit_mixer import independent_state, qaoa_circuit

GAMMA, BETA = 0.2, 0.31
TOL = 1e-12
PARENT = 'd527d061e7b92cf5c440df2cdaac95df6806b15a'

def metadata(kind):
    return dict(kind=kind, parent_commit=PARENT, python=platform.python_version(), qiskit=qiskit.__version__, numpy=np.__version__, data='Fixed synthetic six-qubit development fixture', randomness='None')

def success_callback(event):
    event('candidate_attempt', ordinal=0, gamma=GAMMA, beta=BETA)
    sdk = Statevector.from_instruction(qaoa_circuit(GAMMA, BETA)).data
    oracle = independent_state(GAMMA, BETA)
    error = float(np.max(np.abs(sdk - oracle)))
    norm_error = abs(float(np.vdot(sdk, sdk).real) - 1.0)
    if error >= TOL or norm_error >= TOL:
        raise AssertionError(f'fixed-point oracle mismatch: {error}')
    probabilities = np.abs(sdk) ** 2
    event('candidate_complete', ordinal=0, max_component_error=error, norm_squared_error=norm_error, probabilities_qiskit_index=probabilities.tolist())
    event('winner_validation_attempt', ordinal=0, meaning='fixed-point oracle validation; no selection')
    return dict(status='EXECUTED_FIXED_POINT_SUCCESS', executed_at_utc=now(), counts=dict(search_attempted=1, search_completed=1, winner_oracle_validations=1), gamma=GAMMA, beta=BETA, max_component_error=error, norm_squared_error=norm_error, probability_sum=float(probabilities.sum()), checks=[dict(name='SDK state matches independent amplitude-pairing oracle', passed=True), dict(name='state remains normalized', passed=True)], search_performed=False, hardware_used=False, shots_used=False, transpilation_used=False, limitations=['One predetermined synthetic point', 'Exact local statevector only', 'No optimization, sampling, noise, hardware, speedup or advantage claim'])

def failure_callback(event):
    event('candidate_attempt', ordinal=0, gamma=GAMMA, beta=BETA, injected_fault='RX(beta) replaces RX(2*beta)')
    faulty = Statevector.from_instruction(qaoa_circuit(GAMMA, BETA, mixer_scale=1.0)).data
    oracle = independent_state(GAMMA, BETA)
    error = float(np.max(np.abs(faulty - oracle)))
    event('fault_observed', max_component_error=error, tolerance=TOL, rejected=error >= TOL)
    if error >= TOL:
        raise AssertionError(f'injected half-angle mixer rejected; max error {error:.17g}')
    raise AssertionError('injected fault unexpectedly escaped oracle')

def read_json(path):
    return json.loads(Path(path).read_text())

def main():
    out = Path('integration-output')
    out.mkdir(exist_ok=False)
    success_path = out / '2026-10-21-fixed-success.json'
    failure_path = out / '2026-10-21-injected-failure.json'
    success = execute(success_path, success_callback, metadata('fixed-point-success'))
    failure_exception = None
    try:
        execute(failure_path, failure_callback, metadata('injected-half-angle-failure'))
    except AssertionError as exc:
        failure_exception = str(exc)
    failure_events = [read_json(p) for p in sorted((out / (failure_path.name + '.run')).glob('[0-9]*.json'))]
    checks = [
        dict(name='success output and terminal retained', passed=success_path.exists() and (out/(success_path.name+'.run')/'terminal.json').exists()),
        dict(name='failure output absent and reservation retained', passed=not failure_path.exists() and (out/(failure_path.name+'.run')/'manifest.json').exists()),
        dict(name='failure attempt, observed fault and abort retained', passed=[e['kind'] for e in failure_events] == ['candidate_attempt','fault_observed','aborted']),
        dict(name='injected fault rejected above tolerance', passed=failure_events[1]['payload']['rejected'] is True),
    ]
    if not all(c['passed'] for c in checks):
        raise AssertionError(checks)
    source = Path(__file__)
    summary = dict(status='EXECUTED_FIXED_POINT_RETENTION_INTEGRATION', executed_at_utc=now(), command='.venv-q/bin/python verify_fixed_point_retention.py', parent_commit=PARENT, versions=dict(python=platform.python_version(), qiskit=qiskit.__version__, numpy=np.__version__), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), config=dict(gamma=GAMMA,beta=BETA,tolerance=TOL), success=success, injected_failure=dict(exception=failure_exception, events=failure_events), checks=checks, actual_sdk_circuits_executed=2, search_evaluations=0, data='Fixed synthetic six-qubit development fixture', limitations=['Application-level local retention, not immutable storage', 'One success and one intentional failure at a predetermined point', 'No grid, optimizer, shots, noise, transpilation, cloud service or hardware'])
    Path('2026-10-21-fixed-point-retention.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(dict(status=summary['status'], checks=checks, success_error=success['max_component_error'], injected_error=failure_events[1]['payload']['max_component_error']), indent=2))

if __name__ == '__main__':
    main()
