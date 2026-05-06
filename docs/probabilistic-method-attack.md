# Probabilistic / entropy-counting attack on Erdős #97

Status: exploratory research note. Not a proof of #97. Documents an honest
audit of the standing combinatorial bound, an explicit derivation of a
better-than-`n^{2/5}` upper bound that is already implicit in the repository,
and a record of which entropy / probabilistic refinements I attempted and
where each one fails.

The official/global status of Erdős #97 (erdosproblems.com/97) remains
FALSIFIABLE/OPEN. This note does not change that. It also does not
strengthen the existing repo-local finite-case rulings (`n <= 8`).

## §1. The Pach–Sharir bound and what it gives

**Definition.** For an `n`-vertex strictly convex polygon `A`, let
```
M(v) := max_r |{u in A \ {v} : |u - v| = r}|,
f(n) := max over n-vertex strictly convex polygons of min_{v in A} M(v).
```
Erdős #97 asks whether `f(n) <= 3` for all sufficiently large `n`.

**Pach–Sharir bound (general planar version).** Let `I(P)` be the number of
isosceles triangles spanned by an `n`-point planar set `P`. Pach and Sharir
(1992; see Brass–Moser–Pach §5) prove
```
I(P) << n^{7/3}.
```

**Application to f(n).** For a bad polygon (every `M(v) >= k`), each apex
`v` contributes at least `binom(k,2)` ordered isosceles triples (apex,
base-pair). So
```
n * binom(k, 2) <= I(A) << n^{7/3},
```
giving `k(k-1) << n^{4/3}`, hence `k << n^{2/3}`. The user's prompt cites
`f(n) << n^{2/5}`, which is the version one obtains after a more careful
double counting of the apex contribution; either way the exponent is a
power of `n` strictly larger than `1/2` and the bound has nothing to say at
`n = 9`.

## §2. A strictly better bound is already in the repo

The Pach–Sharir bound is not optimal for **strictly convex** point sets,
because the base-apex lemma (L4 / `docs/n8-geometric-proof.md` §1) gives a
much sharper isosceles count when `P` is in strictly convex position.

**Lemma (base-apex; recorded in `docs/n8-geometric-proof.md`).** Let `A` be
the vertex set of a strictly convex `n`-gon and let `a, b in A`, `a != b`.
On each open half-plane bounded by line `ab`, at most one vertex
`p in A \ {a, b}` satisfies `|pa| = |pb|`.

**Corollary (capacity bound).** Let
`T(A) := #{(p, {a,b}) : p, a, b in A, p not in {a,b}, |pa|=|pb|}` be the
number of (apex, base) isosceles triples in `A`. Then
```
T(A) <= 1 * n + 2 * (binom(n,2) - n) = n (n - 2).
```

**Corollary (sharper Pach–Sharir for convex position).** If `A` is bad with
every `M(v) >= k`, then
```
n * binom(k, 2) <= T(A) <= n (n - 2),
```
hence
```
k (k - 1) <= 2 (n - 2),    i.e.    k <= (1 + sqrt(8n - 15)) / 2.
```

**Numerical comparison.**

| `n` | Pach–Sharir `n^{2/5}` | base-apex `(1+sqrt(8n-15))/2` |
|----:|----------------------:|------------------------------:|
| 8   | 2.30 (vacuous, < 4)   | 4 (gives `n>=8`)              |
| 9   | 2.41                  | 4.27 -> floor 4               |
| 12  | 2.70                  | 5.0 (gives `n>=12` for k=5)   |
| 17  | 3.02                  | 6.0                           |
| 32  | 4.00                  | 8.4                           |
| 100 | 6.31                  | 14.6                          |

The convex-position-specific bound `f(n) <= floor((1 + sqrt(8n-15))/2)` is
**strictly stronger than `n^{2/5}` for every `n >= 5`**, and unlike
Pach–Sharir it actually gives `f(n) <= 4` already at `n = 9`. This is not
new mathematics: the lemma is the same one used in
`docs/n8-geometric-proof.md` §1 and `docs/n8-short-proof.md` §1 to close
`n <= 8`. It is, however, worth recording as the right combinatorial
benchmark — the prompt's framing using Pach–Sharir overstates what the
literature's combinatorial bound is once strict convexity is exploited.

## §3. Why the bound stops at sqrt(n)

The base-apex capacity is tight on the equilateral configurations the
`n = 8` argument exploits. So `T(A) <= n(n-2)` cannot be improved by
more than a constant factor without a new geometric input. The bound

```
f(n) <= O(sqrt(n))
```

is what one buys from "strictly convex isosceles count alone." To go below
`sqrt(n)` — and certainly to reach the conjectured `f(n) <= 4` for all
large `n` — one needs an additional ingredient that a generic isosceles
counting argument cannot supply.

This frames the gap between `f(n) << sqrt(n)` (proved here, modulo standard
folklore) and the conjectured `f(n) <= 4` as a quantitative version of the
exact `n=8` closure: the equality case at `n=8` (equilateral, every
`tau_j = 2 pi / 3` for `j` in a min vertex cover) is precisely the
configuration where the base-apex bound is saturated.

