// Separate full phase enumerator for m=7. It consumes the independently
// regenerated graph list; no partial pair-prefix pruning or direct class labels.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
constexpr int M=7, N=21, P=210;
using Graph=std::array<unsigned,M>;
struct Option {std::array<std::array<int,4>,3> row;std::array<int,2> gains;};
std::array<std::vector<Option>,M> choices;
std::array<int,M> position{},selected{};
int targets[M][2]{},pair_id[N][N]{};
std::vector<std::array<int,4>> inequalities;
std::uint64_t graph_count=0,orders=0,cases=0,right_reject=0,pair_reject=0,metric_reject=0,survivors=0;

bool interlaced(int a,int b,int c,int d) {
    // Sort endpoint tags; they must alternate around the boundary.
    std::array<std::pair<int,int>,4> tags={{{a,0},{b,0},{c,1},{d,1}}};
    std::sort(tags.begin(),tags.end());
    for (int i=0;i<4;++i) if (tags[i].second==tags[(i+1)%4].second) return false;
    return true;
}
bool right_ok(int source,const Option& o) {
    std::array<std::pair<int,int>,4> endpoints{};
    int n=0;
    // Ray order as viewed from the source, not a side-crossing call.
    for (int k=0;k<2;++k) for (int h=1;h<=2;++h) {
        int p=((o.gains[k]+h)%3)*M+position[targets[source][k]];
        endpoints[n++]={(p-position[source]+N)%N,k};
    }
    std::sort(endpoints.begin(),endpoints.end());
    return endpoints[0].second!=endpoints[1].second &&
           endpoints[0].second==endpoints[2].second &&
           endpoints[1].second==endpoints[3].second;
}
bool obstructed_metric(const std::array<std::array<int,4>,N>& rows) {
    std::array<int,P> parent{};
    std::iota(parent.begin(),parent.end(),0);
    auto root=[&](int a) {while (parent[a]!=a) a=parent[a];return a;};
    for (int i=0;i<N;++i) for (int k=1;k<4;++k) {
        int a=root(pair_id[i][rows[i][0]]),b=root(pair_id[i][rows[i][k]]);
        parent[a]=b;
    }
    for (int i=0;i<P;++i) parent[i]=root(i);
    std::array<int,P> radius_index{};
    radius_index.fill(-1);
    std::array<int,M> radial{};
    for (int i=0;i<M;++i) {
        radial[i]=parent[pair_id[position[i]][position[i]+M]];
        radius_index[radial[i]]=i;
    }
    std::array<std::vector<int>,P> edges;
    for (int i=0;i<M-1;++i) edges[radial[i]].push_back(radial[i+1]);
    for (const auto& q:inequalities) {
        std::array<int,4> label{};
        std::array<int,4> coefficient{};
        int used=0;
        for (int k=0;k<4;++k) {
            int c=parent[q[k]], at=0;
            while (at<used && label[at]!=c) ++at;
            if (at==used) label[used++]=c;
            coefficient[at]+=k<2?1:-1;
        }
        int nonzero=0,positive=-1,negative=-1;
        bool only_radial=true;
        std::array<int,M> rcoeff{};
        for (int k=0;k<used;++k) if (coefficient[k]) {
            ++nonzero;
            if (coefficient[k]>0) positive=label[k];else negative=label[k];
            if (radius_index[label[k]]<0) only_radial=false;
            else rcoeff[radius_index[label[k]]]+=coefficient[k];
        }
        if (!nonzero) return true;
        if (only_radial) {
            bool bad=true;
            // Independent prefix-sum form; total coefficient sum is zero.
            int prefix=rcoeff[0];
            for (int k=1;k<M;++k) {if (prefix<0) bad=false;prefix+=rcoeff[k];}
            if (bad) return true;
        }
        if (nonzero==2) edges[negative].push_back(positive);
    }
    // Kahn topological deletion, rather than the primary recursive cycle test.
    std::array<int,P> indegree{};
    for (const auto& list:edges) for (int v:list) ++indegree[v];
    std::vector<int> queue;
    for (int i=0;i<P;++i) if (!indegree[i]) queue.push_back(i);
    for (std::size_t k=0;k<queue.size();++k)
        for (int v:edges[queue[k]]) if (!--indegree[v]) queue.push_back(v);
    return queue.size()!=P;
}
void evaluate() {
    std::array<std::array<int,4>,N> rows{};
    for (int i=0;i<M;++i) for (int phase=0;phase<3;++phase)
        rows[phase*M+position[i]]=choices[i][selected[i]].row[phase];
    // All 210 physical center pairs, not the primary C3 pair reduction.
    for (int i=0;i<N;++i) for (int j=i+1;j<N;++j) {
        std::vector<int> common;
        for (int a:rows[i]) for (int b:rows[j]) if (a==b) common.push_back(a);
        if (common.size()>2 || (common.size()==2 && !interlaced(i,j,common[0],common[1]))) {
            ++pair_reject;return;
        }
    }
    if (obstructed_metric(rows)) ++metric_reject;
    else ++survivors;
}
void enumerate_options(int i) {
    // No pair compatibility prune before a full tuple is constructed.
    if (i==M) {evaluate();return;}
    for (int k=0;k<int(choices[i].size());++k) {selected[i]=k;enumerate_options(i+1);}
}
void angular_order() {
    ++orders;
    std::uint64_t before=1,after=1;
    for (int i=0;i<M;++i) {
        choices[i].clear();std::array<std::vector<int>,2> allowed;
        for (int k=0;k<2;++k) {
            int j=targets[i][k];
            for (int g=0;g<3;++g) {
                int sector=(position[j]-position[i]+M*g+N)%N;
                bool large=M<sector && sector<2*M;
                if ((j<i)==large) allowed[k].push_back(g);
            }
            before*=allowed[k].size();
        }
        for (int a:allowed[0]) for (int b:allowed[1]) {
            Option o;o.gains={a,b};
            for (int p=0;p<3;++p) {
                o.row[p]={((p+1)%3)*M+position[i],((p+2)%3)*M+position[i],
                          ((p+a)%3)*M+position[targets[i][0]],((p+b)%3)*M+position[targets[i][1]]};
            }
            if (right_ok(i,o)) choices[i].push_back(o);
        }
        after*=choices[i].size();
    }
    cases+=before;right_reject+=before-after;
    if (after) enumerate_options(0);
}
int number(const std::string& s) {
    if (s.empty() || s.find_first_not_of("0123456789")!=std::string::npos)
        throw std::runtime_error("nonnegative integer required");
    auto value=std::stoull(s);
    if (value>1000000) throw std::runtime_error("integer too large");
    return int(value);
}
int main(int argc,char** argv) {
    try {
        if (argc!=2 && argc!=4) throw std::runtime_error("usage: oracle GRAPHS [FIRST STOP]");
        const int first=argc==4?number(argv[2]):0, stop=argc==4?number(argv[3]):1000000;
        if (first>stop) throw std::runtime_error("reversed range");
        std::ifstream in(argv[1]);if (!in) throw std::runtime_error("cannot open graph input");
        std::vector<Graph> graphs;std::string line;
        while (std::getline(in,line)) {
            std::istringstream fields(line);Graph g{};std::string word;
            for (int i=0;i<M;++i) {
                if (!(fields>>word)) throw std::runtime_error("short input row");
                g[i]=unsigned(number(word));
                if (g[i]>=128 || __builtin_popcount(g[i])!=2 || (g[i]&(1u<<i)))
                    throw std::runtime_error("invalid row mask");
                for (int j=0;j<i;++j) if ((g[i]&(1u<<j)) && (g[j]&(1u<<i)))
                    throw std::runtime_error("reciprocal input");
            }
            if (fields>>word) throw std::runtime_error("extra graph field");
            graphs.push_back(g);
        }
        if (!in.eof() || first>int(graphs.size())) throw std::runtime_error("input/range error");
        int id=0;
        for (int i=0;i<N;++i) for (int j=i+1;j<N;++j) pair_id[i][j]=pair_id[j][i]=id++;
        for (int a=0;a<N;++a) for (int b=a+1;b<N;++b)
        for (int c=b+1;c<N;++c) for (int d=c+1;d<N;++d) {
            inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][b],pair_id[c][d]});
            inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][d],pair_id[b][c]});
        }
        const int end=std::min(stop,int(graphs.size()));
        for (int k=first;k<end;++k) {
            for (int i=0;i<M;++i) {
                int t=0;for (int j=0;j<M;++j) if (graphs[k][i]&(1u<<j)) targets[i][t++]=j;
            }
            std::array<int,M> order{};std::iota(order.begin(),order.end(),0);
            do {
                for (int i=0;i<M;++i) position[order[i]]=i;
                angular_order();
            } while (std::next_permutation(order.begin()+1,order.end()));
            ++graph_count;
        }
        if (cases!=right_reject+pair_reject+metric_reject+survivors)
            throw std::runtime_error("phase coverage mismatch");
        std::cout<<"{\"exhausted\":true,\"first\":"<<first<<",\"stop\":"<<end
          <<",\"input_graphs\":"<<graphs.size()<<",\"graphs\":"<<graph_count<<",\"angle_orders\":"<<orders
          <<",\"phase_cases\":"<<cases<<",\"right_angle_rejections\":"<<right_reject
          <<",\"pair_rejections\":"<<pair_reject<<",\"metric_rejections\":"<<metric_reject
          <<",\"survivors\":"<<survivors<<"}\n";
        return survivors?1:0;
    } catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 2;}
}
