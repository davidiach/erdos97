# Kalmanson equilateral-hinge lemma

Status: `LEMMA` / `N9_CROSSWALK_REVIEW_PENDING`.

This note extracts one arbitrary-size local obstruction from the
review-pending `n=9` Kalmanson three-row compression.  The lemma is a direct
consequence of strict convex quadrilateral geometry.  Its occurrence in every
hypothetical counterexample is not proved here.

## Lemma

Let distinct vertices `a,b,c,d` occur in that cyclic order in a strictly
convex polygon.  Suppose three full rich classes have the following pair
memberships:

```text
center a: {b,c} is contained in one rich class,
center b: {a,c} is contained in one rich class,
center d: {a,b} is contained in one rich class.
```

Then the configuration is impossible.

Indeed, the three memberships give

```text
D_ab = D_ac,
D_ab = D_bc,
D_ad = D_bd.
```

For the cyclic quadrilateral `a,b,c,d`, the strict Kalmanson inequality `K2`
is

```text
D_ad + D_bc < D_ac + D_bd.
```

The equalities make its two sides equal, a contradiction.  Only the displayed
two witnesses from each class are used, so the same argument applies to
selected rows containing those pairs and to rich classes of any larger size.
It is independent of the total number of polygon vertices.

An equivalent `K1` orientation is

```text
center a: {b,c} is contained in one rich class,
center b: {c,d} is contained in one rich class,
center c: {b,d} is contained in one rich class.
```

Here `D_ab = D_ac` and `D_cd = D_bd`, while the middle row also gives
`D_bc = D_bd`.  Thus

```text
D_ab + D_cd < D_ac + D_bd
```

again has equal sides.  Rotation or reflection of the cyclic quadruple maps
the `K1` and `K2` descriptions to one pair-membership template.  We call any
such occurrence an **equilateral hinge**.

## Exact `n=9` crosswalk

The generated crosswalk reads, but does not regenerate,
`data/certificates/n9_kalmanson_three_row_core_compression.json`.  For every
stored best three-row core it checks all eight cyclic-dihedral orientations of
the stored quadrilateral and requires the core centers to be exactly the three
hinge centers.

The result is:

```text
stored records covered: 184 / 184
matching core orientations per record: exactly 1
stored best certificates: K1 = 95, K2 = 89
stored dihedral core signatures: 56
equilateral-hinge template orbits: 1
```

Scanning every four-vertex cyclic subset in each complete assignment finds
`1,080` oriented hinge instances in total.  Every assignment has between two
and nine; the exact histogram is

```text
{2: 36, 3: 6, 5: 18, 6: 54, 8: 54, 9: 16}.
```

After the unused witnesses in each stored row are forgotten, all 56 full
signatures contain that one pair-membership template.  This is the proof-facing
gain: the next bridge target is no longer a classification of 56 full
signatures, but a theorem forcing three co-radial witness pairs in one hinge
orientation.

## Commands

```bash
python scripts/check_kalmanson_equilateral_hinge_crosswalk.py \
  --check --assert-expected --summary-json
pytest -q \
  tests/test_kalmanson_equilateral_hinge.py \
  tests/test_kalmanson_equilateral_hinge_crosswalk.py
```

## Boundary

The crosswalk is a deterministic proof-mining audit of a review-pending finite
artifact.  It does not independently regenerate the `n=9` frontier, satisfy
the external-review gate, promote the repo-local `n=9` result, prove the
arbitrary-size problem, or produce a counterexample.

The checker also does not establish that weak incidence, fragile-cover, or
bootstrap hypotheses force a hinge.  A future forcing argument needs genuine
minimality or full-rich-class geometry beyond the audited finite crosswalk.
