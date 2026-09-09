"""Constructive selector for exact rational samples of the normalized lens.

Usage: python select_good.py sample.json
Input: {"H":"2", "points":[["0","0"],["1/2","1/4"],["0","2"]]}
The mathematical theorem also allows arbitrary real coordinates; this helper
intentionally accepts exact rational input only.
"""
from fractions import Fraction
from collections import Counter
from typing import Sequence
import argparse,json

def rational(value: object)->Fraction:
    if isinstance(value,(float,bool))or not isinstance(value,(int,str,Fraction)):
        raise TypeError('Use exact integers or rational strings, not floats')
    return Fraction(value)

def select_good_vertex(height: object, points: Sequence[Sequence[object]])->dict:
    H=rational(height)
    if H<=0:raise ValueError('H must be positive')
    if not points:raise ValueError('The point set must be nonempty')
    if any(len(p)!=2 for p in points):raise ValueError('Every point needs two coordinates')
    P=[(rational(p[0]),rational(p[1]))for p in points]
    if len(set(P))!=len(P):raise ValueError('Points must be distinct')
    for x,y in P:
        if x*x>H/2 or y not in (x*x,H-x*x):raise ValueError('Point is not on the specified lens boundary')
    mode='maximum'if H<=Fraction(3,2)else'minimum'
    i=(max if mode=='maximum'else min)(range(len(P)),key=lambda k:abs(P[k][0]))
    c=P[i];fibers=Counter((p[0]-c[0])**2+(p[1]-c[1])**2 for j,p in enumerate(P)if j!=i)
    maximum=max(fibers.values(),default=0);bound=2 if mode=='maximum'else 3
    if maximum>bound:raise ArithmeticError('Exact sample contradicts the proved selector bound')
    return dict(selected_index=i,selected_point=list(map(str,c)),selector=mode,
                maximum_multiplicity=maximum,proved_bound=bound,
                squared_distance_multiplicities={str(r):fibers[r]for r in sorted(fibers)})

def main()->None:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input_json');a=p.parse_args()
    with open(a.input_json,encoding='utf-8')as f:d=json.load(f)
    print(json.dumps(select_good_vertex(d['H'],d['points']),indent=2))
if __name__=='__main__':main()
