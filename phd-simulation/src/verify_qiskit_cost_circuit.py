"""Verify a six-qubit Qiskit cost circuit against the residual-energy oracle.

Run in the locked SDK environment from phd-simulation:
    python src/verify_qiskit_cost_circuit.py

This is local exact statevector simulation, not sampling or hardware execution.
"""
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

    def circuit(gamma, include_offset, exponent_sign=-1, reverse_qubits=False,
                omit_first_coupling=False):
        qc = QuantumCircuit(6)
        sign = -exponent_sign  # RZ(theta)=exp(-i*theta*Z/2).
        if include_offset:
            qc.global_phase = exponent_sign * gamma * float(offset)
        for qubit, field in enumerate(fields):
            target = 5 - qubit if reverse_qubits else qubit
            qc.rz(sign * 2 * gamma * float(field), target)
        active_couplings = couplings[1:] if omit_first_coupling else couplings
        for left, right, value in active_couplings:
            if reverse_qubits:
                left, right = 5 - left, 5 - right
            qc.rzz(sign * 2 * gamma * float(value), left, right)
        return qc

    bits = [bits_for_index(index) for index in range(64)]
    energies = np.asarray([oracle(row) for row in bits], dtype=float)
    raw = np.asarray([complex(index + 1, 64 - index) for index in range(64)])
    initial = raw / np.linalg.norm(raw)

    checks = []

    def check(name, passed, detail=None):
        row = {"name": name, "passed": bool(passed)}
        if detail is not None:
            row["detail"] = detail
        checks.append(row)
        assert passed, name

    check("Qiskit basis index 3 uses logical q0-first bits 110000",
          bits[3] == (1, 1, 0, 0, 0, 0), {"bits_q0_first": bits[3]})

    strict_errors = []
    offset_free_equiv = []
    offset_free_strict_distances = []
    operation_counts = []
    for gamma in GAMMAS:
        reference = Statevector(initial * np.exp(-1j * gamma * energies))
        full_circuit = circuit(gamma, include_offset=True)
        no_offset_circuit = circuit(gamma, include_offset=False)
        full = Statevector(initial).evolve(full_circuit)
        no_offset = Statevector(initial).evolve(no_offset_circuit)
        strict_errors.append(float(np.max(np.abs(reference.data - full.data))))
        offset_free_equiv.append(reference.equiv(no_offset, rtol=0, atol=TOL))
        offset_free_strict_distances.append(
            float(np.max(np.abs(reference.data - no_offset.data))))
        operation_counts.append(dict(full_circuit.count_ops()))

    check("SDK circuit with global phase matches the oracle strictly",
          max(strict_errors) < TOL,
          {"max_component_error": max(strict_errors), "angles": len(GAMMAS)})
    check("SDK circuit without the offset is equivalent up to global phase",
          all(offset_free_equiv), {"equivalent_at_all_angles": offset_free_equiv})
    check("naive strict comparison rejects every offset-free circuit",
          min(offset_free_strict_distances) > 1e-3,
          {"component_distances": offset_free_strict_distances})
    check("each complete cost circuit contains six RZ and fifteen RZZ gates",
          all(counts == {"rzz": 15, "rz": 6} for counts in operation_counts),
          {"operation_counts": operation_counts[0]})

    gamma_fault = 0.2
    reference = Statevector(initial * np.exp(-1j * gamma_fault * energies))
    wrong_sign = Statevector(initial).evolve(
        circuit(gamma_fault, include_offset=True, exponent_sign=1))
    wrong_order = Statevector(initial).evolve(
        circuit(gamma_fault, include_offset=True, reverse_qubits=True))
    missing_term = Statevector(initial).evolve(
        circuit(gamma_fault, include_offset=True, omit_first_coupling=True))
    check("Statevector.equiv rejects the exponent-sign circuit fault",
          not reference.equiv(wrong_sign, rtol=0, atol=TOL))
    check("Statevector.equiv rejects the reversed-qubit-order circuit fault",
          not reference.equiv(wrong_order, rtol=0, atol=TOL))
    check("Statevector.equiv rejects an omitted RZZ interaction",
          not reference.equiv(missing_term, rtol=0, atol=TOL),
          {"omitted_coupling": [couplings[0][0], couplings[0][1], str(couplings[0][2])]})

    norm_squared = float(np.vdot(reference.data, reference.data).real)
    check("SDK output statevector remains normalized",
          abs(norm_squared - 1.0) < TOL, {"norm_squared": norm_squared})

    source = Path(__file__)
    lock = source.parent.parent / "requirements-sdk.txt"
    return {
        "status": "EXECUTED_LOCAL_QISKIT_EXACT_STATEVECTOR_AUDIT",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "qiskit": qiskit.__version__,
        "numpy": np.__version__,
        "command": "python src/verify_qiskit_cost_circuit.py",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "environment_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
        "data": "Existing synthetic six-variable microgrid toy; no external dataset",
        "randomness": "None",
        "quantum_hardware_used": False,
        "sampling_used": False,
        "optimizer_executed": False,
        "simulation": "Qiskit exact Statevector.evolve on a six-qubit QuantumCircuit",
        "basis_contract": "statevector index=sum(bits_q0_first[i]*2**i)",
        "config": {"gammas": GAMMAS, "fault_gamma": gamma_fault,
                   "basis_states": 64, "offset": str(offset),
                   "rz_gates": 6, "rzz_gates": 15, "absolute_tolerance": TOL},
        "checks": checks,
        "limitations": [
            "One synthetic instance and one deterministic input state",
            "Exact local statevector simulation only; no shots, noise, transpilation or hardware",
            "No mixer, parameter optimization, speedup, quantum advantage or novelty claim",
            "Pinned environment is specific to this Python 3.12 Linux run",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
