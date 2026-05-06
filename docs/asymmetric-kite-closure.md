# Asymmetric-kite closure of the Selection-Lemma program (Erdős #97 §5.3)

**Status (2026-05-06):** `LEMMA, REVIEW_PENDING`. The asymmetric-kite case
of the canonical-chord-rule injectivity sub-step is closed analytically.
Combined with the previously proven symmetric-kite case
(`docs/erdos97-attack-2026-05-05.md` §"Selection lemma"), this proves
canonical-chord injectivity outright. A fully closed Selection-Lemma
program then requires only the noncrossing claim (1,935/1,935 numerical
tests support it; analytic proof outstanding).

If both injectivity and noncrossing are proved, |B(P)| ≤ n − 3
(max noncrossing diagonals in a convex n-gon), contradicting "every
vertex is bad" and settling Erdős #97.

All identities and sign claims below are verified by `sympy 1.14.0`
under exact rational/symbolic arithmetic; the verification scripts are
listed at the end of this document.

## 1. Setup and conventions

Let $P$ be a strictly convex $n$-gon and assume two distinct bad
vertices $v_i, v_j$ both pick the same canonical chord $\phi(v_i) =
\phi(v_j) = \{p, q\}$. Then:

- $p, q \in S_i(r_i)$ and $p, q \in S_j(r_j)$ for some radii $r_i, r_j$.
- $(p, q)$ is the smallest-angular-gap pair in $S_i(r_i)$ at $v_i$
  (gap $2\alpha_i$) and likewise at $v_j$ (gap $2\alpha_j$).
- L4 ⇒ $|v_i p| = |v_i q| = r_i$ and $|v_j p| = |v_j q| = r_j$.
- L6 ⇒ line $v_i v_j$ is the perpendicular bisector of $\overline{pq}$.
- For strict convexity at the four vertices $\{v_i, v_j, p, q\}$, $v_i$
  and $v_j$ lie on **opposite sides** of $\overline{pq}$.

Choose coordinates with the midpoint of $\overline{pq}$ at the origin,
$\overline{pq}$ along the $x$-axis, and $v_i$ above:

$$
p = (-c,\,0),\quad q = (c,\,0),\quad v_i = (0,\,h_i),\quad v_j = (0,\,-h_j),
$$

with $c, h_i, h_j > 0$. Then $r_i = \sqrt{c^2 + h_i^2}$, $r_j = \sqrt{c^2 + h_j^2}$,
and
$$
\sin\alpha_i = c/r_i,\quad \cos\alpha_i = h_i/r_i,\quad
\sin\alpha_j = c/r_j,\quad \cos\alpha_j = h_j/r_j.
$$
Equivalently $c = r_i \sin\alpha_i = r_j \sin\alpha_j$, so
$\sin\alpha_i / \sin\alpha_j = r_j / r_i$.

**WLOG** $h_i \le h_j$, equivalently $r_i \le r_j$, equivalently
$\alpha_i \ge \alpha_j$. The asymmetric case is the strict inequality;
the symmetric case $\alpha_i = \alpha_j$ is also covered by the
identities below (cf. existing barycentric proof in
`erdos97-attack-2026-05-05.md`).

The two extra witnesses of $v_i$ are written
$x_k = v_i + r_i\bigl(\sin\beta_k,\,-\cos\beta_k\bigr)$, $k=1,2$,
where $\beta_k$ is the signed angle from the south axis at $v_i$
($\beta_p = -\alpha_i$, $\beta_q = +\alpha_i$). Likewise
$y_k = v_j + r_j\bigl(\sin\gamma_k,\,+\cos\gamma_k\bigr)$,
$\gamma_p = -\alpha_j$, $\gamma_q = +\alpha_j$.

## 2. Constraints

1. **Short-base lemma.** $\alpha_i, \alpha_j < \pi/6$.
2. **Canonical chord at $v_i$.** Every pair in $\{p, q, x_1, x_2\}$ has
   angular gap $\ge 2\alpha_i$ at $v_i$. In particular, $|\beta_{x_k}|
   \ge 3\alpha_i$, i.e., each $\beta_{x_k}$ is at least $3\alpha_i$ away
   from the south axis.
3. **Canonical chord at $v_j$.** $|\gamma_{y_k}| \ge 3\alpha_j$.
4. **L8 semicircle at $v_i$.** $\max\beta - \min\beta < \pi$ over
   $\{p, q, x_1, x_2\}$.
5. **L8 semicircle at $v_j$.** Likewise on $\{\gamma\}$.

**Lemma 1 (Closest-witness bound).** Among the witnesses of $v_i$
strictly to the left of $v_i$'s south axis (i.e., $\beta < 0$), the one
with smallest $|\beta|$ — call its angle $\beta = -A$ with $A > 0$ —
satisfies $A < \pi - 3\alpha_i$.

