// Exact exploratory n=10 search for escapes from Kalmanson self-edges and
// primitive inverse pairs. A terminal is only an abstract filter escape.

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>

using namespace std;

namespace {

#ifndef PROBE_N
#define PROBE_N 10
#endif

constexpr int N = PROBE_N;
constexpr int P = N * (N - 1) / 2;
constexpr int PAIR_CAP = 2;
constexpr int INDEGREE_CAP = 2 * (N - 1) / 3;
static_assert(N >= 5 && N <= 11, "the packed key supports 5 <= N <= 11");

struct Row {
    int mask{};
    array<int, 4> witnesses{};
    array<int, 4> spokes{};
    array<int, 6> witness_pairs{};
};

struct StrictRow {
    array<int, 4> pair_indices{};
    array<int, 4> coefficients{};
};

struct Search {
    int pair_index[N][N];
    vector<pair<int, int>> pairs;
    array<vector<Row>, N> rows;
    vector<StrictRow> strict_rows;
    vector<vector<vector<vector<unsigned char>>>> compatible;
    array<int, N> assigned{};
    array<int, N> selected{};
    array<int, N> indegrees{};
    array<int, P> pair_counts{};
    int assigned_count = 0;
    uint64_t nodes = 0;
    uint64_t self_edges = 0;
    uint64_t inverse_pairs = 0;
    bool found = false;

    Search() {
        memset(pair_index, -1, sizeof(pair_index));
        for (int a = 0; a < N; ++a) {
            for (int b = a + 1; b < N; ++b) {
                pair_index[a][b] = pair_index[b][a] = static_cast<int>(pairs.size());
                pairs.push_back({a, b});
            }
        }
        build_rows();
        build_strict_rows();
        build_compatibility();
    }

    void choose_rows(int center, int next, int needed, vector<int>& current) {
        if (needed == 0) {
            Row row;
            for (int i = 0; i < 4; ++i) {
                row.witnesses[i] = current[i];
                row.mask |= 1 << current[i];
                row.spokes[i] = pair_index[center][current[i]];
            }
            int index = 0;
            for (int i = 0; i < 4; ++i) {
                for (int j = i + 1; j < 4; ++j) {
                    row.witness_pairs[index++] = pair_index[current[i]][current[j]];
                }
            }
            rows[center].push_back(row);
            return;
        }
        for (int value = next; value < N; ++value) {
            if (value == center) {
                continue;
            }
            int available = 0;
            for (int later = value + 1; later < N; ++later) {
                available += later != center;
            }
            if (available < needed - 1) {
                continue;
            }
            current.push_back(value);
            choose_rows(center, value + 1, needed - 1, current);
            current.pop_back();
        }
    }

    void build_rows() {
        for (int center = 0; center < N; ++center) {
            vector<int> current;
            choose_rows(center, 0, 4, current);
            const int expected = (N - 1) * (N - 2) * (N - 3) * (N - 4) / 24;
            if (rows[center].size() != static_cast<size_t>(expected)) {
                throw runtime_error("row enumeration mismatch");
            }
        }
    }

    void add_strict_row(
        int p0, int c0, int p1, int c1, int p2, int c2, int p3, int c3
    ) {
        strict_rows.push_back({{p0, p1, p2, p3}, {c0, c1, c2, c3}});
    }

    void build_strict_rows() {
        for (int a = 0; a < N; ++a) {
            for (int b = a + 1; b < N; ++b) {
                for (int c = b + 1; c < N; ++c) {
                    for (int d = c + 1; d < N; ++d) {
                        add_strict_row(
                            pair_index[a][c], 1, pair_index[b][d], 1,
                            pair_index[a][b], -1, pair_index[c][d], -1
                        );
                        add_strict_row(
                            pair_index[a][c], 1, pair_index[b][d], 1,
                            pair_index[a][d], -1, pair_index[b][c], -1
                        );
                    }
                }
            }
        }
    }

    bool in_open_arc(int a, int b, int x) const {
        int ab = (b - a + N) % N;
        int ax = (x - a + N) % N;
        return x != a && x != b && ax < ab;
    }

