"""Exact synthetic formulation audit; standard library only; no quantum execution."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from fractions import Fraction as F
from itertools import product
from pathlib import Path

D = (2, 3, 4)
P = (3, 5, 6)
C = 5
X = list(product((0, 1), repeat=3))

def demand(x):
    return sum(d*v for d,v in zip(D,x))

def unserved(x):
    return sum(p*(1-v) for p,v in zip(P,x))

def direct(x, lam):
    return unserved(x) + lam * max(0, demand(x)-C)**2

def coeffs(lam, weights=(1,2,4)):
    a = D + weights
    linear = [lam*(v*v-2*C*v) - (P[i] if i < 3 else 0) for i,v in enumerate(a)]
    cross = [(i,j,2*lam*a[i]*a[j]) for i in range(len(a)) for j in range(i+1,len(a))]
    return sum(P)+lam*C*C, linear, cross

def polynomial(z, lam, weights=(1,2,4), omit_cross=False):
    c,h,q = coeffs(lam,weights)
    return c + sum(v*b for v,b in zip(h,z)) + (0 if omit_cross else sum(v*z[i]*z[j] for i,j,v in q))

def run():
    checks=[]
    def check(name, value):
        checks.append({'name':name,'passed':bool(value)})
        if not value:
            raise AssertionError(name)
    # Explicit independently hand-enumerated fixture, lexicographic x order.
    expected=[([0,0,0],0,14),([0,0,1],4,8),([0,1,0],3,9),([0,1,1],7,3),
              ([1,0,0],2,11),([1,0,1],6,5),([1,1,0],5,6),([1,1,1],9,0)]
    table=[{'x':list(x),'demand':demand(x),'unserved':unserved(x),'feasible':demand(x)<=C} for x in X]
    check('manual eight-row oracle',[(r['x'],r['demand'],r['unserved']) for r in table]==expected)
    optimum=min(unserved(x) for x in X if demand(x)<=C)
    ratios=[{'x':list(x),'ratio':str(F(optimum-unserved(x),(demand(x)-C)**2))} for x in X if demand(x)>C]
    threshold=max(F(r['ratio']) for r in ratios)
    check('strict exact threshold is one',threshold==1)
    sweep=[]
    for lam in [F(1,10),F(3,4),F(1),F(101,100),F(2),F(7)]:
        best=min(direct(x,lam) for x in X)
        winners=[list(x) for x in X if direct(x,lam)==best]
        sweep.append({'lambda':str(lam),'minimum':str(best),'minimizers':winners,'all_feasible':all(demand(x)<=C for x in winners)})
    check('lambda one retains infeasible tie',sweep[2]['minimizers']==[[1,0,1],[1,1,0]])
    check('lambda above one has only feasible minimizers',all(r['all_feasible'] for r in sweep[3:]))
    lam=F(2)
    raw=[]
    for z in product((0,1),repeat=6):
        x=z[:3]; s=sum(w*b for w,b in zip((1,2,4),z[3:]))
        residual=demand(x)+s-C
        e=unserved(x)+lam*residual**2
        raw.append({'z':list(z),'slack':s,'residual':residual,'energy':int(e),'polynomial':int(polynomial(z,lam))})
    check('all 64 expanded energies equal residual energies',all(r['energy']==r['polynomial'] for r in raw))
    reduced=[]
    for x in X:
        best=min(r['energy'] for r in raw if r['z'][:3]==list(x))
        reduced.append({'x':list(x),'min_over_slack':best,'direct_penalty':int(direct(x,lam))})
    check('all eight reduced energies equal original hinge penalty',all(r['min_over_slack']==r['direct_penalty'] for r in reduced))
    best=min(r['energy'] for r in raw)
    winners=[r['z'] for r in raw if r['energy']==best]
    check('six-bit unique ground state serves first two loads',winners==[[1,1,0,0,0,0]])
    # Deliberate faults are experiments, not claims of accidental historical bugs.
    short=[]
    for x in X:
        val=min(polynomial(x+y,lam,(1,2)) for y in product((0,1),repeat=2))
        if val!=direct(x,lam): short.append({'x':list(x),'faulty_minimum':int(val),'correct_minimum':int(direct(x,lam))})
    cross=[r['z'] for r in raw if polynomial(tuple(r['z']),lam,omit_cross=True)!=r['energy']]
    check('insufficient slack range is detected',len(short)>0)
    check('omitted cross terms are detected',len(cross)>0)
    constant,linear,quadratic=coeffs(lam)
    return {'status':'EXECUTED_LOCAL_EXACT_ENUMERATION','executed_at_utc':datetime.now(timezone.utc).isoformat(),
        'python':platform.python_version(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'command':'python src/verify_formulation.py','dependencies':'Python standard library',
        'data':'Synthetic fixed toy; no external dataset','randomness':'None; exhaustive deterministic enumeration',
        'hardware_used':False,'config':{'demands':D,'priorities':P,'capacity':C,'slack_weights':[1,2,4],'qubo_lambda':2},
        'table':table,'infeasible_threshold_ratios':ratios,'strict_threshold':str(threshold),'penalty_sweep':sweep,
        'qubo':{'constant':int(constant),'linear':list(map(int,linear)),'upper_triangular_cross':[[i,j,int(v)] for i,j,v in quadratic]},
        'raw_64_states':raw,'reduced_8_states':reduced,'ground_states':winners,
        'fault_injection':{'insufficient_slack':short,'omitted_cross_terms_mismatches':len(cross),'first_cross_counterexample':cross[0]},
        'checks':checks,'limitations':['One synthetic instance','No circuits, hardware or QAOA rerun','No general fault-detection rate or quantum advantage','Ground-state equivalence does not imply equal sampling dynamics']}

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
