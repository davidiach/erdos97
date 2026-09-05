// Exact selected-witness relaxation search. No Euclidean realization is inferred
// from a survivor; exhaustive UNSAT is restricted finite-case review evidence.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
#ifndef SEARCH_N
#define SEARCH_N 11
#endif
constexpr int N=SEARCH_N, P=N*(N-1)/2;
static_assert(N>=5 && N<=16);
struct Row {unsigned mask=0; array<int,4>w{},sp{};array<int,6>ps{};array<unsigned,2>arcs{};};
struct State {array<int,N>choice;array<int,N>indeg{};array<int,P>pc{};int depth=0; State(){choice.fill(-1);}};
struct Stats {uint64_t visits=0,trials=0,pairdead=0,turn=0,zero=0,inverse=0,leaves=0;};
struct Search {
 int pair_id[N][N]{}; array<vector<Row>,N> rows;
 vector<array<int,4>> inequalities;
 vector<vector<vector<uint64_t>>> compat;
 int R=0,W=0; bool use_turn=true,use_k=true;uint64_t limit=0;
 bool aborted=false,stop_at_first=true;vector<array<int,N>> solutions;Stats st;
 static constexpr int HS=8192;
 array<uint64_t,HS>keys{};array<uint32_t,HS>tags{};uint32_t epoch=0;
 Search(){int q=0;for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)pair_id[a][b]=pair_id[b][a]=q++;
  for(int i=0;i<N;i++)for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)for(int d=c+1;d<N;d++){
   if(a==i||b==i||c==i||d==i)continue;Row r;r.w={a,b,c,d};int t=0;
   for(int j=0;j<4;j++){r.mask|=1u<<r.w[j];r.sp[j]=pair_id[i][r.w[j]];for(int k=j+1;k<4;k++)r.ps[t++]=pair_id[r.w[j]][r.w[k]];}
   array<int,4> off;for(int j=0;j<4;j++)off[j]=(r.w[j]-i+N)%N;sort(off.begin(),off.end());
   for(int h=1;h<off[1];h++)r.arcs[0]|=1u<<((i+h)%N);
   for(int h=off[2]+1;h<N;h++)r.arcs[1]|=1u<<((i+h)%N);
   rows[i].push_back(r);
  }
  R=(int)rows[0].size();W=(R+63)/64;
  for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)for(int d=c+1;d<N;d++){
   inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][b],pair_id[c][d]});
   inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][d],pair_id[b][c]});
  }
  compat.resize(N*R,vector<vector<uint64_t>>(N,vector<uint64_t>(W,0)));
  for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int i=0;i<R;i++)for(int j=0;j<R;j++){
   unsigned m=rows[a][i].mask&rows[b][j].mask;int count=__builtin_popcount(m);bool ok=count<2;
   if(count==2){int x=__builtin_ctz(m);m&=m-1;int y=__builtin_ctz(m);ok=cross(a,b,x,y);}
   if(ok){compat[a*R+i][b][j/64]|=1ULL<<(j%64);compat[b*R+j][a][i/64]|=1ULL<<(i%64);}
  }
 }
 bool cross(int a,int b,int c,int d)const{return a!=c&&a!=d&&b!=c&&b!=d&&(((c-a+N)%N<(b-a+N)%N)!=((d-a+N)%N<(b-a+N)%N));}
 static int root(array<int,P>&p,int x){while(p[x]!=x){p[x]=p[p[x]];x=p[x];}return x;}
 int metric(const State&s){
  array<int,P>p; iota(p.begin(),p.end(),0);
  for(int i=0;i<N;i++)if(s.choice[i]>=0){auto&r=rows[i][s.choice[i]];for(int k=1;k<4;k++){int a=root(p,r.sp[0]),b=root(p,r.sp[k]);if(a!=b)p[max(a,b)]=min(a,b);}}
  for(int i=0;i<P;i++)p[i]=root(p,i);
  if(++epoch==0){tags.fill(0);epoch=1;}
  for(auto&q:inequalities){
   array<pair<int,int>,4>v={{{p[q[0]],1},{p[q[1]],1},{p[q[2]],-1},{p[q[3]],-1}}};sort(v.begin(),v.end());
   int len=0;array<pair<int,int>,4>z{};
   for(int j=0;j<4;){int a=v[j].first,b=0;while(j<4&&v[j].first==a)b+=v[j++].second;if(b)z[len++]={a,b};}
   if(!len)return 1;
   int g=0;for(int j=0;j<len;j++)g=gcd(g,abs(z[j].second));
   uint64_t key=uint64_t(len)<<60,inv=key;
   for(int j=0;j<len;j++){int c=z[j].second/g;int code=c==-2?1:c==-1?2:c==1?3:4;key|=uint64_t((z[j].first<<3)|code)<<(10*j);inv|=uint64_t((z[j].first<<3)|(5-code))<<(10*j);}
   auto hash=[](uint64_t x){x^=x>>30;x*=0xbf58476d1ce4e5b9ULL;x^=x>>27;x*=0x94d049bb133111ebULL;x^=x>>31;return int(x&(HS-1));};
   int pos=hash(inv);while(tags[pos]==epoch){if(keys[pos]==inv)return 2;pos=(pos+1)&(HS-1);}
   pos=hash(key);while(tags[pos]==epoch&&keys[pos]!=key)pos=(pos+1)&(HS-1);tags[pos]=epoch;keys[pos]=key;
  }return 0;
 }
 // Four pairwise disjoint strict >pi/2 intervals cannot fit into total 2pi.
 bool turn_bad(const State&s)const{
  array<unsigned,2*N>arcs{};int k=0;for(int i=0;i<N;i++)if(s.choice[i]>=0)for(unsigned a:rows[i][s.choice[i]].arcs)arcs[k++]=a;
  // Every disjoint family has a cut at the start of one of its intervals.
  for(int cut=0;cut<N;cut++){
   array<int,N+1>next;next.fill(N+1);
   for(int i=0;i<k;i++){
    unsigned mask=arcs[i];unsigned rot=((mask>>cut)|(mask<<(N-cut)))&((1u<<N)-1);
    int start=__builtin_ctz(rot),end=32-__builtin_clz(rot);
    if(__builtin_popcount(rot)!=end-start)continue; // interval crosses this cut
    next[start]=min(next[start],end);
   }
   for(int p=N-1;p>=0;p--)next[p]=min(next[p],next[p+1]);
   int at=0,cnt=0;while(at<N&&next[at]<=N){at=next[at];if(++cnt==4)return true;}
  }return false;
 }
 vector<int> options(int c,const State&s)const{
  vector<uint64_t>bits(W,~0ULL);if(R%64)bits.back()=(1ULL<<(R%64))-1;
  for(int i=0;i<N;i++)if(s.choice[i]>=0)for(int w=0;w<W;w++)bits[w]&=compat[i*R+s.choice[i]][c][w];
  vector<int>out;for(int w=0;w<W;w++){uint64_t b=bits[w];while(b){int z=__builtin_ctzll(b),a=64*w+z;b&=b-1;auto&r=rows[c][a];bool ok=true;for(int v:r.w)if(s.indeg[v]>=2*(N-1)/3)ok=false;for(int p:r.ps)if(s.pc[p]>=2)ok=false;if(ok)out.push_back(a);}}
  return out;
 }
 void place(State&s,int c,int a,int delta){s.choice[c]=delta>0?a:-1;s.depth+=delta;for(int v:rows[c][a].w)s.indeg[v]+=delta;for(int p:rows[c][a].ps)s.pc[p]+=delta;}
 void dfs(State&s){
  if(aborted||(!solutions.empty()&&stop_at_first))return;if(limit&&st.visits>=limit){aborted=true;return;}++st.visits;
  if(use_turn&&turn_bad(s)){st.turn++;return;}
  if(use_k){int status=metric(s);if(status==1){st.zero++;return;}if(status==2){st.inverse++;return;}}
  if(s.depth==N){st.leaves++;solutions.push_back(s.choice);return;}
  int best=-1;vector<int>opts;
  for(int c=0;c<N;c++)if(s.choice[c]<0){auto o=options(c,s);if(best<0||o.size()<opts.size()){best=c;opts=move(o);if(opts.empty())break;}}
  if(opts.empty()){st.pairdead++;return;}
  for(int a:opts){st.trials++;place(s,best,a,1);dfs(s);place(s,best,a,-1);if(aborted||(!solutions.empty()&&stop_at_first))return;}
 }
 void print(int slice,double secs)const{
  cout<<"{\"n\":"<<N<<",\"row_count\":"<<R<<",\"slice\":"<<slice<<",\"complete\":"<<(aborted?"false":"true")<<",\"survivor\":"<<(solutions.empty()?"false":"true")<<",\"nodes\":"<<st.visits<<",\"trials\":"<<st.trials<<",\"pair_dead\":"<<st.pairdead<<",\"turn_prunes\":"<<st.turn<<",\"zero_prunes\":"<<st.zero<<",\"inverse_prunes\":"<<st.inverse<<",\"seconds\":"<<secs;
  if(!solutions.empty()){cout<<",\"witnesses\":[";for(int i=0;i<N;i++){if(i)cout<<',';cout<<'[';auto&r=rows[i][solutions[0][i]];for(int j=0;j<4;j++){if(j)cout<<',';cout<<r.w[j];}cout<<']';}cout<<']';}cout<<"}\n";
 }
};
int main(int argc,char**argv){try{int slice=-1;bool t=true,k=true;uint64_t lim=0;for(int i=1;i<argc;i++){string a=argv[i];if(a=="--no-turn")t=false;else if(a=="--no-kalmanson")k=false;else if(a=="--limit"&&i+1<argc)lim=stoull(argv[++i]);else slice=stoi(a);}auto begin=chrono::steady_clock::now();Search search;search.use_turn=t;search.use_k=k;search.limit=lim;State s;if(slice>=0){if(slice>=search.R)throw runtime_error("slice out of range");search.place(s,0,slice,1);}search.dfs(s);search.print(slice,chrono::duration<double>(chrono::steady_clock::now()-begin).count());return search.aborted?3:0;}catch(const exception&e){cerr<<e.what()<<'\n';return 2;}}
