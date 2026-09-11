#!/usr/bin/env python3
"""Necessary angle constraints closed under selected-distance equivalence.
Includes every forced isosceles triangle, even at an unselected center.
"""
from __future__ import annotations
from itertools import combinations
from types import SimpleNamespace
import numpy as np
from scipy.sparse import csr_matrix
from scipy.optimize import linprog
from chain_angle_completion import Engine

class ClosedEngine(Engine):
    def __init__(self,n):
        super().__init__(n)
        self.last_rejection=None
    def forced_classes(self,rows):
        parent=list(range(len(self.edges)))
        def find(k):
            while k!=parent[k]:parent[k]=parent[parent[k]];k=parent[k]
            return k
        for i,W in rows.items():
            base=self.ix[tuple(sorted((i,W[0])))]
            for j in W[1:]:parent[find(self.ix[tuple(sorted((i,j)))])]=find(base)
        groups=[]
        for i in range(self.n):
            cls={}
            for j in range(self.n):
                if j!=i:cls.setdefault(find(self.ix[tuple(sorted((i,j)))]),[]).append(j)
            groups.extend((i,sorted(W))for W in cls.values()if len(W)>=2)
        return groups
    def solve(self,rows):
        groups=self.forced_classes(rows);self.last_rejection=None
        for (a,A),(b,B) in combinations(groups,2):
            if a==b:continue
            common=sorted(set(A).intersection(B))
            if len(common)>2:
                self.last_rejection={'kind':'FORCED_CIRCLE_CAP','centers':[a,b],'common':common}
                return SimpleNamespace(success=False,status=2,message='exact forced circle-cap preflight',x=None)
            if len(common)==2:
                x,y=common
                if ((x-a)%self.n<(b-a)%self.n)==((y-a)%self.n<(b-a)%self.n):
                    self.last_rejection={'kind':'FORCED_CROSSING','centers':[a,b],'common':common}
                    return SimpleNamespace(success=False,status=2,message='exact forced crossing preflight',x=None)
        eq=[self.gauge];b=[0];self.last_equation_origins=[]
        for i,W in groups:
            x,y=self.eqs(i,tuple(W));eq.extend(x);b.extend(y)
            self.last_equation_origins.extend((i,tuple(W))for _ in x)
        return linprog(self.c,A_ub=self.A,b_ub=self.b,A_eq=csr_matrix(eq),b_eq=b,bounds=[(None,None)]*len(self.c),method='highs')
