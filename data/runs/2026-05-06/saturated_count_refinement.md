# Saturated incidence count refinement (Erdos #97, n >= 9)

Status: `EXPLORATORY_ANALYSIS_ONLY`. No closure of `n = 9` is claimed.

## 1. Refined `T(A)` decomposition

For a strictly convex `n`-gon, decompose `T(A)` by cyclic distance `k`:

```text
T(A) = s + sum_{k=2}^{floor(n/2)} d_k
s   = sum over n sides of apex count, cap s <= n
d_k = sum over length-k diagonals, cap d_k <= 2 n if 2 k != n,
      d_{n/2} <= n if n even.
```

For `n = 9`: `T = s + d_2 + d_3 + d_4`, `s <= 9`, each `d_k <= 18`.

## 2. Refined upper bound on `T(A)`

Two refinement attempts were tested:

**(a) Per-length analytic cap reduction.** Checked whether length-2/3/4
diagonals admit a tighter cap than 2. They do not. *Explicit construction*
in `/tmp/saturated_explicit_length2.py`: strictly convex 9-gon with
`v_0=(-1,0)`, `v_1=(0,-0.4)`, `v_2=(1,0)`, five vertices on a semi-ellipse
above with `v_5=(0, 0.9)`. The length-2 diagonal `{v_0, v_2}` has exactly
2 apices (`v_1`, `v_5`). Strict convexity verified. The cap of 2 is
genuinely attained at length 2.

**(b) Witness arc width.** At each vertex `p`, all `n - 1` other vertices
lie inside an open angular wedge of aperture `pi - tau_p < pi`. So `w >= 4`
witnesses span a sub-arc smaller than `pi`. Gives the identity
`sum_p (pi - tau_p) = (n - 2) pi` and forbids obtuse apex angles among
same-class witnesses. Does *not* yield any per-base cap reduction.

Verdict: the standard upper bound `T(A) <= n + 2(C(n,2) - n) = n(n - 2)`
remains the sharpest available from the base-apex framework.

## 3. Tightness — does this close any `n > 8`?

No. Slack `n(n - 2) - 6 n = n(n - 8)`:

```text
n       6n   T_hi  slack
 8      48    48     0    (closed via vertex cover argument)
 9      54    63     9
10      60    80    20
11      66    99    33
12      72   120    48
16      96   224   128
```

For closure at `n` via cap reduction alone, the *average* diagonal apex
cap would have to drop below:

```text
n = 9:  1.667    n = 12: 1.111
n = 10: 1.429    n = 16: 0.769
n = 11: 1.250    n = 20: 0.588
```

Reducing length-2 *and* length-3 diagonal caps from 2 to 1 closes `n = 10`
exactly (slack 0) but leaves `n = 11` with slack 11 and is hopeless for
`n >= 12`. Reducing caps at length 2, 3, *and* 4 closes `n = 11` (slack 0)
but leaves `n = 12` with slack 12. So no fixed-finite per-length cap
reduction can reach `n >= 13` from this ledger.

## 4. Combinatorial feasibility

Counts of integer tuples `(s, d_2, ..., d_{floor(n/2)})` with
`s <= n`, `d_k <= 2 n_k`, and `6 n <= sum <= n(n-2)`:

```text
n =  9 :    715 feasible tuples
n = 10 : 49,126 feasible tuples
n = 11 :424,150 feasible tuples
```

At the *exact lower bound* `T = 6 n` (every vertex contributes exactly 6):
220 feasible tuples for `n = 9`. Pigeonhole: with `s <= n = 9` and
`sum d_k >= 54 - 9 = 45` over 27 diagonals each capped at 2, *at least 18
of 27 diagonals are fully saturated* (have exactly 2 apices). This is a
new structural fact about the `T = 54` slice but does not yield
contradiction by itself.

## 5. Findings

- Base-apex caps (1 sides, 2 diagonals) are *attained* at every cyclic
  distance `k` including `k = 2`. The bound `T(A) <= n(n - 2)` cannot be
  improved by per-base analytic refinement under strict convexity alone.
- Witness-arc-width arguments give a global identity but no per-base
  sharpening.
- Slack `n(n - 8)` grows quadratically; no fixed-length cap reduction
  closes `n >= 13`.

Closure for `n >= 9` requires a new ingredient: per-vertex excess lower
bound `E >= c n`, a non-incidence geometric obstruction, or exploiting
the joint distribution among base lengths. The 18-of-27-saturated fact
at `T = 54` is a candidate handle.

## Reproduction

```text
python /tmp/saturated_analysis.py
python /tmp/saturated_arc_lemma.py
python /tmp/saturated_explicit_length2.py
```

Related: `docs/n8-geometric-proof.md`, `docs/n9-base-apex-frontier.md`,
`scripts/explore_n9_base_apex.py`.
