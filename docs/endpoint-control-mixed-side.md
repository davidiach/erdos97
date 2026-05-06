# Endpoint Control — mixed-side sub-claim, attempted proof

**Status**: partial — symmetric mixed-side case is closed by an elementary
forced-coincidence argument; the asymmetric mixed-side case is **not
closed**. A purely local argument is provably insufficient because the
2+2 mixed configuration is geometrically realisable as a strict-convex
polygon when only two vertices have $M = 4$. The closure of the
mixed-side claim therefore must use the global $m \ge 4$ hypothesis
(every vertex has $M \ge 4$).

This document is a follow-up to
`data/runs/2026-05-05/endpoint_control_analysis.md` and
`docs/canonical-synthesis.md` §5.1. Numerical verification is in
`scripts/test_endpoint_control_mixed.py`.

## 1. Setup recap

Strictly convex $n$-gon $P$, vertex set $V$, witness sets
$W_i = S_i(r_i)$ where $r_i$ attains $M(i)$. Take the standard Lemma-12
setup: $m = \min_i M(i) \ge 4$, fix $(i^\star, r^\star)$ with
$|S_{i^\star}(r^\star)| = m$. Set $A = \{a_1, \dots, a_m\}$ in joint
angular / boundary order around $v_{i^\star}$; $j^- = a_1$, $j^+ = a_m$.
The polygon boundary, traversed once, gives the cyclic sequence

$$v_{i^\star},\, L_1, \dots, L_s,\, j^-,\, a_2, \dots, a_{m-1},\,
j^+,\, R_1, \dots, R_t,\, v_{i^\star},$$

so $V \setminus A \setminus \{i^\star\} = L \sqcup R$, $|L| + |R| = n - m - 1$.

The proven fragment of Lemma 12 (using L1, L3, L7) gives

$$|S_{j^-}(\rho) \cap (A \cup \{i^\star\})| \le 2 \quad \forall\, \rho > 0.$$

The auxiliary **Endpoint Control claim** asserts that, for at least one
$j \in \{j^-, j^+\}$ and every $\rho > 0$,

$$|S_j(\rho) \setminus (A \cup \{i^\star\})| \le m - 3.$$

At $m = 4$ this says $|S_{j^-}(\rho) \setminus (A \cup \{i^\star\})| \le 1$
for one endpoint, which combines with $\le 2$ inside to give $M(j) \le 3 < 4 = m$,
contradicting $m = \min M$.

## 2. The mixed-side sub-claim

The case-split (§4.2 of `endpoint_control_analysis.md`) gives three
sub-claims at $m = 4$ for the 2-outside case at $j^-$:
**(a)** both outside witnesses in $L$, **(b)** one in $L$ and one in $R$,
**(c)** both in $R$.

Two natural strengths of the mixed-side sub-claim coexist in the literature:

> **Mixed-side sub-claim, weak (1+1).** No $\rho > 0$ admits
> $|S_{j^-}(\rho) \cap L| \ge 1$ *and* $|S_{j^-}(\rho) \cap R| \ge 1$
> simultaneously.
>
> **Mixed-side sub-claim, strong (2+2).** No $\rho > 0$ admits
> $|S_{j^-}(\rho) \cap L| \ge 2$ *and* $|S_{j^-}(\rho) \cap R| \ge 2$
> simultaneously.

The original Endpoint Control claim at $m = 4$ requires the **weak**
form: $|S_{j^-}(\rho) \setminus (A \cup \{i^\star\})| \le 1$ rules out
2 outside witnesses, including the 1+1 mixed configuration (case (b)).
The **strong** 2+2 form is logically weaker (it forbids a more specific
config) but still useful as a stepping stone: if it can be closed, it
narrows the remaining open configurations.

In the strong 2+2 form, $|S_{j^-}(\rho)| \ge 4$ is achieved entirely
outside $A \cup \{i^\star\}$ — four "outside" witnesses on a common
circle around $v_{j^-}$, with two in each chain.

