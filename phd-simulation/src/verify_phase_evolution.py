"""Audit diagonal cost evolution for the six-variable synthetic microgrid toy.

This is a standard-library calculation of basis-state phases, not an SDK circuit,
sampler, optimizer, or quantum-hardware run.
Run from phd-simulation: python src/verify_phase_evolution.py
"""
import cmath
import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from verify_formulation import C, D, P, coeffs


TOL = 1e-12
GAMMAS = [0.0, math.pi / 17, 0.2, 0.7]


def run():
    constant, linear, cross = coeffs(F(2))
    offset = constant + sum(linear) / 2 + sum(v for _, _, v in cross) / 4
    fields = [-v / 2 for v in linear]
    couplings = []
    for i, j, value in cross:
        fields[i] -= value / 4
        fields[j] -= value / 4
        couplings.append((i, j, value / 4))

    def oracle(bits):
        served = sum(D[i] * bits[i] for i in range(3))
        spare = bits[3] + 2 * bits[4] + 4 * bits[5]
        return sum(P[i] * (1 - bits[i]) for i in range(3)) + 2 * (served + spare - C) ** 2

    def ising(spins, include_offset=True):
        return (offset if include_offset else 0) + sum(
            h * s for h, s in zip(fields, spins)
        ) + sum(value * spins[i] * spins[j] for i, j, value in couplings)

    def direct_phase(gamma, energy):
        return cmath.exp(-1j * gamma * float(energy))

    def gate_angle_phase(gamma, spins, angle_scale=2.0, exponent_sign=-1.0):
        # RZ(theta)=exp(-i theta Z/2), and likewise for RZZ.  Thus
        # theta=2*gamma*coefficient implements exp(-i gamma coefficient Pauli).
        phase = cmath.exp(exponent_sign * 1j * gamma * float(offset))
        for h, spin in zip(fields, spins):
            theta = angle_scale * gamma * float(h)
            phase *= cmath.exp(exponent_sign * 1j * theta * spin / 2)
        for i, j, value in couplings:
            theta = angle_scale * gamma * float(value)
            phase *= cmath.exp(exponent_sign * 1j * theta * spins[i] * spins[j] / 2)
        return phase

    states = []
    for bits in product((0, 1), repeat=6):
        spins = tuple(1 - 2 * bit for bit in bits)
        states.append((bits, spins, oracle(bits), ising(spins)))

    checks = []

    def check(name, passed, detail=None):
        row = {"name": name, "passed": bool(passed)}
        if detail is not None:
            row["detail"] = detail
        checks.append(row)
        assert passed, name

    energy_mismatches = sum(reference != mapped for _, _, reference, mapped in states)
    check("all 64 mapped energies equal the independent residual oracle", energy_mismatches == 0)

    direct_errors = []
    gate_errors = []
    global_phase_errors = []
    for gamma in GAMMAS:
        common = cmath.exp(1j * gamma * float(offset))
        for _, spins, reference, mapped in states:
            oracle_phase = direct_phase(gamma, reference)
            direct_errors.append(abs(oracle_phase - direct_phase(gamma, mapped)))
            gate_errors.append(abs(oracle_phase - gate_angle_phase(gamma, spins)))
            no_offset_phase = direct_phase(gamma, ising(spins, include_offset=False))
            global_phase_errors.append(abs(no_offset_phase - common * oracle_phase))

    check("oracle and mapped phases agree for 256 state-angle pairs",
          max(direct_errors) < TOL, {"max_abs_error": max(direct_errors), "pairs": len(direct_errors)})
    check("RZ/RZZ factor-of-two convention reproduces all phases",
          max(gate_errors) < TOL, {"max_abs_error": max(gate_errors), "pairs": len(gate_errors)})
    check("dropping the offset changes only the predicted global phase",
          max(global_phase_errors) < TOL,
          {"max_abs_error": max(global_phase_errors), "pairs": len(global_phase_errors)})

    gamma_fault = 0.2
    sign_faults = 0
    half_angle_faults = 0
    for _, spins, reference, _ in states:
        expected = direct_phase(gamma_fault, reference)
        if abs(expected - cmath.exp(1j * gamma_fault * float(reference))) >= TOL:
            sign_faults += 1
        if abs(expected - gate_angle_phase(gamma_fault, spins, angle_scale=1.0)) >= TOL:
            half_angle_faults += 1
    check("deliberate exponent-sign fault is detected", sign_faults > 0,
          {"gamma": gamma_fault, "mismatching_states": sign_faults})
    check("deliberate missing factor-of-two gate-angle fault is detected", half_angle_faults > 0,
          {"gamma": gamma_fault, "mismatching_states": half_angle_faults})

    raw = [complex(i + 1, 64 - i) for i in range(64)]
    norm = math.sqrt(sum(abs(value) ** 2 for value in raw))
    initial = [value / norm for value in raw]
    evolved = [initial[i] * direct_phase(gamma_fault, states[i][2]) for i in range(64)]
    norm_drift = abs(sum(abs(value) ** 2 for value in evolved) - 1.0)
    probability_drift = max(abs(abs(evolved[i]) ** 2 - abs(initial[i]) ** 2) for i in range(64))
    changed_amplitudes = sum(abs(evolved[i] - initial[i]) >= TOL for i in range(64))
    check("diagonal cost evolution preserves statevector norm", norm_drift < TOL,
          {"absolute_norm_squared_drift": norm_drift})
    check("diagonal cost evolution preserves every basis probability", probability_drift < TOL,
          {"max_probability_drift": probability_drift})
    check("nonzero cost evolution changes phases on this fixture", changed_amplitudes > 0,
          {"gamma": gamma_fault, "changed_amplitudes": changed_amplitudes})

    source = Path(__file__)
    return {
        "status": "EXECUTED_LOCAL_STANDARD_LIBRARY_PHASE_AUDIT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "command": "python src/verify_phase_evolution.py",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "dependencies": "Python standard library",
        "data": "Existing synthetic six-variable microgrid toy; no external dataset",
        "randomness": "None",
        "quantum_hardware_used": False,
        "sdk_circuit_executed": False,
        "optimizer_executed": False,
        "conventions": {
            "cost_unitary": "U_C(gamma)=exp(-i*gamma*H_C)",
            "rz": "RZ(theta)=exp(-i*theta*Z/2)",
            "rzz": "RZZ(theta)=exp(-i*theta*ZtensorZ/2)",
            "required_rotation_angle": "theta=2*gamma*coefficient",
        },
        "config": {
            "gammas": GAMMAS,
            "fault_gamma": gamma_fault,
            "offset": str(offset),
            "basis_states": len(states),
            "state_angle_pairs": len(states) * len(GAMMAS),
        },
        "checks": checks,
        "faults": {
            "wrong_exponent_sign_mismatches": sign_faults,
            "missing_factor_two_angle_mismatches": half_angle_faults,
        },
        "limitations": [
            "One synthetic instance and four chosen gamma values",
            "No quantum SDK circuit, transpilation, sampling, mixer or optimizer",
            "Floating-point phase comparisons use absolute tolerance 1e-12",
            "No speedup, quantum advantage or novelty claim",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
