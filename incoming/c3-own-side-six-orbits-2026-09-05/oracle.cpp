// Independent full radial-order/phase search for the fixed six-orbit graph.
// No Python helpers, radial automorphism quotient, floating point, or optimizer.
// This verifies a necessary-condition relaxation, not arbitrary Erdos #97.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

constexpr int N = 18, P = N * (N - 1) / 2;
int targets[6][2] = {{4,5},{4,5},{0,1},{0,1},{2,3},{2,3}};
int pair_id[N][N]{};
std::vector<std::array<int,4>> inequalities;
std::array<int,6> rank{}, pos{};
std::array<int,12> gains{};
std::array<std::vector<int>,12> allowed;
struct Census {
    std::uint64_t radial_orders=0, radial_rejected=0, radial_retained=0;
    std::uint64_t cases=0, crossing=0, circles=0, zero=0, inverse=0, survivors=0;
} stats;

bool arrow(int i, int j) { return targets[i][0] == j || targets[i][1] == j; }
bool alternating(int a, int b, int c, int d) {
    // Distinct centers and common witnesses imply four distinct endpoints.
    if (a > b) std::swap(a,b);
    return (a<c && c<b) != (a<d && d<b);
}

int metric(const std::array<std::uint32_t,N>& rows) {
    std::array<int,P> cls{};
    std::iota(cls.begin(),cls.end(),0);
    // Entire-class relabeling, deliberately different from Python's DSU.
    for (int i=0;i<N;i++) {
        int anchor=-1;
        for (int j=0;j<N;j++) if (rows[i] & (1u<<j)) {
            int current=cls[pair_id[i][j]];
            if (anchor<0) anchor=current;
            else if (anchor!=current) {
                for (int& label:cls) if (label==current) label=anchor;
            }
        }
    }
    std::set<std::array<int,8>> seen;
    for (const auto& q:inequalities) {
        std::array<std::pair<int,int>,4> terms = {{{cls[q[0]],1},{cls[q[1]],1},
                                                 {cls[q[2]],-1},{cls[q[3]],-1}}};
        std::sort(terms.begin(),terms.end());
        std::array<int,8> key{}, opposite{};
        int size=0;
        for (int j=0;j<4;) {
            int label=terms[j].first, coefficient=0;
            while (j<4 && terms[j].first==label) coefficient+=terms[j++].second;
            if (coefficient) {
                key[2*size]=opposite[2*size]=label+1;
                key[2*size+1]=coefficient;
                opposite[2*size+1]=-coefficient;
                ++size;
            }
        }
        if (!size) return 1;
        if (seen.count(opposite)) return 2;
        seen.insert(key);
    }
    return 0;
}

void evaluate() {
    ++stats.cases;
    std::array<std::uint32_t,N> rows{};
    for (int source=0;source<6;source++) for (int phase=0;phase<3;phase++) {
        int center=6*phase+pos[source];
        rows[center]=(1u<<(6*((phase+1)%3)+pos[source]))
                    |(1u<<(6*((phase+2)%3)+pos[source]));
        for (int k=0;k<2;k++) {
            int witness=6*((phase+gains[2*source+k])%3)+pos[targets[source][k]];
            rows[center] |= 1u<<witness;
        }
    }
    for (int i=0;i<N;i++) for (int j=i+1;j<N;j++) {
        std::uint32_t common=rows[i]&rows[j];
        std::vector<int> witnesses;
        for (int k=0;k<N;k++) if (common & (1u<<k)) witnesses.push_back(k);
        if (witnesses.size()>2) { ++stats.circles; return; }
        if (witnesses.size()==2 && !alternating(i,j,witnesses[0],witnesses[1])) {
            ++stats.crossing; return;
        }
    }
    int result=metric(rows);
    if (result==1) ++stats.zero;
    else if (result==2) ++stats.inverse;
    else ++stats.survivors;
}

