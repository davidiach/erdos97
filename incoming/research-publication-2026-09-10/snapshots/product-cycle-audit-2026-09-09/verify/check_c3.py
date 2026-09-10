#!/usr/bin/env python3
"""Exact geometric-premise checker. No optimization or discovery imports.
Reconstruct lengths on physical chords by BFS and rotate each chord explicitly.
The chord-angle convention is inherited from the pinned repository proof.
"""
from collections import defaultdict
from itertools import combinations
from math import gcd
from pathlib import Path
import argparse
import json
import sys
PI=(-1,-1)

def require(b,msg):
    if not b:raise ValueError(msg)

class Geometry:
    def __init__(self,rows):
        require(isinstance(rows,list) and len(rows)>=3,'bad orbit list')
        m=len(rows);n=3*m;self.m=m;self.n=n;self.rows=rows
        for i,row in enumerate(rows):
            require(isinstance(row,list) and len(row)%2==0,'bad row')
            require(len(set(row[::2]))==len(row[::2]),'duplicate supplier')
            for j,g in zip(row[::2],row[1::2]):
                require(type(j)is int and 0<=j<m and j!=i,'bad target')
                require(type(g)is int and 0<=g<3,'bad gain')
                require(i not in rows[j][::2],'reciprocal own-side arrows')
        pairs=list(combinations(range(n),2));graph=defaultdict(set)
        def edge(a,b):return tuple(sorted((a,b)))
        def join(a,b):graph[a].add(b);graph[b].add(a)
        for a,b in pairs:join((a,b),edge((a+m)%n,(b+m)%n))
        for p in range(n):
            i,k=p%m,p//m
            selected=[i+(k+1)%3*m,i+(k+2)%3*m]
            selected += [j+(k+g)%3*m for j,g in zip(rows[i][::2],rows[i][1::2])]
            spokes=[edge(p,j)for j in selected]
            for a,b in zip(spokes,spokes[1:]):join(a,b)
        length={}
        for pair in pairs:
            if pair in length:continue
            stack=[pair];length[pair]=pair
            while stack:
                for q in graph[stack.pop()]:
                    if q not in length:length[q]=pair;stack.append(q)
        self.length=length;self.owners={length[i,i+m]:i for i in range(m)}
        require(len(self.owners)==m,'own-length alias')
        self.less=set()
        for i,row in enumerate(rows):
            for j,g in zip(row[::2],row[1::2]):
                d=(j+g*m-i)%n
                self.less.add((j,i)if m<d<2*m else(i,j))
        self.direction={}
        for a,b in pairs:
            orbit=[edge((a+k*m)%n,(b+k*m)%n)for k in range(3)]
            rep=min(orbit);delta=a+b-sum(rep)
            require(delta%m==0,'bad offset')
            self.direction[a,b]=(rep,delta//m)
        self.variables=sorted({r for r,_ in self.direction.values()})+[PI]

    def angle(self,tri,corner):
        a,b,c=tri
        return ({(a,c):1,(a,b):-1} if corner==0 else
                {(a,b):1,(b,c):-1,PI:3} if corner==1 else {(b,c):1,(a,c):-1})
    @staticmethod
    def add(a,b,wa=1,wb=-1):
        out=defaultdict(int)
        for p,x in a.items():out[p]+=wa*x
        for p,x in b.items():out[p]+=wb*x
        return dict(out)
    def reduced(self,raw,equality):
        out=defaultdict(int)
        for p,x in raw.items():
            if p==PI:out[PI]+=x
            else:
                rep,offset=self.direction[p];out[rep]+=x;out[PI]+=offset*x
        out={p:x for p,x in out.items()if x}
        factor=0
        for x in out.values():factor=gcd(factor,x)
        if not factor:return {}
        if equality and next(out[k] for k in self.variables if k in out)<0:factor=-factor
        return {p:x//factor for p,x in out.items()}
    def premise(self,label,equality):
        require(isinstance(label,list) and label,'missing premise')
        kind=label[0]
        if kind=='pi_positive':
            require(label==['pi_positive'] and not equality,'pi premise')
            raw={PI:1}
        elif kind=='right_angle':
            require(len(label)==4 and equality,'right premise')
            _,i,j,g=label
            require(all(type(v)is int for v in [i,j,g]) and 0<=i<self.m,'right source')
            require((j,g)in list(zip(self.rows[i][::2],self.rows[i][1::2])),'unforced right angle')
            tri=tuple(sorted((i,j+(g+1)%3*self.m,j+(g+2)%3*self.m)))
            raw=self.add(self.angle(tri,tri.index(i)),{PI:3},2,-1)
        else:
            require(kind in ('angle_positive','equal_sides','angle_order'),'unknown premise')
            require(len(label)==(5 if kind=='angle_positive'else 6),'bad label length')
            tri=tuple(label[1:4]);a,b,c=tri
            require(all(type(x)is int for x in tri)and 0<=a<b<c<self.n,'bad triangle')
            at=label[4];require(type(at)is int and at in range(3),'bad angle corner')
            if kind=='angle_positive':
                require(not equality,'positive equality');raw=self.angle(tri,at)
            else:
                to=label[5];require(type(to)is int and to in range(3) and at!=to,'bad other corner')
                opposite=[self.length[b,c],self.length[a,c],self.length[a,b]]
                if kind=='equal_sides':
                    require(equality and opposite[at]==opposite[to],'unforced isosceles equality')
                    raw=self.add(self.angle(tri,at),self.angle(tri,to))
                else:
                    require(not equality,'order equality')
                    require((self.owners.get(opposite[at]),self.owners.get(opposite[to]))in self.less,'unforced angle order')
                    raw=self.add(self.angle(tri,to),self.angle(tri,at))
        return self.reduced(raw,equality)
    def certificate(self,cert):
        require(type(cert)is dict and set(cert)=={'strict','equal'},'bad certificate keys')
        require(isinstance(cert['strict'],list)and cert['strict'],'empty strict sum')
        total=defaultdict(int)
        for kind in ['strict','equal']:
            require(isinstance(cert[kind],list),'bad term list')
            for term in cert[kind]:
                require(isinstance(term,list)and len(term)==2,'bad term')
                label,weight=term
                require(type(weight)is int and (weight>0 if kind=='strict'else weight!=0),'bad integer multiplier')
                v=self.premise(label,kind=='equal');require(v,'zero premise')
                for p,x in v.items():total[p]+=weight*x
        require(not any(total.values()),'certificate does not cancel')
        return True

def main():
    require(not sys.flags.optimize,'assertions must stay enabled')
    ap=argparse.ArgumentParser();ap.add_argument('path');ap.add_argument('--output');args=ap.parse_args()
    data=json.loads(Path(args.path).read_text());cases=data['cases'];seen=set();terms=0
    for c in cases:
        key=json.dumps(c['rows']);require(key not in seen,'duplicate system');seen.add(key)
        Geometry(c['rows']).certificate(c['certificate']);terms+=sum(map(len,c['certificate'].values()))
    report={'status':'PASS_EXACT_FIXED_SYSTEM_CERTIFICATES','cases':len(cases),'integer_terms':terms,'geometric_scope':'strictly convex concentric equilateral triples in specified repeated-sector order, with the listed source-side arrows','exhaustive_nine_orbit_claim':False,'external_review':False}
    text=json.dumps(report,indent=2)+'\n'
    if args.output:Path(args.output).write_text(text)
    print(text)
if __name__=='__main__':main()
