# Near-saturation support obstruction

Status: `LEMMA_DRAFT` / `REVIEW_PENDING`. This note does not claim a general
proof of Erdos Problem #97 and does not claim a counterexample. Independent
proof review is requested before theorem-style use.

This note strengthens the edge-sensitive rich-support pair budget of
`docs/rich-support-counting-lemma.md` by two units for every `n >= 8`. It
extends the support-saturation turn-cover argument of
`docs/support-saturation-obstruction.md` in two directions at once:

1. from uniform support sizes at the exact equality wall to arbitrary mixed
   support-size profiles; and
2. from pair-capacity slack `0` to pair-capacity slack `1`.

The proof reuses only ingredients already recorded in the repository: the
hull-edge and diagonal perpendicular-bisector capacities, the base-apex
one-center-per-side fact, and the equilateral/turn-cover endgame of the
`n <= 8` geometric proof. The new content is the bookkeeping showing those
ingredients survive one missing capacity unit with no assumption on the
support-size profile.

## Setting

Let `P` be a strictly convex polygon with vertices `v_0, ..., v_{n-1}` in
cyclic hull order, `n >= 8`. For each center `i` choose one same-radius
support

```text
R_i subset V \ {v_i},
```

meaning that all members of `R_i` lie on one circle centered at `v_i`. The
sizes `|R_i|` are arbitrary; no 4-badness hypothesis is used in the lemma
draft itself.

For an unordered vertex pair `{x,y}`, define its usage

```text
u({x,y}) = #{ i : {x,y} subset R_i }.
```

The repository's capacity facts (the hull-edge and diagonal caps are proved
in `docs/rich-support-counting-lemma.md` and
`docs/localized-rich-support-counting.md`; the one-center-per-side refinement
is the base-apex lemma of `docs/n8-geometric-proof.md`):

- if `{x,y}` is a hull edge, `u({x,y}) <= 1`;
- if `{x,y}` is a diagonal, `u({x,y}) <= 2`, with at most one using center
  strictly on each side of the line `xy`, and no using center on the line
  itself (a center on both the line and the bisector would be the chord
  midpoint, which is interior to a strictly convex polygon, not a vertex).

Summing capacities gives the known budget

```text
sum_i binom(|R_i|, 2) = sum_pairs u <= n + 2*(binom(n,2) - n) = n(n-2).
```

Define the pair-capacity slack

```text
d = n(n-2) - sum_i binom(|R_i|, 2) = sum_pairs (capacity - usage) >= 0.
```

## Lemma draft (near-saturation obstruction)

For every strictly convex `n`-gon with `n >= 8`, and every choice of
same-radius supports as above,

```text
d >= 2.
```

Equivalently,

```text
sum_i binom(|R_i|, 2) <= n(n-2) - 2.
```

## Proof

Suppose `d <= 1`. Then at most one pair has usage strictly below its
capacity, and its shortfall is exactly one unit.

Write `s_i = |v_i v_{i+1}|` for the side lengths and `tau_j in (0, pi)` for
the exterior turns, indices mod `n`, with `sum_j tau_j = 2*pi`. For `n >= 8`
the `n` gap-2 pairs `{v_i, v_{i+2}}` and the `n` gap-3 pairs `{v_i, v_{i+3}}`
are `2n` pairwise distinct diagonals, so at most one of them is unsaturated.

### Step 1: a saturated gap-2 diagonal forces a side equality

Suppose `u({v_i, v_{i+2}}) = 2`. By the one-center-per-side capacity fact,
the two using centers lie one on each side of the line through `v_i` and
`v_{i+2}`. By strict convexity, the open side of that line containing
`v_{i+1}` contains no other vertex, so the short-side center is `v_{i+1}`
itself. Then `v_i, v_{i+2} in R_{i+1}` lie on one circle centered at
`v_{i+1}`, hence

```text
s_i = |v_{i+1} v_i| = |v_{i+1} v_{i+2}| = s_{i+1}.
```

