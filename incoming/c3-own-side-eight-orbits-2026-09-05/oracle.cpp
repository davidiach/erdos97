// Separate bounded angular-first enumerator. Symbolic geometry, not numerics.
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
constexpr int M=ORBIT_COUNT, N=3*M, P=N*(N-1)/2;
static_assert(3<=M&&M<=8);
struct DSU {std::array<int,P> p;DSU(){std::iota(p.begin(),p.end(),0);}int root(int v){while(v!=p[v]){p[v]=p[p[v]];v=p[v];}return v;}void join(int a,int b){a=root(a);b=root(b);if(a!=b)p[b]=a;}};
struct Row{std::array<int,2> point;std::array<uint32_t,3> witnesses{};unsigned targets=0;};
struct Oracle{
 int pair[N][N]{}, own[M]{};DSU symmetry;
 std::array<std::vector<Row>,M> possible;
 std::vector<std::array<int,4>> inequalities;
 std::array<int,M> selected;uint64_t nodes=0,dead_radius=0,dead_shortcut=0,dead_metric=0,dead_pairs=0,solutions=0,limit=0;
 bool stopped=false;std::ofstream out;
 static bool cross(int a,int b,int c,int d){int x=(c-a+N)%N,y=(d-a+N)%N,z=(b-a+N)%N;return x>0&&y>0&&x!=z&&y!=z&&((x<z)!=(y<z));}
 Oracle(){
  selected.fill(-1);int counter=0;
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b)pair[a][b]=pair[b][a]=counter++;
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b)symmetry.join(pair[a][b],pair[(a+M)%N][(b+M)%N]);
  for(int i=0;i<M;++i)own[i]=pair[i][i+M];
  std::set<std::array<int,4>> unique;
  for(int a=0;a<N;++a)for(int b=a+1;b<N;++b)for(int c=b+1;c<N;++c)for(int d=c+1;d<N;++d){
   std::array<int,2>pos={symmetry.root(pair[a][c]),symmetry.root(pair[b][d])};std::sort(pos.begin(),pos.end());
   for(auto v:{std::array<int,2>{pair[a][b],pair[c][d]},std::array<int,2>{pair[a][d],pair[b][c]}}){std::array<int,2>neg={symmetry.root(v[0]),symmetry.root(v[1])};std::sort(neg.begin(),neg.end());unique.insert({pos[0],pos[1],neg[0],neg[1]});}
  }inequalities.assign(unique.begin(),unique.end());
  for(int i=0;i<M;++i)for(int a=0;a<N;++a)for(int b=a+1;b<N;++b){
   if(a%M==i||b%M==i||a%M==b%M)continue;
   if(!cross((a+M)%N,(a+2*M)%N,(b+M)%N,(b+2*M)%N))continue;
   bool ok=true;
   for(int target:{a,b}){int offset=(target-i+N)%N;bool down=M<offset&&offset<2*M;if((i==0&&!down)||(target%M==0&&down))ok=false;}
   if(!ok)continue;
   Row r;r.point={a,b};if(a%M>b%M)std::swap(r.point[0],r.point[1]);r.targets=(1u<<(a%M))|(1u<<(b%M));
   for(int k=0;k<3;++k){r.witnesses[k]=(1u<<(((k+1)%3)*M+i))|(1u<<(((k+2)%3)*M+i));for(int w:{a,b})r.witnesses[k]|=1u<<((w+k*M)%N);}
   possible[i].push_back(r);
  }
  // Canonical row order is not the primary generator's target/gain loop order.
  for(auto& rs:possible)std::sort(rs.begin(),rs.end(),[](const Row&a,const Row&b){return a.point<b.point;});
 }
 bool compatible(int i,const Row&a,int j,const Row&b)const{
  if((a.targets&(1u<<j))&&(b.targets&(1u<<i)))return false;
  for(int u=0;u<3;++u)for(int v=0;v<3;++v){uint32_t common=a.witnesses[u]&b.witnesses[v];int count=__builtin_popcount(common);if(count>2)return false;if(count==2){int x=__builtin_ctz(common);common&=common-1;int y=__builtin_ctz(common);if(!cross(u*M+i,v*M+j,x,y))return false;}}
  return true;
 }
 bool radial(bool (&lt)[M][M])const{
  for(int i=1;i<M;++i)lt[i][0]=true;
  for(int i=0;i<M;++i)if(selected[i]>=0)for(int p:possible[i][selected[i]].point){int t=p%M,off=(p-i+N)%N;if(M<off&&off<2*M)lt[t][i]=true;else lt[i][t]=true;}
  for(int k=0;k<M;++k)for(int i=0;i<M;++i)for(int j=0;j<M;++j)lt[i][j]=lt[i][j]||(lt[i][k]&&lt[k][j]);
  for(int i=0;i<M;++i)if(lt[i][i])return false;
  return true;
 }
 bool shortcut(const bool (&lt)[M][M])const{
  bool graph[M][M]{},path[M][M]{},longpath[M][M]{};
  for(int i=0;i<M;++i)if(selected[i]>=0)for(int p:possible[i][selected[i]].point)graph[i][p%M]=graph[p%M][i]=true;
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)path[i][j]=graph[i][j]&&lt[i][j];
  for(int k=0;k<M;++k)for(int i=0;i<M;++i)for(int j=0;j<M;++j)if(path[i][k]&&path[k][j])path[i][j]=longpath[i][j]=true;
  for(int i=0;i<M;++i)if(selected[i]>=0)for(int p:possible[i][selected[i]].point)if(longpath[p%M][i])return false;
  return true;
 }
 bool metric(const bool (&lt)[M][M]){
  DSU dsu=symmetry;
  for(int i=0;i<M;++i)if(selected[i]>=0)for(int p:possible[i][selected[i]].point)dsu.join(own[i],pair[i][p]);
  std::array<int,P>root{},owner;owner.fill(-1);
  for(int i=0;i<P;++i)root[i]=dsu.root(i);
  for(int i=0;i<M;++i){if(owner[root[own[i]]]>=0&&owner[root[own[i]]]!=i)throw std::runtime_error("own-side collision");owner[root[own[i]]]=i;}
  std::array<std::vector<int>,P>next;std::array<int,P>indegree{};
  auto edge=[&](int a,int b){next[a].push_back(b);++indegree[b];};
  for(int i=0;i<M;++i)for(int j=0;j<M;++j)if(lt[i][j])edge(root[own[i]],root[own[j]]);
  for(const auto&q:inequalities){int a=root[q[0]],b=root[q[1]],c=root[q[2]],d=root[q[3]];
   // Subtract matching positive/negative terms, then obtain strict comparisons.
   std::array<int,2>pos={a,b},neg={c,d};
   for(int&x:pos)for(int&y:neg)if(x>=0&&x==y){x=-1;y=-1;break;}
   int pp=-1,nn=-1,np=0;for(int x:pos)if(x>=0){pp=x;++np;}for(int y:neg)if(y>=0)nn=y;
   if(!np)return false;
   if(np==1)edge(nn,pp);
   if(owner[a]>=0&&owner[b]>=0&&owner[c]>=0&&owner[d]>=0){
    auto le=[&](int x,int y){return owner[x]==owner[y]||lt[owner[x]][owner[y]];};
    if((le(a,c)&&le(b,d))||(le(a,d)&&le(b,c)))return false;
   }
  }
  // Kahn's algorithm on the full physical-chord index space.
  std::vector<int>queue;queue.reserve(P);for(int i=0;i<P;++i)if(!indegree[i])queue.push_back(i);
  for(size_t at=0;at<queue.size();++at)for(int v:next[queue[at]])if(--indegree[v]==0)queue.push_back(v);
  return queue.size()==P;
 }
 std::vector<int> legal(int center)const{
  std::vector<int>answer;
  for(int r=0;r<int(possible[center].size());++r){bool ok=true;for(int j=0;j<M&&ok;++j)if(selected[j]>=0)ok=compatible(center,possible[center][r],j,possible[j][selected[j]]);if(ok)answer.push_back(r);}
  return answer;
 }
 void dfs(int depth){
  if(stopped)return;
  if(limit&&nodes>=limit){stopped=true;return;}
  ++nodes;bool lt[M][M]{};if(!radial(lt)){++dead_radius;return;}if(!shortcut(lt)){++dead_shortcut;return;}if(!metric(lt)){++dead_metric;return;}
  if(depth==M){++solutions;out<<'[';for(int i=0;i<M;++i){if(i)out<<',';auto pts=possible[i][selected[i]].point;out<<'['<<pts[0]%M<<','<<pts[0]/M<<','<<pts[1]%M<<','<<pts[1]/M<<']';}out<<"]\n";return;}
  int chosen=-1;std::vector<int>candidate;
  for(int i=M-1;i>=0;--i)if(selected[i]<0){auto opts=legal(i);if(chosen<0||opts.size()<candidate.size()){chosen=i;candidate=std::move(opts);if(candidate.empty())break;}}
  if(candidate.empty()){++dead_pairs;return;}
  for(int r:candidate){selected[chosen]=r;dfs(depth+1);selected[chosen]=-1;if(stopped)return;}
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
int main(int argc,char**argv){try{int slice=-1;uint64_t limit=0;std::string output="oracle_survivors.jsonl";
 for(int i=1;i<argc;++i){std::string f=argv[i];auto val=[&](){if(++i>=argc)throw std::runtime_error("missing value");return std::string(argv[i]);};if(f=="--slice")slice=slice_number(val());else if(f=="--output")output=val();else if(f=="--limit")limit=natural_number(val());else throw std::runtime_error("unknown argument");}
 auto start=std::chrono::steady_clock::now();Oracle solver;solver.limit=limit;solver.out.open(output);if(!solver.out)throw std::runtime_error("output failure");int depth=0;
 if(slice>=0){if(slice>=int(solver.possible[0].size()))throw std::runtime_error("slice out of range");solver.selected[0]=slice;depth=1;}
 solver.dfs(depth);solver.out.close();if(!solver.out)throw std::runtime_error("write failure");
 std::cout<<"{\"orbits\":"<<M<<",\"slice\":"<<slice<<",\"nodes\":"<<solver.nodes<<",\"survivors\":"<<solver.solutions<<",\"radius_prunes\":"<<solver.dead_radius<<",\"shortcut_prunes\":"<<solver.dead_shortcut<<",\"metric_prunes\":"<<solver.dead_metric<<",\"pair_dead\":"<<solver.dead_pairs<<",\"exhausted\":"<<(!solver.stopped?"true":"false")<<",\"decision_complete\":"<<(!solver.stopped||solver.solutions?"true":"false")<<",\"termination_reason\":\""<<(solver.stopped?"node_limit":"exhausted")<<"\",\"seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()<<"}\n";
 return solver.stopped?3:0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
