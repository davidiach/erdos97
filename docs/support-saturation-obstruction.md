# Support-saturation obstruction

Status: `LEMMA` / proof-facing equality-case obstruction. This note does not
claim a general proof of Erdos Problem #97 and does not claim a counterexample.

This note strengthens the edge-sensitive rich-support count in
`docs/rich-support-counting-lemma.md` at its equality wall. The counting lemma
says that, for one same-radius support `R_i` chosen at each center of a strict
convex `n`-gon,

```text
sum_i binom(|R_i|, 2) <= n(n - 2).
```

Consequently, if every center has a same-radius support of size at least `k`,
then pair-counting alone gives

```text
n >= binom(k, 2) + 2.
```

The equality case is impossible for `k >= 4`.

## Saturated equality lemma

Let `V = {v_0,...,v_{n-1}}` be the cyclic vertex set of a strictly convex
polygon, and choose one same-radius support

```text
R_i subset V \ {v_i}
```

at every center `v_i`. Suppose `|R_i| >= k >= 4` for every `i` and

```text
n = binom(k, 2) + 2.
```

Then no such support system exists.

Equivalently, for every `k >= 4`, any strict convex polygon whose every vertex
has `k` equidistant witnesses must satisfy

```text
n >= binom(k, 2) + 3.
```

## Proof

At the equality wall,

```text
n * binom(k, 2) = n(n - 2).
```

Since each support has size at least `k`, the rich-support counting lemma can
hold only if every support has size exactly `k` and every witness-pair capacity
is saturated. Thus:

1. every hull-edge witness pair occurs together in exactly one selected
   support;
2. every diagonal witness pair occurs together in exactly two selected
   supports.

The base-apex lemma from `docs/n8-geometric-proof.md` says that, for a fixed
base pair `{a,b}`, all centers using both witnesses lie on the perpendicular
bisector of `ab`, with at most one such center on each side of the line `ab`.
Therefore a saturated diagonal has one selected-support center on each side.

Consider the length-2 diagonal `{v_i,v_{i+2}}`. One side of this diagonal
contains only `v_{i+1}`. Since the diagonal pair is saturated, `v_{i+1}` is the
selected-support center on that short side. Hence

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+2}|.
```

This holds for all `i`, so all side lengths are equal. Let the common side
length be `s`.

Let `tau_j in (0,pi)` be the exterior turn angle at `v_j`. For an equilateral
strict convex polygon,

```text
|v_{j-1} v_{j+1}| = 2s cos(tau_j / 2).
```

Thus `|v_{j-1} v_{j+1}| = s` if and only if

```text
tau_j = 2*pi/3.
```

Now consider the length-3 diagonal `{v_i,v_{i+3}}`. Its short side contains
exactly `v_{i+1}` and `v_{i+2}`. Saturation again gives a selected-support
center on that short side.

If the short-side center is `v_{i+1}`, then

```text
|v_i v_{i+1}| = |v_{i+1} v_{i+3}|,
```

so `|v_{i+1} v_{i+3}| = s`, and therefore `tau_{i+2} = 2*pi/3`.

If the short-side center is `v_{i+2}`, then

```text
|v_i v_{i+2}| = |v_{i+2} v_{i+3}|,
```

so `|v_i v_{i+2}| = s`, and therefore `tau_{i+1} = 2*pi/3`.

Hence the set

```text
M = {j : tau_j = 2*pi/3}
```

hits every adjacent pair of indices in the `n`-cycle. In other words, `M` is a
vertex cover of the cycle. Since `n = binom(k,2) + 2 >= 8`, every such cover
has size at least `4`. Therefore

```text
sum_j tau_j >= 4 * (2*pi/3) = 8*pi/3 > 2*pi,
```

contradicting the total exterior turn `sum_j tau_j = 2*pi` of a strict convex
polygon.

Thus the equality wall is impossible.

## Consequences

The pure support count gives `n >= binom(k,2)+2`; the saturated equality lemma
raises this to

```text
n >= binom(k, 2) + 3       for k >= 4.
```

Concrete small thresholds:

```text
k = 4:  n >= 9
k = 5:  n >= 13
k = 6:  n >= 18
k = 7:  n >= 24
```

For `k=4`, this recovers the repository's no-bad-octagon obstruction from a
support-saturation viewpoint. It does not replace the existing `n <= 8`
selected-witness and geometric proof notes.

For `k=5`, it upgrades the all-five-rich support subcase: pair-counting alone
left the equality wall `n=12`, but saturation rules out that dodecagon case.
Thus every vertex having five equidistant witnesses requires `n >= 13`.

## Verification command

The helper script

```bash
python scripts/check_support_saturation_obstruction.py --check --json
```

checks the upgraded thresholds and the cycle vertex-cover turn arithmetic. It
is only an arithmetic checker for the proof note; it is not a realization
search.

## Boundary

This lemma is only an equality-wall obstruction. It does not rule out mixed
exact-four and size-five catalogues, does not prove the review-pending `n=9` or
`n=10` finite-case artifacts, and does not prove Erdos Problem #97.
For `n=9`, it leaves the existing exact-four frontier and mixed-rich/frontier
crosswalk as the relevant proof targets.
