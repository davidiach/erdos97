#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

using namespace std;

struct RowData {
    int mask;
    array<int, 4> bits;
    array<int, 6> witnessPairs;
    array<int, 4> selectedPairs;
    vector<pair<int, int>> strictEdges;
};

struct Search {
    int N, row_size = 4, pair_cap = 2, max_indegree, M, P;
    vector<pair<int, int>> pairs;
    int pidx[12][12];
    vector<vector<RowData>> rows;
    vector<vector<vector<vector<unsigned char>>>> compat;
    long long nodes = 0, full = 0;
    long long partial_self = 0, partial_cycle = 0, row0_self = 0, row0_cycle = 0;
    bool aborted = false;
    long long node_limit = 0;
    int assigned[12];
    int assignRow[12];
    int assignCount = 0;
    int col[12];
    int wpc[66];

    explicit Search(int n) : N(n) {
        if (N < 5 || N > 10) {
            throw runtime_error("this replay supports 5 <= n <= 10");
        }
        max_indegree = (pair_cap * (N - 1)) / (row_size - 1);
        memset(pidx, -1, sizeof(pidx));
        for (int i = 0; i < N; i++) {
            for (int j = i + 1; j < N; j++) {
                pidx[i][j] = pidx[j][i] = static_cast<int>(pairs.size());
                pairs.push_back({i, j});
            }
        }
        P = static_cast<int>(pairs.size());
        build_rows();
        M = static_cast<int>(rows[0].size());
        build_compat();
        memset(assigned, 0, sizeof(assigned));
        memset(col, 0, sizeof(col));
        memset(wpc, 0, sizeof(wpc));
    }

    int mask_from(const vector<int> &v) {
        int m = 0;
        for (int x : v) {
            m |= 1 << x;
        }
        return m;
    }

    void comb(int c, int start, int k, vector<int> &cur, vector<int> &labels) {
        if (k == 0) {
            RowData rd;
            rd.mask = mask_from(cur);
            for (int i = 0; i < 4; i++) {
                rd.bits[i] = cur[i];
            }
            int q = 0;
            for (int i = 0; i < 4; i++) {
                for (int j = i + 1; j < 4; j++) {
                    rd.witnessPairs[q++] = pidx[cur[i]][cur[j]];
                }
            }
            for (int i = 0; i < 4; i++) {
                rd.selectedPairs[i] = pidx[c][cur[i]];
            }
            array<int, 4> w = rd.bits;
            sort(w.begin(), w.end(), [&](int a, int b) {
                return ((a - c + N) % N) < ((b - c + N) % N);
            });
            for (int os = 0; os < 4; os++) {
                for (int oe = os + 1; oe < 4; oe++) {
                    for (int is = 0; is < 4; is++) {
                        for (int ie = is + 1; ie < 4; ie++) {
                            if (os == is && oe == ie) {
                                continue;
                            }
                            if (os <= is && ie <= oe && (os < is || ie < oe)) {
                                rd.strictEdges.push_back(
                                    {pidx[w[os]][w[oe]], pidx[w[is]][w[ie]]}
                                );
                            }
                        }
                    }
                }
            }
            rows[c].push_back(rd);
            return;
        }
        for (int idx = start; idx <= static_cast<int>(labels.size()) - k; idx++) {
            cur.push_back(labels[idx]);
            comb(c, idx + 1, k - 1, cur, labels);
            cur.pop_back();
        }
    }

    void build_rows() {
        rows.assign(N, {});
        for (int c = 0; c < N; c++) {
            vector<int> labels;
            for (int t = 0; t < N; t++) {
                if (t != c) {
                    labels.push_back(t);
                }
            }
            vector<int> cur;
            comb(c, 0, 4, cur, labels);
        }
    }

    bool in_open_arc(int a, int b, int x) {
        return ((x - a + N) % N) < ((b - a + N) % N) && x != a && x != b;
    }

    bool chords_cross(int a, int b, int c, int d) {
        if (a == c || a == d || b == c || b == d) {
            return false;
        }
        return in_open_arc(a, b, c) != in_open_arc(a, b, d);
    }

