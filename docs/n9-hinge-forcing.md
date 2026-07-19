# n=9 Equilateral-hinge Forcing

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records a direct finite implication for selected four-witness rows on
nine cyclic labels. It is a proof-compression candidate for the repository's
review-pending `n=9` chain. It does not prove Erdos Problem #97, prove the
`n=9` case, complete independent review, or provide a bridge from arbitrary
larger counterexamples to nine vertices.

## Exact finite implication

Let `V = Z/9Z` have its natural cyclic order. For every center `i`, choose a
self-excluding row `S_i` of exactly four labels from one rich distance class.
The underlying rich class may contain more witnesses. Assume:

1. `|S_i intersection S_j| <= 2` for distinct centers `i,j`;
2. if `S_i intersection S_j = {x,y}`, then the center chord `ij` and
   common-witness chord `xy` cross properly.

Here proper crossing means relative-interior intersection, equivalently
alternating endpoints for four distinct cyclic labels. The four labels are
indeed distinct: a common witness cannot equal either of the two
self-excluding row centers.

The machine-checked finite conclusion is that the rows contain an
**equilateral hinge**. In one orientation, some cyclically ordered distinct
labels `a,b,c,d` satisfy

```text
{b,c} subset S_a,
{a,c} subset S_b,
{a,b} subset S_d.
```

The local geometric lemma in `docs/kalmanson-equilateral-hinge.md` shows why
this template is impossible for rich classes in a strictly convex polygon:
its three spoke equalities turn the strict Kalmanson `K2` inequality into
`L < L`.

## Pair capacity and balance are consequences

Neither witness-pair capacity nor selected indegree four is an assumption of
the implication or its complement search.

Fix a pair `{x,y}`. The centers of rows containing that pair lie in the two
open cyclic arcs cut by `x` and `y`. By the intersection cap, any two such rows
meet exactly in `{x,y}`, so the crossing rule puts their centers in opposite
arcs. Three centers cannot be pairwise separated by a two-part partition.
Thus `{x,y}` occurs in at most two rows. If `x,y` are hull neighbors, all
possible centers lie in the same nonempty arc, so the pair occurs at most once.

Fix a label `x`. Write `d_x` for the number of selected rows containing `x`
and `m_xy` for the number containing the pair `{x,y}`. Every four-witness row
containing `x` contributes three such pairs, so

```text
3 d_x = sum_{y != x} m_xy.
```

The preceding argument gives `m_xy <= 1` for either hull neighbor and
`m_xy <= 2` for each of the other six labels. Consequently

```text
3 d_x <= 2 * 1 + 6 * 2 = 14,
```

and hence `d_x <= 4`. The nine rows contribute total indegree `9 * 4 = 36`, so
all nine upper bounds are equalities and every `d_x` is exactly four.

The generated artifact also performs a finite redundancy check: it enumerates
the complete incidence frontier both with and without explicit pair-capacity
and indegree-four filters and obtains the same terminal count, 184.

## Direct complement search

The implementation in `src/erdos97/n9_hinge_forcing.py` searches the labelled
domain directly. It uses bit masks, deterministic minimum-remaining-options
branching, no symmetry quotient, and no stored frontier as search input. It
forbids every dihedral orientation of the hinge template while enforcing the
two assumptions above. The exhaustive search has zero terminal assignments.

```text
hinge-free search nodes: 26,746
row options examined: 6,710,620
maximum search depth: 8 of 9
hinge-free terminals: 0
```

The compiler audit materializes all 1,008 oriented hinge triggers and requires
each to match exactly one result from the public hinge recognizer. It also
rebuilds all 45,360 option-to-trigger table entries used for pruning. The
positive-control search reaches 184 terminals with canonical assignment-set
digest

```text
dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55
```

matching the independently implemented self-contained Kalmanson frontier
replay without reading that replay's artifact as input.

The compact artifact

```text
data/certificates/n9_hinge_forcing.json
```

pins the complete traversal counters and result digests. It also stores a
deterministic countermodel for dropping each of the two assumptions. Every
countermodel is replayed against all retained constraints and rejected when
the dropped constraint is restored. Dropping hinge-freeness is recorded
separately as a positive control and reaches 184 terminal row systems.

These countermodels establish finite independence relative to this abstract
selected four-witness-row domain. They do not say that the geometric lemmas
supplying the two necessary filters are optional in a polygon.

## Conditional `n=9` compression

If the existing reduction and geometric gates survive independent review, the
proof-facing route becomes:

```text
hypothetical bad nonagon
  -> choose four witnesses from one rich class at each cyclic center
  -> intersection and two-overlap crossing filters
  -> pair capacity and balance (the elementary arguments above)
  -> equilateral hinge (this finite checker)
  -> strict Kalmanson contradiction (the local hinge lemma).
```

This replaces the final per-record Kalmanson replay by one finite
hinge-forcing implication. It is still a review-pending compression of the
same `n=9` evidence, not an official theorem-status promotion.

## Commands

Regenerate and check the artifact:

```bash
python scripts/check_n9_hinge_forcing.py --write --assert-expected
python scripts/check_n9_hinge_forcing.py \
  --check --assert-expected --summary-json
pytest -q tests/test_n9_hinge_forcing.py \
  tests/test_check_n9_hinge_forcing.py
pytest -q -m artifact tests/test_n9_hinge_forcing.py \
  tests/test_check_n9_hinge_forcing.py
```

The artifact audit runs the same checked replay. Passing any of these commands
does not complete the repository's external-review gates.
