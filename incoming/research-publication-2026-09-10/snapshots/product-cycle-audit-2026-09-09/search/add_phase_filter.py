"""Add exact one/two-diamond phase obstructions to the retained C++ search.
Only a necessary-condition filter; a finite guard is never an exclusion proof.
"""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'search/nine_with_supplier_arc.cpp'
s=src.read_text()
s=s.replace('pairdead=0,leaves=0,limit=', 'pairdead=0,phasedead=0,leaves=0,limit=')
func=r'''
 // Exact phase-gap filter. Every gap (including the closing gap) is positive.
 // A gain-aligned diamond gives an integer equality on these gaps. If one
 // row or a two-row integer combination is nonzero and one-signed, reject.
 bool phase(const State&s)const {
  vector<array<int,M>> eq;
  auto gain=[&](int i,int j)->int {
   if(s.pick[i]<0)return -1;
   const auto&r=rows[i][s.pick[i]];
   for(int v=0;v<2;++v)if(r.t[v]==j)return r.g[v];
   return -1;
  };
  auto one_signed=[](const array<int,M>&v)->bool {
   bool pos=false,neg=false;
   for(int x:v){pos|=x>0;neg|=x<0;}
   return pos!=neg;
  };
  for(int i=0;i<M;++i)if(s.pick[i]>=0){
   const auto&r=rows[i][s.pick[i]];int j=r.t[0],k=r.t[1];
   if(s.pick[j]<0||s.pick[k]<0)continue;
   const auto&t=rows[j][s.pick[j]];
   for(int h=0;h<2;++h){int l=t.t[h];
    if(l==i||l==j||l==k)continue;
    int d=gain(k,l);if(d<0)continue;
    int a=r.g[0],b=r.g[1],c=t.g[h];
    if((a+c-b-d+6)%3)continue;
    int g=(b-c+3)%3,sigma=(g==2?-1:g);
    array<int,M> v{};
    for(int q=0;q<M;++q)v[q]=(q<i)+(q<l)-(q<j)-(q<k)-sigma;
    if(one_signed(v))return false;
    if(find(eq.begin(),eq.end(),v)==eq.end())eq.push_back(v);
   }
  }
  for(int i=0;i<int(eq.size());++i)for(int j=0;j<i;++j){
   for(int h=0;h<M;++h){
    int a=eq[j][h],b=-eq[i][h];
    if(!a&&!b)continue;
    array<int,M>v{};
    for(int q=0;q<M;++q)v[q]=a*eq[i][q]+b*eq[j][q];
    if(one_signed(v))return false;
   }
  }
  return true;
 }
'''
s=s.replace(' bool radial(',func+'\n bool radial(',1)
s=s.replace('if(!shortcut(s,R)){++sh;return;}if(!metric(s,R))','if(!shortcut(s,R)){++sh;return;}if(!phase(s)){++phasedead;return;}if(!metric(s,R))')
s=s.replace('string path="nine_survivors.jsonl";', 'string path="nine_survivors.jsonl",phase_batch;')
s=s.replace('if(a=="--all")', 'if(a=="--phase-batch")phase_batch=value();\n   else if(a=="--all")')
s=s.replace('  s.output.open(path);',r'''
  if(!phase_batch.empty()){
   ifstream f(phase_batch);if(!f)throw runtime_error("phase batch unavailable");
   int count;f>>count;if(!f||count<0)throw runtime_error("bad phase batch count");
   for(int c=0;c<count;++c){State q;
    for(int i=0;i<M;++i){Row r;f>>r.t[0]>>r.g[0]>>r.t[1]>>r.g[1];
     if(!f||r.t[0]<0||r.t[0]>=M||r.t[1]<0||r.t[1]>=M||r.t[0]==r.t[1]||r.t[0]==i||r.t[1]==i||r.g[0]<0||r.g[0]>2||r.g[1]<0||r.g[1]>2)throw runtime_error("bad phase batch row");
     s.rows[i].push_back(r);q.pick[i]=int(s.rows[i].size())-1;
    }
    cout<<(s.phase(q)?1:0)<<"\n";
   }
   return 0;
  }
  s.output.open(path);''')
s=s.replace('<<",\\\"pair_dead\\\":"<<s.pairdead', '<<",\\\"phase_prunes\\\":"<<s.phasedead<<",\\\"pair_dead\\\":"<<s.pairdead')
# The JSON reporting source contains C++ escaped quotes; assert insertion.
if 'phase_prunes' not in s:
    needle='<<s.met<<",\\\"pair_dead'
    raise RuntimeError('phase report insertion failed: '+needle)
out=ROOT/'search/nine_with_phase.cpp';out.write_text(s)
report={'input':str(src.relative_to(ROOT)),'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':str(out.relative_to(ROOT)),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'one/two-diamond necessary phase filter; no new exhaustive theorem'}
(ROOT/'reports/phase_filter_build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
