/*
 * Fast vertex-circle exhaustive checker for Erdos Problem #97 selected-witness
 * search. Reproduces the algorithm in
 *   src/erdos97/n9_vertex_circle_exhaustive.py
 * and
 *   src/erdos97/generic_vertex_search.py
 * but in optimized C with bitset compatibility tables and a tight backtrack.
 *
 * The default build (compiled with -DN_VAL=11) targets n=11. Built with
 * -DN_VAL=9 it reproduces the reference n=9 counts (16752 nodes, 0 full
 * assignments, 11271 self-edge prunes, 11011 strict-cycle prunes) which is
 * the correctness check for this implementation.
 *
 * Output is JSON-line per row0 with stable per-slice counts, and a final
 * summary line. The companion Python wrapper aggregates these and produces
 * the JSON artifact.
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifndef N_VAL
#define N_VAL 11
#endif

#define ROW_SIZE 4
#define PAIR_CAP 2
#define N N_VAL

/* Compile-time derived sizes. */
#define MAX_INDEGREE ((PAIR_CAP * (N - 1)) / (ROW_SIZE - 1))
#define NUM_PAIRS ((N * (N - 1)) / 2)
/* number of choose(n-1, 4): for n=11 -> 210, n=9 -> 70 */
#if N == 9
#define MAX_OPTS 70
#elif N == 10
#define MAX_OPTS 126
#elif N == 11
#define MAX_OPTS 210
#elif N == 12
#define MAX_OPTS 330
#else
#define MAX_OPTS 1000
#endif

/* Bitset width for a single OPTIONS[j] mask: ceil(MAX_OPTS / 64). */
#define BS_WORDS ((MAX_OPTS + 63) / 64)

/* ----- pair indexing ----- */
static int pair_index_table[N][N];

static int pair_index(int a, int b) {
    if (a == b) return -1;
    if (a > b) { int t = a; a = b; b = t; }
    return pair_index_table[a][b];
}

/* ----- options ----- */
static uint16_t options[N][MAX_OPTS];     /* row mask is 11-bit, fits in u16 */
static int num_options[N];

/* mask -> 4 sorted vertex indices */
static int8_t mask_bits_tbl[1u << N][ROW_SIZE];
/* mask -> 6 pair indices for the C(4,2)=6 witness pairs */
static int16_t row_pair_idx[1u << N][6];
/* (center, mask) -> 4 pair indices for selected witness pairs */
static int16_t sel_pair_idx[N][MAX_OPTS][ROW_SIZE];

/* (center, mask) -> witnesses sorted by cyclic distance (witness - center) % N */
static int8_t cyc_witnesses[N][MAX_OPTS][ROW_SIZE];

/* strict edges: list of (outer_pair_index, inner_pair_index) per (center, idx).
 * For 4 nested-position edges: 4 outer-positions x 4 inner-positions, but edges
 * count only "strictly contains" entries. For row_size=4, count is fixed at
 * the same value the Python code generates: 18 edges per row mask.
 */
#define MAX_STRICT_EDGES 18
static int16_t strict_outer[N][MAX_OPTS][MAX_STRICT_EDGES];
static int16_t strict_inner[N][MAX_OPTS][MAX_STRICT_EDGES];
static int n_strict_edges[N][MAX_OPTS];

/* Compatibility bitsets: compat[i][j][mask_i_index] = bitset over options[j].
 * Stored for both i<j and i>j (transposed for the i>j case) so that we can
 * intersect bitsets uniformly. compat[i][i][...] is unused. */
static uint64_t (*compat)[BS_WORDS] = NULL;

/* Compute index into compat tensor: ((i * N + j) * MAX_OPTS + mi_idx) * BS_WORDS */
static inline uint64_t *compat_row(int i, int j, int mi_idx) {
    return &compat[((i * N + j) * MAX_OPTS) + mi_idx][0];
}

/* ----- helpers ----- */
static int popcount(uint16_t m) {
    return __builtin_popcount(m);
}

static int in_open_arc(int a, int b, int x) {
    int da = (b - a + N) % N;
    int dx = (x - a + N) % N;
    return dx > 0 && dx < da;
}

static int chords_cross(int a, int b, int c, int d) {
    /* Strict crossing of two disjoint chords (a,b) and (c,d) in cyclic order. */
    if (a == c || a == d || b == c || b == d) return 0;
    int ic = in_open_arc(a, b, c);
    int id = in_open_arc(a, b, d);
    return ic != id;
}