## 3. Local obstruction — the attempt

Write $u_1, u_2 \in L$ and $u_3, u_4 \in R$, all at distance $\rho$
from $v_{j^-}$. We use the angular order at $v_{j^-}$
($a_2, a_3, j^+, R_1, \dots, R_t, i^\star, L_1, \dots, L_s$). After
filtering for the four outside witnesses,

$$\phi(u_3) < \phi(u_4) < \phi(i^\star) < \phi(u_1) < \phi(u_2),$$

with $u_3, u_4 \in R$, $u_1, u_2 \in L$. By L8, all four are in an open
semicircle at $v_{j^-}$. By L1,
$\phi(u_2) - \phi(u_3) < \pi - 0$.

### 3.1 L4 + L6 perpendicular-bisector pencil

All six pair-bisectors $\ell_{ab}$ ($1 \le a < b \le 4$) of the four
$u_k$ pass through $v_{j^-}$. By L4, each contains $\le 1$ other polygon
vertex. The angular directions of these six lines at $v_{j^-}$ are the
six pair-midpoint angles $(\phi(u_a) + \phi(u_b))/2$.

Crucially, $v_{i^\star}$ does *not* lie on any pair-bisector $\ell_{ab}$:
if it did, then $u_a, u_b \in W_{i^\star} = A$, contradicting
$u_k \notin A$. Hence:

> **Observation A.** None of the six pair-bisectors $\ell_{ab}$ contains
> $v_{i^\star}$.

This rules out one obvious "second polygon vertex" candidate per line.

### 3.2 Forced parallelism (L4 + L6)

By L4, each $\ell_{ab}$ contains at most one other vertex; call it
$x_{ab}$ if it exists. By L6, if such $x_{ab}$ exists then
$v_{j^-} x_{ab} \perp u_a u_b$.

If two disjoint pair-bisectors $\ell_{12}$ and $\ell_{34}$ share a
common second vertex $x$ (i.e. $x_{12} = x_{34} = x$), then $x$ lies on
both lines — but two distinct lines through $v_{j^-}$ meet only at
$v_{j^-}$, so $x = v_{j^-}$, contradiction. Hence $x_{12} \ne x_{34}$ if
both exist. But the **direction** of $v_{j^-} x_{12}$ is perpendicular
to $u_1 u_2$, and of $v_{j^-} x_{34}$ to $u_3 u_4$. These are different
directions unless $u_1 u_2 \parallel u_3 u_4$.

> **Observation B.** If $u_1 u_2 \parallel u_3 u_4$ then $\ell_{12} = \ell_{34}$
> and both bisectors share the same second-vertex slot; otherwise the
> two lines are distinct.

We did **not** find a forced parallel here.

### 3.3 Symmetric reduction (clean lemma)

If $P$ is invariant under the reflection through the line $v_{i^\star}$
$\to$ midpoint($j^-, j^+$) (so $L$ mirrors $R$, $j^-$ mirrors $j^+$,
etc.), then the strong 2+2 mixed configuration at $v_{j^-}$ is
**impossible**.

*Proof.* Place coordinates with the symmetry axis as the $y$-axis,
$v_{i^\star}$ on the axis, and $v_{j^-} = (-x_0, y_0)$ with $x_0 > 0$.
For $u_L \in L$ at distance $\rho$ from $v_{j^-}$, write
$u_L = (-x_0 + \rho \cos\alpha, y_0 + \rho \sin\alpha)$. Its mirror image
$u_R = (x_0 - \rho\cos\alpha, y_0 + \rho\sin\alpha) \in R$. Demand
$|v_{j^-} - u_R| = \rho$:

$$(-x_0 - (x_0 - \rho\cos\alpha))^2 + (\rho\sin\alpha)^2 = \rho^2$$
$$\Leftrightarrow\; 4x_0^2 - 4x_0\rho\cos\alpha + \rho^2 = \rho^2$$
$$\Leftrightarrow\; x_0 (x_0 - \rho\cos\alpha) = 0.$$