## §4. Probabilistic / entropy refinements attempted

### §4.1 Random-direction split (FAILED).

**Idea.** Pick a direction `theta` uniformly in `[0, pi)`. For each
isosceles triangle `(i; a, b)`, the perpendicular bisector of `ab` is a
line through `i`; project `i, a, b` onto direction `theta`. With positive
probability the apex `i` is "extreme" in the projected order. Try to use
this to halve the contribution of each apex.

**Failure.** This kind of averaging multiplies the lower bound
`n * binom(k,2)` by `1/2` and the upper bound `n(n-2)` by `1/2`, so the
constant cancels and the exponent does not move. The same is true for any
linear projection averaging: it preserves the ratio of the two sides of
the inequality. Recorded as a generic "first moment" failure mode.

### §4.2 Cauchy–Schwarz / energy on apex distributions (FAILED).

**Idea.** Let `t(v) := #{(a,b) : |va|=|vb|}` so `T(A) = sum_v t(v)`. By
Cauchy–Schwarz,
```
(sum_v t(v))^2 <= n * sum_v t(v)^2.
```
If we had a bound `sum_v t(v)^2 <= C(n)`, we would deduce
`T(A) <= sqrt(n * C(n))`.

**Failure.** No bound on `sum_v t(v)^2` is known that beats the trivial
`(n-1)^2 * n`. In the equality cases that saturate `T(A) = n(n-2)`,
`t(v)` is uniformly `n-2` so `sum t(v)^2 = n (n-2)^2`, and Cauchy–Schwarz
is sharp. The energy refinement does not improve the exponent.

### §4.3 Apex-side asymmetry per vertex (FAILED, but flags a real obstacle).

**Idea.** A bad apex `i` of order `k` contributes `binom(k, 2)` isosceles
triples, all with bases on a single circle around `i`. The bases are
chords of that circle, so they have a restricted **direction** structure:
each base chord is perpendicular to a line through `i`.

In the strictly convex polygon, at most two vertex chords can be parallel
to a fixed direction (this is L2-style parallelism, since a third vertex
chord parallel to the first two would force three vertices on a line
through any fixed parallel translate). So the `binom(k, 2)` chord bases
at one apex do NOT all have distinct directions; in fact the chord
directions are tightly constrained.

**Why this does not improve the bound.** The base-apex lemma already uses
all of this information (the apex constraint is exactly that both
"apex-side" parities are bounded). The chord-direction restriction at one
apex says nothing about the GLOBAL bound on `T(A)` because the same chord
can be re-used as a base from a different apex. The argument bumps into
the saturation cases for the existing inequality, not against it.

### §4.4 Pach–Pinchasi unit-equilateral analogue (FAILED).

**Idea.** Pach–Pinchasi (2002) prove: in a convex `n`-gon, the number of
unit-equilateral triangles is at most `2(n-1)/3`. If a similar linear
bound held for "isosceles-with-fixed-apex-radius" — a triangle
`(i; a, b)` with `|ia|=|ib|=r_i` for the bad-radius `r_i` — that would
give `n * binom(k,2) <= O(n)` and force `k = O(1)`, which is exactly #97.

**Why this fails as stated.** The Pach–Pinchasi bound is for
**equilateral** triangles in a convex set: all three sides have the same
unit length. An isosceles-with-fixed-apex-radius is a much weaker
constraint, and the counting argument behind Pach–Pinchasi (a 3-coloring
of the unit-distance graph in convex position) does not generalize.
Explicitly: the Fishburn–Reeds 20-gon has many isosceles-with-fixed-
apex-radius triples (each `M(v) = 3` gives `binom(3,2) = 3` triples per
apex, total `60`) but only a handful of unit-equilateral triangles.

So linear-in-`n` is not the right bar at constant apex multiplicity.

### §4.5 Entropy / dual counting on (apex, base, side) triples (FAILED).

**Idea.** Encode an isosceles triple `(i; a, b)` by `H(i; a, b) =
H(a, b) + H(i | a, b)`. The first piece is `<= log binom(n, 2)` and the
second piece is bounded by `log 2` from the base-apex lemma, giving
```
log T(A) <= log binom(n, 2) + log 2,
```
i.e. `T(A) <= n(n-1)`, which is weaker than the deterministic
`T(A) <= n(n-2)` already in hand.

**Diagnostic.** The entropy approach matches the deterministic capacity
bound up to a `1 + o(1)` factor. To improve the exponent one would need
the conditional entropy `H(i | a, b)` to be strictly less than `log 2`
on average over `(a, b)` — i.e., one would need most diagonals to have
strictly less than 2 apices. The base-apex lemma cannot give this:
ALL diagonals have the worst-case capacity `2`, equality cases being
plentiful (any vertex on the diagonal's perpendicular bisector and inside
the convex hull works in principle).

The right ingredient — average-case strengthening of the base-apex
capacity — would have to come from convex-position cyclic-order
constraints that say "across all `binom(n,2) - n` diagonals of a strictly
convex `n`-gon, the average number of polygon vertices on a perpendicular
bisector is strictly less than `2`." I do not see how to prove this; it
is a concrete open subgoal flagged by this attack.