### Step 2: all sides are equal

At most one gap-2 diagonal is unsaturated, so at least `n-1` of the `n`
cyclic side equalities `s_i = s_{i+1}` hold. A cycle minus at most one edge
is still connected, so all sides are equal; call the common value `s`.

### Step 3: a saturated gap-3 diagonal forces one exterior turn `2*pi/3`

Suppose `u({v_i, v_{i+3}}) = 2`. As in Step 1, exactly one using center lies
on the short side of the line through `v_i` and `v_{i+3}`, and that side
contains exactly the vertices `v_{i+1}` and `v_{i+2}`.

If the short-side center is `v_{i+1}`, then
`|v_{i+1} v_{i+3}| = |v_{i+1} v_i| = s`. In the triangle
`v_{i+1} v_{i+2} v_{i+3}`, the two legs at `v_{i+2}` are consecutive polygon
sides of length `s` and the apex angle at `v_{i+2}` is the interior angle
`pi - tau_{i+2}`, so

```text
|v_{i+1} v_{i+3}| = 2 s cos(tau_{i+2} / 2).
```

Setting this equal to `s` gives `cos(tau_{i+2}/2) = 1/2`, and since
`tau_{i+2}/2 in (0, pi/2)`, this forces `tau_{i+2} = 2*pi/3`.

If the short-side center is `v_{i+2}`, the symmetric computation forces
`tau_{i+1} = 2*pi/3`.

Either way the set `M = { j : tau_j = 2*pi/3 }` meets `{i+1, i+2}`.

### Step 4: `M` is large

The index pairs `{i+1, i+2}` for `i = 0, ..., n-1` are exactly the `n` edges
of the cycle on turn indices. At most one gap-3 diagonal is unsaturated, so
`M` meets at least `n-1` of those `n` edges.

- If all `n` gap-3 diagonals are saturated, `M` is a vertex cover of the
  `n`-cycle, so `|M| >= ceil(n/2) >= 4` for `n >= 8`.
- If one is unsaturated, `M` is a vertex cover of the `n`-cycle minus one
  edge, which is a path with `n-1` edges, so
  `|M| >= ceil((n-1)/2) >= 4` for `n >= 8`.

The single missing unit, if any, sits in exactly one of three places: on a
gap-3 diagonal (then all gap-2 diagonals are saturated, so Step 2 is
unaffected, and the cover loses one edge); on a gap-2 diagonal (then all
gap-3 diagonals are saturated, so the cover is the full cycle, and Step 2
survives by the chain argument); or on a hull edge or a gap `>= 4` diagonal
(then every short diagonal is saturated and both steps hold with no loss).
In every `d <= 1` case both Step 2 and the cover bound `|M| >= 4` hold.

### Step 5: turn contradiction

All exterior turns are positive, so

```text
2*pi = sum_j tau_j >= sum_{j in M} tau_j = |M| * (2*pi/3) >= 8*pi/3 > 2*pi,
```

a contradiction. Hence `d >= 2`.

## Consequences

All consequences below inherit the `REVIEW_PENDING` status of this note.

### Uniform thresholds are recovered

If every center has `|R_i| >= k >= 4`, then for `n <= 7` the raw budget
already excludes the support system (`6n > n(n-2)`, recorded in
`docs/rich-support-counting-lemma.md`), and for `n >= 8` the sharpened
budget applies: `n * binom(k,2) <= n(n-2) - 2` forces
`n - 2 - binom(k,2) >= 1`, i.e.

```text
n >= binom(k, 2) + 3.
```

This recovers the thresholds of `docs/support-saturation-obstruction.md`
(`k=4: n>=9`, `k=5: n>=13`, ...) as direct budget corollaries. The uniform
equality-wall lemma is the special case `d = 0` with all sizes equal.

### Sharpened mixed-profile counts for 4-bad polygons

