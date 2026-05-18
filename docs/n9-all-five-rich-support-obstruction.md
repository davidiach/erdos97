# n=9 all-five-rich support obstruction

Status: `REVIEW_PENDING_DIAGNOSTIC` / generator-independent finite support
catalogue. No general proof of Erdos Problem #97 is claimed. No
counterexample is claimed.

This note records a support-level subcase that is independent of the generated
radius-blocker packets. Work in the cyclic order `0,1,2,3,4,5,6,7,8`. For
each center, enumerate every five-subset of the other eight labels. A complete
assignment would choose one such size-five support at each center.

The checker applies only two exact necessary filters:

- two distinct distance circles share at most two witness vertices;
- if two centers share exactly two witnesses, the center chord and the
  shared-witness chord must cross in the cyclic order.

These are the same circle-intersection and radical-axis crossing conditions
recorded in `docs/claims.md`.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_all_five_rich_support_obstruction.json
```

Verify it with:

```bash
python scripts/check_n9_all_five_rich_support_obstruction.py --check --assert-expected --json
```

There are `56` possible size-five supports at each of the `9` centers, for
`5,416,169,448,144,896` raw assignments. The pair catalogue checks all `36`
center-pairs and `112,896` support-pairs:

```text
compatible support-pairs by center gap:
gap 1: 140 each
gap 2: 440 each
gap 3: 640 each
gap 4: 740 each
```

The exact backtracking search visits `136` assignment nodes, reaches depth
`2`, and leaves `0` complete assignments. The closing filters are only the
row-pair cap and two-overlap crossing rule; no vertex-circle quotient replay
or generated selected-row packet is used.

## Consequence

Repo-locally, this rules out the subcase where a strict convex nonagon
counterexample has some rich distance class of size at least five at every
center. If such a nonagon existed, choosing any five witnesses inside each
large rich class would give a complete size-five support assignment satisfying
the checked pair filters.

## Boundary

This does not enumerate mixed exact-four and size-five rich catalogues. It
does not prove `n=9`, does not prove the adaptive radius-blocker bridge, does
not prove Erdos Problem #97, and does not provide a counterexample.

The next useful bridge target is the mixed catalogue: at least one center must
remain exact-four-only in any `n=9` selected-witness counterexample.
