#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <fstream>
#include <chrono>
#include <string>
#include <stdexcept>
#include <numeric>
#include <set>
#include <vector>
using namespace std;
constexpr int M=9,N=27,K=M+3*M*(M-1)/2;
struct Row{array<int,2> t{},g{},cl{};array<uint32_t,3> mask{};uint32_t targets=0;array<uint32_t,M> less{};};
struct State{array<int,M> pick;int depth=0;State(){pick.fill(-1);}};
struct S{
 int pid[N][N]{};array<vector<Row>,M> rows; vector<array<int,4>> ineq;
 array<array<vector<vector<uint64_t>>,M>,M> comp;
 uint64_t visits=0,rad=0,sh=0,met=0,pairdead=0,phasedead=0,leaves=0,limit=25000000;
 bool abort=false,first=true;
 ofstream output;
 static bool cross(int a,int b,int c,int d){if(a==b||a==c||a==d||b==c||b==d||c==d)return false;if(a>b)swap(a,b);return (a<c&&c<b)!=(a<d&&d<b);}
 static bool three_core(int i,const Row&a,int j,const Row&b){
  for(int o=0;o<2;++o){int A=a.t[o]+a.g[o]*M,Y=a.t[1-o]+a.g[1-o]*M;
   for(int s:{-1,1}){int C=(Y+s*M+N)%N;if(C%M!=j)continue;int phase=C/M;
    for(int v=0;v<2;++v){int Z=b.t[v]+((phase+b.g[v])%3)*M,D=(Z-s*M+N)%N;
     auto pos=[&](int x){return (s*(x-A)%N+N)%N;};int Bp=pos(i),Cp=pos(C),Dp=pos(D);
     if(0<Bp&&Bp<Cp&&Cp<Dp&&Dp<M)return true;
    }
   }
  }return false;
 }
 bool pair_ok(int i,const Row&a,int j,const Row&b)const{
  if((a.targets&(1u<<j))&&(b.targets&(1u<<i)))return false;
  for(int p=0;p<3;++p){auto co=a.mask[0]&b.mask[p];int n=__builtin_popcount(co);if(n>2)return false;if(n==2){int c=__builtin_ctz(co);co&=co-1;int d=__builtin_ctz(co);if(!cross(i,p*M+j,c,d))return false;}}
  if(three_core(i,a,j,b)||three_core(j,b,i,a))return false;
  return true;
 }
 S(){
  int labels[M][M]{};int nx=M;for(int i=0;i<M;++i)for(int j=i+1;j<M;++j){labels[i][j]=nx;nx+=3;}
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b){int i=a%M,j=b%M,p=a/M,q=b/M;int cl=i==j?i:(i<j?labels[i][j]+(q-p+3)%3:labels[j][i]+(p-q+3)%3);pid[a][b]=pid[b][a]=cl;}
  set<array<int,4>> U;
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b)for(int c=b+1;c<N;++c)for(int d=c+1;d<N;++d){int x=pid[a][c],y=pid[b][d];if(x>y)swap(x,y);array<int,2> z1{pid[a][b],pid[c][d]},z2{pid[a][d],pid[b][c]};for(auto z:{z1,z2}){if(z[0]>z[1])swap(z[0],z[1]);U.insert({x,y,z[0],z[1]});}}
  ineq.assign(U.begin(),U.end());
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)for(int k=j+1;k<M;++k){if(j==i||k==i)continue;for(int g=0;g<3;++g)for(int h=0;h<3;++h){
   if(!cross(((g+1)%3)*M+j,((g+2)%3)*M+j,((h+1)%3)*M+k,((h+2)%3)*M+k))continue;
   Row r;r.t={j,k};r.g={g,h};r.targets=(1u<<j)|(1u<<k);bool ok=true;
   for(int v=0;v<2;++v){int t=r.t[v],gain=r.g[v];bool down=gain==(t>i?1:2);if((i==0&&!down)||(t==0&&down)){ok=false;break;}if(down)r.less[t]|=1u<<i;else r.less[i]|=1u<<t;r.cl[v]=pid[i][gain*M+t];}
   if(!ok)continue;
   for(int p=0;p<3;++p){r.mask[p]=(1u<<(((p+1)%3)*M+i))|(1u<<(((p+2)%3)*M+i));for(int v=0;v<2;++v)r.mask[p]|=1u<<(((p+r.g[v])%3)*M+r.t[v]);}
   // Supplier-arc radial lifting: one row, with every intervening orbit.
   for(int o=0;o<2;++o){int A=r.t[o]+r.g[o]*M,Y=r.t[1-o]+r.g[1-o]*M;
    for(int sign:{-1,1}){int C=(Y+sign*M+N)%N;
     auto pos=[&](int x){return (sign*(x-A)%N+N)%N;};
     if(0<pos(i)&&pos(i)<pos(C)&&pos(C)<M){
      r.less[C%M]|=1u<<(A%M);
      for(int D=0;D<N;++D)if(pos(C)<pos(D)&&pos(D)<M)r.less[C%M]|=1u<<(D%M);
     }
    }
   }
   rows[i].push_back(r);
  }}
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)if(i!=j){comp[i][j].assign(rows[i].size(),vector<uint64_t>((rows[j].size()+63)/64));for(int a=0;a<(int)rows[i].size();++a)for(int b=0;b<(int)rows[j].size();++b)if(pair_ok(i,rows[i][a],j,rows[j][b]))comp[i][j][a][b/64]|=1ull<<(b%64);}
  cerr<<"rows0="<<rows[0].size()<<" ineq="<<ineq.size()<<"\n";
 }

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

 bool radial(const State&s,array<uint32_t,M>&R)const{for(int i=1;i<M;++i)R[i]|=1u;for(int i=0;i<M;++i)if(s.pick[i]>=0){auto&r=rows[i][s.pick[i]];for(int v=0;v<M;++v)R[v]|=r.less[v];}for(int k=0;k<M;++k)for(int i=0;i<M;++i)if(R[i]&(1u<<k))R[i]|=R[k];for(int i=0;i<M;++i)if(R[i]&(1u<<i))return false;return true;}
 bool shortcut(const State&s,const array<uint32_t,M>&R)const{array<uint32_t,M> up{},lng{},adj{};for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int j:rows[i][s.pick[i]].t){adj[i]|=1u<<j;adj[j]|=1u<<i;}for(int i=0;i<M;++i)up[i]=adj[i]&R[i];for(int k=0;k<M;++k)for(int i=0;i<M;++i)if(up[i]&(1u<<k)){lng[i]|=up[k];up[i]|=up[k];}for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int j:rows[i][s.pick[i]].t)if(lng[j]&(1u<<i))return false;return true;}
 bool metric(const State&s,const array<uint32_t,M>&R)const{
  array<int,K> cls; iota(cls.begin(),cls.end(),0);for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int cl:rows[i][s.pick[i]].cl)cls[cl]=i;
  array<vector<int>,K> A;for(int i=0;i<M;++i)for(int j=0;j<M;++j)if(R[i]&(1u<<j))A[i].push_back(j);
  for(auto q:ineq){int a=cls[q[0]],b=cls[q[1]],c=cls[q[2]],d=cls[q[3]];if(a==c){if(b==d)return false;A[d].push_back(b);}else if(a==d){if(b==c)return false;A[c].push_back(b);}else if(b==c)A[d].push_back(a);else if(b==d)A[c].push_back(a);else if(a<M&&b<M&&c<M&&d<M){auto le=[&](int x,int y){return x==y||(R[x]&(1u<<y));};if((le(a,c)&&le(b,d))||(le(a,d)&&le(b,c)))return false;}}
  array<unsigned char,K> st{};auto cyc=[&](auto&&self,int u)->bool{if(st[u]==1)return true;if(st[u]==2)return false;st[u]=1;for(int v:A[u])if(self(self,v))return true;st[u]=2;return false;};for(int i=0;i<K;++i)if(cyc(cyc,i))return false;return true;
 }
 vector<int> opts(int c,const State&s)const{int Rn=rows[c].size(),W=(Rn+63)/64;vector<uint64_t>b(W,~0ull);if(Rn%64)b.back()=(1ull<<(Rn%64))-1;for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int w=0;w<W;++w)b[w]&=comp[i][c][s.pick[i]][w];vector<int>o;for(int w=0;w<W;++w){auto x=b[w];while(x){int bit=__builtin_ctzll(x);x&=x-1;o.push_back(64*w+bit);}}return o;}
 void dfs(State&s){if(abort||(first&&leaves))return;if(++visits>limit){abort=true;return;}array<uint32_t,M>R{};if(!radial(s,R)){++rad;return;}if(!shortcut(s,R)){++sh;return;}if(!phase(s)){++phasedead;return;}if(!metric(s,R)){++met;return;}if(s.depth==M){
    array<uint32_t,N> sel{}; array<array<array<int,2>,2>,N> rr{};
    for(int p=0;p<N;++p){int i=p%M,k=p/M; sel[p]|=(1u<<(i+((k+1)%3)*M))|(1u<<(i+((k+2)%3)*M)); auto &row=rows[i][s.pick[i]]; for(int v=0;v<2;++v){int j=row.t[v],g=row.g[v]; sel[p]|=1u<<(j+((k+g)%3)*M); rr[p][v]={j+((k+g+1)%3)*M,j+((k+g+2)%3)*M};}}
    bool contain=false;
    for(int c=0;c<N&&!contain;++c){uint32_t ws=sel[c]; for(int p=0;p<N&&!contain;++p)if(ws&(1u<<p)){for(int b=0;b<N&&!contain;++b)if(b!=p&&(ws&(1u<<b))){int A=(c-p+N)%N,B=(b-p+N)%N;int lo=min(A,B),hi=max(A,B);for(int v=0;v<2;++v){int x=(rr[p][v][0]-p+N)%N,y=(rr[p][v][1]-p+N)%N;if(x>y)swap(x,y);if(0<lo&&lo<=x&&x<y&&y<=hi&&hi<N){contain=true;break;}}}}}
    if(contain){++met;return;}
    ++leaves;output<<"[";for(int i=0;i<M;++i){auto&r=rows[i][s.pick[i]];if(i)output<<",";output<<"["<<r.t[0]<<","<<r.g[0]<<","<<r.t[1]<<","<<r.g[1]<<"]";}output<<"]\n";return;}int best=-1;vector<int>O;for(int c=0;c<M;++c)if(s.pick[c]<0){auto q=opts(c,s);if(best<0||q.size()<O.size()){best=c;O=move(q);if(O.empty())break;}}if(O.empty()){++pairdead;return;}for(int x:O){s.pick[best]=x;++s.depth;dfs(s);--s.depth;s.pick[best]=-1;if(abort||(first&&leaves))return;}}
};
int main(int argc,char**argv){
 try{
  auto start=chrono::steady_clock::now();S s;State st;int slice=-1;string path="nine_survivors.jsonl",phase_batch;
  for(int i=1;i<argc;++i){string a=argv[i];auto value=[&](){if(++i>=argc)throw runtime_error("missing argument");return string(argv[i]);};
   if(a=="--phase-batch")phase_batch=value();
   else if(a=="--all")s.first=false;
   else if(a=="--limit")s.limit=stoull(value());
   else if(a=="--slice")slice=stoi(value());
   else if(a=="--output")path=value();else throw runtime_error("unknown argument");
  }

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
  s.output.open(path);if(!s.output)throw runtime_error("output unavailable");
  if(slice>=0){if(slice>=int(s.rows[0].size()))throw runtime_error("bad slice");st.pick[0]=slice;st.depth=1;}
  s.dfs(st);s.output.close();
  cout<<"{\"slice\":"<<slice<<",\"limit\":"<<s.limit<<",\"nodes\":"<<s.visits<<",\"radius_prunes\":"<<s.rad<<",\"shortcut_prunes\":"<<s.sh<<",\"metric_prunes\":"<<s.met<<",\"phase_prunes\":"<<s.phasedead<<",\"pair_dead\":"<<s.pairdead<<",\"leaves\":"<<s.leaves<<",\"aborted\":"<<(s.abort?"true":"false")<<",\"exhausted\":"<<(!s.abort&&(!s.first||!s.leaves)?"true":"false")<<",\"termination\":\""<<(s.abort?"node_limit":s.first&&s.leaves?"survivor_found":"exhausted")<<"\",\"seconds\":"<<chrono::duration<double>(chrono::steady_clock::now()-start).count()<<"}\n";
  return s.abort?3:0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 2;}
}
