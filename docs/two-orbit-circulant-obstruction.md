# Two-orbit circulant obstruction (all offsets, all radii)

Trust label: `LEMMA` draft, review pending. The statement and proof below are
elementary and self-contained, with a redundant machine audit, but they have
not had independent external review, so this note is not promoted into the
source-of-truth dashboard claims yet. This is a restricted-family obstruction
only: it is not a proof of Erdos Problem #97, and it is not a counterexample
or a counterexample search.

## Statement

Let `m >= 3`, `h = pi/m`. Consider any strictly convex polygon on `2m`
vertices whose vertex set is the union of two concentric regular `m`-gons

```text
A_k = R * exp(i * 2kh),        k = 0..m-1,   R > 0,
B_k = x * R * exp(i * (phi + 2kh)),   k = 0..m-1,   x > 0,
```

with any relative rotation `phi` and any radius ratio `x` (all `2m` points
distinct). Then at least one vertex has no four other vertices on a circle
centered at that vertex.

Equivalently: no two-orbit `C_m` configuration is a counterexample candidate
for Erdos Problem #97 (it cannot be "4-bad" in the repo sense).

This supersedes, within its family, two earlier fixed-instance results: the
half-step quarter-turn ansatz obstruction
(`docs/two-orbit-radius-propagation.md`, which fixed both the offset and the
witness pattern) and the alternating two-radius paired-distance note. The new
content is that *every* offset `phi`, *every* radius ratio, and *every*
witness pattern are excluded at once.

## Proof

Fix `R = 1`. Reindexing `B_k -> B_{k+1}` shifts `phi` by `2h`, and complex
conjugation reflects the configuration while negating `phi`, so we may take
`phi in [0, h]`.

### Step 1: equal distances force `phi in {0, h}`

Distances from `A_0`:

- Same orbit: `|A_0 - A_k|^2 = 4 sin^2(kh)`. The values for
  `k = 1..floor(m/2)` are strictly increasing, and `k`, `m-k` give the same
  value. So a circle centered at `A_0` meets the `A`-orbit in at most one
  *pair* `{A_a, A_{-a}}` with `1 <= a < m/2`, or in the single antipode
  `A_{m/2}` when `m` is even.
- Cross orbit: `|A_0 - B_k|^2 = 1 + x^2 - 2x cos(phi + 2kh)`. Two distinct
  cross vertices are equidistant from `A_0` iff
  `cos(phi + 2kh) = cos(phi + 2lh)` with `k != l`, which forces
  `phi = -(k+l)h (mod pi)`. The only such values in `[0, h]` are `0` and
  `h`.

If `phi` is not `0` or `h`, every circle centered at `A_0` contains at most
one cross vertex, and at most a same-orbit pair besides (the pair and the
antipode cannot share a radius, since `4 sin^2(ah) = 4` forces `a = m/2`).
That caps the count at `3 < 4`, so vertex `A_0` already fails. Hence
`phi in {0, h}`.

### Step 2: `phi = 0` is impossible

Then `A_k` and `B_k` lie on the same ray from the center `O`, with `x != 1`
because the points are distinct. `O` is interior to the hull (it is the
center of the regular `m`-gon `{A_k}`, `m >= 3`). The nearer of the two
points lies strictly between `O` and the farther one, hence strictly inside
the hull, contradicting strict convexity.

### Step 3: `phi = h` forces the row shape and one equation

Now `|A_0 - B_k|^2 = 1 + x^2 - 2x cos((2k+1)h)`. Writing `o = 2k+1`, the
odd residues `o` and `2m-o` give equal values; the values for odd
`o = 1, 3, ...` up to `m` are strictly decreasing in `cos(oh)`, i.e.
pairwise distinct. So a circle centered at `A_0` meets the `B`-orbit in at
most one pair `{B_k, B_{m-1-k}}` (odd `o <= m-1`), or the single pole
`B_{(m-1)/2}` at squared distance `(1+x)^2` when `m` is odd.

Four vertices on one circle centered at `A_0` therefore require one
same-orbit pair plus one cross-orbit pair: every other composition is short
of four or forces a radius coincidence that collapses (pair plus antipode
forces `a = m/2`; pair plus pole forces `cos(oh) = -1`, i.e. the pair *is*
the pole; two cross pairs force equal cosines). Hence there are
`a in {1, ..., ceil(m/2) - 1}` and odd `p in {1, ..., m-1}` with

```text
E_A:   4 sin^2(ah) = 1 + x^2 - 2x cos(ph).
```

### Step 4: strict convexity pins `x` to the window `(cos h, sec h)`

With `phi = h` the `2m` points sit at the distinct angles
`0, h, 2h, ..., (2m-1)h`, alternating `A, B`. All points are extreme iff the
closed polygon in this angular order is strictly convex, iff both signed
turn types are positive:

```text
det(B_0 - A_0, A_1 - B_0) = 2 sin h (x - cos h) > 0,
det(A_1 - B_0, B_1 - A_1) = 2x sin h (1 - x cos h) > 0,
```

giving exactly `cos h < x < sec h` (the same window as
`docs/two-orbit-radius-propagation.md`).

### Step 5: `E_A` has no root in the window

