// Certificate replay with explicit equality graphs, not the search's DSU or hashes.
// This verifies the supplied elementary proof stream. It does not discover
// contradictions or accept a residual as geometric. Python checks residual proofs.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr int M = 7, N = 21, P = 210;
using Graph = std::array<std::array<int, 2>, M>;
using Selected = std::array<std::array<int, 4>, N>;
std::array<std::array<int, N>, N> pair_index{};
std::vector<std::array<int, 2>> pairs;
std::vector<std::array<int, 4>> inequalities;

void require(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
void initialize() {
    for (int a = 0; a < N; ++a) for (int b = a + 1; b < N; ++b) {
        pair_index[a][b] = pair_index[b][a] = int(pairs.size());
        pairs.push_back({a, b});
    }
    for (int a = 0; a < N; ++a) for (int b = a + 1; b < N; ++b)
        for (int c = b + 1; c < N; ++c) for (int d = c + 1; d < N; ++d) {
            inequalities.push_back({pair_index[a][c], pair_index[b][d], pair_index[a][b], pair_index[c][d]});
            inequalities.push_back({pair_index[a][c], pair_index[b][d], pair_index[a][d], pair_index[b][c]});
        }
}
unsigned read_byte(std::istream& input) {
    int x = input.get();
    require(x != std::char_traits<char>::eof(), "truncated proof stream");
    return unsigned(x);
}
unsigned read_u16(std::istream& input) {
    unsigned low = read_byte(input);
    return low + 256 * read_byte(input);
}
std::array<int, P> equality_components(const Selected& selected) {
    std::array<std::array<int, 12>, P> adjacency{};
    std::array<int, P> degree{};
    auto edge = [&](int a, int b) {
        if (a == b) return;
        require(degree[a] < 12 && degree[b] < 12, "equality graph capacity exceeded");
        adjacency[a][degree[a]++] = b;
        adjacency[b][degree[b]++] = a;
    };
    for (auto ab : pairs)
        edge(pair_index[ab[0]][ab[1]], pair_index[(ab[0] + M) % N][(ab[1] + M) % N]);
    for (int i = 0; i < N; ++i)
        for (int k = 1; k < 4; ++k)
            edge(pair_index[i][selected[i][0]], pair_index[i][selected[i][k]]);
    std::array<int, P> label{};
    label.fill(-1);
    for (int first = 0; first < P; ++first) {
        if (label[first] >= 0) continue;
        std::array<int, P> queue{};
        int head = 0, tail = 0;
        label[first] = first;
        queue[tail++] = first;
        while (head < tail) {
            int a = queue[head++];
            for (int k = 0; k < degree[a]; ++k) {
                int b = adjacency[a][k];
                if (label[b] < 0) { label[b] = first; queue[tail++] = b; }
            }
        }
    }
    return label;
}
std::map<int, int> primitive(unsigned index, const std::array<int, P>& labels) {
    require(index < inequalities.size(), "inequality index out of range");
    auto q = inequalities[index];
    std::map<int, int> result;
    ++result[labels[q[0]]]; ++result[labels[q[1]]];
    --result[labels[q[2]]]; --result[labels[q[3]]];
    int divisor = 0;
    for (auto it = result.begin(); it != result.end();) {
        if (it->second == 0) it = result.erase(it);
        else { divisor = std::gcd(divisor, std::abs(it->second)); ++it; }
    }
    for (auto& kv : result) kv.second /= divisor;
    return result;
}
void verify_elementary(unsigned kind, unsigned x, unsigned y, const Selected& selected) {
    if (kind == 1) {
        int a = int(x) / N, b = int(x) % N;
        int c = int(y) / N, d = int(y) % N;
        require(0 <= a && a < b && b < N && 0 <= c && c < d && d < N, "bad crossing indices");
        std::vector<int> common;
        for (int u : selected[a])
            if (std::find(selected[b].begin(), selected[b].end(), u) != selected[b].end()) common.push_back(u);
        require(std::find(common.begin(), common.end(), c) != common.end() &&
                std::find(common.begin(), common.end(), d) != common.end(), "unsupported witness equality");
        if (common.size() > 2) return; // two distinct circles cannot share three points
        require(common.size() == 2, "insufficient common witnesses");
        // Shared vertices cannot be either row center, because rows exclude self.
        require(c != a && c != b && d != a && d != b, "non-distinct chord endpoints");
        require((a < c && c < b) == (a < d && d < b), "claimed noncrossing chords cross");
        return;
    }
    require(kind == 2 || kind == 3, "unknown elementary certificate");
    auto labels = equality_components(selected);
    auto a = primitive(x, labels);
    if (kind == 2) {
        require(y == 65535 && a.empty(), "false zero-vector certificate");
    } else {
        auto b = primitive(y, labels);
        require(x != y && !a.empty() && !b.empty(), "degenerate inverse certificate");
        for (auto& kv : b) kv.second = -kv.second;
        require(a == b, "strict Kalmanson vectors are not positive-scalar opposites");
    }
}
}

