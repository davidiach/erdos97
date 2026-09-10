"""Create a maintained search adaptation without editing the preceding snapshot."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'inputs/search9.cpp').read_text()
s=s.replace('#include <iostream>','#include <iostream>\n#include <fstream>\n#include <chrono>\n#include <string>\n#include <stdexcept>')
s=s.replace('bool abort=false;','bool abort=false,first=true;\n ofstream output;')
a=''' static bool three_core(int i,const Row&a,int j,const Row&b){
  for(int o=0;o<2;++o){int A=a.t[o]+a.g[o]*M,Y=a.t[1-o]+a.g[1-o]*M;
   for(int s:{-1,1}){int C=(Y+s*M+N)%N;if(C%M!=j)continue;int phase=C/M;
    for(int v=0;v<2;++v){int Z=b.t[v]+((phase+b.g[v])%3)*M,D=(Z-s*M+N)%N;
     auto pos=[&](int x){return (s*(x-A)%N+N)%N;};int Bp=pos(i),Cp=pos(C),Dp=pos(D);
     if(0<Bp&&Bp<Cp&&Cp<Dp&&Dp<M)return true;
    }
   }
  }return false;
 }
'''
s=s.replace(' bool pair_ok(',a+' bool pair_ok(')
s=s.replace('  return true;\n }\n S(){','  if(three_core(i,a,j,b)||three_core(j,b,i,a))return false;\n  return true;\n }\n S(){')
s=s.replace('if(abort||leaves)','if(abort||(first&&leaves))')
s=s.replace('++leaves;cout<<','++leaves;output<<').replace('if(i)cout<<','if(i)output<<').replace(';cout<<',';output<<').replace('}cout<<','}output<<')
s=s[:s.index('int main(){')]+'''int main(int argc,char**argv){
 try{
  auto start=chrono::steady_clock::now();S s;State st;int slice=-1;string path="nine_survivors.jsonl";
  for(int i=1;i<argc;++i){string a=argv[i];auto value=[&](){if(++i>=argc)throw runtime_error("missing argument");return string(argv[i]);};
   if(a=="--all")s.first=false;
   else if(a=="--limit")s.limit=stoull(value());
   else if(a=="--slice")slice=stoi(value());
   else if(a=="--output")path=value();else throw runtime_error("unknown argument");
  }
  s.output.open(path);if(!s.output)throw runtime_error("output unavailable");
  if(slice>=0){if(slice>=int(s.rows[0].size()))throw runtime_error("bad slice");st.pick[0]=slice;st.depth=1;}
  s.dfs(st);s.output.close();
  cout<<"{\\"slice\\":"<<slice<<",\\"limit\\":"<<s.limit<<",\\"nodes\\":"<<s.visits<<",\\"radius_prunes\\":"<<s.rad<<",\\"shortcut_prunes\\":"<<s.sh<<",\\"metric_prunes\\":"<<s.met<<",\\"pair_dead\\":"<<s.pairdead<<",\\"leaves\\":"<<s.leaves<<",\\"aborted\\":"<<(s.abort?"true":"false")<<",\\"exhausted\\":"<<(!s.abort&&(!s.first||!s.leaves)?"true":"false")<<",\\"termination\\":\\""<<(s.abort?"node_limit":s.first&&s.leaves?"survivor_found":"exhausted")<<"\\",\\"seconds\\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"}\\n";
  return s.abort?3:0;
 }catch(const exception&e){cerr<<e.what()<<"\\n";return 2;}
}
'''
(ROOT/'search/nine_with_three_arrow.cpp').write_text(s)
