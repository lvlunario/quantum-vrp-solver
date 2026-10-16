"""R15 reference audit only: standard library, synthetic data, no angle search."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

DEMANDS = (2, 3, 4)
PRIORITIES = (3, 5, 6)
CAPACITY = 5

def decision(x):
    bits = [(x >> j) & 1 for j in range(3)]
    return sum(d*b for d,b in zip(DEMANDS,bits)), sum(w*(1-b) for w,b in zip(PRIORITIES,bits))

def run():
    root = Path(__file__).resolve().parent.parent
    checks = []
    def check(name, ok):
        checks.append(dict(name=name, passed=bool(ok)))
        if not ok:
            raise AssertionError(name)
    original = [dict(x=x, demand=decision(x)[0], loss=decision(x)[1]) for x in range(8)]
    feasible = [r for r in original if r['demand'] <= CAPACITY]
    optimal_loss = min(r['loss'] for r in feasible)
    optimal_x = [r['x'] for r in feasible if r['loss'] == optimal_loss]
    encoded = []
    for i in range(64):
        x, slack = i % 8, i // 8
        demand, loss = decision(x)
        encoded.append(dict(index=i,x=x,slack=slack,energy=loss+2*(demand+slack-CAPACITY)**2,
                            physical=demand<=CAPACITY,consistent=demand+slack==CAPACITY))
    ground = min(r['energy'] for r in encoded)
    minimizers = [r['index'] for r in encoded if r['energy']==ground]
    def metrics(weights):
        return dict(mean_energy=str(sum(weights[r['index']]*r['energy'] for r in encoded)),
                    physical_mass=str(sum(weights[r['index']] for r in encoded if r['physical'])),
                    encoded_mass=str(sum(weights[r['index']] for r in encoded if r['consistent'])),
                    optimal_load_mass=str(sum(weights[r['index']] for r in encoded if r['x'] in optimal_x)),
                    ground_mass=str(sum(weights[r['index']] for r in encoded if r['energy']==ground)))
    uniform = metrics([Fraction(1,64)]*64)
    order = sorted(range(3), key=lambda j:(-Fraction(PRIORITIES[j],DEMANDS[j]),j))
    load=0; x=0
    for j in order:
        if load+DEMANDS[j]<=CAPACITY:
            load+=DEMANDS[j]; x|=1<<j
    greedy_index=x+8*(CAPACITY-load)
    greedy=metrics([Fraction(int(i==greedy_index)) for i in range(64)])
    canonical_weights=[Fraction(0)]*64
    for r in original:
        canonical_weights[r['x']+8*max(0,CAPACITY-r['demand'])]+=Fraction(1,8)
    canonical=metrics(canonical_weights)
    check('five original feasible choices',len(feasible)==5)
    check('all original minimizers retained: x=3 loss=6',optimal_x==[3] and optimal_loss==6)
    check('all encoded minimizers retained: index=3 energy=6',minimizers==[3] and ground==6)
    check('encoded consistency implies physical safety',all(not r['consistent'] or r['physical'] for r in encoded))
    check('uniform energy is 50',uniform['mean_energy']=='50')
    check('uniform physical mass 5/8 versus encoding 5/64',uniform['physical_mass']=='5/8' and uniform['encoded_mass']=='5/64')
    check('uniform optimal load 1/8 versus ground 1/64',uniform['optimal_load_mass']=='1/8' and uniform['ground_mass']=='1/64')
    check('greedy order is 1,0,2 and reproduces optimum',order==[1,0,2] and greedy_index==3 and greedy['mean_energy']=='6')
    check('canonical-slack baseline normalized',sum(canonical_weights)==1)
    check('canonical-slack encoding differs from uniform six-bit representation',canonical['encoded_mass']=='5/8' and canonical['encoded_mass']!=uniform['encoded_mass'])
    old=json.loads((root/'results/2026-10-15-readout.json').read_text())
    check('independent enumeration agrees with all 64 prior raw rows',all(
        (a['index'],a['energy'],a['physical'],a['consistent'])==
        (b['index'],b['energy'],b['physical'],b['encoded'])
        for a,b in zip(encoded,old['raw_basis'])) and len(old['raw_basis'])==64)
    paths=['src/verify_baseline_references.py','docs/baseline-protocol-v1.md','results/2026-10-15-readout.json']
    return dict(status='EXECUTED_CLASSICAL_REFERENCE_AUDIT_NOT_QAOA_SEARCH',executed_at_utc=datetime.now(timezone.utc).isoformat(),
        command='python src/verify_baseline_references.py',python=platform.python_version(),
        source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
        data='Synthetic fixed development fixture; no external data',randomness='None; exact rational arithmetic',
        config=dict(demands=DEMANDS,priorities=PRIORITIES,capacity=CAPACITY,penalty=2),
        original_decisions=original,encoded_states=encoded,optimal_original=optimal_x,encoded_minimizers=minimizers,
        uniform_encoded=uniform,greedy=dict(order=order,index=greedy_index,metrics=greedy),
        uniform_load_canonical_slack=canonical,checks=checks,
        search_status='PLANNED/UNEXECUTED',hardware_used=False,
        limitations=['One development fixture; no holdout','No Qiskit circuit or parameter search executed today',
                     'Enumeration is a truth reference, not a budget-matched competitor','Greedy optimality here is not a general guarantee'])
if __name__=='__main__':
    print(json.dumps(run(),indent=2))

