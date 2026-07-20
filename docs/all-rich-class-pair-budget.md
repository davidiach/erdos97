# All-rich-class pair budget

Status: `LEMMA` / proof-facing global and localized counting bounds. No general
proof of Erdos Problem #97 and no counterexample are claimed.

The existing rich-support budget chooses one same-radius support at each
center. The same perpendicular-bisector argument applies simultaneously to
**every** rich distance class at every center. This companion lemma records
that stronger quantifier explicitly and then combines it with the minimal
two-deletion profiles.

## Setup

Let `P` be a strictly convex `n`-gon. For each center `y`, let

```text
R(y) = {C_y(r) : |C_y(r)| >= 4}
```

be its complete family of rich distance classes. Distinct members of `R(y)`
are disjoint, although disjointness is not needed for the global pair count.

## Global all-class budget

One has

```text
sum_y sum_{C in R(y)} binom(|C|,2) <= n(n-2).        (1)
```

Proof. Fix an unordered witness pair `{a,b}`. If it lies together in a class
at center `y`, then `y` is on the perpendicular bisector of `ab`. For a
non-edge pair this line contains at most two vertices of a strictly convex
polygon, so `{a,b}` occurs in at most two rich classes globally. At a fixed
center it belongs to only one distance class.

If `{a,b}` is a hull edge, its perpendicular bisector already intersects the
polygon boundary at the edge midpoint. It has at most one further boundary
intersection and hence at most one vertex-center. Thus the `n` hull-edge pairs
have capacity one and the other `binom(n,2)-n` pairs have capacity two.
Double-counting `(y,C,{a,b})` gives

```text
n + 2*(binom(n,2)-n) = n(n-2),
```

which proves (1).

## Localized all-class budget

For every fixed witness vertex `x`,

```text
sum_y sum_{C in R(y): x in C} (|C|-1) <= 2n-4.      (2)
```

Indeed, the left side counts pairs `{x,z}` inside all rich classes. The two
hull-neighbor pairs of `x` have capacity one, and its `n-3` other witness
pairs have capacity two. Therefore their total capacity is

```text
2*1 + (n-3)*2 = 2n-4.
```

Again, this counts all rich classes, not one chosen support at each center.

### Localized rich-class incidence consequence

Let `d_x` be the number of rich classes, over all centers, that contain a
fixed witness vertex `x`.  Every such class contributes at least three to the
left side of (2), so with

```text
L_n = floor((2n-4)/3)
```

one has `d_x<=L_n` and hence

```text
sum_y sum_{C in R(y)} |C| <= n*L_n.                 (3)
```

For a 4-bad polygon, one size-four class per center contributes the baseline
`4n`.  A complete `T5` profile contributes one extra incidence and a complete
`T44` profile contributes four.  Therefore

```text
b + 4c <= n*(L_n-4).                                (4)
```

At `n=9`, `L_n=4`, so equality is forced throughout: every center has exactly
one rich class, it has size four, and every witness label occurs in exactly
four rich classes.  Thus every center is `T4`, `b=c=0`, and the exclusive-pair
charge below gives `e=0`.  This is a complete-profile consequence, not merely
a statement about one chosen maximum support.

## Baseline and unambiguous profile excess

Assume now that `P` is 4-bad: every center has at least one rich class. Define
the all-class mass and excess at a center by

```text
m_y = sum_{C in R(y)} binom(|C|,2),
epsilon_y = m_y - 6.
```

The baseline `m_y>=6` is valid at every center because even a single smallest
possible rich class has size four and contributes `binom(4,2)=6`. Extra rich
classes and larger classes only increase `m_y`. Consequently

```text
sum_y epsilon_y <= n(n-2)-6n = n(n-8).              (5)
```

To combine this with `docs/minimal-two-deletion-profile.md`, use disjoint,
complete-profile counts:

- `b` is the number of centers whose **entire** rich family consists of one
  size-five class (`T5`);
- `c` is the number of centers whose **entire** rich family consists of two
  size-four classes (`T44`).

These types do not overlap. A `T5` center has mass `10` and excess `4`; a
`T44` center has mass `12` and excess `6`. Every other bad-center profile has
nonnegative excess. Hence

```text
4b + 6c <= n(n-8).                                  (6)
```

No assumption is made that every center is one of `T4,T5,T44`; those are only
the profiles capable of certifying a two-vertex deletion. Other centers are
absorbed into the nonnegative unused excess in (6).

## Combination with exclusive mutual pairs

Let `e` be the number of exclusive mutual pairs from the two-deletion lemma.
Those pairs are vertex-disjoint, and charging them to richer two-deletion
certifiers gives

```text
e <= 2b + 4c.                                        (7)
```

Every exclusive-pair endpoint is itself a `T4` center.  Since the `e` pairs
are disjoint and the three complete profile types are disjoint,

```text
2e + b + c <= n.                                    (8)
```

Equations (7)-(8) imply `e<=4(b+c)` and therefore
`e<=floor(4n/9)`.  The complete endpoint-class shape gives two further
necessary bounds.  Put `m=n-2e` for the number of nonendpoints.  Each endpoint
row contains its mate and three nonendpoints, so the endpoint rows contribute
`6e` nonendpoint incidences.  By (3),

```text
6e <= m*L_n.                                        (9)
```

They also contribute `6e` unordered nonendpoint-pair occurrences.  If `h` is
the number of polygon edges with both endpoints among the `m` nonendpoints,
the edge-sensitive capacity proof of (1) gives

```text
6e <= m*(m-1)-h,
h >= max(0,m-2e)=max(0,n-4e).                      (10)
```

The lower bound on `h` is the cyclic-run count: `2e` endpoint vertices can
separate at most `2e` nonendpoint runs.  Even dropping the favorable `h` term
and solving the resulting quadratic gives the clean universal consequence

```text
e <= floor((n+1-sqrt(3n+1))/2).                    (11)
```

Together with the `floor(4n/9)` bound above, this gives a concise combined
upper bound; equations (9)-(10) retain the sharper pointwise capacities.

The exact aggregate consequences are now:

- at `n=8,9`, localized equality forces all centers to be `T4`, hence `e=0`;
- for `n=10,...,20`, the upper bounds from (7)-(11) are respectively
  `2,3,3,3,4,4,5,5,5,6,6`;
- for every `n`, these equations give a reproducible integer upper bound,
  without asserting that an incidence system attaining it exists.

Thus the new all-class quantifier is a real strengthening of the support
ledger, but these bounds still do not force an exclusive mutual pair or a
contradiction in the open range.

## Verification

```bash
python scripts/check_all_rich_class_pair_budget.py --check --json
python -m pytest -q tests/test_all_rich_class_pair_budget.py
```

The checker verifies the capacity identities, profile excesses, endpoint
incidence and pair capacities, and the exact integer relaxation combining
(4) and (6)-(11) for `8<=n<=64`.  It does not assert attainability of the
reported upper bounds, verify Euclidean geometry, or assume that a
counterexample exists.

## Scope

Equations (1)--(6) are proved all-rich-class counting lemmas.  Equations
(7)--(11) are necessary consequences for a hypothetical minimal 4-bad
polygon.  Their present combination is not a global bridge contradiction; a
useful next step would have to exploit the geometry or overlap pattern of the
endpoint triples, rather than only their aggregate capacity.
