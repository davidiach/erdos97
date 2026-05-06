# Geometric n=9 extension: analysis

Status: `EXPLORATORY_ANALYSIS_ONLY`. This note does not close `n = 9`.
The case `n >= 9` of Erdos #97 remains open.

## Summary of findings

1. The equilateral-implies-contradiction argument works rigorously for every
   `n >= 7`, conditional on the polygon being equilateral. Verified.
2. At `n = 9`, the base-apex bound has slack `9 = n(n-2) - 6n`, so saturation
   does NOT force every length-2 diagonal to have an apex on its short side.
   Hence the n=8 deduction "all sides equal" does NOT carry over to n=9.
3. The existing repository note `docs/n9-base-apex-frontier.md` and script
   `scripts/explore_n9_base_apex.py` already record this gap: 65 of 95
   unlabeled excess distributions are closed by the strict turn-cover
   diagnostic; the unresolved 30 have low profile excess and high capacity
   deficit and currently escape the closure.
4. No new airtight closure of `n = 9` is found here. A genuine
   anti-concentration or capacity-distribution lemma is still required. I
   record the exact analytic gaps below.

## 1. Equilateral n-gon contradiction (rigorous, conditional)

Let `A = {v_0, ..., v_{n-1}}` be a strictly convex equilateral bad `n`-gon
with side length `s` and exterior turn `tau_j` at `v_j`. Then
`sum_j tau_j = 2 pi`. For an equilateral convex polygon,

```text
|v_{j-1} v_{j+1}| = 2 s cos(tau_j / 2),
```

so `|v_{j-1} v_{j+1}| = s` iff `tau_j = 2 pi / 3`. The base-apex lemma still
caps each length-3 diagonal at two apices.

**Crucial conditional step.** Assume every length-3 diagonal `{v_i, v_{i+3}}`
has at least one apex on its short side (which is `{v_{i+1}, v_{i+2}}`). Then:

- if `v_{i+1}` is the apex, `|v_i v_{i+1}| = |v_{i+1} v_{i+3}|`, so
  `s = |v_{i+1} v_{i+3}|` and `tau_{i+2} = 2 pi / 3`;
- if `v_{i+2}` is the apex, `|v_i v_{i+2}| = |v_{i+2} v_{i+3}|`, so
  `|v_i v_{i+2}| = s` and `tau_{i+1} = 2 pi / 3`.

Therefore for each `i`, at least one of `tau_{i+1}, tau_{i+2}` equals
`2 pi / 3`. The set `M = {j : tau_j = 2 pi / 3}` is a vertex cover of the
edge set `{(i+1, i+2) : i in Z_n}` of the n-cycle. Minimum vertex cover of an
n-cycle has size `ceil(n / 2)`. So

```text
sum_j tau_j >= ceil(n/2) * (2 pi / 3).
```

For `n = 7`: `ceil(7/2) * 2pi/3 = 4 * 2pi/3 = 8 pi / 3 ~= 8.378 > 2 pi`. OK.
For `n = 8`: `4 * 2pi/3 = 8pi/3 > 2pi`. OK.
For `n = 9`: `5 * 2pi/3 = 10pi/3 ~= 10.47 > 2pi`. OK.
For `n = 10`: `5 * 2pi/3 = 10pi/3 > 2pi`. OK.
For `n = 11`: `6 * 2pi/3 = 4pi > 2pi`. OK.

In general for `n >= 7`, `ceil(n/2) * 2pi/3 >= n pi / 3 > 2 pi`. Verified.

Trust label: `RIGOROUS` conditional on (a) equilateral side lengths and
(b) every length-3 diagonal having at least one apex on the short side.

## 2. Why the n=8 saturation closure does not transfer to n=9

At `n = 8`, the inequality `6n <= n(n-2)` is equality, forcing:
- every per-vertex profile is `(4,1,1,1)`;
- every side has exactly one apex;
- every diagonal has exactly two apices, one on each side.

The last point forces every length-2 diagonal `{v_i, v_{i+2}}` to have an
apex on its short side, namely `v_{i+1}` (the only candidate). That gives
`|v_i v_{i+1}| = |v_{i+1} v_{i+2}|` for every `i`, hence equilateral.
Saturation also forces every length-3 diagonal to have an apex on its short
side. Both conditional hypotheses of section 1 are then granted, and the
contradiction closes `n = 8`.

At `n = 9`, the slack ledger is

```text
n(n-2) - 6n = 9.
```

Concretely, write `E = sum_v s_v` where `s_v = sum_k C(m_k, 2) - 6` is the
profile excess at vertex `v`, and let `D` be the total capacity deficit
across all sides and diagonals. Then `E + D = 9` with `E, D >= 0`.