    void build_compat() {
        compat.assign(N, {});
        for (int i = 0; i < N; i++) {
            compat[i].assign(M, {});
            for (int r = 0; r < M; r++) {
                compat[i][r].assign(N, {});
            }
        }
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                if (i == j) {
                    continue;
                }
                for (int ri = 0; ri < static_cast<int>(rows[i].size()); ri++) {
                    compat[i][ri][j].assign(rows[j].size(), 0);
                    for (int rj = 0; rj < static_cast<int>(rows[j].size()); rj++) {
                        int inter = rows[i][ri].mask & rows[j][rj].mask;
                        int cnt = __builtin_popcount(static_cast<unsigned>(inter));
                        bool ok = true;
                        if (cnt > pair_cap) {
                            ok = false;
                        } else if (cnt == pair_cap) {
                            int b[2], k = 0;
                            for (int x = 0; x < N; x++) {
                                if ((inter >> x) & 1) {
                                    b[k++] = x;
                                }
                            }
                            ok = chords_cross(i, j, b[0], b[1]);
                        }
                        compat[i][ri][j][rj] = ok;
                    }
                }
            }
        }
    }

    string status() {
        int parent[66];
        for (int i = 0; i < P; i++) {
            parent[i] = i;
        }
        function<int(int)> find = [&](int x) {
            while (parent[x] != x) {
                parent[x] = parent[parent[x]];
                x = parent[x];
            }
            return x;
        };
        auto unite = [&](int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra == rb) {
                return;
            }
            if (rb < ra) {
                swap(ra, rb);
            }
            parent[rb] = ra;
        };
        for (int c = 0; c < N; c++) {
            if (assigned[c]) {
                auto &rd = rows[c][assignRow[c]];
                int base = rd.selectedPairs[0];
                for (int i = 1; i < 4; i++) {
                    unite(base, rd.selectedPairs[i]);
                }
            }
        }
        uint64_t adj[66];
        for (int i = 0; i < P; i++) {
            adj[i] = 0;
        }
        for (int c = 0; c < N; c++) {
            if (assigned[c]) {
                auto &rd = rows[c][assignRow[c]];
                for (auto &e : rd.strictEdges) {
                    int ro = find(e.first), ri = find(e.second);
                    if (ro == ri) {
                        return "self_edge";
                    }
                    adj[ro] |= 1ULL << ri;
                }
            }
        }
        unsigned char color[66];
        memset(color, 0, sizeof(color));
        function<bool(int)> dfs = [&](int v) {
            color[v] = 1;
            uint64_t m = adj[v];
            while (m) {
                int u = __builtin_ctzll(m);
                m &= m - 1;
                if (color[u] == 1) {
                    return true;
                }
                if (color[u] == 0 && dfs(u)) {
                    return true;
                }
            }
            color[v] = 2;
            return false;
        };
        for (int v = 0; v < P; v++) {
            if (adj[v] && color[v] == 0 && dfs(v)) {
                return "strict_cycle";
            }
        }
        return "ok";
    }

    vector<int> valid(int c) {
        vector<int> out;
        for (int r = 0; r < static_cast<int>(rows[c].size()); r++) {
            bool ok = true;
            for (int oc = 0; oc < N; oc++) {
                if (assigned[oc] && !compat[c][r][oc][assignRow[oc]]) {
                    ok = false;
                    break;
                }
            }
            if (!ok) {
                continue;
            }
            auto &rd = rows[c][r];
            for (int t : rd.bits) {
                if (col[t] >= max_indegree) {
                    ok = false;
                    break;
                }
            }
            if (!ok) {
                continue;
            }
            for (int pi : rd.witnessPairs) {
                if (wpc[pi] >= pair_cap) {
                    ok = false;
                    break;
                }
            }
            if (ok) {
                out.push_back(r);
            }
        }
        return out;
    }

    void add(int c, int r) {
        assigned[c] = 1;
        assignRow[c] = r;
        assignCount++;
        for (int t : rows[c][r].bits) {
            col[t]++;
        }
        for (int pi : rows[c][r].witnessPairs) {
            wpc[pi]++;
        }
    }

    void remove(int c, int r) {
        for (int pi : rows[c][r].witnessPairs) {
            wpc[pi]--;
        }
        for (int t : rows[c][r].bits) {
            col[t]--;
        }
        assigned[c] = 0;
        assignCount--;
    }

    void dfs() {
        if (aborted) {
            return;
        }
        nodes++;
        if (node_limit && nodes >= node_limit) {
            aborted = true;
            return;
        }
        if (assignCount == N) {
            full++;
            return;
        }
        int best = -1;
        vector<int> bestopts;
        bool first = true;
        for (int c = 0; c < N; c++) {
            if (!assigned[c]) {
                auto opts = valid(c);
                if (first || opts.size() < bestopts.size()) {
                    first = false;
                    best = c;
                    bestopts = std::move(opts);
                    if (bestopts.empty()) {
                        break;
                    }
                }
            }
        }
        if (bestopts.empty()) {
            return;
        }
        for (int r : bestopts) {
            add(best, r);
            string st = status();
            if (st == "ok") {
                dfs();
            } else if (st == "self_edge") {
                partial_self++;
            } else {
                partial_cycle++;
            }
            remove(best, r);
            if (aborted) {
                return;
            }
        }
    }

    struct RowSummary {
        int idx;
        array<int, 4> wit;
        long long nodes, full, self, cycle;
    };

    vector<RowSummary> run(int start, int end, bool progress) {
        vector<RowSummary> sums;
        auto t0 = chrono::steady_clock::now();
        for (int r = start; r < end; r++) {
            long long bn = nodes, bf = full, bs = partial_self, bc = partial_cycle;
            add(0, r);
            string st = status();
            if (st == "ok") {
                dfs();
            } else if (st == "self_edge") {
                row0_self++;
            } else {
                row0_cycle++;
            }
            remove(0, r);
            sums.push_back({r, rows[0][r].bits, nodes - bn, full - bf, partial_self - bs, partial_cycle - bc});
            if (progress && (r % 10 == 0 || r == end - 1)) {
                auto dt = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
                cerr << "row0 " << r << " nodes " << nodes << " full " << full
                     << " self " << partial_self << " cyc " << partial_cycle
                     << " t " << dt << "\n";
            }
            if (aborted) {
                break;
            }
        }
        return sums;
    }
};

