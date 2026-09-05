// Exact bounded own-side C3 search. All prunes are integer/combinatorial.
// See README.md for their geometric proofs and the restricted claim scope.
// This is not an unrestricted Erdős #97 solver.
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#ifndef ORBIT_COUNT
#define ORBIT_COUNT 7
#endif
constexpr int M = ORBIT_COUNT, N = 3*M, P = N*(N-1)/2, C = M+P;
static_assert(5 <= M && M <= 7, "Audited bounded domain is five to seven orbits");
using Graph = std::array<unsigned,M>;
Graph graph{};
int target[M][2]{}, pos[M]{}, pair_id[N][N]{}, choice[M]{};
std::vector<std::array<int,4>> inequalities;
struct Option {
    std::array<unsigned,N> rows{};
    std::array<int,2> gain{};
};
std::array<std::vector<Option>,M> options;
struct Counts {
    std::uint64_t raw=0, oriented=0, shortcut=0, graphs=0, orders=0;
    std::uint64_t cases=0, right=0, pair=0, radial=0, cycle=0, frontier=0, survivors=0;
    std::uint64_t nodes=0;
} count;
std::ofstream output;
bool defer_right=false;
std::size_t graph_index=0;

int integer(const std::string& s) {
    if (s.empty() || s.find_first_not_of("0123456789") != std::string::npos)
        throw std::runtime_error("expected a nonnegative decimal integer");
    const auto n=std::stoull(s);
    if (n>std::uint64_t(std::numeric_limits<int>::max()))
        throw std::runtime_error("integer exceeds supported range");
    return int(n);
}
void validate_graph(const Graph& g) {
    for (int i=0;i<M;++i) {
        if (g[i] >= (1u<<M) || __builtin_popcount(g[i]) != 2 || (g[i]&(1u<<i)))
            throw std::runtime_error("invalid two-out row");
        for (int j=0;j<i;++j)
            if ((g[i]&(1u<<j)) && (g[j]&(1u<<i)))
                throw std::runtime_error("reciprocal pair in graph input");
    }
}
bool shortcut_primary() {
    std::array<unsigned,M> adjacent{};
    for (int i=0;i<M;++i) for (int j=0;j<M;++j) if (graph[i]&(1u<<j)) {
        adjacent[i]|=1u<<j; adjacent[j]|=1u<<i;
    }
    for (int lo=0;lo<M;++lo) {
        unsigned seen=1u<<lo;
        for (int hi=lo+1;hi<M;++hi) {
            const unsigned predecessors=seen&adjacent[hi];
            if ((predecessors&~(1u<<lo)) && (graph[hi]&(1u<<lo))) return true;
            if (predecessors) seen|=1u<<hi;
        }
    }
    return false;
}
bool shortcut_oracle() {
    // Second representation: Floyd closure of the increasing-edge DAG.
    bool reach[M][M]{}, long_path[M][M]{};
    for (int i=0;i<M;++i) for (int j=i+1;j<M;++j)
        reach[i][j]=(graph[i]&(1u<<j)) || (graph[j]&(1u<<i));
    for (int k=0;k<M;++k) for (int i=0;i<k;++i) for (int j=k+1;j<M;++j)
        if (reach[i][k] && reach[k][j]) reach[i][j]=long_path[i][j]=true;
    for (int hi=0;hi<M;++hi) for (int lo=0;lo<hi;++lo)
        if ((graph[hi]&(1u<<lo)) && long_path[lo][hi]) return true;
    return false;
}
void enumerate_graphs(int center, bool raw_oracle) {
    if (center==M) {
        if (raw_oracle) {
            ++count.raw;
            for (int i=0;i<M;++i) for (int j=0;j<i;++j)
                if ((graph[i]&(1u<<j)) && (graph[j]&(1u<<i))) return;
        }
        ++count.oriented;
        if (raw_oracle ? shortcut_oracle() : shortcut_primary()) { ++count.shortcut; return; }
        ++count.graphs;
        for (int i=0;i<M;++i) output<<(i?" ":"")<<graph[i];
        output<<'\n';
        return;
    }
    for (int a=0;a<M;++a) for (int b=a+1;b<M;++b) {
        if (a==center || b==center) continue;
        if (!raw_oracle && ((a<center && (graph[a]&(1u<<center))) ||
                           (b<center && (graph[b]&(1u<<center))))) continue;
        graph[center]=(1u<<a)|(1u<<b);
        enumerate_graphs(center+1,raw_oracle);
    }
}
bool crossing(int a,int b,int c,int d) {
    if (a==b || a==c || a==d || b==c || b==d || c==d) return false;
    if (a>b) std::swap(a,b);
    return (a<c && c<b)!=(a<d && d<b);
}
bool right_angle_ok(int source,const Option& o) {
    const int j=target[source][0], k=target[source][1];
    const int g=o.gain[0], h=o.gain[1];
    // The two sides opposite the selected supplier vertices must cross.
    return crossing(((g+1)%3)*M+pos[j],((g+2)%3)*M+pos[j],
                    ((h+1)%3)*M+pos[k],((h+2)%3)*M+pos[k]);
}
bool pair_ok(int x,const Option& a,int y,const Option& b) {
    // Simultaneous C3 rotation reduces nine center pairs to these three.
    for (int phase=0;phase<3;++phase) {
        const int i=pos[x], j=phase*M+pos[y];
        unsigned common=a.rows[i]&b.rows[j];
        const int size=__builtin_popcount(common);
        if (size>2) return false;
        if (size==2) {
            const int c=__builtin_ctz(common); common&=common-1;
            const int d=__builtin_ctz(common);
            if (!crossing(i,j,c,d)) return false;
        }
    }
    return true;
}
int metric() {
    // Own-side spokes throughout orbit v all have the ordinary length rho_v.
    // Unselected pairs stay separate: NO sufficiency or unproved equality is used.
    std::array<int,P> cls{};
    for (int i=0;i<P;++i) cls[i]=M+i;
    for (int v=0;v<M;++v) for (int phase=0;phase<3;++phase) {
        const int i=phase*M+pos[v];
        unsigned row=options[v][choice[v]].rows[i];
        while (row) {
            const int j=__builtin_ctz(row); row&=row-1;
            int& label=cls[pair_id[i][j]];
            if (label<M && label!=v) throw std::runtime_error("unexpected class collision");
            label=v;
        }
    }
    std::array<std::vector<int>,C> adj;
    // Weak radial order. These edges alone are acyclic.
    for (int i=0;i<M-1;++i) adj[i].push_back(i+1);
    for (const auto& q:inequalities) {
        const int a=cls[q[0]], b=cls[q[1]], c=cls[q[2]], d=cls[q[3]];
        // d_a+d_b-d_c-d_d > 0; cancellations give strict comparisons.
        if (a==c) { if (b==d) return 1; adj[d].push_back(b); }
        else if (a==d) { if (b==c) return 1; adj[c].push_back(b); }
        else if (b==c) adj[d].push_back(a);
        else if (b==d) adj[c].push_back(a);
        if (a<M && b<M && c<M && d<M) {
            std::array<int,M> coefficients{};
            ++coefficients[a]; ++coefficients[b]; --coefficients[c]; --coefficients[d];
            int suffix=0; bool nonpositive=true;
            for (int j=M-1;j>0;--j) {
                suffix+=coefficients[j];
                if (suffix>0) { nonpositive=false; break; }
            }
            if (nonpositive) return 1;
        }
    }
    std::array<unsigned char,C> state{};
    auto cycle=[&](auto&& self,int u)->bool {
        if (state[u]==1) return true;
        if (state[u]==2) return false;
        state[u]=1;
        for (int v:adj[u]) if (self(self,v)) return true;
        state[u]=2; return false;
    };
    // Any cycle contains a strict Kalmanson comparison, so is impossible.
    for (int i=0;i<C;++i) if (cycle(cycle,i)) return 2;
    return 0;
}
void emit_case(int rejecting_center) {
    // Compact record: [graph index, row masks, angle order, gains, rejecting center].
    output<<'['<<graph_index<<",[";
    for (int i=0;i<M;++i) output<<(i?",":"")<<graph[i];
    output<<"],[";
    for (int p=0;p<M;++p) for (int v=0;v<M;++v) if (pos[v]==p) output<<(p?",":"")<<v;
    output<<"],[";
    for (int v=0;v<M;++v) for (int k=0;k<2;++k)
        output<<((v || k)?",":"")<<options[v][choice[v]].gain[k];
    output<<"],"<<rejecting_center<<"]\n";
}
void phases(int source) {
    ++count.nodes;
    if (source==M) {
        const int status=metric();
        if (status==1) { ++count.radial; return; }
        if (status==2) { ++count.cycle; return; }
        ++count.frontier;
        int rejecting=-1;
        for (int v=0;v<M;++v) if (!right_angle_ok(v,options[v][choice[v]])) { rejecting=v; break; }
        if (rejecting>=0) ++count.right;
        else ++count.survivors;
        emit_case(rejecting);
        return;
    }
    std::uint64_t weight=1;
    for (int j=source+1;j<M;++j) weight*=options[j].size();
    for (int k=0;k<int(options[source].size());++k) {
        bool ok=true;
        for (int j=0;j<source;++j)
            if (!pair_ok(source,options[source][k],j,options[j][choice[j]])) { ok=false; break; }
        if (!ok) { count.pair+=weight; continue; }
        choice[source]=k; phases(source+1);
    }
}
bool prepare_order() {
    std::uint64_t raw=1, valid=1;
    for (int i=0;i<M;++i) {
        std::array<std::vector<int>,2> allowed;
        for (int k=0;k<2;++k) {
            const int j=target[i][k];
            if (j<i) allowed[k]={pos[j]>pos[i]?1:2};
            else allowed[k]={0,pos[j]>pos[i]?2:1};
            raw*=allowed[k].size();
        }
        options[i].clear();
        for (int g:allowed[0]) for (int h:allowed[1]) {
            Option o; o.gain={g,h};
            for (int p=0;p<3;++p) {
                const int center=p*M+pos[i];
                o.rows[center]=(1u<<(((p+1)%3)*M+pos[i]))|(1u<<(((p+2)%3)*M+pos[i]));
                for (int k=0;k<2;++k)
                    o.rows[center]|=1u<<(((p+o.gain[k])%3)*M+pos[target[i][k]]);
            }
            if (defer_right || right_angle_ok(i,o)) options[i].push_back(o);
        }
        valid*=options[i].size();
    }
    count.cases+=raw;
    if (!defer_right) count.right+=raw-valid;
    return valid!=0;
}
void initialize_pairs() {
    int id=0;
    for (int i=0;i<N;++i) for (int j=i+1;j<N;++j) pair_id[i][j]=pair_id[j][i]=id++;
    for (int a=0;a<N;++a) for (int b=a+1;b<N;++b)
    for (int c=b+1;c<N;++c) for (int d=c+1;d<N;++d) {
        inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][b],pair_id[c][d]});
        inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][d],pair_id[b][c]});
    }
}
std::vector<Graph> read_graphs(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("cannot open graph input");
    std::vector<Graph> records; std::string line;
    while (std::getline(in,line)) {
        if (line.empty()) throw std::runtime_error("empty graph input line");
        std::istringstream words(line); Graph g{}; std::string value;
        for (int i=0;i<M;++i) {
            if (!(words>>value)) throw std::runtime_error("short graph input row");
            g[i]=unsigned(integer(value));
        }
        if (words>>value) throw std::runtime_error("extra graph input value");
        validate_graph(g); records.push_back(g);
    }
    if (!in.eof()) throw std::runtime_error("graph input read failure");
    return records;
}
int main(int argc,char** argv) {
    try {
        std::string mode, input, out;
        int first=0, stop=std::numeric_limits<int>::max(); bool raw=false;
        for (int i=1;i<argc;++i) {
            const std::string flag=argv[i];
            auto value=[&](){if (++i>=argc) throw std::runtime_error("missing option value"); return std::string(argv[i]);};
            if (flag=="--graphs" || flag=="--phases") {
                if (!mode.empty()) throw std::runtime_error("choose one mode");
                mode=flag;
                if (flag=="--phases") input=value();
            } else if (flag=="--output") out=value();
            else if (flag=="--start") first=integer(value());
            else if (flag=="--stop") stop=integer(value());
            else if (flag=="--raw-oracle") raw=true;
            else if (flag=="--defer-right-angle") defer_right=true;
            else throw std::runtime_error("unknown option: "+flag);
        }
        if (mode.empty() || out.empty() || first>stop ||
            (mode=="--graphs" && (defer_right || first!=0 || stop!=std::numeric_limits<int>::max())) ||
            (mode=="--phases" && raw)) throw std::runtime_error("invalid mode/options");
        output.open(out);
        if (!output) throw std::runtime_error("cannot open output");
        const auto begin=std::chrono::steady_clock::now();
        std::size_t total=0, last=0;
        if (mode=="--graphs") enumerate_graphs(0,raw);
        else {
            initialize_pairs(); const auto graphs=read_graphs(input); total=graphs.size();
            if (std::size_t(first)>total) throw std::runtime_error("start exceeds input coverage");
            last=std::min(total,std::size_t(stop));
            for (graph_index=std::size_t(first);graph_index<last;++graph_index) {
                graph=graphs[graph_index];
                for (int i=0;i<M;++i) {
                    int k=0; for (int j=0;j<M;++j) if (graph[i]&(1u<<j)) target[i][k++]=j;
                }
                std::array<int,M> order{}; std::iota(order.begin(),order.end(),0);
                do {
                    ++count.orders;
                    for (int i=0;i<M;++i) pos[order[i]]=i;
                    if (prepare_order()) phases(0);
                } while (std::next_permutation(order.begin()+1,order.end()));
                ++count.graphs;
            }
            if (count.cases!=count.right+count.pair+count.radial+count.cycle+count.survivors)
                throw std::runtime_error("case partition failed");
        }
        output.close();
        if (!output) throw std::runtime_error("output write failed");
        std::cout<<"{\"schema\":1,\"orbits\":"<<M<<",\"mode\":\""<<(mode=="--graphs"?"graphs":"phases")
          <<"\",\"raw_oracle\":"<<(raw?"true":"false")<<",\"defer_right_angle\":"<<(defer_right?"true":"false")
          <<",\"exhausted\":true,\"first\":"<<first<<",\"stop\":"<<last<<",\"input_graphs\":"<<total
          <<",\"raw_tuples\":"<<count.raw<<",\"oriented_graphs\":"<<count.oriented
          <<",\"shortcut_rejections\":"<<count.shortcut<<",\"graphs\":"<<count.graphs
          <<",\"angle_orders\":"<<count.orders<<",\"phase_cases\":"<<count.cases
          <<",\"right_angle_rejections\":"<<count.right<<",\"pair_rejections\":"<<count.pair
          <<",\"radial_kalmanson_rejections\":"<<count.radial<<",\"cycle_kalmanson_rejections\":"<<count.cycle
          <<",\"pre_right_frontier\":"<<count.frontier<<",\"survivors\":"<<count.survivors
          <<",\"phase_dfs_nodes\":"<<count.nodes
          <<",\"seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count()<<"}\n";
        return count.survivors?1:0;
    } catch (const std::exception& e) {std::cerr<<e.what()<<'\n';return 2;}
}
