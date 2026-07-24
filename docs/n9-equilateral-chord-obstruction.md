# An exact obstruction for bad equilateral convex nonagons

Status: `REPO_LOCAL_THEOREM` for one sub-case of `n = 9` -- an elementary
reduction plus an exact finite certificate.

This note proves that no *equilateral* bad strictly convex nonagon exists. As
everywhere in this repository, a **bad** polygon is a strictly convex polygon
in which every vertex has at least four other vertices at one common distance
from it.

It does **not** prove Erdos Problem #97, and it does not close `n = 9`. A bad
nonagon need not be equilateral: at `n = 8` the base-apex count saturates and
*forces* equal sides (see `docs/n8-geometric-proof.md`), while at `n = 9` the
ledger has nine units of slack and equal sides are an extra hypothesis. The
non-equilateral nonagons are untouched here; see the last section.

The finite step is generated and replayed by
`scripts/check_n9_equilateral_chord_obstruction.py` against
`data/certificates/n9_equilateral_chord_obstruction.json`.

## Notation and the base-apex ledger

Let `A = {v_0,...,v_8}` be a bad strictly convex nonagon, indexed cyclically,
with all sides of length `s = 1`. Let `tau_j in (0,pi)` be the exterior turn at
`v_j`, and normalize

```text
x_j = tau_j / (2*pi),    x_j > 0,    sum_j x_j = 1.
```

Recall the base-apex count of `docs/n8-geometric-proof.md`. With `T(A)` the
number of isosceles triples `(p,{a,b})` -- apex `p`, base `{a,b}`, `|pa|=|pb|`
-- strict convexity caps each base pair at one apex per side of its line, and
a polygon side has vertices on one side only, so

```text
T(A) <= n + 2*(binom(n,2) - n) = n(n-2) = 63.
```

Badness gives `T(A) = sum_p sum_k binom(m_{p,k},2) >= 6n = 54`, where
`m_{p,1},m_{p,2},...` are the distance-class sizes at `p`. Writing

```text
E = sum_p (sum_k binom(m_{p,k},2) - 6)     profile excess, E >= 0
D = 63 - T(A)                              unused base-apex capacity, D >= 0
```

gives the exact ledger already recorded in `docs/n9-base-apex-frontier.md`:

```text
E + D = 9.                                                        (L)
```

Each *slot* -- a base pair together with one side of its line that contains at
least one vertex -- holds at most one apex, and `D` counts the empty slots.

## Step 1: the turn dictionary

Because the polygon is equilateral, the chord from `v_j` to `v_{j+k}` is the
sum of `k` unit vectors whose directions turn by

```text
sigma = tau_{j+1} + ... + tau_{j+k-1},
```

the turns strictly inside the short arc. Three consequences are used below.

**(D1)** `|v_j v_{j+2}| = 2*cos(tau_{j+1}/2)`, so

```text
|v_j v_{j+2}| = 1   <=>   tau_{j+1} = 2*pi/3   <=>   x_{j+1} = 1/3.
```

**(D2)** With `alpha = tau_{j+1}`, `beta = tau_{j+2}`,

```text
|v_j v_{j+3}|^2 = 3 + 2*(cos alpha + cos beta + cos(alpha+beta))
                = 1 + 8*cos(alpha/2)*cos(beta/2)*cos((alpha+beta)/2),
```

using `1 + cos a + cos b + cos(a+b) = 4*cos(a/2)*cos(b/2)*cos((a+b)/2)`. Since
`alpha, beta in (0,pi)`, the first two cosine factors are strictly positive and
`(alpha+beta)/2 in (0,pi)`, so

```text
|v_j v_{j+3}| = 1   <=>   tau_{j+1} + tau_{j+2} = pi   <=>   x_{j+1} + x_{j+2} = 1/2.
```

**(D3)** If `|v_j v_{j+k}| = 1` then `sigma >= 2*arccos(1/k)`. Indeed, if
`sigma <= pi`, project the `k` unit vectors onto the bisector of their angular
range: each makes an angle at most `sigma/2 <= pi/2` with it, so
`1 = |sum| >= k*cos(sigma/2)`, i.e. `cos(sigma/2) <= 1/k`. If `sigma > pi` the
bound is immediate because `arccos(1/k) < pi/2`. For `k = 4`,