    bool chords_cross(int a, int b, int c, int d) const {
        if (a == c || a == d || b == c || b == d) {
            return false;
        }
        return in_open_arc(a, b, c) != in_open_arc(a, b, d);
    }

    bool rows_compatible(int first, const Row& left, int second, const Row& right) const {
        int intersection = left.mask & right.mask;
        int count = __builtin_popcount(static_cast<unsigned>(intersection));
        if (count > 2) {
            return false;
        }
        if (count < 2) {
            return true;
        }
        int witnesses[2];
        int index = 0;
        for (int value = 0; value < N; ++value) {
            if (intersection & (1 << value)) {
                witnesses[index++] = value;
            }
        }
        return chords_cross(first, second, witnesses[0], witnesses[1]);
    }

    void build_compatibility() {
        compatible.resize(N);
        for (int first = 0; first < N; ++first) {
            compatible[first].resize(rows[first].size());
            for (int left = 0; left < static_cast<int>(rows[first].size()); ++left) {
                compatible[first][left].resize(N);
                for (int second = 0; second < N; ++second) {
                    if (first == second) {
                        continue;
                    }
                    compatible[first][left][second].resize(rows[second].size());
                    for (int right = 0; right < static_cast<int>(rows[second].size()); ++right) {
                        compatible[first][left][second][right] = rows_compatible(
                            first, rows[first][left], second, rows[second][right]
                        );
                    }
                }
            }
        }
    }

    static int find_root(array<int, P>& parent, int value) {
        while (parent[value] != value) {
            parent[value] = parent[parent[value]];
            value = parent[value];
        }
        return value;
    }

    static void unite(array<int, P>& parent, int left, int right) {
        left = find_root(parent, left);
        right = find_root(parent, right);
        if (left == right) {
            return;
        }
        if (right < left) {
            swap(left, right);
        }
        parent[right] = left;
    }

    // Encode a primitive sparse quotient vector. Coefficients before
    // normalization are in {-2,-1,1,2}.
    static uint64_t packed_vector(
        const array<int, P>& parent_roots,
        const StrictRow& row,
        bool inverse
    ) {
        array<int, P> coefficients{};
        for (int i = 0; i < 4; ++i) {
            coefficients[parent_roots[row.pair_indices[i]]] +=
                inverse ? -row.coefficients[i] : row.coefficients[i];
        }
        int divisor = 0;
        for (int coefficient : coefficients) {
            divisor = gcd(divisor, abs(coefficient));
        }
        if (divisor > 1) {
            for (int& coefficient : coefficients) {
                coefficient /= divisor;
            }
        }
        uint64_t packed = 0;
        int length = 0;
        for (int root = 0; root < P; ++root) {
            int coefficient = coefficients[root];
            if (coefficient == 0) {
                continue;
            }
            int code = coefficient == -2 ? 1 : coefficient == -1 ? 2 :
                       coefficient == 1 ? 3 : coefficient == 2 ? 4 : 0;
            if (code == 0) {
                throw runtime_error("unexpected quotient coefficient");
            }
            uint64_t item = static_cast<uint64_t>((root << 3) | code);
            // A root needs six bits (0..44) and the coefficient code needs
            // three, so entries occupy nine nonoverlapping bits.
            packed |= item << (9 * length);
            ++length;
        }
        packed |= static_cast<uint64_t>(length) << 60;
        return packed;
    }

    // 0 = clean, 1 = self-edge, 2 = positive-scalar inverse pair.
    int kalmanson_status() const {
        array<int, P> parent;
        for (int index = 0; index < P; ++index) {
            parent[index] = index;
        }
        for (int center = 0; center < N; ++center) {
            if (!assigned[center]) {
                continue;
            }
            const Row& row = rows[center][selected[center]];
            for (int index = 1; index < 4; ++index) {
                unite(parent, row.spokes[0], row.spokes[index]);
            }
        }
        for (int index = 0; index < P; ++index) {
            parent[index] = find_root(parent, index);
        }
        unordered_set<uint64_t> seen;
        seen.reserve(strict_rows.size() * 2);
        for (const StrictRow& row : strict_rows) {
            uint64_t key = packed_vector(parent, row, false);
            if ((key >> 60) == 0) {
                return 1;
            }
            uint64_t inverse = packed_vector(parent, row, true);
            if (seen.find(inverse) != seen.end()) {
                return 2;
            }
            seen.insert(key);
        }
        return 0;
    }