/* ----- combination enumeration ----- */
static void build_options(void) {
    /* For each center, enumerate 4-subsets of {0..N-1}\{center}. */
    for (int center = 0; center < N; center++) {
        int targets[N - 1];
        int t = 0;
        for (int v = 0; v < N; v++) if (v != center) targets[t++] = v;
        int idx = 0;
        for (int a = 0; a < N - 1 - 3; a++)
        for (int b = a + 1; b < N - 1 - 2; b++)
        for (int c = b + 1; c < N - 1 - 1; c++)
        for (int d = c + 1; d < N - 1; d++) {
            uint16_t m = (uint16_t)((1u << targets[a]) | (1u << targets[b]) |
                                   (1u << targets[c]) | (1u << targets[d]));
            options[center][idx++] = m;
        }
        num_options[center] = idx;
    }
}

static void build_pair_index(void) {
    int idx = 0;
    for (int i = 0; i < N; i++)
        for (int j = i + 1; j < N; j++)
            pair_index_table[i][j] = pair_index_table[j][i] = idx++;
}

static void build_mask_tables(void) {
    /* Initialize sentinel. */
    for (int i = 0; i < N; i++)
        for (int idx = 0; idx < MAX_OPTS; idx++)
            for (int k = 0; k < ROW_SIZE; k++)
                cyc_witnesses[i][idx][k] = -1;

    /* For every encountered mask, fill mask_bits_tbl, row_pair_idx, and per
     * (center, mask) the cyclic ordering and selected pairs. */
    char filled[1u << N] = {0};

    for (int center = 0; center < N; center++) {
        for (int idx = 0; idx < num_options[center]; idx++) {
            uint16_t m = options[center][idx];
            if (!filled[m]) {
                int k = 0;
                for (int v = 0; v < N; v++)
                    if ((m >> v) & 1u) mask_bits_tbl[m][k++] = (int8_t)v;
                /* row pair indices: C(4,2)=6 unordered pairs */
                int p = 0;
                for (int x = 0; x < ROW_SIZE; x++)
                    for (int y = x + 1; y < ROW_SIZE; y++)
                        row_pair_idx[m][p++] =
                            (int16_t)pair_index(mask_bits_tbl[m][x], mask_bits_tbl[m][y]);
                filled[m] = 1;
            }
            /* Selected pair indices: pair(center, witness) for each witness. */
            for (int k = 0; k < ROW_SIZE; k++) {
                sel_pair_idx[center][idx][k] =
                    (int16_t)pair_index(center, mask_bits_tbl[m][k]);
            }
            /* Cyclic ordering: sort by (w - center) mod N. */
            int8_t sorted[ROW_SIZE];
            int dist[ROW_SIZE];
            for (int k = 0; k < ROW_SIZE; k++) {
                sorted[k] = mask_bits_tbl[m][k];
                dist[k] = (sorted[k] - center + N) % N;
            }
            /* tiny insertion sort by dist asc */
            for (int a = 1; a < ROW_SIZE; a++) {
                int kd = dist[a]; int kv = sorted[a]; int b = a - 1;
                while (b >= 0 && dist[b] > kd) {
                    dist[b + 1] = dist[b]; sorted[b + 1] = sorted[b]; b--;
                }
                dist[b + 1] = kd; sorted[b + 1] = kv;
            }
            for (int k = 0; k < ROW_SIZE; k++) cyc_witnesses[center][idx][k] = sorted[k];

            /* strict edges for (center, idx): enumerate all (outer_start, outer_end,
             * inner_start, inner_end) tuples with outer strictly contains inner.
             */
            int e = 0;
            for (int os = 0; os < ROW_SIZE; os++)
            for (int oe = os + 1; oe < ROW_SIZE; oe++)
            for (int is_ = 0; is_ < ROW_SIZE; is_++)
            for (int ie = is_ + 1; ie < ROW_SIZE; ie++) {
                if (os == is_ && oe == ie) continue;
                int contains = (os <= is_) && (ie <= oe) && (os < is_ || ie < oe);
                if (contains) {
                    int outer_p = pair_index(sorted[os], sorted[oe]);
                    int inner_p = pair_index(sorted[is_], sorted[ie]);
                    strict_outer[center][idx][e] = (int16_t)outer_p;
                    strict_inner[center][idx][e] = (int16_t)inner_p;
                    e++;
                }
            }
            n_strict_edges[center][idx] = e;
        }
    }
}

