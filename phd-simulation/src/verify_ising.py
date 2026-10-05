"""Exact QUBO/Ising and decoding audit on the existing synthetic toy.

No SDK, quantum circuit, sampling or hardware execution is performed.
Run from phd-simulation: python src/verify_ising.py
"""
import hashlib
import json
import platform
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from verify_formulation import coeffs, D, P, C


def run():
    constant, linear, cross = coeffs(F(2))
    offset = constant + sum(linear) / 2 + sum(v for _, _, v in cross) / 4
    fields = [-v / 2 for v in linear]
    couplings = []
    for i, j, v in cross:
        fields[i] -= v / 4
        fields[j] -= v / 4
        couplings.append((i, j, v / 4))

    def energy(spins, field_sign=1, include_offset=True):
        return (offset if include_offset else 0) + field_sign * sum(
            a*s for a, s in zip(fields, spins)) + sum(
            v*spins[i]*spins[j] for i, j, v in couplings)

    # Independent residual oracle: does not use mapped or expanded coefficients.
    def oracle(bits):
        served = sum(D[i]*bits[i] for i in range(3))
        spare = bits[3] + 2*bits[4] + 4*bits[5]
        return sum(P[i]*(1-bits[i]) for i in range(3)) + 2*(served+spare-C)**2

    rows = []
    for bits in product((0, 1), repeat=6):
        spins = tuple(1-2*b for b in bits)
        index = sum(b << i for i, b in enumerate(bits))
        displayed = format(index, '06b')
        decoded = tuple(int(b) for b in reversed(displayed))
        wrong_decode = tuple(int(b) for b in displayed)
        rows.append({'bits_q0_first':bits, 'spins':spins, 'index':index,
                     'display_q5_to_q0':displayed, 'decoded':decoded,
                     'oracle_energy':oracle(bits), 'ising_energy':str(energy(spins)),
                     'wrong_field_sign_energy':str(energy(spins, -1)),
                     'no_offset_energy':str(energy(spins, include_offset=False)),
                     'wrong_decode_energy':oracle(wrong_decode)})
    minimum = min(r['oracle_energy'] for r in rows)
    winners = [r for r in rows if r['oracle_energy']==minimum]
    checks = []
    def check(name, passed):
        checks.append({'name':name, 'passed':bool(passed)})
        assert passed, name
    check('all 64 Ising energies equal independent residual oracle',
          all(F(r['ising_energy'])==r['oracle_energy'] for r in rows))
    check('all 64 displayed strings round-trip to logical bits',
          all(r['decoded']==r['bits_q0_first'] for r in rows))
    check('indices cover each integer 0 through 63 exactly once',
          sorted(r['index'] for r in rows)==list(range(64)))
    check('unique ground state matches hand fixture',
          [(r['bits_q0_first'], r['index'], r['display_q5_to_q0'], r['oracle_energy'])
           for r in winners]==[((1,1,0,0,0,0),3,'000011',6)])
    sign_faults = [r for r in rows if F(r['wrong_field_sign_energy'])!=r['oracle_energy']]
    decode_faults = [r for r in rows if r['wrong_decode_energy']!=r['oracle_energy']]
    check('deliberate field sign fault is detected', len(sign_faults)>0)
    check('deliberate display reversal fault is detected', len(decode_faults)>0)
    check('missing offset creates same exact error on every basis state',
          all(F(r['no_offset_energy'])-r['oracle_energy']==-offset for r in rows))
    check('omitting offset preserves all minimizers',
          [r['bits_q0_first'] for r in rows if F(r['no_offset_energy'])==min(
              F(v['no_offset_energy']) for v in rows)]==[r['bits_q0_first'] for r in winners])
    source = Path(__file__)
    return {'status':'EXECUTED_LOCAL_EXACT_ENUMERATION',
            'executed_at_utc':datetime.now(timezone.utc).isoformat(),
            'python':platform.python_version(), 'command':'python src/verify_ising.py',
            'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in (source, source.with_name('verify_formulation.py'))},
            'dependencies':'Python standard library',
            'data':'Existing synthetic toy; no external dataset', 'randomness':'None',
            'quantum_hardware_used':False, 'circuit_executed':False,
            'config':{'demands':D,'priorities':P,'capacity':C,'penalty':2,
                      'slack_weights':[1,2,4],'spin_convention':'s_i=1-2*b_i',
                      'logical_order':['x0','x1','x2','slack1','slack2','slack4']},
            'ising':{'offset':str(offset),'fields':list(map(str,fields)),
                     'couplings':[[i,j,str(v)] for i,j,v in couplings]},
            'ground_states':winners, 'raw_64_states':rows, 'checks':checks,
            'faults':{'wrong_field_sign_mismatches':len(sign_faults),
                      'wrong_decode_mismatches':len(decode_faults),
                      'first_decode_counterexample':decode_faults[0]},
            'limitations':['One synthetic instance', 'No QAOA or quantum SDK execution',
                           'No benchmark speedup or novelty claim',
                           'Display test assumes one six-bit register with q_i mapped to c_i']}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