    vector<int> valid_options(int center) const {
        vector<int> output;
        for (int option = 0; option < static_cast<int>(rows[center].size()); ++option) {
            const Row& row = rows[center][option];
            bool ok = true;
            for (int other = 0; other < N && ok; ++other) {
                if (assigned[other] && !compatible[center][option][other][selected[other]]) {
                    ok = false;
                }
            }
            for (int witness : row.witnesses) {
                if (indegrees[witness] >= INDEGREE_CAP) {
                    ok = false;
                }
            }
            for (int pair_value : row.witness_pairs) {
                if (pair_counts[pair_value] >= PAIR_CAP) {
                    ok = false;
                }
            }
            if (ok) {
                output.push_back(option);
            }
        }
        return output;
    }

    void update(int center, int option, int delta) {
        const Row& row = rows[center][option];
        assigned[center] = delta > 0;
        selected[center] = option;
        assigned_count += delta;
        for (int witness : row.witnesses) {
            indegrees[witness] += delta;
        }
        for (int pair_value : row.witness_pairs) {
            pair_counts[pair_value] += delta;
        }
    }

    void print_witness() const {
        cout << "\"witness\":[";
        for (int center = 0; center < N; ++center) {
            if (center) cout << ',';
            cout << '[';
            const Row& row = rows[center][selected[center]];
            for (int index = 0; index < 4; ++index) {
                if (index) cout << ',';
                cout << row.witnesses[index];
            }
            cout << ']';
        }
        cout << ']';
    }

    void dfs() {
        if (found) return;
        ++nodes;
        if (assigned_count == N) {
            found = true;
            return;
        }
        int best_center = -1;
        vector<int> best_options;
        bool first = true;
        for (int center = 0; center < N; ++center) {
            if (assigned[center]) continue;
            vector<int> options = valid_options(center);
            if (first || options.size() < best_options.size()) {
                first = false;
                best_center = center;
                best_options = move(options);
                if (best_options.empty()) break;
            }
        }
        for (int option : best_options) {
            update(best_center, option, 1);
            int status = kalmanson_status();
            if (status == 1) ++self_edges;
            else if (status == 2) ++inverse_pairs;
            else dfs();
            if (found) return;
            update(best_center, option, -1);
        }
    }
};

}  // namespace

int main(int argc, char** argv) {
    Search search;
    int row0_index = -1;
    if (argc == 2) {
        row0_index = stoi(argv[1]);
        if (row0_index < 0 || row0_index >= static_cast<int>(search.rows[0].size())) {
            cerr << "row0 index out of range\n";
            return 2;
        }
        search.update(0, row0_index, 1);
        int status = search.kalmanson_status();
        if (status == 1) ++search.self_edges;
        else if (status == 2) ++search.inverse_pairs;
        else search.dfs();
    } else if (argc == 1) {
        search.dfs();
    } else {
        cerr << "usage: n10_kalmanson_pair_filter_probe [row0-index]\n";
        return 2;
    }
    cout << '{';
    cout << "\"n\":" << N << ',';
    cout << "\"nodes\":" << search.nodes << ',';
    cout << "\"self_edge_prunes\":" << search.self_edges << ',';
    cout << "\"inverse_pair_prunes\":" << search.inverse_pairs << ',';
    cout << "\"satisfiable\":" << (search.found ? "true" : "false");
    if (row0_index >= 0) {
        cout << ",\"row0_index\":" << row0_index;
    }
    if (search.found) {
        cout << ',';
        search.print_witness();
    }
    cout << "}\n";
    return 0;
}