So we cannot conclude either "equilateral" or "all length-3 diagonals have
short-side apex" without further work. Trust label: `RIGOROUS`. This is the
exact gap.

## 3. Refined side-length control at n=9

I tried three angles of attack and record the outcomes.

(a) `Anti-concentration`. If we could show every vertex has profile in
`{(4,1,1,1,1), (4,2,1,1)}`, the per-vertex excess sum is at most `9` only
if at most nine vertices have `(4,2,1,1)` (with some having
`(4,1,1,1,1)`). But the script `explore_n9_base_apex.py` (assumption
`anti_concentration_0_1`) already shows that even after enforcing this
restriction, 7 of the 10 unlabeled excess distributions remain unresolved
by the turn-cover diagnostic. So pure anti-concentration is insufficient.

(b) `Capacity placement`. Try to show that capacity deficit `D` cannot
preferentially fall on length-2 / length-3 diagonals. The motif tables in
`docs/n9-base-apex-frontier.md` enumerate the minimum escape motifs:
under the strict-positivity threshold, three relevant deficits placed on
length-2 / length-3 diagonals always escape. Under the conservative
threshold, two suffice. There is no obvious geometric rule that forbids
placement of three (resp. two) capacity deficits on these short diagonals,
so capacity placement alone does not close n=9.

(c) `Structured saturation`. Using `guaranteed_full_length2_bases_when_D_is_X`
from the script:

```text
D = 0  -> 9 length-2 diagonals fully saturated  (forces equilateral)
D = 4  -> 5 length-2 diagonals fully saturated
D = 9  -> 0 length-2 diagonals fully saturated (worst case)
```

So if `D <= 0` then all 9 length-2 diagonals are saturated, hence
equilateral. But `D = 0` forces `E = 9` and is just one of many cases.

Trust label: `RIGOROUS`. None of these refinements close n=9.

## 4. Saturated case at n=10, 11, 12

At `n = k` the slack is `k(k-2) - 6k = k(k-5)`. At `n = 10` the slack is
`50`, at `n = 11` it is `66`, at `n = 12` it is `84`. The saturation
argument that worked at n=8 was special to the equality case `6n = n(n-2)`,
i.e., `n = 8`. For `n >= 9`, no saturation argument is applicable; the
equilateral conclusion must be reached via different geometric means or not
at all in this framework.

So the answer to "try saturated case at n=10, 11, 12" is: the saturated
case is empty for those `n` because the bounds are not equal there. The
prompt's framing was misleading on this point. Trust label: `RIGOROUS`.

## 5. The key remaining question and the honest answer

The user asked: does the bad-n-gon structure FORCE equilateral side lengths?

The honest answer is: **no, not via the base-apex count alone, for any n > 8**.
The base-apex count produces the equilateral conclusion only when both
inequalities are forced to equality, and this only happens at n=8.

To extend the geometric proof to n=9, one needs a genuinely new ingredient.
Candidate next steps that are NOT done here:
- a sharp anti-concentration lemma forcing profile in `{(4,1,1,1,1)}` only;
- a structural lemma showing that capacity deficits cannot fall on
  short diagonals without producing some other geometric obstruction;
- a non-equilateral length-3 turn-cover analogue;
- a separate path independent of the equilateral reduction.

## Verification of the prompt's claimed equilateral-contradiction argument

The bullet "vertex cover of n-cycle has size `ceil(n/2)` ... `n*pi/3 > 2pi` iff `n > 6`"
is correct. For `n = 9`, the contradiction is `5 * 2pi/3 = 10pi/3 > 2pi`,
which is rigorous. The argument generalizes to all `n >= 7`. **But** the
hypothesis "the polygon is equilateral" is not freely available at any
`n >= 9`. So this argument does not close `n >= 9` without an additional
"equilateral is forced" lemma, which I was unable to establish.

## Conclusion

- The equilateral n-gon contradiction is correct for every `n >= 7`
  (rigorous conditional argument).
- At `n = 8`, equilateral is forced by saturation, so the conditional
  argument closes the case. This matches `docs/n8-geometric-proof.md`.
- At `n >= 9`, equilateral is not forced by any argument I produced, and
  the existing repository scripts confirm that pure anti-concentration is
  insufficient. The base-apex route therefore does not close `n = 9` here.
- No claim of an n=9 closure is made. The repo's official status that
  `n >= 9` is open is preserved.

Trust labels used: `RIGOROUS` for completed steps; no `PROOF` claims.
