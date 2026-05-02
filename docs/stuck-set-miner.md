# Fixed-selection stuck-set miner

Status: research tooling. No general proof and no counterexample are claimed.

The stuck-set miner analyzes a fixed selected-witness system `S_i`. It is meant
to expose obstructions to the bridge/peeling program without promoting them to
geometric claims.

## Semantics

For a selected pattern, a subset `U` is stuck if `|U| >= 4` and every center
`v in U` has at most two selected witnesses inside `U`.

This obstructs the strong fixed-row Key Peeling property. It does not prove that
the underlying abstract pattern is geometrically realizable or unrealizable,
because a real bad polygon could have other rich-radius choices not represented
by the fixed rows.

The tool separately reports:

- `forward_ear_order`: whether some three-vertex seed can grow by adding
  vertices with three selected witnesses already present.
- `greedy_reverse_peeling`: one deterministic peeling run from the full set.
  A failure gives a concrete stuck motif, but a success is not a no-stuck proof.
- `key_peeling_status`: the exhaustive stuck-search status over the requested
  subset-size window.
- `filters.fragile_cover`: an incidence-level fragile-cover snapshot assuming
  any selected row may be declared fragile.
- `filters.radius_propagation`: a fixed-order, disjunctive short-chord
  radius-inequality check.

If the search starts above size `4`, or stops before `n` without finding a
stuck set, the status is `UNKNOWN_TRUNCATED_SEARCH`.

For the first run on the current live sparse/Sidon frontier, see
`docs/stuck-frontier-snapshot.md`.

## Usage

Analyze one built-in pattern:

```bash
python scripts/find_minimal_stuck_sets.py --pattern C19_skew
```

Search only larger motifs:

```bash
python scripts/find_minimal_stuck_sets.py --pattern C19_skew --min-set-size 8 --json
```

Analyze all built-in patterns:

```bash
python scripts/find_minimal_stuck_sets.py --all-built-ins
```

Analyze the reconstructed `n=8` survivor classes:

```bash
python scripts/find_minimal_stuck_sets.py \
  --n8-survivors data/incidence/n8_reconstructed_15_survivors.json
```

Write a certificate:

```bash
python scripts/find_minimal_stuck_sets.py \
  --pattern C19_skew \
  --write-certificate data/certificates/c19_stuck_sets.json \
  --json
```

The JSON output includes cheap exact filter diagnostics for the full fixed
pattern: row-pair cap, column-pair cap, `phi` edge count, odd forced
perpendicularity cycles, natural-order crossing violations, and the current
minimum-radius short-chord filter result.

## Mining New Motifs

`scripts/mine_stuck_motifs.py` uses the optional `z3-solver` dev dependency to
ask for a full selected-witness system with a prescribed stuck subset. It then
runs the same exact filters used by `find_minimal_stuck_sets.py`.

Example:

```bash
python scripts/mine_stuck_motifs.py --n 9 --stuck-size 4 --max-models 100
```

By default, the solver enforces:

- row size `4` and no self-selection;
- row-pair intersection cap;
- column-pair cap;
- all labels are selected by at least one row;
- adjacent-row overlap at most `1` in natural order;
- two-overlap crossing compatibility in natural order.

The post-solver filters also require no odd forced-perpendicularity cycle,
radius-propagation survival, and incidence-level fragile-cover compatibility.
Each of these can be relaxed with a named `--allow-*` flag.

For motifs that are genuinely adversarial to the ear-orderable rank program,
add:

```bash
python scripts/mine_stuck_motifs.py \
  --n 10 \
  --stuck-size 4 \
  --max-models 500 \
  --require-no-forward-ear-order
```

This rejects models admitting any forward ear order from a three-vertex seed.
The solver also adds a cheap necessary seed screen, but the final check is done
by the exact `forward_ear_order` routine.

The stuck subset is fixed to labels `0..stuck_size-1`, so this is a bounded
motif search, not an isomorphism-complete enumeration.

