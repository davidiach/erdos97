// Independent representations for the finite search's pruning predicates.
// This tests the implementation, not the Euclidean lemmas or all n=11 nodes.
#define main selected_witness_original_main
#include "exact_search.cpp"
#undef main
#include <map>
#include <random>
#include <set>
#include <tuple>

bool crosses_reference(int a, int b, int c, int d) {
    if (a > b) std::swap(a, b);
    if (c > d) std::swap(c, d);
    return (a < c && c < b && b < d) || (c < a && a < d && d < b);
}

bool turn_reference(const Search& search, const State& state) {
    std::vector<unsigned> arcs;
    for (int i = 0; i < N; ++i) {
        if (state.choice[i] < 0) continue;
        for (unsigned a : search.rows[i][state.choice[i]].arcs) arcs.push_back(a);
    }
    for (size_t a = 0; a < arcs.size(); ++a)
        for (size_t b = a + 1; b < arcs.size(); ++b) {
            if (arcs[a] & arcs[b]) continue;
            for (size_t c = b + 1; c < arcs.size(); ++c) {
                const unsigned ab = arcs[a] | arcs[b];
                if (ab & arcs[c]) continue;
                for (size_t d = c + 1; d < arcs.size(); ++d)
                    if (!((ab | arcs[c]) & arcs[d])) return true;
            }
        }
    return false;
}

int metric_reference(const Search& search, const State& state) {
    // Relabel every member of a class, rather than using the search's DSU.
    std::array<int, P> label;
    std::iota(label.begin(), label.end(), 0);
    for (int i = 0; i < N; ++i) {
        if (state.choice[i] < 0) continue;
        const auto& row = search.rows[i][state.choice[i]];
        for (int j = 1; j < 4; ++j) {
            int from = label[row.sp[j]], to = label[row.sp[0]];
            for (int& x : label) if (x == from) x = to;
        }
    }
    std::set<std::vector<std::pair<int, int>>> seen;
    // Rebuild the inequalities directly from cyclic quadruples.
    for (int a = 0; a < N; ++a)
        for (int b = a + 1; b < N; ++b)
            for (int c = b + 1; c < N; ++c)
                for (int d = c + 1; d < N; ++d)
                    for (int side = 0; side < 2; ++side) {
                        std::map<int, int> coefficients;
                        ++coefficients[label[search.pair_id[a][c]]];
                        ++coefficients[label[search.pair_id[b][d]]];
                        --coefficients[label[search.pair_id[a][side ? d : b]]];
                        --coefficients[label[search.pair_id[side ? b : c][side ? c : d]]];
                        int divisor = 0;
                        for (auto [root, value] : coefficients)
                            divisor = std::gcd(divisor, std::abs(value));
                        if (!divisor) return 1;
                        std::vector<std::pair<int, int>> normal, inverse;
                        for (auto [root, value] : coefficients) if (value) {
                            normal.push_back({root, value / divisor});
                            inverse.push_back({root, -value / divisor});
                        }
                        if (seen.count(inverse)) return 2;
                        seen.insert(normal);
                    }
    return 0;
}

std::vector<int> options_reference(int center, const Search& search, const State& state) {
    std::array<int, N> indegree{};
    std::array<int, P> pair_count{};
    for (int i = 0; i < N; ++i) if (state.choice[i] >= 0) {
        for (int v : search.rows[i][state.choice[i]].w) ++indegree[v];
        for (int p : search.rows[i][state.choice[i]].ps) ++pair_count[p];
    }
    if (indegree != state.indeg || pair_count != state.pc)
        throw std::runtime_error("incremental count mismatch");
    std::vector<int> result;
    for (int option = 0; option < search.R; ++option) {
        const auto& row = search.rows[center][option];
        bool ok = true;
        for (int i = 0; i < N && ok; ++i) if (state.choice[i] >= 0) {
            std::vector<int> common;
            const auto& other = search.rows[i][state.choice[i]];
            std::set_intersection(row.w.begin(), row.w.end(), other.w.begin(), other.w.end(),
                                  std::back_inserter(common));
            if (common.size() > 2) ok = false;
            if (common.size() == 2 && !crosses_reference(center, i, common[0], common[1]))
                ok = false;
        }
        for (int v : row.w) if (indegree[v] >= 2 * (N - 1) / 3) ok = false;
        for (int p : row.ps) if (pair_count[p] >= 2) ok = false;
        if (ok) result.push_back(option);
    }
    return result;
}

int main(int argc, char** argv) {
    try {
        Search search;
        if (argc == 2 && std::string(argv[1]) == "--calibrate") {
            if (N != 9) throw std::runtime_error("calibration requires SEARCH_N=9");
            search.use_turn = search.use_k = false;
            search.stop_at_first = false;
            State state;
            search.dfs(state);
            if (search.st.leaves != 184) throw std::runtime_error("n=9 frontier mismatch");
            std::cout << "{\"n\":9,\"incidence_frontier\":184,\"nodes\":"
                      << search.st.visits << "}\n";
            return 0;
        }
        if (argc != 1) throw std::runtime_error("usage: oracle [--calibrate]");
        std::mt19937 rng(970905);
        int checked = 0;
        for (int run = 0; run < 1000; ++run) {
            State state;
            std::array<int, N> order;
            std::iota(order.begin(), order.end(), 0);
            std::shuffle(order.begin(), order.end(), rng);
            for (int depth = 0; depth < N; ++depth) {
                if (search.turn_bad(state) != turn_reference(search, state))
                    throw std::runtime_error("turn-packing predicate mismatch");
                // Exact type must agree because both traverse quadruples in the same order.
                if (search.metric(state) != metric_reference(search, state))
                    throw std::runtime_error("Kalmanson predicate mismatch");
                int center = order[depth];
                auto options = search.options(center, state);
                if (options != options_reference(center, search, state))
                    throw std::runtime_error("row-option predicate mismatch");
                ++checked;
                if (run % 2) {
                    if (options.empty()) break;
                    search.place(state, center, options[rng() % options.size()], 1);
                } else {
                    search.place(state, center, int(rng() % search.R), 1);
                }
            }
        }
        std::cout << "{\"n\":" << N << ",\"seed\":970905,\"states_checked\":"
                  << checked << ",\"predicate_mismatches\":0}\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