static void build_compatibility(void) {
    /* compat[i][j][mi_idx] = bitset over options[j] of compatible mj indices.
     * Built for both directions (i<j and i>j) by transposing. */
    size_t total = (size_t)N * (size_t)N * (size_t)MAX_OPTS;
    compat = (uint64_t (*)[BS_WORDS])calloc(total, sizeof(uint64_t[BS_WORDS]));
    if (!compat) { fprintf(stderr, "calloc compat failed\n"); exit(1); }

    for (int i = 0; i < N; i++) {
        for (int j = i + 1; j < N; j++) {
            for (int mi_idx = 0; mi_idx < num_options[i]; mi_idx++) {
                uint16_t mi = options[i][mi_idx];
                uint64_t *bs_ij = compat_row(i, j, mi_idx);
                for (int mj_idx = 0; mj_idx < num_options[j]; mj_idx++) {
                    uint16_t mj = options[j][mj_idx];
                    uint16_t common = (uint16_t)(mi & mj);
                    int csz = popcount(common);
                    int ok = 1;
                    if (csz > PAIR_CAP) ok = 0;
                    else if (csz == PAIR_CAP) {
                        /* find the two common vertices */
                        int cv[2]; int t = 0;
                        for (int v = 0; v < N && t < 2; v++)
                            if ((common >> v) & 1u) cv[t++] = v;
                        ok = chords_cross(i, j, cv[0], cv[1]);
                    }
                    if (ok) {
                        bs_ij[mj_idx >> 6] |= (1ULL << (mj_idx & 63));
                        /* Mirror into compat[j][i][mj_idx]: mi_idx is allowed. */
                        compat_row(j, i, mj_idx)[mi_idx >> 6] |= (1ULL << (mi_idx & 63));
                    }
                }
            }
        }
    }
}

/* ----- backtracking search state ----- */
static int g_n;
static int assigned_centers_mask;  /* bitmask of assigned centers */

static int column_counts[N];
static int witness_pair_counts[NUM_PAIRS];

/* Per-center allowed-options bitset over options[c]. We keep a stack of these,
 * one per assigned center, so backtrack restoration is cheap.
 * Layout: allowed[depth][center] is the bitset for `center` at depth `depth`.
 * On backtrack we just decrement depth.
 */
static uint64_t allowed_bs[N + 1][N][BS_WORDS];

/* Counters */
static uint64_t nodes_visited;
static uint64_t full_assignments;
static uint64_t partial_self_edge;
static uint64_t partial_strict_cycle;
static uint64_t debug_search_recurs;
static uint64_t debug_status_ok_iters;

/* Runtime-tunable: when fwd_check=1, skip recursion when any unassigned center
 * has empty allowed_bs after compatibility AND. This speeds up the search but
 * makes nodes_visited NOT match the generic Python checker (which has no
 * forward-checking short-circuit). full_assignments and prune counts remain
 * identical. Default: fwd_check=0 to keep nodes_visited matching Python.
 */
static int fwd_check = 0;

/* Union-find scratch over NUM_PAIRS. */
static int uf_parent[NUM_PAIRS];

static int uf_find(int x) {
    while (uf_parent[x] != x) {
        uf_parent[x] = uf_parent[uf_parent[x]];
        x = uf_parent[x];
    }
    return x;
}

static void uf_union(int a, int b) {
    int ra = uf_find(a), rb = uf_find(b);
    if (ra == rb) return;
    if (rb < ra) { int t = ra; ra = rb; rb = t; }
    uf_parent[rb] = ra;
}

/* Adjacency for cycle check on the quotient graph. We keep up to NUM_PAIRS
 * roots and an adjacency list of out-edges. */
static int adj_head[NUM_PAIRS];
static int adj_next[N * MAX_STRICT_EDGES * 2];
static int adj_to[N * MAX_STRICT_EDGES * 2];
static int adj_size;
static int color[NUM_PAIRS];

/* Iterative DFS cycle detection: returns 1 if cycle found. */
static int cycle_dfs(int start) {
    /* Iterative coloring DFS: 0 white, 1 gray (on stack), 2 black. */
    int stack_node[NUM_PAIRS * 2];
    int stack_iter[NUM_PAIRS * 2];
    int top = 0;
    stack_node[top] = start;
    stack_iter[top] = adj_head[start];
    color[start] = 1;
    while (top >= 0) {
        int u = stack_node[top];
        int e = stack_iter[top];
        if (e == -1) {
            color[u] = 2;
            top--;
            continue;
        }
        int v = adj_to[e];
        stack_iter[top] = adj_next[e];
        if (color[v] == 1) return 1;
        if (color[v] == 0) {
            color[v] = 1;
            top++;
            stack_node[top] = v;
            stack_iter[top] = adj_head[v];
        }
    }
    return 0;
}