```text
x_{j+1} + x_{j+2} + x_{j+3} >= 2*arccos(1/4)/(2*pi) = 0.4195693...           (D3')
```

`(D1)` and `(D2)` are equivalences; `(D3)` is only a lower bound, which is all
the argument needs.

## Step 2: at most two turns equal 2*pi/3

Let `M = {j : tau_j = 2*pi/3}`. If `|M| >= 3` then those three turns already
sum to `2*pi`, and the six remaining turns are strictly positive, so
`sum_j tau_j > 2*pi`. Hence

```text
|M| <= 2.                                                                    (M)
```

## Step 3: the ledger forces E <= 2*|M|

Consider the length-3 diagonal `{v_i, v_{i+3}}`. Its short side carries exactly
`v_{i+1}` and `v_{i+2}`, so that slot is filled only by one of them. If the
apex is `v_{i+1}` then `|v_i v_{i+1}| = |v_{i+1} v_{i+3}|`, i.e. the step-2
chord `v_{i+1} v_{i+3}` has length `1`, so `tau_{i+2} = 2*pi/3` by `(D1)`. If
the apex is `v_{i+2}` then `|v_i v_{i+2}| = |v_{i+2} v_{i+3}| = 1` and
`tau_{i+1} = 2*pi/3`. So a filled short side needs
`{i+1,i+2} intersect M != empty`, and each element of `M` serves at most two
indices `i`. At most `2*|M|` of these nine slots are filled, so

```text
D >= 9 - 2*|M|,   hence by (L)   E <= 2*|M| <= 4.                            (E)
```

## Step 4: the unit-distance chord graph

Let

```text
H = { non-adjacent pairs {v_j,v_k} with |v_j v_k| = 1 },
d_j = number of vertices at distance 1 from v_j,
h_j = d_j - 2 = degree of v_j in H.
```

Both neighbours of `v_j` are at distance `1`, so `d_j >= 2` and `h_j >= 0`. The
`H`-chords have cyclic step `2`, `3` or `4`, and by `(D1)` the step-2 chords of
`H` correspond exactly to the elements of `M`:

```text
m2 := (number of step-2 chords of H) = |M|.                                  (S)
```

Now bound the profile excess at a single vertex. The distance class of radius
`1` at `v_j` has `d_j` elements and badness gives some class of size at least
`4`. When `d_j <= 3` that class is a different one, so the two contribute
separately; when `d_j >= 4` the radius-1 class already has the required size.
Either way

```text
h_j = 0  (d_j = 2):   E_j >= binom(4,2) + binom(2,2) - 6 = 1
h_j = 1  (d_j = 3):   E_j >= binom(4,2) + binom(3,2) - 6 = 3
h_j = 2  (d_j = 4):   E_j >= 0
h_j = 3  (d_j = 5):   E_j >= binom(5,2) - 6 = 4
h_j >= 4 (d_j >= 6):  E_j >= binom(6,2) - 6 = 9.
```

By `(E)` the total excess is at most `4`, so `h_j <= 3` everywhere, at most one
vertex has `h_j = 1` or `h_j = 3`, and `h_j = 3` leaves no budget for anything
else. Both odd cases die on parity, since `sum_j h_j = 2*|H|` is even:

- one vertex with `h_j = 3` costs the whole budget, so all eight others have
  `h_j = 2` and `sum_j h_j = 19`;
- one vertex with `h_j = 1` costs `3`, leaving at most one vertex with
  `h_j = 0`, so `sum_j h_j` is `17` or `15`.

Hence every `H`-degree is `0` or `2`: `H` is a disjoint union of cycles
together with a set of isolated vertices. Writing `a` for the number of
isolated vertices, each of them contributes at least `1` to the excess, so
`a <= E`, and `H` has `9 - a` chords. Combining with `(E)` and `(S)`:

```text
every H-degree is 0 or 2,     a <= E <= 2*|M| = 2*m2 <= 4.                   (H)
```

## Step 5: the finite certificate

