// Exact, exhaustive phase enumeration for supplied radial graphs.
// Each case emits a five-byte elementary certificate or a residual index.
// Residuals require separate exact angle certificates; none is a realization.
#include <algorithm>
#include <array>
#include <bitset>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
constexpr int M=7,N=3*M,P=N*(N-1)/2;
int piid[N][N];
array<int,P> rot_base;
vector<array<int,4>> inequalities;
vector<array<int,5>> quad_specs;
vector<array<int,2>> allpairs;
uint64_t totals[5]={};
int root(array<int,P>&p,int a){while(p[a]!=a){p[a]=p[p[a]];a=p[a];}return a;}
void join(array<int,P>&p,int a,int b){a=root(p,a);b=root(p,b);if(a!=b)p[max(a,b)]=min(a,b);}
void init(){int id=0;for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){piid[a][b]=piid[b][a]=id++;allpairs.push_back({a,b});}
 iota(rot_base.begin(),rot_base.end(),0);
 for(auto ab:allpairs) join(rot_base,piid[ab[0]][ab[1]],piid[(ab[0]+M)%N][(ab[1]+M)%N]);
 for(int a=0;a<P;a++)rot_base[a]=root(rot_base,a);
 for(int a=0;a<N;a++)for(int b=a+1;b<N;b++)for(int c=b+1;c<N;c++)for(int d=c+1;d<N;d++){
 inequalities.push_back({piid[a][c],piid[b][d],piid[a][b],piid[c][d]});quad_specs.push_back({a,b,c,d,0});
 inequalities.push_back({piid[a][c],piid[b][d],piid[a][d],piid[b][c]});quad_specs.push_back({a,b,c,d,1});}
}
bool crosses(int a,int b,int c,int d){if(a==c||a==d||b==c||b==d)return false;return (a<c&&c<b)!=(a<d&&d<b);}
uint64_t keyvec(const array<int,P>&p,const array<int,4>&q,bool invert){
 array<pair<int,int>,4>v;for(int i=0;i<4;i++)v[i]={p[q[i]],(i<2?1:-1)*(invert?-1:1)};
 sort(v.begin(),v.end());int k=0;array<pair<int,int>,4>w;
 for(int i=0;i<4;){int a=v[i].first,c=0;while(i<4&&v[i].first==a)c+=v[i++].second;if(c)w[k++]={a,c};}
 int g=0;for(int i=0;i<k;i++)g=gcd(g,abs(w[i].second));
 uint64_t result=uint64_t(k)<<60;for(int i=0;i<k;i++)result|=uint64_t(8*w[i].first+3+w[i].second/g)<<(11*i);
 return result;
}
// outcome 1 crossing/circle, 2 zero K, 3 inverse K, 4 survivor.
int test(const array<unsigned,N>&r, array<int,4>&cert){
 for(int a=0;a<N;a++)for(int b=a+1;b<N;b++){
  unsigned z=r[a]&r[b]; int t=__builtin_popcount(z); if(t<2)continue;
  int c=__builtin_ctz(z);z&=z-1;int d=__builtin_ctz(z);
  if(t>2||!crosses(a,b,c,d)){cert={a,b,c,d};return 1;}
 }
 auto p=rot_base;
 for(int i=0;i<N;i++){unsigned w=r[i];int a=__builtin_ctz(w);w&=w-1;while(w){int b=__builtin_ctz(w);w&=w-1;join(p,piid[i][a],piid[i][b]);}}
 for(int a=0;a<P;a++)p[a]=root(p,a);
 unordered_map<uint64_t,int>seen;seen.reserve(inequalities.size()*2);
 for(int j=0;j<(int)inequalities.size();j++){
  uint64_t k=keyvec(p,inequalities[j],false);if(k==0){cert={j,-1,0,0};return 2;}
  auto it=seen.find(keyvec(p,inequalities[j],true));if(it!=seen.end()){cert={it->second,j,0,0};return 3;}seen.emplace(k,j);
 }return 4;
}
void write_u16(ostream& out,unsigned value) {
 if(value>65535)throw runtime_error("proof integer out of range");
 out.put(char(value&255));out.put(char((value>>8)&255));
}
int main(int argc,char**argv){try{
 if(argc!=2)throw runtime_error("usage: phase_search PROOF.bin < radial_graphs.txt");
 init(); ofstream proof(argv[1],ios::binary);if(!proof)throw runtime_error("cannot create proof");
 proof.write("C3P7v1\r\n",8);uint64_t residual=0;
 array<array<int,2>,M> rows;int graphid=0;
 while(cin>>rows[0][0]>>rows[0][1]){
  for(int i=1;i<M;i++)if(!(cin>>rows[i][0]>>rows[i][1]))throw runtime_error("truncated graph row");
  for(int i=0;i<M;i++){
   if(rows[i][0]<0 || rows[i][1]>=M || rows[i][0]>=rows[i][1] || rows[i][0]==i || rows[i][1]==i)
    throw runtime_error("invalid graph targets");
   for(int j:rows[i])if(rows[j][0]==i||rows[j][1]==i)throw runtime_error("reciprocal arrow");
  }
  array<int,M>order,pos; iota(order.begin(),order.end(),0);
  uint64_t counts[5]={};
  do{
   for(int i=0;i<M;i++)pos[order[i]]=i;
   array<int,2*M>gs;vector<int>ups;
   for(int i=0;i<M;i++)for(int k=0;k<2;k++){int j=rows[i][k],t=2*i+k;if(i<j){gs[t]=0;ups.push_back(t);}else gs[t]=pos[j]>pos[i]?1:2;}
   for(int mask=0;mask<(1<<ups.size());mask++){
    for(int a=0;a<(int)ups.size();a++){int t=ups[a],i=t/2,j=rows[i][t%2];gs[t]=(mask&(1<<a))?(pos[j]>pos[i]?2:1):0;}
    array<unsigned,N>full{};
    for(int i=0;i<M;i++)for(int h=0;h<3;h++){
     unsigned bits=(1u<<(M*((h+1)%3)+pos[i]))|(1u<<(M*((h+2)%3)+pos[i]));
     for(int k=0;k<2;k++)bits|=1u<<(M*((h+gs[2*i+k])%3)+pos[rows[i][k]]);
     full[h*M+pos[i]]=bits;
    }
    array<int,4>cert;int outcome=test(full,cert); counts[0]++;counts[outcome]++;
    proof.put(char(outcome));
    if(outcome==1){write_u16(proof,cert[0]*N+cert[1]);write_u16(proof,cert[2]*N+cert[3]);}
    else if(outcome==2){write_u16(proof,cert[0]);write_u16(proof,65535);}
    else if(outcome==3){write_u16(proof,cert[0]);write_u16(proof,cert[1]);}
    else {write_u16(proof,residual++);write_u16(proof,0);}
    if(!proof)throw runtime_error("proof write failed");
    if(outcome==4){
     cout<<"{\"graph\":"<<graphid<<",\"order\":[";for(int i=0;i<M;i++){if(i)cout<<',';cout<<order[i];}
     cout<<"],\"gains\":[";for(int i=0;i<2*M;i++){if(i)cout<<',';cout<<gs[i];}cout<<"]}"<<endl;

    }
   }
  }while(next_permutation(order.begin()+1,order.end()));
  cerr<<"graph "<<graphid<<" cases "<<counts[0]<<" crossing "<<counts[1]<<" zero "<<counts[2]<<" inverse "<<counts[3]<<" survivors "<<counts[4]<<endl;
  for(int k=0;k<5;k++)totals[k]+=counts[k];
  graphid++;
 }
 if(!cin.eof())throw runtime_error("invalid input token");
 proof.flush();if(!proof)throw runtime_error("proof flush failed");
 cerr<<"TOTAL";for(auto c:totals)cerr<<' '<<c;cerr<<endl;
 return 0;
 }catch(const exception& e){cerr<<"ERROR: "<<e.what()<<endl;return 2;}
}