Let `g(x) = x^2 + 1 - 2x cos(ph)`. On the window, `g' = 2(x - cos(ph)) > 0`
since `x > cos h >= cos(ph)`. So `E_A` has a root in the open window iff

```text
g(cos h) < 4 sin^2(ah) < g(sec h).
```

Write `p = 2r + 1` and `C_j = cos(2jh)`. Using
`2 cos h cos(ph) = C_r + C_{r+1}` and `4 sin^2(ah) = 2 - 2 C_a`, the two
inequalities become

```text
T > -sin^2 h      and      T < (1 - 2 C_a) sin^2 h,
where  T = C_r + C_{r+1} - 2 C_a.
```

We show no valid `(a, r)` satisfies both, splitting on `a` versus `r`. The
difference identities used are
`C_j - C_{j+1} = 2 sin((2j+1)h) sin h` and
`C_{j-1} - C_{j+1} = 2 sin(2jh) sin(2h)`; index ranges keep every sine
argument in `(0, pi)`, in particular `sin((2j+1)h) >= sin h` whenever
`1 <= 2j+1 <= m-1`.

- Case `a <= r - 1` (so `r >= 2`): here
  `-T = (C_a - C_r) + (C_a - C_{r+1})
      >= (C_{r-1} - C_r) + (C_{r-1} - C_{r+1})
       = 2 sin((2r-1)h) sin h + 2 sin(2rh) sin(2h) > 2 sin^2 h`,
  using `sin((2r-1)h) >= sin h` and `sin(2rh) > 0`. So `T < -sin^2 h`:
  the lower inequality fails.
- Case `a = r`: `T = C_{r+1} - C_r = -2 sin((2r+1)h) sin h <= -2 sin^2 h`,
  again failing the lower inequality.
- Case `a = r + 1`: `T = C_r - C_{r+1} = 2 sin((2r+1)h) sin h > 0`, and the
  upper inequality reduces (via `2 cos(theta + h) sin h =
  sin(theta + 2h) - sin(theta)` with `theta = (2r+1)h`) to
  `2 sin(theta + h) cos h < sin h`. But `theta + h in [2h, pi - h]` gives
  `sin(theta + h) >= sin h`, so the left side is at least
  `2 sin h cos h = sin(2h) >= sin h`, with equality only at `m = 3`
  (`theta = h = pi/3`), where the root is exactly `x = sec h`, excluded by
  the open window. The upper inequality fails for every `m >= 3`.
- Case `a >= r + 2` (forces `a >= 2` and `m >= 2a + 1 >= 5`): using
  `C_r >= C_{a-2}`, `C_{r+1} >= C_{a-1}` and
  `2 C_a cos^2 h = C_a + (C_{a-1} + C_{a+1})/2`,

  ```text
  T - (1 - 2 C_a) sin^2 h
      = C_r + C_{r+1} - C_a - (C_{a-1} + C_{a+1})/2 - sin^2 h
     >= (C_{a-2} - C_a) + (C_{a-1} - C_{a+1})/2 - sin^2 h
      = sin(2h) * (2 sin((2a-2)h) + sin(2ah)) - sin^2 h.
  ```

  Since `2a <= m - 1`, both sines are positive, and
  `sin((2a-2)h) >= sin(2h)` (the argument lies in `[2h, pi - 3h]` and
  `m >= 5`), so the bound is at least
  `2 sin^2(2h) - sin^2 h = (8 cos^2 h - 1) sin^2 h > 0` for `m >= 3`. The
  upper inequality fails strictly.

So `E_A` never has a root in the open window: vertex `A_0` cannot have four
equidistant vertices while the configuration stays strictly convex. (The
`B`-orbit rows give a symmetric equation, but the `A`-row failure already
finishes the proof.) QED (review pending).

## Machine audit

`scripts/check_two_orbit_dynamic_window_lemma.py` independently checks, for
every `m` in a range and every valid `(a, p)`, that the quadratic `E_A` has
no root in the open window, using two redundant formulations (direct root
location and the `T`-interval form) that are required to agree, with
60-digit arithmetic and exact sympy escalation near boundaries:

```bash
python scripts/check_two_orbit_dynamic_window_lemma.py --max-m 120 --assert-clear
```

Recorded result: `m = 3..120`, `142,190` pairs checked, zero window roots,
and exactly one boundary equality hit, at `m = 3`, `a = 1`, `p = 1`, which
is the `x = sec h` equality case identified in Step 5 and excluded by strict
convexity. The default `--max-m 400` run is also clear.

## Scope and non-claims

- The lemma constrains only vertex sets that are unions of two concentric
  regular `m`-gons. It says nothing about three or more orbits, non-cyclic
  configurations, or the general problem; the official/global status of
  Erdos Problem #97 remains falsifiable/open.
- The numerical dynamic-witness sweep
  (`docs/dynamic-witness-free-pattern-search.md`) is consistent with this
  lemma: all its strictly convex `t = 2` cells plateau at relative spreads
  around `1e-2` or above at healthy margins.
- Next bridge-facing question recorded for the loop: extend the angle-forcing
  step to `t >= 3` orbits, where cross-orbit cosine equalities no longer
  force a single half-step alignment and the same reduction needs a
  case catalogue.
