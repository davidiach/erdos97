"""Integer phase certificates from gain-aligned four-arrow diamonds.
Geometric justification is written in proof_attempts/diamond_phase.md.
No optimizer, coordinate residual, or assumed product parametrization is used.
"""
from collections import defaultdict
from itertools import combinations

def require(ok,message):
    if not ok:raise ValueError(message)

def arrow_gain(rows,i,j):
    require(type(i)is int and type(j)is int and 0<=i<len(rows)and 0<=j<len(rows),'bad orbit label')
    pairs=list(zip(rows[i][::2],rows[i][1::2]));hits=[g for t,g in pairs if t==j]
    require(len(hits)==1,'missing or duplicate diamond arrow')
    require(type(hits[0])is int and 0<=hits[0]<3,'bad rotation gain')
    return hits[0]

def relation(rows,i,j,k,l):
    require(len({i,j,k,l})==4,'diamond needs four distinct orbits')
    a,b,c,d=(arrow_gain(rows,i,j),arrow_gain(rows,i,k),arrow_gain(rows,j,l),arrow_gain(rows,k,l))
    require((a+c-b-d)%3==0,'unmatched total gains')
    g=(b-c)%3;sigma=(0,1,-1)[g]
    v=defaultdict(int)
    for x,s in [(i,1),(l,1),(j,-1),(k,-1)]:v[x]+=s
    v['L']-=sigma
    return {x:s for x,s in v.items()if s}

def diamonds(rows):
    out=[]
    for i,row in enumerate(rows):
        for j,k in combinations(row[::2],2):
            for l in set(rows[j][::2])&set(rows[k][::2]):
                if len({i,j,k,l})<4:continue
                try:v=relation(rows,i,j,k,l)
                except ValueError:continue
                out.append({'labels':[i,j,k,l],'coefficients':[[str(x),s]for x,s in v.items()]})
    return out

def check(rows,certificate):
    require(set(certificate)=={'strict','equal'},'bad phase certificate keys')
    require(certificate['strict'],'no strict contribution');total=defaultdict(int)
    for label,w in certificate['strict']:
        require(type(w)is int and w>0,'strict multiplier must be positive integer')
        require(len(label)==3,'bad phase order label');kind,i,j=label
        require(type(i)is int and type(j)is int and 0<=i<j<len(rows),'unforced sector order')
        if kind=='phase_gap':v={j:1,i:-1}
        elif kind=='sector_span':v={'L':1,i:1,j:-1}
        else:raise ValueError('unknown strict phase premise')
        for x,s in v.items():total[x]+=s*w
    for label,w in certificate['equal']:
        require(type(w)is int and w!=0,'equality multiplier must be nonzero integer')
        require(len(label)==5 and label[0]=='diamond','bad diamond premise')
        v=relation(rows,*label[1:])
        for x,s in v.items():total[x]+=s*w
    require(not any(total.values()),'phase certificate does not cancel')
    return True

TWO_DIAMOND_CERTIFICATE={
 'strict':[[['phase_gap',1,3],1],[['sector_span',0,8],1]],
 'equal':[[['diamond',0,1,2,6],-1],[['diamond',2,6,8,3],-1]]}
