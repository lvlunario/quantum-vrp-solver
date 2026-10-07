"""Build the statevector acceptance oracle for a future quantum-SDK circuit.

This executes a bounded NumPy calculation. It does not claim an SDK circuit run.
Run from phd-simulation: python src/verify_statevector_interface.py
"""
import cmath
import hashlib
import importlib.util
import json
import math
import platform
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

import numpy as np

from verify_formulation import C, D, P, coeffs


TOL = 1e-12
GAMMAS = [math.pi / 17, 0.2, 0.7]


def run():
    constant, linear, cross = coeffs(F(2))
    offset = constant + sum(linear) / 2 + sum(value for _, _, value in cross) / 4
    fields = [-value / 2 for value in linear]
    couplings = []
    for i, j, value in cross:
        fields[i] -= value / 4
        fields[j] -= value / 4
        couplings.append((i, j, value / 4))

    def bits_for_index(index):
        return tuple((index >> qubit) & 1 for qubit in range(6))

    def oracle(bits):
        served = sum(D[i] * bits[i] for i in range(3))
        spare = bits[3] + 2 * bits[4] + 4 * bits[5]
        return sum(P[i] * (1 - bits[i]) for i in range(3)) + 2 * (served + spare - C) ** 2

    def ising(bits, include_offset=True):
        spins = tuple(1 - 2 * bit for bit in bits)
        energy = (offset if include_offset else 0) + sum(
            h * spin for h, spin in zip(fields, spins)
        ) + sum(value * spins[i] * spins[j] for i, j, value in couplings)
        return energy

    def evolve(initial, energies, gamma, exponent_sign=-1):
        phases = np.exp(exponent_sign * 1j * gamma * np.asarray(energies, dtype=float))
        return initial * phases

    def global_phase_residual(reference, candidate):
        pivot = int(np.argmax(np.abs(reference)))
        phase = candidate[pivot] / reference[pivot]
        residual = float(np.max(np.abs(candidate - phase * reference)))
        return phase, residual

    bits = [bits_for_index(index) for index in range(64)]
    oracle_energies = [oracle(row) for row in bits]
    mapped_energies = [ising(row) for row in bits]
    no_offset_energies = [ising(row, include_offset=False) for row in bits]
    reversed_energies = [oracle(tuple(reversed(row))) for row in bits]

    raw = np.asarray([complex(index + 1, 64 - index) for index in range(64)])
    initial = raw / np.linalg.norm(raw)

    checks = []

    def check(name, passed, detail=None):
        row = {"name": name, "passed": bool(passed)}
        if detail is not None:
            row["detail"] = detail
        checks.append(row)
        assert passed, name

    check("index contract maps index 3 to logical bits 110000",
          bits[3] == (1, 1, 0, 0, 0, 0), {"bits_q0_first": bits[3]})
    check("mapped energies equal the residual oracle for all 64 indices",
          mapped_energies == oracle_energies)

    strict_errors = []
    no_offset_residuals = []
    no_offset_phase_errors = []
    no_offset_strict_distances = []
    for gamma in GAMMAS:
        reference = evolve(initial, oracle_energies, gamma)
        mapped = evolve(initial, mapped_energies, gamma)
        without_offset = evolve(initial, no_offset_energies, gamma)
        strict_errors.append(float(np.max(np.abs(reference - mapped))))
        recovered_phase, residual = global_phase_residual(reference, without_offset)
        expected_phase = cmath.exp(1j * gamma * float(offset))
        no_offset_residuals.append(residual)
        no_offset_phase_errors.append(abs(recovered_phase - expected_phase))
        no_offset_strict_distances.append(float(np.max(np.abs(reference - without_offset))))

    check("strict statevectors agree when the constant offset is included",
          max(strict_errors) < TOL,
          {"max_component_error": max(strict_errors), "angles": len(GAMMAS)})
    check("offset-free statevectors agree up to global phase",
          max(no_offset_residuals) < TOL,
          {"max_component_residual": max(no_offset_residuals)})
    check("recovered global phase equals exp(+i*gamma*offset)",
          max(no_offset_phase_errors) < TOL,
          {"max_phase_error": max(no_offset_phase_errors), "offset": str(offset)})
    check("strict comparison would reject the valid offset-free statevectors",
          min(no_offset_strict_distances) > 1e-3,
          {"component_distances": no_offset_strict_distances})

    fault_gamma = 0.2
    reference = evolve(initial, oracle_energies, fault_gamma)
    wrong_sign = evolve(initial, oracle_energies, fault_gamma, exponent_sign=1)
    wrong_order = evolve(initial, reversed_energies, fault_gamma)
    _, wrong_sign_residual = global_phase_residual(reference, wrong_sign)
    _, wrong_order_residual = global_phase_residual(reference, wrong_order)
    changed_order_energies = sum(a != b for a, b in zip(oracle_energies, reversed_energies))
    check("global-phase comparison rejects the exponent-sign fault",
          wrong_sign_residual > 1e-3,
          {"gamma": fault_gamma, "max_component_residual": wrong_sign_residual})
    check("global-phase comparison rejects the reversed-qubit-order fault",
          wrong_order_residual > 1e-3,
          {"gamma": fault_gamma, "max_component_residual": wrong_order_residual,
           "changed_basis_energies": changed_order_energies})

    reference_norm = float(np.vdot(reference, reference).real)
    check("reference statevector remains normalized",
          abs(reference_norm - 1.0) < TOL,
          {"norm_squared": reference_norm})

    qiskit_spec = importlib.util.find_spec("qiskit")
    source = Path(__file__)
    return {
        "status": "EXECUTED_LOCAL_NUMPY_ACCEPTANCE_HARNESS_SDK_UNAVAILABLE",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "command": "python src/verify_statevector_interface.py",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dependencies": {"numpy": np.__version__},
        "data": "Existing synthetic six-variable microgrid toy; no external dataset",
        "randomness": "None",
        "quantum_hardware_used": False,
        "sdk_circuit_executed": False,
        "qiskit_available": qiskit_spec is not None,
        "basis_contract": "statevector index=sum(bits_q0_first[i]*2**i)",
        "comparison_contract": "infer one unit-modulus global phase from the largest reference amplitude, then compare every component",
        "config": {"gammas": GAMMAS, "fault_gamma": fault_gamma, "basis_states": 64,
                   "offset": str(offset), "absolute_tolerance": TOL},
        "checks": checks,
        "limitations": [
            "NumPy acceptance oracle only; Qiskit is unavailable in the execution environment",
            "No SDK circuit, transpilation, sampler, mixer, optimizer or hardware execution",
            "One deterministic synthetic input state and three nonzero angles",
            "No speedup, quantum advantage or novelty claim",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
