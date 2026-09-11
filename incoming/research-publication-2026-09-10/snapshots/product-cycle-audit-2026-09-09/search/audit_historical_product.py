"""Replay float64 hull diagnostics on the retained numerical product, not certification."""
from pathlib import Path
import json,sys,numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[1]

def audit():
    d=json.loads((ROOT/'inputs/product6_best.json').read_text())
    # Input uses lists of real/imaginary pairs, retained byte-for-byte.
    out={'classification':'NUMERICAL_HULL_DIAGNOSTIC_ONLY','input':'inputs/product6_best.json','factors':[]}
    omega=np.exp(2j*np.pi/3)
    for name in['a','b']:
        z=np.array([complex(*x)for x in d[name]]);p=(z[:,None]*omega**np.arange(3)).ravel();h=ConvexHull(np.c_[p.real,p.imag])
        out['factors'].append({'name':name,'points':len(p),'hull_vertices':len(h.vertices),'hull_labels':h.vertices.tolist(),'radii':abs(z).tolist()})
    return out
if __name__=='__main__':
    r=audit();p=ROOT/'reports/historical_product_factor_audit.json';p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