In a hypothetical 4-bad `n`-gon, choose a maximum rich class at each center,
so `|R_i| >= 4` everywhere, and let `q` be the number of centers with
`|R_i| >= 5`. Then `6n + 4q <= n(n-2) - 2`, i.e.

```text
q <= (n^2 - 8n - 2) / 4.
```

```text
n = 9:  q <= 1  (raw budget: 2; the nonagon profile-deficiency refinement
                 in docs/rich-support-counting-lemma.md and the localized
                 per-label cap in docs/localized-rich-support-counting.md
                 each already give 0)
n = 10: q <= 4  (raw budget: 5)  => at least 6 exact-four centers
n = 11: q <= 7  (raw budget: 8)  => at least 4 exact-four centers
n = 12: q <= 11 (raw budget: 12) => at least 1 exact-four center
n = 13: no constraint beyond the trivial q <= 13
```

Among all support-size profiles with every size at least `4` that the raw
budget allows, the profiles newly excluded by this lemma (raw slack `0` or
`1`) are exactly:

```text
n = 9:  (4,4,4,4,4,4,4,4,6)          cost 63, slack 0
        (4,4,4,4,4,4,4,5,5)          cost 62, slack 1
n = 10: (4,4,4,4,4,4,4,4,5,7)        cost 79, slack 1
        (4,4,4,4,4,5,5,5,5,5)        cost 80, slack 0
n = 11: (4,4,4,4,4,4,4,4,6,6,7)      cost 99, slack 0
        (4,4,4,4,4,4,4,5,5,6,7)      cost 98, slack 1
        (4,4,4,4,5,5,5,5,5,5,6)      cost 99, slack 0
        (4,4,4,5,5,5,5,5,5,5,5)      cost 98, slack 1
n = 12: 14 profiles, including the uniform (5)*12
n = 13: 30 profiles; the surviving maximum q stays at the trivial 13
```

The two `n = 9` profiles were already excluded by the nonagon
profile-deficiency refinement of `docs/rich-support-counting-lemma.md`, so
at `n = 9` this lemma only rederives known exclusions. At `n = 12`, the `q <= 11` bound itself was already known,
because the only raw-feasible profile with `q = 12` is the uniform `(5)*12`
killed by the uniform saturation lemma; the thirteen mixed `n = 12`
profiles are newly excluded objects but do not move that count. The
genuinely bound-improving rows are `n = 10` and `n = 11`.

For `n = 8`, the 4-bad cost `6*8 = 48` exceeds the sharpened budget `46`, so
a 4-bad octagon is excluded by the budget alone. This is a consistency
remark: it repackages the equality-case endgame of
`docs/n8-geometric-proof.md` and does not replace the repository's `n <= 8`
source-of-truth theorem or its review history.

### Relation to existing n=10 evidence