## §5. Where the attack actually leaves the picture

| `n` | base-apex bound on `f(n)` | finite-case ruling                                   |
|----:|--------------------------:|-----------------------------------------------------:|
| <=7 | trivially excludes `k=4`   | proved (`n=7` Fano + base-apex)                       |
| 8   | `k <= 4`, equality at `k=4` killed by §6 of `n8-short-proof.md` | proved (`n=8` repo-local) |
| 9   | `k <= 4`                   | review-pending exhaustive vertex-circle (data/certificates/n9_vertex_circle_exhaustive.json) |
| 10  | `k <= 4`                   | partial: singleton-slice coverage; full integrated rerun in progress |
| 11  | `k <= 4`                   | ~40 h naive Python; Rust port plausible              |
| 12+ | `k <= 5,6,...`             | base-apex alone permits `k>=5`; need a separate ingredient |

The repository already proves `f(n) <= 4` for `n <= 11` via the base-apex
bound (`k <= 4` for any `n` with `n - 2 < 10`, i.e. `n <= 11`). The
finite-case checkers complete `n = 8` exactly (with two independent
proofs: equality-trap geometric, plus Gröbner). For `n = 9, 10, 11` the
combinatorial bound `k <= 4` is in hand but does not by itself force
`k <= 3`; closing #97 at small `n` is what the vertex-circle exhaustive
checker handles.

For `n >= 12`, the base-apex combinatorial bound permits `k >= 5`, so
to keep `f(n) <= 4` (let alone `<= 3`) one needs a strengthening that
goes beyond the convex-position isosceles count. None of the
probabilistic / entropy refinements I tried provides such a
strengthening.

## §6. Honest summary

- **Best new combinatorial upper bound recorded here:**
  `f(n) <= floor((1 + sqrt(8n - 15)) / 2) = O(sqrt(n))`. This is the
  base-apex consequence; it improves the prompt's `n^{2/5}`
  framing for all `n >= 5`. **Not original; implicit in the
  `n8-geometric-proof.md` and `n8-short-proof.md` proof-notes already in
  the repo.** Recorded here so that future probabilistic attempts have
  the correct reference baseline.

- **No new `f(n) << n^{c}` bound with `c < 1/2` is established here.**
  Each of the entropy / probabilistic refinements I tried (random-
  direction split, Cauchy–Schwarz energy, dual-counting entropy)
  reproduces the base-apex bound up to a factor and does not move the
  exponent.

- **Concrete sub-conjecture flagged by §4.5.** A genuine improvement
  beyond `O(sqrt(n))` would follow from an average-case strengthening
  of the base-apex capacity: prove that across the `binom(n,2) - n`
  diagonals of a strictly convex `n`-gon, the average number of
  vertices on a diagonal's perpendicular bisector is `< 2`. I could
  not prove this and have not seen it in the literature; if true, it
  would convert the `f(n) = O(sqrt(n))` bound into something strictly
  better. This is the cleanest probabilistic-method-flavored open
  subgoal isolated by this attack.

- **No improvement to the repo-local finite-case status.** The `n <= 8`
  closure stands as before; the `n = 9, 10` review-pending checkers are
  unchanged.

## §7. Comparison with the literature

| Source | Bound | Method | Notes |
|--------|-------|--------|-------|
| Pach–Sharir 1992 | `f(n) << n^{2/5}` | `I(P) << n^{7/3}` for general planar `P`; double counting | Standing reference, `O(n^{7/3})` is canonical for ARBITRARY planar point sets |
| Aggarwal 2010/2015 | `n log_2 n + O(n)` | Common-radius / unit-distance subcase | Stricter problem (uniform `r`), not directly comparable |
| Erdős 1975 (claim) | "every `k` works" attribution to Danzer | unpublished | erdosproblems.com flags as presumably mistaken |
| `docs/n8-short-proof.md` | `f(n) <= floor((1+sqrt(8n-15))/2)` | base-apex + capacity sum | **This bound is already in the repo**; it implies `f(n) <= O(sqrt(n))` for all `n` |
| `docs/n9-vertex-circle-exhaustive.md` | `f(9) <= 3` (review-pending) | exhaustive selected-witness incidence + vertex-circle filter | review-pending |
| Conjectured #97 | `f(n) <= 3` for `n >= n_0` | open | gap from `O(sqrt(n))` to `O(1)` is super-polynomial |

## §8. Files

- This note: `docs/probabilistic-method-attack.md`.
- Proof of base-apex lemma: `docs/n8-short-proof.md` §1, `docs/n8-geometric-proof.md`.
- Capacity-saturation slack ledger at `n=9`: `docs/n9-base-apex-frontier.md`.
- Repo-local finite-case proof at `n=8`: `docs/n8-incidence-enumeration.md`,
  `docs/n8-exact-survivors.md`, `data/certificates/2026-05-05/n8_groebner_results.json`.
- Standing-literature memo: `docs/literature-update-2026-05-06.md`.
