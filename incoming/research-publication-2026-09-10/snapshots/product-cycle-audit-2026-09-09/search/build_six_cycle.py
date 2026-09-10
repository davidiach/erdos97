"""An exact same-upper-half-plane six-cycle; deliberately nonconvex control."""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'verify'))
from quartic_field import K,S,MOD,INITIAL,cmul,cdiv,rotate

def build():
    v=((S-2)/2,(-5*S*S+6*S-2)/(6*(S-2)))
    zeta=(K(1)/2,K(1)/2)
    u=cdiv(zeta,cmul(v,v))
    z=[(K(1),K(0))]
    for m in [u,v,v,u,v]:z.append(cmul(z[-1],m))
    p=[]
    for t in z:
        for _ in range(3):p.append(t);t=rotate(t)
    order=sorted([3*j+k for j in [1,4]for k in range(3)],key=lambda i:math.atan2(math.sqrt(3)*p[i][1].approximate(),p[i][0].approximate()))
    return {'kind':'exact_upper_six_cycle_nonconvex_control','coordinate_convention':'(x,y) denotes Cartesian (x,sqrt(3)*y), coefficients in Q[s]',
      'minimal_polynomial_ascending':[str(c)for c in MOD],'isolating_interval':[str(t)for t in INITIAL],
      'coordinates':[[x.dump(),y.dump()]for x,y in p],
      'orbit_representatives':[[x.dump(),y.dump()]for x,y in z],
      'multipliers':[[x.dump(),y.dump()]for x,y in [u,v,v,u,v,v]],
      'hull_order':order,'interior_labels':[i for i in range(18)if i not in order],
      'monodromy':'omega','all_rich_claim':False,'strictly_convex_claim':False}
if __name__=='__main__':
    d=build();p=ROOT/'candidate_counterexamples/upper_six_cycle_exact_nonconvex_18.json';p.write_text(json.dumps(d,indent=2)+'\n');print(p)
