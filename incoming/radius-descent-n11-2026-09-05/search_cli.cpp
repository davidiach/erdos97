// Reporting-only adapter. Keep the hash-pinned search implementation unchanged.
#define main archived_search_main
#include "exact_search.cpp"
#undef main
#include <limits>

namespace {
uint64_t parse_unsigned(const string& value, const string& label) {
    if (value.empty() || value.find_first_not_of("0123456789") != string::npos)
        throw invalid_argument(label + " must be a nonnegative integer");
    size_t used = 0;
    auto number = stoull(value, &used);
    if (used != value.size()) throw invalid_argument("invalid " + label);
    return number;
}

void report(const Search& search, int slice, double seconds) {
    const bool survivor = !search.solutions.empty();
    const bool stopped_at_survivor = search.stop_at_first && survivor;
    // Conservatively withhold exhaustion when first-survivor stopping is used,
    // even if that survivor happened to be the last possible leaf.
    const bool exhausted = !search.aborted && !stopped_at_survivor;
    const bool decision_complete = survivor || exhausted;
    const char* reason = search.aborted ? "node_limit" :
                         stopped_at_survivor ? "survivor_found" : "exhausted";
    cout << boolalpha
         << "{\"schema\":2,\"n\":" << N
         << ",\"row_count\":" << search.R << ",\"slice\":" << slice
         << ",\"complete\":" << exhausted // deprecated alias, now unambiguous
         << ",\"exhausted\":" << exhausted
         << ",\"decision_complete\":" << decision_complete
         << ",\"termination_reason\":\"" << reason << '"'
         << ",\"survivor\":" << survivor
         << ",\"relaxation_unsat\":" << (exhausted && !survivor)
         << ",\"enumerate_all\":" << !search.stop_at_first
         << ",\"solution_count\":" << search.solutions.size()
         << ",\"nodes\":" << search.st.visits
         << ",\"trials\":" << search.st.trials
         << ",\"pair_dead\":" << search.st.pairdead
         << ",\"turn_prunes\":" << search.st.turn
         << ",\"zero_prunes\":" << search.st.zero
         << ",\"inverse_prunes\":" << search.st.inverse
         << ",\"seconds\":" << seconds;
    if (survivor) {
        cout << ",\"witnesses\":[";
        for (int i = 0; i < N; ++i) {
            if (i) cout << ',';
            cout << '[';
            const auto& row = search.rows[i][search.solutions[0][i]];
            for (int j = 0; j < 4; ++j) {
                if (j) cout << ',';
                cout << row.w[j];
            }
            cout << ']';
        }
        cout << ']';
    }
    cout << "}\n";
}
} // namespace

int main(int argc, char** argv) {
    try {
        int slice = -1;
        bool use_turn = true, use_k = true, enumerate_all = false;
        uint64_t limit = 0;
        for (int i = 1; i < argc; ++i) {
            const string arg = argv[i];
            if (arg == "--no-turn") use_turn = false;
            else if (arg == "--no-kalmanson") use_k = false;
            else if (arg == "--enumerate-all") enumerate_all = true;
            else if (arg == "--limit") {
                if (++i == argc) throw invalid_argument("--limit needs a value");
                limit = parse_unsigned(argv[i], "limit");
            } else {
                if (slice != -1) throw invalid_argument("only one slice may be supplied");
                const auto value = parse_unsigned(arg, "slice");
                if (value > uint64_t(numeric_limits<int>::max()))
                    throw invalid_argument("slice out of range");
                slice = int(value);
            }
        }
        const auto begin = chrono::steady_clock::now();
        Search search;
        search.use_turn = use_turn;
        search.use_k = use_k;
        search.limit = limit;
        search.stop_at_first = !enumerate_all;
        State state;
        if (slice >= 0) {
            if (slice >= search.R) throw invalid_argument("slice out of range");
            search.place(state, 0, slice, 1);
        }
        search.dfs(state);
        report(search, slice, chrono::duration<double>(chrono::steady_clock::now() - begin).count());
        return search.aborted ? 3 : 0;
    } catch (const exception& error) {
        cerr << error.what() << '\n';
        return 2;
    }
}