The review-pending `n=10` mixed rich-support capacity diagnostic
(`docs/n10-mixed-rich-support-capacity.md`) obstructs all support
assignments with `q = 3, ..., 7` size-five supports under the row-pair cap,
two-overlap crossing, and witness-pair capacity filters, by exhaustive
search. The counting bound here is weaker at `n = 10` (`q <= 4` versus the
search's `q <= 2`), but it is a proof-facing budget statement with no
enumeration, and it is the first improvement at `n = 11`, where no search
result exists.

## Boundary: why slack 2 is out of reach for this method

The argument does not extend to `d = 2` as stated, and this note claims
nothing about `d = 2`. The method boundary is exactly one failure mode.

**The genuine failure mode: the equilateral step.** If the two missing
units sit on two DISTINCT gap-2 diagonals, the side-equality chain loses
two edges of the `n`-cycle. A cycle minus two distinct edges is always
disconnected (it has `n` vertices, `n - 2` edges, and no cycle), so the
sides are only forced into at most two length classes. Step 3's conversion
of a chord equality into `tau = 2*pi/3` needs all three relevant sides at
the pivot equal, which can now fail, and no turn contradiction follows from
these steps.

**Every other slack-2 distribution still contradicts.** Step 5 admits a
strict sharpening: since every exterior turn is positive and
`sum_j tau_j = 2*pi` exactly, a forced-turn set `M` with `|M| >= 3` is
already impossible for `n >= 4`. If `M` is a proper subset of the turn
indices, the remaining turns add a strictly positive amount to
`|M| * (2*pi/3) >= 2*pi`; if `M` is everything, the total is
`n * 2*pi/3 > 2*pi`. Under any slack-2 distribution other than the
two-distinct-gap-2 case, the side chain loses at most one edge (a single
gap-2 diagonal short by one or by two units removes only one chain edge),
so all sides are equal, and the turn-index cycle loses at most two cover
edges, leaving a vertex cover of size at least `ceil((n-2)/2) >= 3` for
`n >= 8`. The strict sharpening then closes the case.

The headline proof deliberately uses the non-strict test `|M| >= 4`, which
genuinely fails on some two-edge removals (for `n = 8`, adjacent-pair
removals leave a minimum cover of exactly `3`). The uniform statement
therefore still stops at slack `1` because of the equilateral failure mode
above, not because of the turn count.

These are records about this proof method, not claims about the
realizability of the remaining slack-2 support systems.

## Known counterexample attempts

Adversarial checks performed against the statement, with no countermodel
found:

- the strict-turn re-derivation above, which located and corrected an error
  in an earlier draft of this note's boundary records but left the lemma
  statement and Steps 1-5 unchanged;
- exact brute-force verification of every vertex-cover bound used by Steps
  4-5 and the boundary records (all cycle-minus-`0`/`1`/`2`-edge covers for
  `n = 3..12`);
- exhaustive enumeration of all raw-feasible 4-bad support-size profiles
  for `n = 9..13`, cross-checked against the sharpened budget;
- the two-distinct-gap-2 slack-2 family, which is a boundary of the proof
  method but not a countermodel: it concerns `d = 2`, outside the claim.

## Survival of known 3-neighbor examples

Known `k = 3` constructions (for example the Danzer-style 9-point
three-neighbor examples recorded as literature risk in
`docs/public-provenance.md`) give each center a support of size `3`, with
total pair cost `n * binom(3,2) = 3n`. For every `n >= 8`,
`3n <= n(n-2) - 2`, so the sharpened budget imposes nothing on
three-neighbor configurations and is consistent with their existence.

## What this does not prove

- It does not prove `n = 9`, `n = 10`, `n = 11`, or any finite case beyond
  the counting statement itself.
- It does not prove Erdos Problem #97 and does not produce or certify a
  counterexample.
- It does not change the official/global falsifiable/open status or the
  repository's `n <= 8` source-of-truth result.
- The 4-bad consequences are support-size profile constraints only; they say
  nothing about which selected-witness systems on the surviving profiles are
  realizable.
- It does not supersede the nonagon profile-deficiency refinement of
  `docs/rich-support-counting-lemma.md` or the localized per-label cap of
  `docs/localized-rich-support-counting.md` at `n = 9`; both remain
  stronger there.

## Verification command

```bash
python scripts/check_near_saturation_support_obstruction.py --check --json
```

The checker verifies the budget arithmetic, the `d <= 1` case bookkeeping
(distinctness of the `2n` short diagonals, chain connectivity after one
missing edge, vertex-cover sizes, turn-unit comparison), the sharpened
small-`n` consequence table, the exact list of newly excluded boundary
profiles, consistency with the raw-budget and uniform-saturation lemmas, and
the slack-2 method-boundary records (the chain-disconnection failure mode
and the cover bounds behind the strict-turn closure of the other
distributions). It is an arithmetic checker for the proof note; it is not a
realization search.

The stored artifact
`data/certificates/near_saturation_support_obstruction.json` is generated by

```bash
python scripts/check_near_saturation_support_obstruction.py --write-artifact
```

and replayed by

```bash
python scripts/check_near_saturation_support_obstruction.py --check --check-artifact --json
```
