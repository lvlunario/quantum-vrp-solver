"""R14: independent readout audit on a fixed synthetic six-qubit fixture.

Run from phd-simulation with the existing requirements-sdk.txt environment.
No optimizer, shots, transpilation, cloud service or hardware is used.
"""
import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import qiskit
from qiskit.quantum_info import Statevector, SparsePauliOp
from verify_qiskit_mixer import ANGLE_PAIRS, qaoa_circuit, ising_terms

TOL = 1e-11
# Hand-enumerated load fixture: integer x0 + 2*x1 + 4*x2 -> (load, loss).
LOADS = (0, 2, 3, 5, 4, 6, 7, 9)
LOSSES = (14, 11, 9, 6, 8, 5, 3, 0)


def fixture(index):
    x, slack = index % 8, index // 8
    residual = LOADS[x] + slack - 5
    return LOSSES[x] + 2 * residual**2, LOADS[x] <= 5, residual == 0


def summarize(probabilities):
    p = np.asarray(probabilities, dtype=float)
    if p.shape != (64,) or not np.isfinite(p).all() or p.min() < 0 or abs(p.sum()-1) > TOL:
        raise ValueError('Expected 64 finite nonnegative normalized probabilities')
    energy = math.fsum(float(p[i]) * fixture(i)[0] for i in range(64))
    physical = math.fsum(float(p[i]) for i in range(64) if fixture(i)[1])
    encoded = math.fsum(float(p[i]) for i in range(64) if fixture(i)[2])
    marginal = [math.fsum(float(p[x + 8*s]) for s in range(8)) for x in range(8)]
    return dict(expected_energy=energy, physical_feasibility=physical,
                encoding_consistency=encoded, load_marginal=marginal)


def observable():
    offset, fields, couplings = ising_terms()
    terms = [('IIIIII', float(offset))]
    for i, h in enumerate(fields):
        label = list('IIIIII'); label[5-i] = 'Z'
        terms.append((''.join(label), float(h)))
    for i, j, h in couplings:
        label = list('IIIIII'); label[5-i] = label[5-j] = 'Z'
        terms.append((''.join(label), float(h)))
    return SparsePauliOp.from_list(terms)


