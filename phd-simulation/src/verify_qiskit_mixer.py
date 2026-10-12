"""Audit a single ideal QAOA mixer layer on the synthetic six-qubit toy.

Run from ``phd-simulation`` in the pinned SDK environment:
    python src/verify_qiskit_mixer.py --output results/2026-10-12-qiskit-mixer.json

This uses local exact statevector evolution. It runs no optimizer, sampler,
noise model, transpiler, cloud service, or quantum hardware.
"""
import argparse
import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from verify_formulation import C, D, P, coeffs


TOL = 1e-12
ANGLE_PAIRS = [(0.2, 0.31), (math.pi / 17, 0.63), (0.7, 0.19)]


def ising_terms():
    constant, linear, cross = coeffs(F(2))
    offset = constant + sum(linear) / 2 + sum(value for _, _, value in cross) / 4
    fields = [-value / 2 for value in linear]
    couplings = []
    for i, j, value in cross:
        fields[i] -= value / 4
        fields[j] -= value / 4
        couplings.append((i, j, value / 4))
    return offset, fields, couplings


def bits_for_index(index):
    return tuple((index >> qubit) & 1 for qubit in range(6))


def energy(bits):
    served = sum(D[i] * bits[i] for i in range(3))
    slack = bits[3] + 2 * bits[4] + 4 * bits[5]
    return sum(P[i] * (1 - bits[i]) for i in range(3)) + 2 * (served + slack - C) ** 2


def apply_independent_mixer(state, beta):
    """Apply product_j exp(-i beta X_j) by explicit amplitude pairing."""
    mixed = np.asarray(state, dtype=complex).copy()
    cosine, sine = math.cos(beta), math.sin(beta)
    for qubit in range(6):
        stride = 1 << qubit
        updated = mixed.copy()
        for base in range(0, 64, 2 * stride):
            for offset in range(stride):
                zero = base + offset
                one = zero + stride
                updated[zero] = cosine * mixed[zero] - 1j * sine * mixed[one]
                updated[one] = -1j * sine * mixed[zero] + cosine * mixed[one]
        mixed = updated
    return mixed


def qaoa_circuit(gamma, beta, mixer_scale=2.0, mixer_sign=1.0, reverse_layers=False):
    offset, fields, couplings = ising_terms()
    qc = QuantumCircuit(6)
    qc.h(range(6))

    def add_cost():
        qc.global_phase += -gamma * float(offset)
        for qubit, field in enumerate(fields):
            qc.rz(2 * gamma * float(field), qubit)
        for left, right, value in couplings:
            qc.rzz(2 * gamma * float(value), left, right)

    def add_mixer():
        for qubit in range(6):
            qc.rx(mixer_sign * mixer_scale * beta, qubit)

    if reverse_layers:
        add_mixer()
        add_cost()
    else:
        add_cost()
        add_mixer()
    return qc


def independent_state(gamma, beta):
    energies = np.asarray([energy(bits_for_index(i)) for i in range(64)], dtype=float)
    uniform = np.ones(64, dtype=complex) / 8.0
    cost_state = uniform * np.exp(-1j * gamma * energies)
    return apply_independent_mixer(cost_state, beta)