/* Compute vertex-circle status from current full assignment at given depth.
 * Returns:
 *   0 = ok
 *   1 = self_edge
 *   2 = strict_cycle
 */
static int vertex_circle_status(int active_centers, int *centers, int *idxs) {
    /* Reset union-find. */
    for (int p = 0; p < NUM_PAIRS; p++) uf_parent[p] = p;
    /* Quotient by selected pairs (within each row, all 4 are equal). */
    for (int k = 0; k < active_centers; k++) {
        int c = centers[k];
        int mi = idxs[k];
        int base = sel_pair_idx[c][mi][0];
        for (int t = 1; t < ROW_SIZE; t++) {
            uf_union(base, sel_pair_idx[c][mi][t]);
        }
    }
    /* Build edges in quotient graph; detect self-edges. */
    adj_size = 0;
    for (int p = 0; p < NUM_PAIRS; p++) adj_head[p] = -1;
    for (int k = 0; k < active_centers; k++) {
        int c = centers[k];
        int mi = idxs[k];
        int ne = n_strict_edges[c][mi];
        for (int e = 0; e < ne; e++) {
            int outer_root = uf_find(strict_outer[c][mi][e]);
            int inner_root = uf_find(strict_inner[c][mi][e]);
            if (outer_root == inner_root) return 1;
            int aid = adj_size++;
            adj_to[aid] = inner_root;
            adj_next[aid] = adj_head[outer_root];
            adj_head[outer_root] = aid;
        }
    }
    /* Cycle check on the quotient DAG (we tolerate parallel edges). */
    for (int p = 0; p < NUM_PAIRS; p++) color[p] = 0;
    for (int p = 0; p < NUM_PAIRS; p++) {
        if (adj_head[p] != -1 && color[p] == 0) {
            if (cycle_dfs(p)) return 2;
        }
    }
    return 0;
}

/* Pick the unassigned center with min remaining options after applying all
 * filters: bitset compat, column-degree cap, witness-pair cap. */
static int pick_branch_center(int depth) {
    int best = -1, best_count = -1;
    for (int c = 0; c < N; c++) {
        if (assigned_centers_mask & (1 << c)) continue;
        uint64_t *bs = allowed_bs[depth][c];
        int cnt = 0;
        for (int w = 0; w < BS_WORDS; w++) {
            uint64_t word = bs[w];
            while (word) {
                int bit = __builtin_ctzll(word);
                word &= word - 1;
                int mi_idx = (w << 6) | bit;
                if (mi_idx >= num_options[c]) continue;
                uint16_t m = options[c][mi_idx];
                int8_t *vmb = mask_bits_tbl[m];
                int ok = 1;
                for (int k = 0; k < ROW_SIZE; k++) {
                    if (column_counts[vmb[k]] >= MAX_INDEGREE) { ok = 0; break; }
                }
                if (ok) {
                    for (int k = 0; k < 6; k++) {
                        if (witness_pair_counts[row_pair_idx[m][k]] >= PAIR_CAP) { ok = 0; break; }
                    }
                }
                if (ok) cnt++;
            }
        }
        if (best == -1 || cnt < best_count) {
            best = c;
            best_count = cnt;
            if (cnt == 0) return c;
        }
    }
    return best;
}