int main(int argc, char** argv) {
    try {
        require(argc == 2, "usage: phase_replay PROOF.bin < radial_graphs.txt");
        initialize();
        std::ifstream proof(argv[1], std::ios::binary);
        require(bool(proof), "cannot open proof");
        char header[8]; proof.read(header, 8);
        require(proof.gcount() == 8 && std::string(header, 8) == "C3P7v1\r\n", "wrong proof format");
        std::array<uint64_t, 5> count{};
        int graph_count = 0;
        std::string line;
        while (std::getline(std::cin, line)) {
            require(!line.empty(), "empty graph input");
            Graph graph{}; std::istringstream stream(line);
            for (auto& row : graph) for (int& target : row)
                require(bool(stream >> target), "incomplete graph input");
            std::string trailing;
            require(!(stream >> trailing), "trailing graph fields");
            for (int i = 0; i < M; ++i) {
                require(graph[i][0] >= 0 && graph[i][0] < graph[i][1] && graph[i][1] < M &&
                        graph[i][0] != i && graph[i][1] != i, "invalid graph row");
                for (int j : graph[i])
                    require(graph[j][0] != i && graph[j][1] != i, "reciprocal graph input");
            }
            std::array<int, M> order{};
            std::iota(order.begin(), order.end(), 0);
            do {
                std::array<int, M> position{};
                for (int i = 0; i < M; ++i) position[order[i]] = i;
                std::vector<std::array<int, 2>> choices;
                unsigned alternatives = 1;
                for (int i = 0; i < M; ++i) for (int j : graph[i]) {
                    if (i < j) { choices.push_back({0, position[j] > position[i] ? 2 : 1}); alternatives *= 2; }
                    else choices.push_back({position[j] > position[i] ? 1 : 2, -1});
                }
                for (unsigned code = 0; code < alternatives; ++code) {
                    unsigned rest = code;
                    std::array<int, 2 * M> gains{};
                    for (int k = 0; k < 2 * M; ++k) {
                        if (choices[k][1] < 0) gains[k] = choices[k][0];
                        else { gains[k] = choices[k][rest % 2]; rest /= 2; }
                    }
                    require(rest == 0, "mixed-radix decoding failure");
                    Selected selected{};
                    for (int i = 0; i < M; ++i) for (int layer = 0; layer < 3; ++layer) {
                        auto& row = selected[M * layer + position[i]];
                        row[0] = M * ((layer + 1) % 3) + position[i];
                        row[1] = M * ((layer + 2) % 3) + position[i];
                        for (int j = 0; j < 2; ++j)
                            row[j + 2] = M * ((layer + gains[2*i+j]) % 3) + position[graph[i][j]];
                    }
                    unsigned kind = read_byte(proof), a = read_u16(proof), b = read_u16(proof);
                    require(1 <= kind && kind <= 4, "unknown proof record kind");
                    ++count[0];
                    if (kind < 4) verify_elementary(kind, a, b, selected);
                    else {
                        require(a == count[4] && b == 0, "residual coverage/index mismatch");
                        std::cout << "{\"rows\":[";
                        for (int i = 0; i < M; ++i) {
                            if (i) std::cout << ',';
                            std::cout << ((1 << graph[i][0]) | (1 << graph[i][1]));
                        }
                        std::cout << "],\"order\":[";
                        for (int i = 0; i < M; ++i) { if (i) std::cout << ','; std::cout << order[i]; }
                        std::cout << "],\"gains\":[";
                        for (int i = 0; i < 2*M; ++i) { if (i) std::cout << ','; std::cout << gains[i]; }
                        std::cout << "]}\n";
                    }
                    ++count[kind];
                }
            } while (std::next_permutation(order.begin() + 1, order.end()));
            ++graph_count;
        }
        require(graph_count > 0 && std::cin.eof(), "no graph data or input failure");
        require(proof.get() == std::char_traits<char>::eof(), "trailing proof records");
        std::cerr << "{\"graphs\":" << graph_count << ",\"cases\":" << count[0]
                  << ",\"crossing\":" << count[1] << ",\"kalmanson_zero\":" << count[2]
                  << ",\"kalmanson_inverse\":" << count[3] << ",\"angle_residuals\":" << count[4]
                  << ",\"exhausted_supplied_domain\":true,\"elementary_replay_passed\":true}\n";
        return 0;
    } catch (const std::exception& e) { std::cerr << "ERROR: " << e.what() << '\n'; return 2; }
}
