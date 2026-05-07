# n=10 Vertex-circle Singleton-slice Draft

Status: `MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING`.

This note records an incoming n=10 finite-case search as an audit target. It
does not claim a general proof of Erdos Problem #97 and does not claim a
counterexample. The official/global status remains falsifiable/open. The
established source-of-truth local result remains the repo-local,
machine-checked selected-witness `n <= 8` artifact; the n=9 and n=10
vertex-circle packages are still review-pending.

## What is checked

The checker labels a hypothetical bad decagon in cyclic order `0,...,9` and
enumerates selected-witness rows `S_i`, each a 4-subset of the other vertices.
It uses the same exact necessary filters as the review-pending n=9
vertex-circle checker:

- two selected rows share at most two witnesses;
- if two selected rows share exactly two witnesses, the source chord and
  witness chord cross in the cyclic order;
- each witness pair appears in at most two selected rows;
- each target vertex has selected indegree at most
  `floor(2*(10-1)/(4-1)) = 6`;
- vertex-circle strict chord monotonicity creates no self-edge or strict
  directed cycle after quotienting by selected-distance equalities.

Every actual bad decagon would induce at least one selected-witness assignment
satisfying these necessary conditions. The artifact reports that none survives
this checker. This is a finite-case draft conditional on implementation audit,
not a public theorem-style claim.

## Imported counts

The checked-in artifact is
`data/certificates/n10_vertex_circle_singleton_slices.json`. It converts the
archive `n10_rows.jsonl` into explicit singleton row0 records, so each raw row
has a `row0_index`, `row0_range`, `row0_mask`, and `row0_witnesses`. The
explicit witness lists are derived from the repo-native
`GenericVertexSearch(10).options[0]` order and are included to make the
`[0,126)` coverage audit easier to read.

```text
row0 choices covered:      126 / 126
aborted slices:            0
full assignments:          0
nodes visited:             4,142,738
partial self-edge prunes:  4,467,592
partial strict cycles:     5,318,250
```

The companion generic Python checker reproduces the repo's n=9 counts exactly
and spot-checks selected row0 singletons `0`, `63`, and `125` for the n=10
artifact. A full repo-native n=10 rerun is intentionally not part of the fast
tier; it should be treated as artifact-tier work.

## Secondary first-five replay

The archived secondary artifact
`data/certificates/2026-05-05/n10_secondary.json` replays the first five row0
singletons under the same pair/crossing/indegree/vertex-circle filters plus an
extra triple-intersection necessary filter. It is a cross-check of the prefix
only, not a replacement for the 126-slice artifact and not a promotion of the
n=10 draft.

```text
row0 choices covered:      5 / 126
full assignments:          0
nodes visited:             114,144
partial self-edge prunes:  106,827
partial strict cycles:     120,823
```

The checked replay verifies that rows `0..4` match the primary singleton
artifact exactly for witness lists, node counts, full counts, and prune counts,
and that every listed `full_survivors` record is empty.

## Commands

Validate the imported artifact counts:

```bash
python scripts/check_n10_vertex_circle_singletons.py --assert-expected
```

Validate the artifact and rerun selected row0 singletons `0`, `63`, and `125`
with the generic checker:

```bash
python scripts/check_n10_vertex_circle_singletons.py \
  --assert-expected \
  --spot-check-row0 0 \
  --spot-check-row0 63 \
  --spot-check-row0 125
```

The legacy shorthand below is still supported and checks only row0 singleton
`0`:

```bash
python scripts/check_n10_vertex_circle_singletons.py \
  --assert-expected \
  --spot-check-generic
```

Validate the secondary first-five replay against the primary singleton
artifact:

```bash
python scripts/check_n10_secondary_singleton_replay.py \
  --check \
  --assert-expected \
  --json
```

Regenerate the checked-in artifact from the archived JSONL:

```bash
python scripts/check_n10_vertex_circle_singletons.py \
  --import-jsonl "C:\Users\User\Desktop\code\erd archive\outputs\data\1\3\10\n10_rows.jsonl" \
  --write \
  --assert-expected
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_n10_vertex_circle_singletons.py -q -m "artifact"
```

## Review standard

Before this artifact is promoted beyond draft status, an independent review
should check:

- the geometric necessity of every pruning rule;
- that row0 singleton coverage is exactly `[0,126)` with no hidden symmetry
  quotient;
- that the minimum-remaining-options row choice changes only search order;
- that vertex-circle partial pruning uses only already-fixed selected rows and
  selected-distance equalities;
- that the generic repo-native checker and the archived C++ checker agree
  beyond the selected n=10 singleton spot-checks, or that a second independent verifier
  replays all terminal conflicts;
- that the secondary first-five replay is treated only as prefix agreement
  under an extra necessary filter, not as all-slice coverage;
- that the artifact remains scoped to the selected-witness n=10 finite case
  and does not alter the global status.
