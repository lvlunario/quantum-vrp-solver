"""Executed educational experiment; synthetic data; no quantum hardware used."""
import hashlib
import json
import platform
from pathlib import Path
import numpy as np

def costs():
    # Bit i controls load i; x=1 means served. Capacity units are synthetic.
    bits = ((np.arange(8)[:, None] >> np.arange(3)) & 1)
    demand = bits @ np.array([2, 3, 4])
    unserved = (1 - bits) @ np.array([3, 5, 6])
    return bits, demand, unserved

def probabilities(energy, gamma, beta):
    state = np.exp(-1j * gamma * energy) / np.sqrt(8)
    for q in range(3):
        old = state.copy()
        state = np.cos(beta) * old - 1j * np.sin(beta) * old[np.arange(8) ^ (1 << q)]
    return np.abs(state) ** 2

def run():
    bits, demand, unserved = costs()
    feasible = demand <= 5
    optimum = int(unserved[feasible].min())
    records = []
    for penalty in [0.1, 1.0, 4.0]:
        energy = unserved + penalty * np.maximum(0, demand - 5) ** 2
        best = None
        for gamma in np.linspace(0, 2 * np.pi, 41, endpoint=False):
            for beta in np.linspace(0, np.pi, 41, endpoint=False):
                p = probabilities(energy, gamma, beta)
                expected = float(p @ energy)
                if best is None or expected < best[0]:
                    best = expected, float(gamma), float(beta), p
        expected, gamma, beta, p = best
        idx = int(energy.argmin())
        records.append(dict(penalty=penalty, exact_penalized_min=float(energy[idx]),
                            exact_penalized_argmin=bits[idx].tolist(),
                            penalized_argmin_feasible=bool(feasible[idx]),
                            qaoa_expected_energy=expected, gamma=gamma, beta=beta,
                            qaoa_feasible_probability=float(p[feasible].sum()),
                            qaoa_optimal_feasible_probability=float(p[feasible & (unserved == optimum)].sum()),
                            probabilities=p.tolist()))
    return dict(status='EXECUTED_LOCAL_STATEVECTOR', synthetic=True,
                hardware_used=False, python=platform.python_version(), numpy=np.__version__,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                model='3-load single-period capacity-constrained service selection',
                warning='Diagonal oracle toy; not yet a QUBO or realistic power-flow model. No speedup claim.',
                objective='minimize weighted unserved load subject to demand <= 5',
                demand=[2,3,4], priority=[3,5,6], capacity=5,
                exact_feasible_optimum=optimum,
                exact_feasible_optimal_bits=bits[feasible & (unserved == optimum)].tolist(),
                uniform_feasible_probability=float(feasible.mean()),
                uniform_optimal_feasible_probability=float((feasible & (unserved == optimum)).mean()),
                qaoa_depth=1, angle_evaluations_per_penalty=1681, records=records)

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
