"""Exact control and finite level-count regression for proof.md; not its proof."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations,product
import argparse,json,sys
from exact import (poly,add,sub,mul,square,scale,ev,divrem,gcd,roots_closed,
                   sign_at_root,X,ZERO)
ROOT=Path(__file__).resolve().parent
if sys.flags.optimize:raise RuntimeError('exact verification requires non-optimized Python')
def require(ok,message):
    if not ok:raise ValueError(message)
def canonical(d):return json.dumps(d,indent=2,sort_keys=True)+'\n'
def constant(c):return poly([c])
def norm(p):return add(square(p[0]),square(p[1]))
def delta(p,q):return sub(p[0],q[0]),sub(p[1],q[1])
def dist(p,q):return norm(delta(p,q))
def turn(p,q,r):
    a,b=delta(q,p),delta(r,p);return sub(mul(a[0],b[1]),mul(a[1],b[0]))
def data_from_control(d):
    require(len(d['upper_parameters'])==3 and all(isinstance(x,str)for x in d['upper_parameters']),'parameters must be three exact rational strings')
    require(len(d['lower_root_interval'])==2 and all(isinstance(x,str)for x in d['lower_root_interval']),'root bounds must be exact rational strings')
    ts=list(map(F,d['upper_parameters']));ts+=[-sum(ts)]
    require(len(set(ts))==4,'four formal parameters must be distinct')
    c=sum(a*b*z for a,b,z in combinations(ts,3))/2
    H=c*c+(1-sum(a*b for a,b in combinations(ts,2)))/2
    p=(constant(c),constant(c*c))
    points=[p]+[(constant(t),constant(H-t*t))for t in ts[:3]]+[(X,square(X))]
    R=ev(dist(p,points[1]),F(0))
    f=sub(dist(p,points[-1]),constant(R))
    lo,hi=map(F,d['lower_root_interval'])
    require(c>0 and R>0 and lo<hi,'invalid control parameters')
    require(roots_closed(f,lo,hi)==1,'control root not uniquely isolated')
    return ts,c,H,R,points,f,lo,hi

def check_control(d):
    ts,c,H,R,pts,f,lo,hi=data_from_control(d)
    require(H>0 and 2*c*c<H,'center is not on the lens interior arc')
    require(all(2*t*t<H for t in ts[:3]),'retained upper point outside lens')
    require(2*ts[3]*ts[3]>H,'fourth formal root must be outside lens')
    sign=lambda p:sign_at_root(p,f,lo,hi)
    require(sign(sub(constant(H),scale(square(X),2)))>0,'new lower point outside lens')
    for j in range(1,5):require(sign(sub(dist(pts[0],pts[j]),constant(R)))==0,'false rich row')
    order=d['order'];require(sorted(order)==list(range(5)),'invalid cyclic order')
    supports=[]
    for a,b in zip(order,order[1:]+order[:1]):
        for j in order:
            if j in (a,b):continue
            t=turn(pts[a],pts[b],pts[j]);require(sign(t)>0,'nonpositive supporting determinant')
            supports.append({'edge':[a,b],'vertex':j,'polynomial':list(map(str,t))})
    selector=d['invalid_selector'];require(selector in ['minimum','maximum'],'unknown selector')
    desired=1 if selector=='minimum' else -1
    require((H<F(3,2))if selector=='minimum' else (H>F(3,2)),'wrong height regime')
    for q in pts[1:]:require(sign(sub(square(q[0]),constant(c*c)))==desired,'not a UNIQUE extremal center')
    maxima=[];classes=[]
    for i in range(5):
        row=[]
        for j in range(5):
            if i==j:continue
            v=dist(pts[i],pts[j])
            found=False
            for other,labels in row:
                if sign(sub(v,other))==0:labels.append(j);found=True;break
            if not found:row.append((v,[j]))
        classes.append([labels for _,labels in row]);maxima.append(max(len(labels)for _,labels in row))
    require(maxima[0]==4 and all(v<=3 for v in maxima[1:]),'unexpected control richness')
    return dict(name=d['name'],invalid_selector=selector,c=str(c),H=str(H),squared_radius=str(R),
                formal_upper_parameters=list(map(str,ts)),lower_polynomial=list(map(str,f)),
                lower_root_interval=d['lower_root_interval'],order=order,
                max_multiplicities=maxima,distance_classes=classes,
                supporting_halfplanes=supports,support_count=len(supports),all_vertices_rich=False)

def level_polynomials(H,c,R):
    # Direct coefficient expansion, not a call to symbolic algebra.
    return (poly([c*c+c**4-R,-2*c,1-2*c*c,0,1]),
            poly([c*c+(H-c*c)**2-R,-2*c,1-2*H+2*c*c,0,1]))
def count_level(H,b,c,R,mode):
    require(H>0 and 0<=c<=b and 2*b*b<=H and R>0,'invalid lens level input')
    require(mode in ('minimum','maximum'),'unknown selector')
    require((H>=F(3,2))if mode=='minimum' else (H<=F(3,2)),'selector outside proved regime')
    A,B=level_polynomials(H,c,R)
    intervals=[(-c,c)]if mode=='maximum' else [(-b,-c),(c,b)]
    counts=[]
    for f in (A,B):
        z=sum(roots_closed(f,l,h)for l,h in intervals)
        if mode=='minimum' and c==0 and ev(f,0)==0:z-=1
        counts.append(z)
    overlap=0
    if 2*b*b==H:
        for t in (-b,b):
            if any(l<=t<=h for l,h in intervals) and ev(A,t)==0:
                require(ev(B,t)==0,'junction mismatch');overlap+=1
    total=sum(counts)-overlap
    return {'H':str(H),'b':str(b),'c':str(c),'squared_radius':str(R),'selector':mode,
            'lower_roots':counts[0],'upper_roots':counts[1],
            'common_endpoint_duplicates':overlap,'distinct_witness_count':total}

def generate_grid():
    cases=[]
    setups=[(2*b*b,b,None)for b in map(F,['1/10','1/4','1/2','3/4','6/7','7/8','1','3/2','2','3'])]
    # Test the switch height exactly using rational subarcs of its boundary.
    setups.extend((F(3,2),b,mode)for b in [F(3,4),F(5,6)]for mode in ['minimum','maximum'])
    for H,b,fixed in setups:
        mode=fixed or ('maximum'if H<=F(3,2)else'minimum')
        for fraction in map(F,['0','1/8','1/4','1/2','3/4','7/8','1']):
            c=b*fraction;ell=H-2*c*c
            radii={F(1,16),F(1,4),F(1),4*c*c,ell*ell,
                   (b-c)**2+(b*b-c*c)**2,(b+c)**2+(b*b-c*c)**2}
            radii={r*k for r,k in product(radii,[F(1,2),F(1),F(3,2)])if r>0}
            for R in sorted(radii):
                d=count_level(H,b,c,R,mode)
                require(d['distinct_witness_count']<=(2 if mode=='maximum' else 3),'regression contradicts theorem')
                cases.append(d)
    sharp=count_level(F(7907,3800),F(1019,1000),F(3,5),F(44468521,14440000),'minimum')
    require(sharp['distinct_witness_count']==3,'deep-selector equality control lost')
    cases.append(sharp)
    return cases

def run():
    controls=json.loads((ROOT/'data/controls.json').read_text())['controls']
    cc=[check_control(d)for d in controls];grid=generate_grid()
    return {'schema':'erdos97.mixed_parabolic_lens.v1','status':'passed',
            'claim':'all-size symmetric parabolic-lens theorem has a written proof in proof.md',
            'not_an_unrestricted_solution':True,'finite_regression_is_not_the_proof':True,
            'independent_external_review':False,'formalized':False,
            'controls':cc,'control_support_count':sum(c['support_count']for c in cc),
            'grid_case_count':len(grid),'maximum_grid_witness_count':max(x['distinct_witness_count']for x in grid),
            'grid':grid}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--check',action='store_true');args=ap.parse_args()
    d=run();text=canonical(d);path=ROOT/'data/verification.json'
    if args.write:path.write_text(text)
    if args.check:require(path.read_text()==text,'stored exact verification differs')
    print(canonical({k:v for k,v in d.items()if k not in ('grid','controls')}))
if __name__=='__main__':main()
