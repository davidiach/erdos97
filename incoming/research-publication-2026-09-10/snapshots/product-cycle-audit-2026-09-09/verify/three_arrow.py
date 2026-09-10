"""Locate and verify a fixed three-arrow geometric obstruction.
Arrows are source-side matches of concentric equilateral triples. See proof note.
"""
def witnesses(rows,p):
    m=len(rows);i,k=p%m,p//m
    return [j+(k+g)%3*m for j,g in zip(rows[i][::2],rows[i][1::2])]

def find(rows):
    m=len(rows);n=3*m
    out=[]
    for B in range(m):
        targets=witnesses(rows,B)
        for A in targets:
            for Y in targets:
                if A==Y:continue
                for s in [-1,1]:
                    C=(Y+s*m)%n
                    for Z in witnesses(rows,C):
                        D=(Z-s*m)%n
                        delta=[(s*(v-A))%n for v in [B,C,D]]
                        if 0<delta[0]<delta[1]<delta[2]<m:
                            out.append({'A':A,'B':B,'C':C,'D':D,'orientation':s})
    return out

def check(rows,c):
    m=len(rows);n=3*m
    if set(c)!={'A','B','C','D','orientation'}:raise ValueError('bad keys')
    A,B,C,D,s=[c[k]for k in ['A','B','C','D','orientation']]
    if any(type(v)is not int for v in [A,B,C,D,s])or s not in [-1,1]or any(v<0 or v>=n for v in [A,B,C,D]):raise ValueError('bad labels')
    d=[s*(v-A)%n for v in [B,C,D]]
    if not 0<d[0]<d[1]<d[2]<m:raise ValueError('bad sector order')
    if A not in witnesses(rows,B)or(C-s*m)%n not in witnesses(rows,B)or(D+s*m)%n not in witnesses(rows,C):raise ValueError('missing arrow')
    return True