def run():
    energies = np.asarray([energy(bits_for_index(i)) for i in range(64)], dtype=float)
    checks = []

    def check(name, passed, detail=None):
        row = {"name": name, "passed": bool(passed)}
        if detail is not None:
            row["detail"] = detail
        checks.append(row)
        assert passed, name

    check(
        "basis index 3 retains logical q0-first bits 110000",
        bits_for_index(3) == (1, 1, 0, 0, 0, 0),
        {"bits_q0_first": bits_for_index(3)},
    )

    strict_errors = []
    norm_errors = []
    expected_energies = []
    operation_counts = []
    for gamma, beta in ANGLE_PAIRS:
        sdk = Statevector.from_instruction(qaoa_circuit(gamma, beta))
        oracle = independent_state(gamma, beta)
        strict_errors.append(float(np.max(np.abs(sdk.data - oracle))))
        norm_errors.append(abs(float(np.vdot(sdk.data, sdk.data).real) - 1.0))
        expected_energies.append(float(np.dot(np.abs(sdk.data) ** 2, energies)))
        operation_counts.append(dict(qaoa_circuit(gamma, beta).count_ops()))

    check(
        "Qiskit p=1 states match the independent mixer oracle strictly",
        max(strict_errors) < TOL,
        {"max_component_error": max(strict_errors), "angle_pairs": len(ANGLE_PAIRS)},
    )
    check(
        "all p=1 statevectors remain normalized",
        max(norm_errors) < TOL,
        {"max_norm_squared_error": max(norm_errors)},
    )
    expected_counts = {"rzz": 15, "h": 6, "rz": 6, "rx": 6}
    check(
        "each p=1 circuit has the expected H, cost, and mixer gate counts",
        all(counts == expected_counts for counts in operation_counts),
        {"operation_counts": operation_counts[0]},
    )

    gamma, beta = ANGLE_PAIRS[0]
    cost_only_oracle = Statevector(np.ones(64, dtype=complex) / 8.0 * np.exp(-1j * gamma * energies))
    beta_zero = Statevector.from_instruction(qaoa_circuit(gamma, 0.0))
    check(
        "beta zero makes the mixer an identity",
        np.max(np.abs(cost_only_oracle.data - beta_zero.data)) < TOL,
    )

    gamma_zero = Statevector.from_instruction(qaoa_circuit(0.0, beta))
    uniform_probabilities = np.full(64, 1 / 64)
    check(
        "gamma zero leaves all measurement probabilities uniform",
        np.max(np.abs(gamma_zero.probabilities() - uniform_probabilities)) < TOL,
        {"max_probability_error": float(np.max(np.abs(gamma_zero.probabilities() - uniform_probabilities)))},
    )

    reference = Statevector(independent_state(gamma, beta))
    half_angle = Statevector.from_instruction(qaoa_circuit(gamma, beta, mixer_scale=1.0))
    wrong_sign = Statevector.from_instruction(qaoa_circuit(gamma, beta, mixer_sign=-1.0))
    wrong_order = Statevector.from_instruction(qaoa_circuit(gamma, beta, reverse_layers=True))
    check("Statevector.equiv rejects RX(beta) missing the factor of two", not reference.equiv(half_angle, rtol=0, atol=TOL))
    check("Statevector.equiv rejects the reversed mixer sign", not reference.equiv(wrong_sign, rtol=0, atol=TOL))
    check("Statevector.equiv rejects mixer-before-cost layer order", not reference.equiv(wrong_order, rtol=0, atol=TOL))

    cost_probabilities = cost_only_oracle.probabilities()
    mixed_probabilities = Statevector.from_instruction(qaoa_circuit(gamma, beta)).probabilities()
    redistribution = float(np.max(np.abs(mixed_probabilities - cost_probabilities)))
    check(
        "a nonzero mixer redistributes probabilities on the phase-rich fixture",
        redistribution > 1e-6,
        {"max_probability_change": redistribution},
    )

    source = Path(__file__)
    lock = source.parent.parent / "requirements-sdk.txt"
    return {
        "status": "EXECUTED_LOCAL_QISKIT_EXACT_STATEVECTOR_MIXER_AUDIT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "qiskit": qiskit.__version__,
        "numpy": np.__version__,
        "command": "python src/verify_qiskit_mixer.py --output results/2026-10-12-qiskit-mixer.json",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "environment_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "data": "Existing synthetic six-variable microgrid toy; no external dataset",
        "randomness": "None",
        "quantum_hardware_used": False,
        "sampling_used": False,
        "optimizer_executed": False,
        "transpiler_executed": False,
        "simulation": "Qiskit exact Statevector.from_instruction for a six-qubit p=1 circuit",
        "objective_convention": "E is minimized; cost phase is exp(-i*gamma*E)",
        "basis_contract": "statevector index=sum(bits_q0_first[i]*2**i)",
        "config": {
            "angle_pairs": ANGLE_PAIRS,
            "basis_states": 64,
            "mixer_gate": "RX(2*beta)",
            "absolute_tolerance": TOL,
        },
        "expected_energies_reported_for_reproduction_not_optimization": expected_energies,
        "checks": checks,
        "limitations": [
            "One synthetic instance and three predetermined angle pairs",
            "Exact local statevector simulation only; no shots, noise, transpilation or hardware",
            "No parameter search, classical comparison, speedup, quantum advantage or novelty claim",
            "Selected injected faults do not estimate a general mutation-detection rate",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