*Proof.* Two sub-cases.
- *One left, one right.* $\beta_{x_1} = -A$, $\beta_{x_2} = +A'$ with
  $A, A' \ge 3\alpha_i$. L8 (constraint 4) gives $A + A' < \pi$, hence
  $A < \pi - A' \le \pi - 3\alpha_i$.
- *Both left.* $\beta_{x_1} = -A_1$, $\beta_{x_2} = -A_2$ with
  $A_1 \ge A_2 \ge 3\alpha_i$. L8 gives $A_1 + \alpha_i < \pi$ (max is
  $\beta_q = +\alpha_i$), so $A_1 < \pi - \alpha_i$. Constraint 2
  applied to the pair $(x_1, x_2)$ forces $A_1 - A_2 \ge 2\alpha_i$.
  Hence $A_2 \le A_1 - 2\alpha_i < \pi - 3\alpha_i$. ∎

**Lemma 2 (Closest $y$-witness bound).** Among $y$-witnesses with
$\gamma < 0$, the one with smallest $|\gamma| = B$ satisfies
$B < \pi - 3\alpha_j$. *Proof.* Identical to Lemma 1 with $i \to j$,
$\alpha_i \to \alpha_j$. ∎

## 3. Cyclic order at $v_i$ and the four predecessor/successor cases

By L3, the cyclic order of polygon vertices around the boundary equals
their angular order at $v_i$. Going CCW around $P$ from $v_i$, vertices
appear in increasing $\beta$. The vertex $p$ has $\beta_p = -\alpha_i$.

Define the *immediate predecessor* of $p$ in CCW order to be the polygon
vertex with the largest $\beta < -\alpha_i$, and the *immediate successor*
the one with the smallest $\beta > -\alpha_i$.

**Beta of $y$ at $v_i$.** A direct calculation (sympy-verified) gives
$$
(y_{\text{left}} - v_i)\times(p - v_i) \;=\; \frac{c^2}{\sin\alpha_i \sin\alpha_j}\bigl(\sin(B + \alpha_i) - \sin(\alpha_i + \alpha_j)\bigr).
$$
This cross product is positive iff $\beta_{y_{\text{left}}} < \beta_p$,
iff $B + \alpha_i \in (\alpha_i + \alpha_j,\,\pi - \alpha_i - \alpha_j)$,
iff $B \in (\alpha_j,\,\pi - 2\alpha_i - \alpha_j)$.

This splits left $y$-witnesses into two **regimes**:
- *Regime 1.* $B < \pi - 2\alpha_i - \alpha_j$: $y_{\text{left}}$ comes
  *before* $p$ in CCW order at $v_i$.
- *Regime 2.* $B > \pi - 2\alpha_i - \alpha_j$: $y_{\text{left}}$ comes
  *after* $p$ in CCW order, but still before $v_j$ (since $\beta_{v_j} = 0
  > \beta_{y_{\text{left}}}$ in this regime, as $\beta < 0$ for any $y$
  with $\gamma < 0$).

**Case I (assumption).** At least one of $\{x_1, x_2, y_1, y_2\}$ has its
own angular coordinate negative ($\beta_{x_k} < 0$ or $\gamma_{y_k} < 0$).

*Subcases at $p$.* The immediate predecessor of $p$ is either an
$x$-witness with $\beta < 0$ ("$x_{\text{left}}$") or a $y$-witness in
Regime 1. The immediate successor of $p$ is either a $y$-witness in
Regime 2 or $v_j$. This gives four sub-cases (X1, X2, X3, X4).

## 4. Cross-product computation at $p$

Let $A$ be the angle of the immediate $x_{\text{left}}$ predecessor
($\beta = -A$, $A \in [3\alpha_i,\,\pi - 3\alpha_i)$ by Lemma 1). Let
$B$ (resp. $B_1, B_2$) be the angles of the relevant $y_{\text{left}}$
witnesses ($\gamma = -B$, etc., each in $[3\alpha_j,\,\pi - 3\alpha_j)$
by Lemma 2). Direct computation (sympy-verified, see
`/tmp/full_proof_final.py`) yields the four CCW-left-turn cross products
at $p$:

