// Experimental exact angular-first own-side search; not a proof claim by itself.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <limits>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#ifndef ORBIT_COUNT
#define ORBIT_COUNT 8
#endif
constexpr int M=ORBIT_COUNT,N=3*M,K=M+3*M*(M-1)/2;
static_assert(M>=3 && M<=8);
struct Row {std::array<int,2> t{},g{},cl{};std::array<uint32_t,3> mask{};uint32_t targets=0;std::array<uint32_t,M> less{};};
struct State {std::array<int,M> pick;int depth=0;State(){pick.fill(-1);}};
struct Search {
 int pid[N][N]{};std::array<std::vector<Row>,M> rows;
 std::vector<std::array<int,4>> ineq;
 std::array<std::array<std::vector<std::vector<uint64_t>>,M>,M> comp;
 uint64_t visits=0,radialdead=0,shortdead=0,metricdead=0,pairdead=0,leaves=0,limit=0;
 bool aborted=false,first=true,metric_on=true,shortcut_on=true;
 std::ofstream solutions;
 static bool cross(int a,int b,int c,int d){if(a==b||a==c||a==d||b==c||b==d||c==d)return false;if(a>b)std::swap(a,b);return (a<c&&c<b)!=(a<d&&d<b);}
 bool pair_ok(int i,const Row&a,int j,const Row&b)const {
  if((a.targets&(1u<<j)) && (b.targets&(1u<<i)))return false;
  for(int phase=0;phase<3;++phase){
   auto common=a.mask[0]&b.mask[phase];int size=__builtin_popcount(common);
   if(size>2)return false;
   if(size==2){int c=__builtin_ctz(common);common&=common-1;int d=__builtin_ctz(common);if(!cross(i,phase*M+j,c,d))return false;}
  }return true;
 }
 Search(){
  int labels[M][M]{};int next=M;
  for(int i=0;i<M;++i)for(int j=i+1;j<M;++j){labels[i][j]=next;next+=3;}
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b){int i=a%M,j=b%M,p=a/M,q=b/M;int cl=i==j?i:(i<j?labels[i][j]+(q-p+3)%3:labels[j][i]+(p-q+3)%3);pid[a][b]=pid[b][a]=cl;}
  std::set<std::array<int,4>> unique;
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b)for(int c=b+1;c<N;++c)for(int d=c+1;d<N;++d){
   int x=pid[a][c],y=pid[b][d];if(x>y)std::swap(x,y);
   for(auto z: {std::array<int,2>{pid[a][b],pid[c][d]},std::array<int,2>{pid[a][d],pid[b][c]}}){if(z[0]>z[1])std::swap(z[0],z[1]);unique.insert({x,y,z[0],z[1]});}
  }ineq.assign(unique.begin(),unique.end());
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)for(int k=j+1;k<M;++k){
   if(j==i||k==i)continue;
   for(int g=0;g<3;++g)for(int h=0;h<3;++h){
    if(!cross(((g+1)%3)*M+j,((g+2)%3)*M+j,((h+1)%3)*M+k,((h+2)%3)*M+k))continue;
    Row r;r.t={j,k};r.g={g,h};r.targets=(1u<<j)|(1u<<k);bool valid=true;
    for(int v=0;v<2;++v){int t=r.t[v],gain=r.g[v];bool down=gain==(t>i?1:2);
     if((i==0&&!down)||(t==0&&down)){valid=false;break;}
     if(down)r.less[t]|=1u<<i;else r.less[i]|=1u<<t;
     r.cl[v]=pid[i][gain*M+t];
    }if(!valid)continue;
    for(int p=0;p<3;++p){r.mask[p]=(1u<<(((p+1)%3)*M+i))|(1u<<(((p+2)%3)*M+i));for(int v=0;v<2;++v)r.mask[p]|=1u<<(((p+r.g[v])%3)*M+r.t[v]);}
    rows[i].push_back(r);
   }
  }
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)if(i!=j){comp[i][j].assign(rows[i].size(),std::vector<uint64_t>((rows[j].size()+63)/64));for(int a=0;a<int(rows[i].size());++a)for(int b=0;b<int(rows[j].size());++b)if(pair_ok(i,rows[i][a],j,rows[j][b]))comp[i][j][a][b/64]|=1ull<<(b%64);}
 }
 bool radial(const State&s,std::array<uint32_t,M>&reach)const{
  for(int i=1;i<M;++i)reach[i]|=1u; // r_i <= r_0, maximal norm at angular label zero.
  for(int i=0;i<M;++i)if(s.pick[i]>=0){auto&r=rows[i][s.pick[i]];for(int v=0;v<M;++v)reach[v]|=r.less[v];}
  for(int k=0;k<M;++k)for(int i=0;i<M;++i)if(reach[i]&(1u<<k))reach[i]|=reach[k];
  for(int i=0;i<M;++i)if(reach[i]&(1u<<i))return false;
  return true;
 }
 bool shortcut(const State&s,const std::array<uint32_t,M>&radius)const{
  std::array<uint32_t,M> up{},longer{},adj{};
  for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int j:rows[i][s.pick[i]].t){adj[i]|=1u<<j;adj[j]|=1u<<i;}
  for(int i=0;i<M;++i)up[i]=adj[i]&radius[i];
  // Transitive closure in arbitrary label order, plus track length >= 2.
  for(int k=0;k<M;++k)for(int i=0;i<M;++i)if(up[i]&(1u<<k)){longer[i]|=up[k];up[i]|=up[k];}
  for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int j:rows[i][s.pick[i]].t)if(longer[j]&(1u<<i))return false;
  return true;
 }
 bool metric(const State&s,const std::array<uint32_t,M>&radius)const{
  std::array<int,K> cls;std::iota(cls.begin(),cls.end(),0);
  for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int cl:rows[i][s.pick[i]].cl)cls[cl]=i;
  std::array<std::vector<int>,K> adj;
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)if(radius[i]&(1u<<j))adj[i].push_back(j);
  for(auto&q:ineq){int a=cls[q[0]],b=cls[q[1]],c=cls[q[2]],d=cls[q[3]];
   if(a==c){if(b==d)return false;adj[d].push_back(b);}
   else if(a==d){if(b==c)return false;adj[c].push_back(b);}
   else if(b==c)adj[d].push_back(a);
   else if(b==d)adj[c].push_back(a);
   else if(a<M&&b<M&&c<M&&d<M){auto le=[&](int x,int y){return x==y||(radius[x]&(1u<<y));};if((le(a,c)&&le(b,d))||(le(a,d)&&le(b,c)))return false;}
  }
  std::array<unsigned char,K> state{};
  auto cycle=[&](auto&& self,int u)->bool{if(state[u]==1)return true;if(state[u]==2)return false;state[u]=1;for(int v:adj[u])if(self(self,v))return true;state[u]=2;return false;};
  for(int i=0;i<K;++i)if(cycle(cycle,i))return false;
  return true;
 }
 std::vector<int> options(int c,const State&s)const{
  int R=rows[c].size(),W=(R+63)/64;std::vector<uint64_t>bits(W,~0ull);if(R%64)bits.back()=(1ull<<(R%64))-1;
  for(int i=0;i<M;++i)if(s.pick[i]>=0)for(int w=0;w<W;++w)bits[w]&=comp[i][c][s.pick[i]][w];
  std::vector<int>out;for(int w=0;w<W;++w){auto b=bits[w];while(b){int bit=__builtin_ctzll(b);b&=b-1;out.push_back(64*w+bit);}}return out;
 }
 void dfs(State&s){
  if(aborted||(first&&leaves))return;
  if(limit&&visits>=limit){aborted=true;return;}
  ++visits;
  std::array<uint32_t,M>reach{};if(!radial(s,reach)){++radialdead;return;}
  if(shortcut_on&&!shortcut(s,reach)){++shortdead;return;}
  if(metric_on&&!metric(s,reach)){++metricdead;return;}
  if(s.depth==M){++leaves;solutions<<"[";for(int i=0;i<M;++i){auto&r=rows[i][s.pick[i]];if(i)solutions<<",";solutions<<"["<<r.t[0]<<","<<r.g[0]<<","<<r.t[1]<<","<<r.g[1]<<"]";}solutions<<"]\n";return;}
  int best=-1;std::vector<int>opts;
  for(int c=0;c<M;++c)if(s.pick[c]<0){auto o=options(c,s);if(best<0||o.size()<opts.size()){best=c;opts=std::move(o);if(opts.empty())break;}}
  if(opts.empty()){++pairdead;return;}
  for(int a:opts){s.pick[best]=a;++s.depth;dfs(s);--s.depth;s.pick[best]=-1;if(aborted||(first&&leaves))return;}
 }
};
uint64_t natural_number(const std::string& text) {
    if (text.empty() || text.find_first_not_of("0123456789") != std::string::npos)
        throw std::runtime_error("expected a nonnegative decimal integer");
    return std::stoull(text);
}
int slice_number(const std::string& text) {
    auto value=natural_number(text);
    if (value>uint64_t(std::numeric_limits<int>::max()))
        throw std::runtime_error("slice exceeds supported integer range");
    return int(value);
}
int main(int argc,char**argv){try{auto start=std::chrono::steady_clock::now();Search solver;std::string out="angular_survivors.jsonl";int slice=-1;
 for(int i=1;i<argc;++i){std::string s=argv[i];auto value=[&](){if(++i>=argc)throw std::runtime_error("missing argument");return std::string(argv[i]);};if(s=="--limit")solver.limit=natural_number(value());else if(s=="--all")solver.first=false;else if(s=="--output")out=value();else if(s=="--slice")slice=slice_number(value());else if(s=="--no-metric")solver.metric_on=false;else if(s=="--no-shortcut")solver.shortcut_on=false;else throw std::runtime_error("unknown option");}
 solver.solutions.open(out);if(!solver.solutions)throw std::runtime_error("output failure");State state;
 if(slice>=0){if(slice>=int(solver.rows[0].size()))throw std::runtime_error("bad slice");state.pick[0]=slice;state.depth=1;}
 solver.dfs(state);
 solver.solutions.close();if(!solver.solutions)throw std::runtime_error("output write failure");
 std::cout<<"{\"orbits\":"<<M<<",\"slice\":"<<slice<<",\"row0_count\":"<<solver.rows[0].size()<<",\"inequalities\":"<<solver.ineq.size()<<",\"nodes\":"<<solver.visits<<",\"radius_prunes\":"<<solver.radialdead<<",\"shortcut_prunes\":"<<solver.shortdead<<",\"metric_prunes\":"<<solver.metricdead<<",\"pair_dead\":"<<solver.pairdead<<",\"survivors\":"<<solver.leaves<<",\"exhausted\":"<<(!solver.aborted&&(!solver.first||!solver.leaves)?"true":"false")<<",\"aborted\":"<<(solver.aborted?"true":"false")<<",\"decision_complete\":"<<(!solver.aborted||solver.leaves?"true":"false")<<",\"termination_reason\":\""<<(solver.aborted?"node_limit":(solver.first&&solver.leaves?"survivor_found":"exhausted"))<<"\",\"metric_enabled\":"<<(solver.metric_on?"true":"false")<<",\"shortcut_enabled\":"<<(solver.shortcut_on?"true":"false")<<",\"seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"}\n";
 return solver.aborted?3:0;
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 2;}}