void enumerate_gains(int edge) {
    if (edge==12) { evaluate(); return; }
    for (int gain:allowed[edge]) { gains[edge]=gain; enumerate_gains(edge+1); }
}

int target_main(int argc, char** argv) {
    try {
        bool all_angles=false;
        if (argc==2 && std::string(argv[1])=="--all-angle-orders") all_angles=true;
        else if (argc!=1) throw std::runtime_error("usage: oracle [--all-angle-orders]");
        int id=0;
        for (int i=0;i<N;i++) for (int j=i+1;j<N;j++) pair_id[i][j]=pair_id[j][i]=id++;
        for (int a=0;a<N;a++) for (int b=a+1;b<N;b++)
        for (int c=b+1;c<N;c++) for (int d=c+1;d<N;d++) {
            inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][b],pair_id[c][d]});
            inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][d],pair_id[b][c]});
        }
        std::array<int,6> radius_order={0,1,2,3,4,5};
        do {
            ++stats.radial_orders;
            for (int k=0;k<6;k++) rank[radius_order[k]]=k;
            bool bad=false;
            for (int i=0;i<6;i++) for (int j=i+1;j<6;j++) for (int k=j+1;k<6;k++) {
                int a=radius_order[i], b=radius_order[j], c=radius_order[k];
                if (a/2!=b/2 && b/2!=c/2 && a/2!=c/2 && arrow(c,a)) bad=true;
            }
            if (bad) { ++stats.radial_rejected; continue; }
            ++stats.radial_retained;
            std::array<int,6> order={0,1,2,3,4,5};
            do {
                for (int k=0;k<6;k++) pos[order[k]]=k;
                for (int source=0;source<6;source++) for (int k=0;k<2;k++) {
                    int target=targets[source][k], edge=2*source+k;
                    allowed[edge].clear();
                    for (int gain=0;gain<3;gain++) {
                        int angle=(pos[target]-pos[source]+6*gain+18)%18;
                        bool downward=rank[target]<rank[source];
                        if (downward ? (6<angle && angle<12) : (angle<6 || angle>12))
                            allowed[edge].push_back(gain);
                    }
                }
                enumerate_gains(0);
            } while (std::next_permutation(order.begin()+(all_angles?0:1),order.end()));
        } while (std::next_permutation(radius_order.begin(),radius_order.end()));
        std::uint64_t factor=all_angles?6:1;
        bool expected=stats.radial_orders==720 && stats.radial_rejected==672
            && stats.radial_retained==48 && stats.cases==92160*factor
            && stats.crossing==79488*factor && stats.inverse==12672*factor
            && stats.circles==0 && stats.zero==0 && stats.survivors==0;
        std::cout << "{\"radial_orders\":"<<stats.radial_orders
          <<",\"radial_rejected\":"<<stats.radial_rejected<<",\"radial_retained\":"<<stats.radial_retained
          <<",\"angle_orders_per_radial_order\":"<<(all_angles?720:120)<<",\"cases\":"<<stats.cases
          <<",\"crossing\":"<<stats.crossing<<",\"two_circle\":"<<stats.circles
          <<",\"kalmanson_zero\":"<<stats.zero<<",\"kalmanson_inverse\":"<<stats.inverse
          <<",\"survivors\":"<<stats.survivors<<",\"expected_counts_match\":"<<(expected?"true":"false")<<"}\n";
        return expected?0:1;
    } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 2; }
}


// This mode independently enumerates every row choice before testing reciprocal
// edges. Its increasing-path test is Floyd closure, not Python parent search.
std::array<std::uint64_t,7> raw_graphs{}, oriented{}, shortcut_rejected{};
int graph_size=0;

bool has_shortcut() {
    bool reach[6][6]{}, long_path[6][6]{};
    for (int i=0;i<graph_size;i++) for (int j=i+1;j<graph_size;j++)
        reach[i][j]=arrow(i,j)||arrow(j,i);
    for (int k=0;k<graph_size;k++) for (int i=0;i<k;i++)
        for (int j=k+1;j<graph_size;j++) if (reach[i][k] && reach[k][j]) {
            reach[i][j]=true;
            long_path[i][j]=true;
        }
    for (int hi=0;hi<graph_size;hi++) for (int lo=0;lo<hi;lo++)
        if (arrow(hi,lo) && long_path[lo][hi]) return true;
    return false;
}