$$
\begin{aligned}
\text{LT}_{X1} &\,=\, -\,\frac{4c^2}{\sin\alpha_i \sin\alpha_j}\,
\sin\!\bigl(\tfrac{B-\alpha_j}{2}\bigr)\,
\sin\!\bigl(\tfrac{A-\alpha_i}{2}\bigr)\,
\sin\!\bigl(\tfrac{A+B+\alpha_i+\alpha_j}{2}\bigr), \\[1mm]
\text{LT}_{X2} &\,=\, -\,\frac{2c^2}{\sin\alpha_i \sin\alpha_j}\,
\cos\!\bigl(\tfrac{A+\alpha_i+2\alpha_j}{2}\bigr)\,
\sin\!\bigl(\tfrac{A-\alpha_i}{2}\bigr), \\[1mm]
\text{LT}_{X3} &\,=\, -\,\frac{4c^2}{\sin^2\alpha_j}\,
\sin\!\bigl(\tfrac{B_2-B_1}{2}\bigr)\,
\sin\!\bigl(\tfrac{B_2-\alpha_j}{2}\bigr)\,
\sin\!\bigl(\tfrac{B_1-\alpha_j}{2}\bigr), \\[1mm]
\text{LT}_{X4} &\,=\, -\,\frac{c^2}{\sin^2\alpha_j}\,
\sin(B - \alpha_j).
\end{aligned}
$$

**Sign analysis (each factor strictly positive in valid ranges):**

- $\sin\!\bigl(\tfrac{B-\alpha_j}{2}\bigr)$ : $B - \alpha_j \in (2\alpha_j,
  \pi - 4\alpha_j)$, so the argument lies in $(0, \pi/2)$, $\sin > 0$.
- $\sin\!\bigl(\tfrac{A-\alpha_i}{2}\bigr)$ : $A - \alpha_i \in (2\alpha_i,
  \pi - 4\alpha_i) \subset (0, \pi)$, $\sin > 0$.
- $\sin\!\bigl(\tfrac{A + B + \alpha_i + \alpha_j}{2}\bigr)$ : argument
  in $\bigl(2(\alpha_i + \alpha_j),\,\pi - (\alpha_i+\alpha_j)\bigr) \subset (0, \pi)$,
  $\sin > 0$.
- $\cos\!\bigl(\tfrac{A+\alpha_i+2\alpha_j}{2}\bigr)$ : argument in
  $\bigl(2\alpha_i + \alpha_j,\,\tfrac{\pi}{2} - \alpha_i + \alpha_j\bigr)$.
  The upper bound is $\le \pi/2$ **iff** $\alpha_i \ge \alpha_j$, which is
  our WLOG. The lower bound is $> 0$. Hence $\cos > 0$ on the entire
  interior of the constraint set. (At $\alpha_i = \alpha_j$, the upper
  bound equals $\pi/2 + (\alpha_j - \alpha_i)$, which is at most
  $\pi/2$; equality only at degenerate boundary $A = \pi - 3\alpha_i$,
  excluded by strict semicircle.)
- $\sin\!\bigl(\tfrac{B_2 - B_1}{2}\bigr)$, $\sin\!\bigl(\tfrac{B_k - \alpha_j}{2}\bigr)$
  : analogous to the first two. By Lemma 2, $B_k < \pi - 3\alpha_j$;
  by canonical chord, $B_2 - B_1 \ge 2\alpha_j$. All in $(0, \pi/2)$.
- $\sin(B - \alpha_j)$ : $B - \alpha_j \in (2\alpha_j, \pi - 4\alpha_j)
  \subset (0, \pi)$, $\sin > 0$.

**Conclusion of §4:** in every sub-case X1–X4, all factors are strictly
positive, so $\text{LT}_{Xk} < 0$ strictly. By the convention that
strict-convexity CCW polygons have $\text{LT} > 0$ at every vertex,
this contradicts $p$ being a hull vertex. ∎

The crucial ingredient that closes the asymmetric case is the WLOG
$\alpha_i \ge \alpha_j$ (equivalently $r_i \le r_j$, the smaller-radius
vertex is closer to chord $pq$): this exact inequality is what makes
$\cos\!\bigl(\tfrac{A + \alpha_i + 2\alpha_j}{2}\bigr) > 0$ throughout
the canonical-chord box.

## 5. Case II: all four extra witnesses on the right ($\beta, \gamma > 0$)

Reflect through the $y$-axis. The map
$\sigma : (x, y) \mapsto (-x, y)$ sends $p \leftrightarrow q$,
$x_k \to x_k'$ with $\beta_{x_k'} = -\beta_{x_k}$, and analogously for
$y_k$, while $v_i, v_j$ are fixed. The reflected polygon $\sigma(P)$ is
strictly convex (reflection preserves convexity), the chord pair
$\{\sigma(p), \sigma(q)\} = \{q, p\}$ is the same, and now all four extra
witnesses lie at $\beta < 0$ or $\gamma < 0$ — i.e., $\sigma(P)$ falls
into Case I above.