/* Backtrack at `depth`: assigned_centers_mask reflects depth assignments. */
static void search(int depth, int *centers_stack, int *idx_stack) {
    nodes_visited++;
    if (depth == N) {
        full_assignments++;
        return;
    }
    int center = pick_branch_center(depth);
    if (center < 0) return;
    uint64_t *bs = allowed_bs[depth][center];
    /* Iterate set bits. */
    for (int w = 0; w < BS_WORDS; w++) {
        uint64_t word = bs[w];
        while (word) {
            int bit = __builtin_ctzll(word);
            word &= word - 1;
            int mi_idx = (w << 6) | bit;
            if (mi_idx >= num_options[center]) continue;

            /* Apply column count constraint via mask. */
            uint16_t m = options[center][mi_idx];
            int8_t *vmb = mask_bits_tbl[m];
            int col_ok = 1;
            for (int k = 0; k < ROW_SIZE; k++) {
                if (column_counts[vmb[k]] >= MAX_INDEGREE) { col_ok = 0; break; }
            }
            if (!col_ok) continue;

            /* Witness pair-cap. */
            int wp_ok = 1;
            for (int k = 0; k < 6; k++) {
                if (witness_pair_counts[row_pair_idx[m][k]] >= PAIR_CAP) { wp_ok = 0; break; }
            }
            if (!wp_ok) continue;

            /* Apply assignment. */
            for (int k = 0; k < ROW_SIZE; k++) column_counts[vmb[k]]++;
            for (int k = 0; k < 6; k++) witness_pair_counts[row_pair_idx[m][k]]++;
            assigned_centers_mask |= (1 << center);
            centers_stack[depth] = center;
            idx_stack[depth] = mi_idx;

            /* Vertex-circle check at the new partial assignment. */
            int status = vertex_circle_status(depth + 1, centers_stack, idx_stack);

            if (status == 0) {
                debug_status_ok_iters++;
                /* Update allowed_bs for next depth: intersect with compatibility
                 * for all unassigned centers. With the symmetrized compat table
                 * this is just a bitwise AND in either direction.
                 */
                memcpy(allowed_bs[depth + 1], allowed_bs[depth], sizeof(allowed_bs[0]));
                int feasible = 1;
                for (int c2 = 0; c2 < N; c2++) {
                    if (c2 == center) continue;
                    if (assigned_centers_mask & (1 << c2)) continue;
                    uint64_t *src = compat_row(center, c2, mi_idx);
                    uint64_t *dst = allowed_bs[depth + 1][c2];
                    uint64_t any = 0;
                    for (int w2 = 0; w2 < BS_WORDS; w2++) {
                        dst[w2] &= src[w2];
                        any |= dst[w2];
                    }
                    if (fwd_check && !any) { feasible = 0; break; }
                }
                if (feasible) {
                    debug_search_recurs++;
                    search(depth + 1, centers_stack, idx_stack);
                }
            } else if (status == 1) {
                partial_self_edge++;
            } else {
                partial_strict_cycle++;
            }

            /* Unwind. */
            assigned_centers_mask &= ~(1 << center);
            for (int k = 0; k < 6; k++) witness_pair_counts[row_pair_idx[m][k]]--;
            for (int k = 0; k < ROW_SIZE; k++) column_counts[vmb[k]]--;
        }
    }
}

/* Build the TRANSPOSED compatibility row, so that for source center > target,
 * we can fetch the allowed bitset over options[target] directly. We do not
 * actually need this for n=11 if the speed is sufficient; the scanning above
 * is acceptable.
 */

/* Run the search starting from a fixed row0_index, return per-row0 counts. */
static void run_one_row0(int row0_idx, FILE *out, double *elapsed_out) {
    nodes_visited = 0;
    full_assignments = 0;
    partial_self_edge = 0;
    partial_strict_cycle = 0;
    debug_search_recurs = 0;
    debug_status_ok_iters = 0;

    /* Initialize allowed sets at depth=0 to "all" for every center. */
    for (int c = 0; c < N; c++) {
        uint64_t *bs = allowed_bs[0][c];
        for (int w = 0; w < BS_WORDS; w++) bs[w] = 0;
        for (int idx = 0; idx < num_options[c]; idx++) {
            bs[idx >> 6] |= (1ULL << (idx & 63));
        }
    }
    for (int c = 0; c < N; c++) column_counts[c] = 0;
    for (int p = 0; p < NUM_PAIRS; p++) witness_pair_counts[p] = 0;
    assigned_centers_mask = 0;

    /* Pin row0 = options[0][row0_idx]. */
    int centers_stack[N];
    int idx_stack[N];

    uint16_t m = options[0][row0_idx];
    /* Apply to column / witness counts. */
    int8_t *vmb = mask_bits_tbl[m];
    for (int k = 0; k < ROW_SIZE; k++) column_counts[vmb[k]]++;
    for (int k = 0; k < 6; k++) witness_pair_counts[row_pair_idx[m][k]]++;
    assigned_centers_mask |= 1;
    centers_stack[0] = 0;
    idx_stack[0] = row0_idx;

    /* Vertex-circle check at depth 1. */
    int status = vertex_circle_status(1, centers_stack, idx_stack);

    struct timespec ts0, ts1;
    clock_gettime(CLOCK_MONOTONIC, &ts0);

    if (status == 0) {
        memcpy(allowed_bs[1], allowed_bs[0], sizeof(allowed_bs[0]));
        for (int c2 = 1; c2 < N; c2++) {
            uint64_t *src = compat_row(0, c2, row0_idx);
            uint64_t *dst = allowed_bs[1][c2];
            for (int w2 = 0; w2 < BS_WORDS; w2++) dst[w2] &= src[w2];
        }
        search(1, centers_stack, idx_stack);
    } else if (status == 1) {
        /* row0 alone fails; this counts as a row0_<status> bookkeeping (Python
         * stores it under counts["row0_self_edge"]); we flag separately. */
        partial_self_edge++;
    } else if (status == 2) {
        partial_strict_cycle++;
    }

    clock_gettime(CLOCK_MONOTONIC, &ts1);
    double dt = (ts1.tv_sec - ts0.tv_sec) + (ts1.tv_nsec - ts0.tv_nsec) * 1e-9;
    *elapsed_out = dt;

    fprintf(out,
            "{\"row0_index\": %d, \"row0_mask\": %u, \"nodes_visited\": %" PRIu64
            ", \"full_assignments\": %" PRIu64
            ", \"partial_self_edge_prunes\": %" PRIu64
            ", \"partial_strict_cycle_prunes\": %" PRIu64
            ", \"elapsed_seconds\": %.6f}\n",
            row0_idx, (unsigned)m,
            nodes_visited, full_assignments,
            partial_self_edge, partial_strict_cycle, dt);
    (void)debug_search_recurs;
    (void)debug_status_ok_iters;
    fflush(out);
}

