# n=9 Vertex-circle Compact Independent Brancher

Status: `REVIEW_PENDING_COMPACT_INDEPENDENT_BRANCHER`.

This note records a compact, independent audit path for the review-pending
`n=9` vertex-circle finite-case result. It does not claim a proof of `n=9`,
does not claim a counterexample, does not complete independent review of the
existing exhaustive checker, and does not update the official/global status of
Erdos Problem #97.

The companion checker is:

```bash
python scripts/check_n9_vertex_circle_compact_brancher.py --assert-expected --json
```

The stored artifact form is:

```bash
python scripts/check_n9_vertex_circle_compact_brancher.py --write --assert-expected
python scripts/check_n9_vertex_circle_compact_brancher.py --check --assert-expected --json
```

It writes:

```text
data/certificates/n9_vertex_circle_compact_brancher.json
```

## What is new

The checker regenerates the `n=9` selected-witness frontier without importing
the project `n=9` brancher modules and without reading the stored 184-row
frontier artifact. It uses only these direct predicates:

- every center chooses a four-set not containing itself;
- two selected rows intersect in at most two witnesses;
- a two-witness row overlap must satisfy the crossing rule between the center
  chord and the shared-witness chord in cyclic order `0,1,...,8`;
- each unordered witness pair appears in at most two rows.

After that incidence/count enumeration, it applies the row-wise vertex-circle
quotient obstruction directly: selected rows identify center-witness distance
pairs, nested chords in one selected row give strict inequalities, and a
self-edge or directed cycle in the strict quotient graph is impossible.

## Checked result

The compact brancher visits `100817` search nodes and regenerates exactly
`184` terminal incidence/count frontier assignments. The assignment set digest
is:

```text
dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55
```

That digest matches the sorted-row digest used by the existing frontier
coverage crosswalk, but this checker does not import that crosswalk and does
not read the stored 184-assignment frontier artifact.

All `184` terminal assignments are vertex-circle quotient obstructed:

```text
self_edge:    158
strict_cycle: 26
clean:        0
```

It also reproduces the direct frontier bookkeeping histograms:

```text
center-pair intersection histogram: 0 -> 72, 1 -> 3168, 2 -> 3384
witness-pair profiles:             1:18|2:18 -> 148, 0:2|1:14|2:20 -> 36
selected-indegree values:          4 -> 1656
```

## Trust boundary

This is useful independent audit evidence because it recomputes the incidence
frontier and the vertex-circle quotient obstruction in one small script. It is
still review-pending finite-case evidence only. It does not prove the
geometric lemmas from scratch, does not certify the broader source-of-truth
claim stack, does not handle `n > 9`, and does not prove Erdos Problem #97.