Since $x_0 > 0$ this forces $\cos\alpha = x_0/\rho$, hence
$u_L = (0, y_0 + \rho\sin\alpha) = u_R$ on the $y$-axis. So a *single*
mirror pair $(u_L, u_R)$ collapses to one $y$-axis point, not two. Two
*distinct* mirror-symmetric pairs would have to give two distinct
$\rho$'s — but they all share the same $\rho$ in the 2+2 setup,
contradiction. $\square$

This closes the symmetric mixed-side case, but the **asymmetric** case
remains open.

### 3.4 Where the closure fails

Without a symmetry assumption, the 2+2 mixed configuration is
realizable at the local level: an explicit numerical search
(`scripts/test_endpoint_control_mixed.py`, $n = 10, 12$) finds many
strict-convex polygons with $M(i^\star) = M(j^-) = 4$ and the strong
2+2 mixed pattern at $v_{j^-}$. **However, in every such example, some
*other* vertex has $M \le 1$**, so $m = \min M < 4$ and the polygon is
not a $\#97$ counterexample.

This is the crux: the mixed-side sub-claim is *not a local statement*
about the configuration $(v_{i^\star}, A, v_{j^-}, u_1, \dots, u_4)$
alone. It must use the global $m \ge 4$ hypothesis — equivalently, the
hypothesis that **every** other polygon vertex also has $\ge 4$
cocircular witnesses.

The natural way to invoke the global hypothesis is to track witnesses
at the $u_k$'s and the chain vertices in $L \setminus \{u_1, u_2\}$,
$R \setminus \{u_3, u_4\}$, and propagate via L4 + L5 + L6. This is
exactly the "boundary-chain intersection" reformulation suggested in
`endpoint_control_analysis.md` §10. We have not found a closure.

## 4. Numerical verification

The script `scripts/test_endpoint_control_mixed.py`:
- Constructs random strictly-convex $n$-gons with $M(v_{i^\star}) \ge 4$
  by direct placement of an A-cluster on a circle around $v_{i^\star}$
  plus surrounding $L, R$ chains in convex position.
- Forces the 2+2 mixed configuration at $v_{j^-}$ by sliding two $L$-
  vertices and two $R$-vertices to a common distance $\rho$ from $v_{j^-}$
  along their existing radial rays.
- Records strict-convexity and the global $m = \min_i M(i)$.

Sample output ($n = 10$, 1000 trials, $\varepsilon = 10^{-6}$):

| metric | count |
|---|---|
| polygons constructed | 1000 |
| $M(i^\star) \ge 4$ | 1000 |
| strong-mixed (≥1 in $L$ and $R$) | 442 |
| strong 2+2 (≥2 in $L$ and $R$) | 363 |
| strong-mixed and strict-convex | 442 |
| strong-mixed and $M(j^-) \ge 4$ | 363 |
| strong-mixed and **global** $m \ge 4$ | **0** |

For $n = 12$: 132/984 strong 2+2 cases produced; **none** at global
$m \ge 4$.