void evaluate_graph() {
    ++raw_graphs[graph_size];
    for (int i=0;i<graph_size;i++) for (int j=i+1;j<graph_size;j++)
        if (arrow(i,j) && arrow(j,i)) return;
    ++oriented[graph_size];
    if (has_shortcut()) { ++shortcut_rejected[graph_size]; return; }
    if (graph_size!=6) throw std::runtime_error("unexpected smaller graph survivor");
    for (int i=0;i<6;i++) rank[i]=i;
    std::array<int,6> order={0,1,2,3,4,5};
    do {
        for (int k=0;k<6;k++) pos[order[k]]=k;
        for (int source=0;source<6;source++) for (int k=0;k<2;k++) {
            int target=targets[source][k], edge=2*source+k;
            allowed[edge].clear();
            for (int gain=0;gain<3;gain++) {
                int sector=(pos[target]-pos[source]+6*gain+18)%18;
                bool down=target<source;
                if (down ? (6<sector && sector<12) : (sector<6 || sector>12))
                    allowed[edge].push_back(gain);
            }
        }
        enumerate_gains(0);
    } while (std::next_permutation(order.begin(),order.end()));
}

void enumerate_graphs(int center) {
    if (center==graph_size) { evaluate_graph(); return; }
    for (int a=0;a<graph_size;a++) for (int b=a+1;b<graph_size;b++) {
        if (a==center || b==center) continue;
        targets[center][0]=a; targets[center][1]=b;
        enumerate_graphs(center+1);
    }
}

int all_systems_main() {
    int id=0;
    for (int i=0;i<N;i++) for (int j=i+1;j<N;j++) pair_id[i][j]=pair_id[j][i]=id++;
    for (int a=0;a<N;a++) for (int b=a+1;b<N;b++)
    for (int c=b+1;c<N;c++) for (int d=c+1;d<N;d++) {
        inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][b],pair_id[c][d]});
        inequalities.push_back({pair_id[a][c],pair_id[b][d],pair_id[a][d],pair_id[b][c]});
    }
    for (graph_size=5;graph_size<=6;graph_size++) enumerate_graphs(0);
    bool expected=raw_graphs[5]==7776 && raw_graphs[6]==1000000
        && oriented[5]==24 && oriented[6]==14490
        && shortcut_rejected[5]==24 && shortcut_rejected[6]==14486
        && stats.cases==46080 && stats.crossing==42528 && stats.inverse==3552
        && stats.circles==0 && stats.zero==0 && stats.survivors==0;
    std::cout<<"{\"mode\":\"all_systems\",\"raw_n5\":"<<raw_graphs[5]
        <<",\"raw_n6\":"<<raw_graphs[6]<<",\"oriented_n5\":"<<oriented[5]
        <<",\"oriented_n6\":"<<oriented[6]<<",\"shortcut_rejected_n5\":"<<shortcut_rejected[5]
        <<",\"shortcut_rejected_n6\":"<<shortcut_rejected[6]<<",\"angle_orders\":720"
        <<",\"phase_cases\":"<<stats.cases<<",\"crossing\":"<<stats.crossing
        <<",\"kalmanson_inverse\":"<<stats.inverse<<",\"survivors\":"<<stats.survivors
        <<",\"expected_counts_match\":"<<(expected?"true":"false")<<"}\n";
    return expected?0:1;
}

int main(int argc, char** argv) {
    try {
        if (argc==2 && std::string(argv[1])=="--all-systems") return all_systems_main();
        return target_main(argc,argv);
    } catch (const std::exception& e) { std::cerr<<e.what()<<'\n'; return 2; }
}