def run():
    checks = []
    def check(name, passed):
        checks.append(dict(name=name, passed=bool(passed)))
        if not passed: raise AssertionError(name)
    energies = np.array([fixture(i)[0] for i in range(64)])
    obs = observable()
    diagonal = np.diag(obs.to_matrix()).real
    check('all 64 observable diagonal entries match hand-enumerated load/slack fixture', np.max(abs(diagonal-energies)) < TOL)
    check('unique encoded energy minimum is index 3 with energy 6', np.flatnonzero(energies == energies.min()).tolist() == [3] and energies[3] == 6)
    basis_errors = []
    for i in range(64):
        p = np.eye(1, 64, i).ravel()
        r = summarize(p)
        basis_errors.append(max(abs(r['expected_energy']-fixture(i)[0]), abs(r['physical_feasibility']-fixture(i)[1]), abs(r['encoding_consistency']-fixture(i)[2])))
    check('all 64 one-hot readouts match physical and encoded labels', max(basis_errors) < TOL)
    uniform = summarize(np.full(64, 1/64))
    check('uniform fixture has physical mass 5/8 and encoded mass 5/64', abs(uniform['physical_feasibility']-5/8) < TOL and abs(uniform['encoding_consistency']-5/64) < TOL)
    # E[loss]=7; residual mean=3 and variance=12.5, hence 7+2*(9+12.5)=50.
    check('uniform mean energy is independently 50', abs(uniform['expected_energy']-50) < TOL)
    rows = []
    for gamma, beta in ANGLE_PAIRS:
        state = Statevector.from_instruction(qaoa_circuit(gamma, beta))
        p = state.probabilities()
        report = summarize(p)
        dictionary = state.probabilities_dict()
        decoded = np.zeros(64)
        for label, probability in dictionary.items(): decoded[int(label, 2)] = probability
        expectation = complex(state.expectation_value(obs))
        phased = summarize(np.abs(state.data * np.exp(0.73j))**2)
        check(f'{gamma,beta}: SDK observable and independent expected energy agree', abs(expectation.real-report['expected_energy']) < TOL and abs(expectation.imag) < TOL)
        check(f'{gamma,beta}: dictionary labels recover all probabilities', np.max(abs(decoded-p)) < TOL)
        check(f'{gamma,beta}: summing slack reproduces physical mass', abs(sum(report['load_marginal'][x] for x in range(8) if LOADS[x] <= 5)-report['physical_feasibility']) < TOL)
        check(f'{gamma,beta}: encoding mass is a subset of physical mass', 0 <= report['encoding_consistency'] <= report['physical_feasibility'] <= 1+TOL)
        check(f'{gamma,beta}: readout ignores global phase', max(abs(report[k]-phased[k]) for k in ('expected_energy','physical_feasibility','encoding_consistency')) < TOL)
        rows.append(dict(gamma=gamma, beta=beta, **report, sdk_expected_energy=expectation.real, probabilities_qiskit_index=p.tolist()))
    p = np.array(rows[0]['probabilities_qiskit_index'])
    reverse = np.array([int(f'{i:06b}'[::-1], 2) for i in range(64)])
    faulty_reverse = float(p @ energies[reverse])
    faulty_amplitude = float(np.sqrt(p) @ energies)
    offset = float(ising_terms()[0])
    shifted = float(p @ (energies - offset))
    correct = rows[0]['expected_energy']
    check('reversed bit-order energy fault detected on fixed state', abs(faulty_reverse-correct) > 1e-6)
    check('amplitudes substituted for probabilities detected', abs(faulty_amplitude-correct) > 1e-6)
    check('omitted identity offset changes energy by exactly the offset', abs((correct-shifted)-offset) < TOL and abs(offset) > 1)
    check('conflating physical feasibility and encoding consistency detected', abs(rows[0]['physical_feasibility']-rows[0]['encoding_consistency']) > 1e-6)
    check('positive affine energy transform preserves minimizers and transforms mean', np.argmin(3*energies+7) == 3 and abs(float(p@(3*energies+7))-(3*correct+7)) < TOL)
    rejected = 0
    for bad in (np.zeros(64), np.full(64, np.nan), np.r_[-1, np.full(63, 2/63)], np.ones(8)):
        try: summarize(bad)
        except ValueError: rejected += 1
    check('reject malformed, negative, nonfinite and unnormalized readout', rejected == 4)
    root = Path(__file__).resolve().parent.parent
    files = ['src/verify_readout.py','src/verify_qiskit_mixer.py','src/verify_formulation.py','requirements-sdk.txt']
    return dict(status='EXECUTED_LOCAL_QISKIT_EXACT_READOUT_AUDIT', executed_at_utc=datetime.now(timezone.utc).isoformat(),
        command='python src/verify_readout.py > results/2026-10-15-readout.json',
        versions=dict(python=platform.python_version(), numpy=np.__version__, qiskit=qiskit.__version__),
        source_sha256={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},
        config=dict(demands=[2,3,4], priorities=[3,5,6], capacity=5, penalty=2, slack_weights=[1,2,4], angle_pairs=ANGLE_PAIRS, tolerance=TOL),
        data='Fixed synthetic toy; no external data', randomness='None', optimizer_used=False, shots_used=False, hardware_used=False,
        uniform_reference=uniform, raw_basis=[dict(index=i,energy=fixture(i)[0],physical=fixture(i)[1],encoded=fixture(i)[2]) for i in range(64)],
        fixed_state_results=rows, mutations=dict(reversed_bit_energy=faulty_reverse,amplitude_weighted_energy=faulty_amplitude,offset_free_energy=shifted,identity_offset=offset), checks=checks,
        limitations=['One synthetic instance, three fixed angle pairs; no parameter selection or optimization', 'Ideal exact statevectors only; no shots, noise, transpilation or hardware', 'Selected faults do not estimate a general detection rate', 'Not a realistic microgrid benchmark or evidence of quantum advantage'])


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