Every stuck-analysis or motif payload includes a `fingerprint` block. The
`cyclic_dihedral_sha256` value is canonical under cyclic rotation and reversal
of the fixed order. It is intentionally not canonical under arbitrary
relabeling, because these tools are tracking fixed cyclic-order filters.

Current smoke-test behavior under the natural-order filters and
`--require-no-forward-ear-order`:

```text
n=9,  stuck_size=4: exhausted in the bounded search used by tests
n=10, stuck_size=4: found a surviving no-forward fixed-selection motif
n=11, stuck_size=4: found a surviving no-forward fixed-selection motif
n=12, stuck_size=4: found a surviving no-forward fixed-selection motif
```

These are search diagnostics, not finite-case theorems.

## Geometry Smoke Search

Mined motifs include `selected_rows`, so they can be passed directly into the
existing numerical search stack:

```bash
python scripts/mine_stuck_motifs.py \
  --n 10 \
  --stuck-size 4 \
  --max-models 80 \
  --require-no-forward-ear-order \
  --write-certificate data/runs/scratch/mined_n10_stuck4_no_forward.json

python scripts/search_pattern_json.py \
  --input data/runs/scratch/mined_n10_stuck4_no_forward.json \
  --optimizer slsqp \
  --restarts 20 \
  --max-nfev 3000
```

The search result is numerical evidence only. Optimizer failure is reported as
a failed numerical run, not as an obstruction. A low residual would still need
exact coordinates, interval certificates, SMT certificates, or a formal proof
before it could support an exact claim.

## Sweeps

Use `scripts/sweep_stuck_motifs.py` to reproduce a small parameter grid without
leaving per-motif artifacts behind:

```bash
python scripts/sweep_stuck_motifs.py \
  --n-range 9 12 \
  --stuck-sizes 4 \
  --max-models 220 \
  --solver-seed 0 \
  --require-no-forward-ear-order
```

Add `--run-geometry` for a lightweight numerical smoke search on every found
motif:

```bash
python scripts/sweep_stuck_motifs.py \
  --n 11 \
  --stuck-sizes 4 \
  --max-models 80 \
  --solver-seed 0 \
  --require-no-forward-ear-order \
  --run-geometry \
  --geometry-optimizer trf \
  --geometry-restarts 3 \
  --geometry-max-nfev 300
```

Model counts are solver diagnostics. They are useful for reproducibility with a
fixed seed, but they should not be read as mathematical thresholds. Sweep runs
use a stable SMT variable prefix derived from the base prefix, `n`, stuck size,
and solver seed. This keeps a parameter item independent of its position in a
larger sweep while avoiding symbol reuse between different items. Each motif
search also uses a fresh Z3 context. Use `--variable-prefix` when a
pytest/regression context needs a distinct symbol namespace.

## Radius Propagation

For each row `i`, the four selected witnesses have at least one consecutive
angular gap smaller than `pi/3`. If the short pair is `{a,b}` and `b in S_a`,
then `r_a < r_i`; if `a in S_b`, then `r_b < r_i`.

The implementation therefore searches over the disjunction of possible short
pairs, one per row. The status `RADIUS_CYCLE_OBSTRUCTED` means every such
choice forces a strict radius cycle. The status `PASS_ACYCLIC_CHOICE` means the
pattern survives this necessary filter; it is not evidence of realizability.

## Fragile Cover

The fragile-cover snapshot is incidence-only. It treats every selected row as
eligible to be a fragile row and asks whether selected cohorts can cover all
vertices. Actual fragility requires metric uniqueness of an exact four-cohort,
which this tool does not certify.

For `n > 20`, exact cover-subset enumeration is skipped by default. Use
`--fragile-cover-max-size` to search a bounded cover-size window. A CLI summary
label such as `NONE<=7` means no incidence cover was found through size `7`;
it is not a complete no-cover certificate unless the JSON field
`search_complete` is true.