int main(int argc, char **argv) {
    int N = 10, start = 0, end = -1;
    string out;
    bool progress = false, norows = false;
    for (int i = 1; i < argc; i++) {
        string a = argv[i];
        if (a == "--n") {
            N = stoi(argv[++i]);
        } else if (a == "--start") {
            start = stoi(argv[++i]);
        } else if (a == "--end") {
            end = stoi(argv[++i]);
        } else if (a == "--out") {
            out = argv[++i];
        } else if (a == "--progress") {
            progress = true;
        } else if (a == "--no-rows") {
            norows = true;
        }
    }
    Search s(N);
    if (end < 0) {
        end = s.M;
    }
    auto sums = s.run(start, end, progress);
    ostringstream js;
    js << "{\n  \"summary\": {\n";
    js << "    \"N\": " << N << ",\n";
    js << "    \"M\": " << s.M << ",\n";
    js << "    \"row0_start\": " << start << ",\n";
    js << "    \"row0_end\": " << end << ",\n";
    js << "    \"vertex_circle_pruning\": true,\n";
    js << "    \"nodes\": " << s.nodes << ",\n";
    js << "    \"full\": " << s.full << ",\n";
    js << "    \"aborted\": " << (s.aborted ? "true" : "false") << ",\n";
    js << "    \"counts\": {\"partial_self_edge\": " << s.partial_self
       << ", \"partial_strict_cycle\": " << s.partial_cycle << "}\n  }";
    if (!norows) {
        js << ",\n  \"row_summaries\": [\n";
        for (size_t i = 0; i < sums.size(); i++) {
            auto &r = sums[i];
            js << "    {\"row0_index\": " << r.idx << ", \"row0_witnesses\": [";
            for (int k = 0; k < 4; k++) {
                if (k) {
                    js << ", ";
                }
                js << r.wit[k];
            }
            js << "], \"nodes\": " << r.nodes << ", \"full\": " << r.full
               << ", \"counts\": {";
            bool first = true;
            if (r.self) {
                js << "\"partial_self_edge\": " << r.self;
                first = false;
            }
            if (r.cycle) {
                if (!first) {
                    js << ", ";
                }
                js << "\"partial_strict_cycle\": " << r.cycle;
            }
            js << "}}" << (i + 1 < sums.size() ? "," : "") << "\n";
        }
        js << "  ]";
    }
    js << "\n}\n";
    string text = js.str();
    if (!out.empty()) {
        ofstream(out) << text;
    }
    cout << text;
}
