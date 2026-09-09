"""Exact scalar exterior-turn necessary-inequality control.

These values are not asserted to be turning angles of a planar realization.
They certify only the stated linear inequalities. In particular no claim is
made that they match the angles in all independently realizable local stars.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from collections import defaultdict
import argparse,json
ROOT=Path(__file__).resolve().parent

def check_matrix(path,turns):
    words=Path(path).read_text().split();n=int(words[0]);scale=int(words[1]);radius=int(words[2]);vals=list(map(int,words[3:]))
    if n!=len(turns)or len(vals)!=n*n or scale<=0 or radius<=0:raise ValueError('bad matrix/turn size')
    if any(not isinstance(t,F)for t in turns)or min(turns)<=0 or max(turns)>=2 or sum(turns)!=4:raise ValueError('invalid exact positive turns or total')
    D=[vals[i*n:(i+1)*n]for i in range(n)];count=0;fibers=0;minimum=F(4);supports=set()
    for i in range(n):
        buckets=defaultdict(list)
        for j in range(n):
            if j!=i:buckets[D[i][j]].append((j-i)%n)
        for ws in buckets.values():
            if len(ws)<2:continue
            fibers+=1;ws.sort()
            for a,b in combinations(ws,2):
                # Directly check every pair, not just two strongest supports.
                forward=tuple((i+h)%n for h in range(1,b))
                reverse=tuple((i+h)%n for h in range(a+1,n))
                for support in (forward,reverse):
                    s=sum(turns[j]for j in support)
                    if s<=1:raise ValueError(f'non-strict turn inequality at center {i} offsets {a},{b}')
                    minimum=min(minimum,s);supports.add(support);count+=1
    return {'status':'passed','n':n,'repeated_distance_fibers':fibers,
      'strict_pair_turn_inequalities_checked':count,'distinct_supports':len(supports),
      'exact_total_normalized_turn':str(sum(turns)),
      'minimum_normalized_turn':str(min(turns)),
      'maximum_normalized_turn':str(max(turns)),
      'minimum_forced_support_sum':str(minimum),
      'normalization':'t_i=2*tau_i/pi; sum(t_i)=4',
      'scope':'scalar necessary inequalities only; no globally compatible Euclidean angles claimed'}

def run(certificate=None):
    cert=json.loads(Path(certificate or ROOT/'evidence/turn_values.json').read_text())
    if cert.get('schema')!='erdos97.scalar_turn_control.v1':raise ValueError('wrong turn schema')
    turns=[F(s)for s in cert['normalized_turns']]
    return {name:check_matrix(ROOT/'evidence'/file,turns)for name,file in [('strict_ptolemy_metric','grid_metric_integer_matrix.txt'),('locally_planar_star_metric','circle_star_matrix.txt')]}

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args();r=run()
    text=json.dumps(r,indent=2,sort_keys=True)+'\n';out=ROOT/'evidence/turn_report.json'
    if a.check and out.read_text()!=text:raise ValueError('saved turn report differs')
    if a.write:out.write_text(text)
    print(text,end='')
if __name__=='__main__':main()