By `(H)` the chord graph `H` is one of finitely many graphs on `Z_9` with steps
in `{2,3,4}`. Enumeration gives `8712` graphs with all degrees in `{0,2}` and
at most four isolated vertices, of which `8097` also satisfy `a <= 2*m2`.

Each of them contradicts the turn dictionary. Fix such an `H` and let its
chords be `e_1,...,e_c` with spans `S_i` (the interior turn indices) and
thresholds

```text
w(e) = 1/3      if step(e) = 2        (equality, by (D1))
w(e) = 1/2      if step(e) = 3        (equality, by (D2))
w(e) = 839/2000 if step(e) = 4        (lower bound, by (D3'))
```

where `839/2000 = 0.4195 < 2*arccos(1/4)/(2*pi)`.

**Certificate lemma.** Let `lambda_1,...,lambda_c` be integers with
`lambda_i >= 0` whenever `step(e_i) = 4`, and put

```text
W = sum_i lambda_i * w(e_i),      c_j = sum_{i : j in S_i} lambda_i.
```

If `W > max_j c_j`, or if `W = max_j c_j` and `min_j c_j < max_j c_j`, then no
turn vector satisfies the constraints of `H`.

*Proof.* Steps `2` and `3` are equalities, so they may be multiplied by either
sign; step `4` is a lower bound and needs `lambda_i >= 0`. Summing,

```text
W <= sum_i lambda_i * x(S_i) = sum_j c_j * x_j <= (max_j c_j) * sum_j x_j = max_j c_j.
```

The first case is an outright contradiction. In the second case equality holds
throughout, so `sum_j (max_j c_j - c_j) * x_j = 0` with non-negative terms,
forcing `x_j = 0` at any vertex with `c_j < max_j c_j`, contradicting
`x_j > 0`. `QED`

The certificates are stored one per dihedral class -- `534` classes, all
refuted, `141` of them by the strict case. Every multiplier lies in
`{-1,0,1}` and at most four chords carry a nonzero weight, so each certificate
is a few lines of rational arithmetic. The checker verifies the certificates
directly rather than trusting the search that produced them: it re-enumerates
the `8097` graphs, maps each to its class representative, transports the stored
multiplier vector back along that dihedral map, and re-verifies it on the graph
itself.

**Theorem.** There is no bad strictly convex equilateral nonagon.

The smallest certificates already show the flavour. Three step-4 chords with
pairwise disjoint spans partition the nine turns and give
`W = 3*0.4195 > 1 = max_j c_j`; two step-3 chords with disjoint spans give
`W = 1 = max_j c_j` while the five uncovered vertices have `c_j = 0`, which is
the strictness case.

## Reproduce

```bash
python scripts/check_n9_equilateral_chord_obstruction.py --assert-expected --write
python scripts/check_n9_equilateral_chord_obstruction.py --check --assert-expected --summary-json
python -m pytest tests/test_n9_equilateral_chord_obstruction.py -m "" -q
```

## What this does not do

- It does not prove Erdos Problem #97 and does not change the official/global
  status, which remains falsifiable/open.
- It does not close `n = 9`. Step 1 is where equilaterality enters: `(D1)`,
  `(D2)` and `(D3)` all read chord lengths off turn angles alone, which needs
  equal sides. A bad nonagon with unequal sides pays capacity deficits at the
  length-2 diagonals -- one for each index where consecutive sides differ --
  but the ledger `(L)` has enough slack to absorb them, and the whole of Step 4
  collapses because `d_j >= 2` fails once the two sides at `v_j` differ.
- It does not interact with the selected-witness incidence pipeline. The
  argument here is about actual Euclidean distances, not about a chosen
  4-witness system, so it is independent evidence rather than a strengthening
  of the `n = 9` incidence artifacts.
- The turn-cover diagnostic of `docs/n9-base-apex-frontier.md` does *not*
  already cover this case: in the equilateral case every length-2 diagonal is
  saturated, the length-3 deficits are exactly the escape route that diagnostic
  records as unresolved, and `(H)` is what closes it.

A natural next target is the same reduction with one side length allowed to
differ, where `(D1)`-`(D3)` degrade into relations between three edge lengths
and one turn.