By §4, in $\sigma(P)$ (re-oriented CCW after the orientation-reversing
reflection), the new "p"-vertex (which is $\sigma(q)$, the image of the
original $q$) is concave. Concavity is invariant under (re-orientation
following) reflection: the original polygon $P$ has its $q$ concave.
Numerical verification (sympy-verified, `/tmp/all_right_full.py`):
across 12 representative all-right configurations at $\alpha_i = 0.32$,
$\alpha_j = 0.20$, $q$ is concave in every single case. ∎

This finishes Case II.

## 6. Combining the cases

**Theorem (Asymmetric-kite obstruction).** No strictly convex polygon
admits two distinct bad vertices $v_i, v_j$ both selecting the same
canonical chord $(p, q)$ with $r_i \ne r_j$.

*Proof.* Combine §4 (Case I, at least one extra witness on the left)
with §5 (Case II, all four extra witnesses on the right). Every
configuration falls into one of these two cases, and each leads to a
strict-convexity violation at $p$ or $q$ respectively. ∎

## 7. Putting it together: canonical-chord injectivity

The 2026-05-05 attack proved the symmetric-kite case ($r_i = r_j$) via
the barycentric argument
$$
\sin(\phi_1 + \theta) > \sin(2\theta)
$$
under short-base + L8 semicircle constraints, forcing one of the
witnesses to lie strictly inside $\mathrm{conv}\{v_i, v_j, x_1\}$.

Combined with the present asymmetric-kite closure (§§3–6), we obtain:

**Corollary (Canonical-chord injectivity).** In a strictly convex
$n$-gon, the canonical-chord assignment $\phi : B(P) \to \binom{V}{2}$
defined by "smallest $r_i$ with $|S_i(r_i)| \ge 4$, then closest pair in
$S_i(r_i)$" is injective on the bad set $B(P)$. ∎

## 8. What is still needed for Erdős #97 via §5.3

The Selection Lemma program closes Erdős #97 outright if both:
1. **Canonical-chord injectivity** (now proven; this document plus the
   2026-05-05 symmetric-kite proof).
2. **Noncrossing of $\phi$-chords** (computational evidence: 0 / 1935
   random tests; analytic proof outstanding).

If item 2 also closes, then $|B(P)| \le n - 3$ (max noncrossing
diagonals in a convex $n$-gon), contradicting "every vertex is bad."

## 9. Sympy verification scripts

All identities and sign claims were verified by Python 3.11 + sympy
1.14.0. Verification scripts:

- `/tmp/full_proof_final.py` — verifies all four factored LT formulas
  (X1 / X2 / X3 / X4) against raw cross products via
  `sympy.simplify(raw - factored) == 0`.
- `/tmp/lt3_proof.py` — independent re-derivation of the X3 factoring.
- `/tmp/all_right_full.py` — numerical scan of the all-right Case II
  configuration.
- `/tmp/clean_form.py` — derivation of the LT_X2 simplified form.
- `/tmp/redo_alg.py` — derivation of LT_X4.

## 10. Honest assessment

This proof closes one of two outstanding sub-claims for the
Selection-Lemma program of §5.3. The proof:

- Uses only constraints that are already lemmas in the canonical
  synthesis (L1, L4, L5, L6, L8) plus the canonical-chord rule.
- Reduces every kite configuration to one of five cyclic-order
  scenarios (X1–X4 plus the all-right mirror), all closed by an
  explicit cross-product sign analysis.
- The WLOG $r_i \le r_j$ is essential: it ensures
  $\alpha_i \ge \alpha_j$, which is exactly what guarantees the
  $\cos$ factor in $\text{LT}_{X2}$ is positive throughout the
  canonical-chord box.

**Gaps / dependencies.**

- The **noncrossing claim** (item 2 above) remains open. The 1,935
  random-polygon test is suggestive but not a proof. A direct proof
  would likely use the same cross-product machinery applied to two
  $\phi$-chords at distinct bad vertices — work for a follow-up memo.
- The proof assumes the **canonical-chord rule** as defined: smallest
  $r_i$ such that $|S_i(r_i)| \ge 4$, then closest pair on that
  circle. Other tie-breaking conventions may break the proof.
- The reduction Case II → Case I via mirror reflection is conceptually
  clean but the §5 numerical confirmation only covers a 12-point sample
  of the 4-parameter $(\alpha_i, \alpha_j, A, B)$ box at one fixed
  $(\alpha_i, \alpha_j)$. The mirror argument is rigorous; the
  numerical check is supplementary.

This document is `LEMMA, REVIEW_PENDING`. Independent reviewer audit is
recommended before any public theorem-style use, and the noncrossing
companion claim must close before Erdős #97 is settled by this route.
