# n=9 Kalmanson Self-edge Replay

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records a compact independent replay path for the review-pending
`n=9` selected-witness frontier. It does not claim a general proof of Erdos
Problem #97, does not claim a counterexample, and does not promote `n=9` beyond
the repo's existing review-pending finite-case status.

## Scope

The checker labels a hypothetical bad nonagon in cyclic order `0,...,8`. For
each center `i`, it chooses one selected witness row

```text
S_i subset {0,...,8} \ {i}, |S_i| = 4.
```

It enumerates all row systems surviving only exact necessary filters:

- two selected rows share at most two witnesses;
- if two rows share exactly two witnesses, the center chord crosses the
  common-witness chord in the fixed cyclic order;
- adjacent centers therefore cannot share two witnesses;
- each unordered witness pair occurs together in at most two rows.

The brancher reaches `184` terminal selected-witness systems, matching the
pre-vertex-circle frontier in the existing review-pending
`n9_vertex_circle_exhaustive` package.

## Kalmanson self-edge

For a strictly convex cyclic quadrilateral `a < b < c < d`, the ordinary
distance matrix satisfies the strict Kalmanson inequalities

```text
D_ab + D_cd < D_ac + D_bd
D_ad + D_bc < D_ac + D_bd
```

by applying strict triangle inequalities at the intersection of the diagonals.
Selected witness rows identify ordinary distance variables:

```text
D_ia = D_ib = D_ic = D_id,  for a,b,c,d in S_i.
```

The checker quotients unordered distance pairs by these selected equalities.
If one strict Kalmanson inequality has the same quotient multiset on both
sides, it becomes `L < L`, so the selected-witness system is impossible.

The stored certificate gives one such self-edge for each of the `184` terminal
systems:

```text
terminal assignments: 184
killed by Kalmanson self-edge: 184
unkilled: 0
certificate_sha256:
  8e5344265e774ce352d64e16e0480eaff4ad6051a69051a304a3f9145db0e3c5
```

For the first stored assignment, the quadruple `(0,1,2,7)` gives

```text
D_01 + D_27 < D_02 + D_17.
```

The selected-distance quotient identifies all four displayed variables, so the
strict inequality collapses to `2X < 2X`.

## Commands

Regenerate the full artifact:

```bash
python scripts/check_n9_kalmanson_selfedge.py --write --assert-expected --summary-only
```

Replay the checked-in certificate without rerunning the brancher:

```bash
python scripts/check_n9_kalmanson_selfedge.py \
  --verify-certificate data/certificates/n9_kalmanson_selfedge.json \
  --assert-expected --summary-json
```

The replay mode verifies the stored self-edge rows and the stable digest from
the certificate list. It is a certificate replay, not an independent proof of
the brancher filters. Use `--json` when the full replay payload is needed.

Independent reviewer-facing replay:

```bash
python scripts/check_n9_kalmanson_selfedge_independent_replay.py \
  --check --assert-expected --summary-json
```

This second replay intentionally does not import
`erdos97.n9_kalmanson_selfedge` and does not run the search brancher. It treats
the checked-in JSON as input data, then independently checks row shape,
two-overlap crossing, witness-pair capacity, selected-distance quotienting,
the stored strict Kalmanson self-edge, and the certificate-list digest. Use
`--json` when the first stored self-edge example record is needed.

Fresh frontier regeneration replay:

```bash
python scripts/check_n9_kalmanson_selfedge_frontier_replay.py \
  --check --assert-expected --summary-json
```

This third replay was imported from the 2026-06-19 GPT packet triage and then
reshaped into repo-native `--check`/`--write` form. Unlike the stored-input
replay, it imports no `erdos97` package modules and does not read
`data/certificates/n9_kalmanson_selfedge.json`. It regenerates the
fixed-cyclic-order selected-witness frontier directly, reaches `100818` search
nodes and `184` terminal assignments, and finds one strict Kalmanson self-edge
for each terminal assignment:

```text
terminal assignments after filters: 184
killed by Kalmanson self-edge: 184
unkilled: 0
Kalmanson split: K1 = 150, K2 = 34
certificate_sha256:
  3e6e208cd4212f9275eba2f0be9e32558da9b77544304d33d09abc953feeee9d
```

The generated artifact is
`data/certificates/n9_kalmanson_selfedge_frontier_replay.json`. It is
corroborating audit evidence only, not an independent review completion or a
status promotion.

## Audit boundary

This artifact is useful because it replaces the earlier mixed Kalmanson
archive variants with one uniform certificate type: every terminal `n=9`
selected-witness assignment has a single strict Kalmanson self-edge after
selected-distance quotienting.

It still needs independent review before any theorem-style use. In particular,
reviewers should check the two-overlap crossing predicate, the witness-pair
capacity filter, the absence of hidden symmetry quotients, the selected-distance
quotient construction, and the strict Kalmanson inequality convention. Even if
accepted, this is only a finite `n=9` selected-witness obstruction and does not
settle Erdos Problem #97 for larger `n`.