So the empirical claim under attack ($m \ge 4 \Rightarrow$ no strong
2+2 mixed at $j^-$) is supported by numerical evidence in the random
search; we have *not* found a counterexample to it. But neither have we
proved it. The mechanism that prevents global $m \ge 4$ in the mixed
case is the same mechanism that may eventually rule out all $m = 4$
configurations entirely (= Erdős #97), so it is not surprising the
present writeup cannot close it within L1–L10 alone.

## 5. Honest summary of attempt

* **Symmetric mixed-side closed.** The 2+2 mixed configuration at
  $v_{j^-}$ in any reflection-symmetric polygon (axis through
  $v_{i^\star}$ and midpoint of $j^- j^+$) is impossible — the
  reflection-equality forces the two mirror-paired witnesses to coincide
  on the axis. This is an elementary calculation; no L4/L6 needed.
  (§3.3.)
* **Asymmetric mixed-side open.** The 2+2 mixed configuration is
  realisable as a strict-convex polygon with two of $n$ vertices having
  $M \ge 4$ (numerical existence, §4). Therefore no purely local
  L1–L10 contradiction can close it.
* **Global hypothesis required.** Closing the asymmetric mixed-side case
  must use the global $m \ge 4$ hypothesis, equivalently, witness data
  at the $u_k$'s, the remaining $L, R$ vertices, and the inner $A$
  vertices. The natural attack is to track $W_{u_k} \cap W_{u_\ell}$
  via L5 and the L6 perpendicularity to set up an over-determined
  linear system in vertex positions. This was proposed in
  `endpoint_control_analysis.md` §10 (boundary-chain intersection
  reformulation) and remains open.
* **No counterexample found.** Numerical search up to $n = 12$ produced
  no global-$m \ge 4$ polygon with the strong 2+2 mixed-side
  configuration. This is consistent with both (a) the claim being
  true (provably hard to close) and (b) the search being too narrow.

## 6. Concrete next steps

1. **Replace strong 2+2 with the weaker "$\ge 2$ outside total" version**
   of the sub-claim — the user's framing is sharper than the original
   $|S_{j^-}(\rho) \setminus (A \cup \{i^\star\})| \le 1$ requires. The
   minimum violating configuration is *one* outside witness in $L$ and
   *one* in $R$, not 2+2. A 1+1 mixed obstruction would suffice for the
   reduction.

   With the 1+1 framing, an attempted proof:
   - Pair $\{u, u'\}$ with $u \in L$, $u' \in R$, $|j^- - u| = |j^- - u'| = \rho$.
   - Bisector of $\{u, u'\}$ is the angle bisector of $\angle u\, j^-\, u'$,
     a line through $j^-$ pointing into the polygon.
   - L4: at most one *other* polygon vertex on this bisector. By L6,
     that vertex (if exists) is the unique $v$ with $u, u' \in W_v$.
   - But $u \in L, u' \in R$ are in different boundary chains, and their
     bisector at $j^-$ has angular direction $\approx \phi(i^\star)$ —
     the angle bisector at $j^-$ of $\angle u\, j^-\, u'$ passes through
     $v_{i^\star}$'s angular direction *approximately*.
   - It does **not** pass through $v_{i^\star}$ exactly (Observation A).
   - The closure I cannot reach: derive a *forced* coincidence of
     $v_{i^\star}$ with the bisector via the additional global $m \ge 4$
     hypothesis at the $a_k$'s.

2. **Sharpen via tie-breaking.** Choose $(i^\star, r^\star)$ with the
   secondary minimisation criterion $\arg\min_{(i, r)} |L| + |R|$ — i.e.
   minimize the total outside-$A$ size. This was suggested in
   `endpoint_control_analysis.md` §10.3. The hope: this rules out
   configurations where $L \cup R$ is "large enough" to host four
   cocircular outside witnesses of $v_{j^-}$, by forcing $L \cup R$ to be
   small. Open.

3. **Direct enumeration.** For $n = 9, 10, 11$, enumerate all incidence
   patterns with the 2+2 mixed-side at $j^-$ and global $m \ge 4$, and
   check geometric realisability. This is a large but finite search;
   the existing $n = 8$ pipeline (`docs/n8-incidence-enumeration.md`)
   provides the framework. Open as a computational task.

## 7. Files

* This document: `docs/endpoint-control-mixed-side.md`.
* Numerical probe: `scripts/test_endpoint_control_mixed.py`.
* Prior analysis: `data/runs/2026-05-05/endpoint_control_analysis.md`.
* Synthesis section: `docs/canonical-synthesis.md` §5.1.

This document does **not** claim a proof of the Erdős #97 endpoint-control
auxiliary claim, nor a proof of #97. The symmetric sub-case (§3.3) is a
genuine but very narrow result; the asymmetric case is open with a clear
identification of the obstruction.