int main(int argc, char **argv) {
    int row0_start = 0;
    int row0_end = -1;
    const char *out_path = NULL;
    for (int a = 1; a < argc; a++) {
        if (!strcmp(argv[a], "--start") && a + 1 < argc) {
            row0_start = atoi(argv[++a]);
        } else if (!strcmp(argv[a], "--end") && a + 1 < argc) {
            row0_end = atoi(argv[++a]);
        } else if (!strcmp(argv[a], "--out") && a + 1 < argc) {
            out_path = argv[++a];
        } else if (!strcmp(argv[a], "--fwd-check")) {
            fwd_check = 1;
        } else if (!strcmp(argv[a], "--info")) {
            /* will print after init */
        }
    }

    g_n = N;
    build_pair_index();
    build_options();
    build_mask_tables();
    build_compatibility();

    if (row0_end < 0) row0_end = num_options[0];
    if (row0_start < 0) row0_start = 0;
    if (row0_end > num_options[0]) row0_end = num_options[0];

    FILE *out = stdout;
    if (out_path) {
        out = fopen(out_path, "w");
        if (!out) { fprintf(stderr, "open %s failed\n", out_path); return 1; }
    }

    fprintf(out,
            "{\"_meta\": true, \"n\": %d, \"row_size\": %d, \"pair_cap\": %d, \"max_indegree\": %d, "
            "\"num_pairs\": %d, \"row0_total\": %d, \"row0_start\": %d, \"row0_end\": %d, "
            "\"fwd_check\": %d}\n",
            N, ROW_SIZE, PAIR_CAP, MAX_INDEGREE, NUM_PAIRS, num_options[0],
            row0_start, row0_end, fwd_check);
    fflush(out);

    uint64_t total_nodes = 0, total_full = 0, total_se = 0, total_sc = 0;
    double total_elapsed = 0.0;

    for (int idx = row0_start; idx < row0_end; idx++) {
        double dt;
        run_one_row0(idx, out, &dt);
        total_nodes += nodes_visited;
        total_full += full_assignments;
        total_se += partial_self_edge;
        total_sc += partial_strict_cycle;
        total_elapsed += dt;
    }

    fprintf(out,
            "{\"_summary\": true, \"n\": %d, \"row0_start\": %d, \"row0_end\": %d, "
            "\"total_nodes_visited\": %" PRIu64 ", \"total_full_assignments\": %" PRIu64
            ", \"total_partial_self_edge\": %" PRIu64
            ", \"total_partial_strict_cycle\": %" PRIu64
            ", \"total_elapsed_seconds\": %.6f}\n",
            N, row0_start, row0_end,
            total_nodes, total_full, total_se, total_sc, total_elapsed);

    if (out_path) fclose(out);
    free(compat);
    return 0;
}
