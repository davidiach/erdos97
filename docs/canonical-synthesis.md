# Erdős Problem #97 — Canonical Synthesis

*Single canonical reconciliation. Merges `erdos97_final_consolidated.md` (deep / wide structure) with `erdos97_four_stage_consolidation.md` (external-citation audit + claim taxonomy). Supersedes both.*

*Last revised: 2026-04-27. Full source files retained as detail backstops.*

**Update note:** the repo now contains checked `n=8` incidence-completeness
and exact-obstruction artifacts. This long synthesis is retained as provenance
for earlier gaps and failed arguments; use `STATE.md`, `RESULTS.md`,
`docs/n8-incidence-enumeration.md`, and `docs/n8-exact-survivors.md` for the
current finite-case status.

**Round-two note:** a later handoff adds an exact Kalmanson/Farkas certificate
killing one fixed `C19_skew` cyclic order. This does not change the global/open
status and does not kill abstract `C19_skew` over all cyclic orders. Use
`docs/round2/round2_merged_report.md` for that fixed-order artifact.

## What is new in this canonical version

Relative to `erdos97_final_consolidated.md`:

1. **Corrected the uniform-radius reduction (§5.5).** The prior synthesis claimed the uniform-radius subcase of #97 was "folklore-resolved by Füredi's $2n-7$ bound for all $n \ge 7$." This was a direction-of-bound error: $2n-7$ is an Edelsbrunner--Hajnal lower-bound *construction*, not an upper bound. Füredi's separate convex-`n`-gon unit-distance work belongs to the upper-bound side. The needed $< 2n$ upper bound is the open Erdős–Fishburn conjecture. The uniform-radius subcase is therefore **open**, conditional on Erdős–Fishburn. The correction propagates to §1.5, §10, the TL;DR table, and Appendix A.
2. **Added external citation anchors** as footnotes to all background literature claims (Aggarwal 2010, Edelsbrunner–Hajnal 1991, Fishburn–Reeds 1992, Nivasch et al. 2013, the erdosproblems.com #97 entry, the DeepMind `formal-conjectures` Lean file). Background numbers no longer rely on archive-internal cross-talk.
3. **Added a claim taxonomy** (Appendix C) tagging top-level claims as `VERIFIED`, `CONDITIONAL`, `EVIDENCE`, `REJECTED`, or `PROVENANCE-WARNING`.
4. **Added SHA-256 source inventory** (Appendix D) from the four-stage consolidation, for reproducibility.

Relative to `erdos97_four_stage_consolidation.md`:

5. **Adopted the long file's L1–L10 lemma numbering.** The four-stage file used L1–L9 with a different mapping (its L3 = first file's L5). The long file's numbering matches more of the source notes, so cross-references stay clean.
6. **Preserved verbatim coordinates** for the §7 counterexamples and the §8 search artifacts, which the four-stage file abbreviated.

---

## TL;DR

**Problem (Erdős #97).** For a strictly convex polygon with vertex set $V \subset \mathbb{R}^2$, define $E(i) = \max_{r > 0} \#\{j \ne i : \|p_i - p_j\| = r\}$. Does every strictly convex polygon have some vertex with $E(i) \le 3$?

**Official/global status: FALSIFIABLE/OPEN.** Listed open on
erdosproblems.com/97 (last edited 2025-10-27); \$100 prize.

**Local repo status:** no general proof and no counterexample are claimed.
The strongest local result is the selected-witness finite-case obstruction
through `n <= 8`, in the repo-local machine-checked sense.

| `n` | Current repo-local status | Method |
|---|---|---|
| `5, 6, 7` | Proved locally; no selected-witness counterexample. | Incidence counting and `n=7` Fano/parity obstruction. |
| `8` | Ruled out in repo-local, machine-checked finite-case sense; external review recommended. | Incidence-completeness enumeration to 15 canonical classes plus exact survivor obstruction. |
| `>= 9` | Open. | No general proof or counterexample claimed. |

**Background.** The $k=3$ analogue is **false**: Danzer (1963) constructed a convex 9-gon with $E(i) = 3$ everywhere; Fishburn–Reeds (1992) did the same with a uniform radius. So $k = 4$ is the boundary case Erdős conjectured.

**Five active proof programs, each with one well-localized open gap:**

| Program | Gap | Status |
|---|---|---|
| Lemma 12 / endpoint descent | Endpoint-Control Auxiliary Claim (§5.1) | Reduction proved; descent step open. |
| Ear-elimination + rigidity | Bridge Lemma A′ / Key Peeling Lemma (§5.2) | Rank theorem proved (mod L7-gauge repair); combinatorial bridge open. |
| Selection lemma / noncrossing diagonals | Canonical-chord injectivity (§5.3) | Reduction proved; injectivity conjectural. |
| Smallest enclosing circle / 3-cap | Three-cap bridge lemma (§5.4) | Diameter case proved (Moser cap lemma); three-cap case open. |
| Distance-bound reduction | Both subcases open (§5.5) | Uniform-radius case requires Erdős–Fishburn ($< 2n$), still open. Variable-radius case is the actual content of #97 for $n \ge 8$. |

**Single highest-leverage open task:** **Bridge Lemma A′** — if every realizable counterexample admits an ear-orderable witness selection, #97 falls to the rigidity argument that's already proved (mod the gauge-fixing repair).

**Single highest-leverage *concrete* next task:** independently audit the `n=8` incidence-completeness checker and exact obstruction certificates, then push the finite pipeline toward `n = 9`.

---

## Reading order

- **5 minutes:** TL;DR, §1 (problem), §2 (lemma library, table only), §3 (small cases at a glance), §5 (table), §9 (priorities).
- **30 minutes:** Add §4 (n=8 detail), §5 (program details), §6 (failed routes), §7 (counterexamples).
- **Working session:** Add §8 (computational state) and §10 (reconciliation log).

---

## §1. Problem statement, equivalences, background

### §1.1 Definition

Let $P$ be a strictly convex polygon in $\mathbb{R}^2$ with vertex set $V = \{v_1, \dots, v_n\}$ in cyclic order, $n \ge 5$. For each vertex $v_i$ and radius $r > 0$:

$$S_i(r) := \{v_j \in V \setminus \{v_i\} : \|v_i - v_j\| = r\}, \qquad M(i) := \max_{r > 0} |S_i(r)|.$$

Sometimes also written $E(v_i) := M(i)$.

**Erdős #97.** Does every strictly convex polygon have at least one vertex $v_i$ with $M(i) \le 3$?

**4-bad polygon (= $k=4$ counterexample).** A strictly convex polygon with $M(i) \ge 4$ for every $i$. A single explicit example would refute #97; none has been found.

### §1.2 The witness-set convention (critical)

For each vertex $v_i$ in a hypothetical counterexample, choose a fixed 4-element subset

$$W_i \subseteq S_i(r_i) \quad\text{with}\quad |W_i| = 4,$$

i.e. four other vertices on a single circle centered at $v_i$. The choice is non-canonical when $|S_i(r_i)| > 4$; rigorous proofs explicitly track which selection is used.

**Two definitions of "witness" appear in the source archive:**

- **Strong (cocircular):** four other vertices on a single circle around $v_i$. **This is the right definition for #97.**
- **Weak:** four other vertices each appearing in some pair of vertices equidistant from $v_i$, not necessarily concyclic.

Several superseded notes used the weak definition and reached invalid conclusions (notably for $n = 7$). **All proofs in this document use the strong definition.**

### §1.3 Equivalent reformulations (all PROVED-equivalent)

A counterexample is equivalent to each of:

1. **Circle-incidence form.** $n$ circles $C_i$ centered at the $v_i$, each containing $\ge 4$ other polygon vertices.
2. **Pinned-distance multiset form.** The multiset $\{\|v_i - v_j\|^2 : j \ne i\}$ has a value of multiplicity $\ge 4$ at every $i$.
3. **Circumcenter form.** Every $v_i$ is the circumcenter of some 4-subset of $V \setminus \{v_i\}$.
4. **Paraboloid lift form.** Lift each $p_i = (x_i, y_i)$ to $\hat{p}_i = (x_i, y_i, x_i^2 + y_i^2)$. Then $v_i$ has 4 equidistant other vertices iff the four lifts are coplanar in a plane *parallel to the tangent plane* of the paraboloid $z = x^2 + y^2$ at $\hat{v}_i$. Three lifted points always determine a plane; four require a genuine coplanarity condition. **This is why $k = 4$ is qualitatively harder than $k = 3$.**

### §1.4 Heuristic constraint count

A 4-bad $n$-gon imposes $3n$ scalar equality constraints on $2n$ coordinates. After modding out translation + rotation + scale (4 dimensions), the system is overdetermined by $3n - (2n - 4) = n + 4$. **Heuristic only:** the constraint variety can be nonempty even when expected dimension is negative, and convexity is semialgebraic, not algebraic.

### §1.5 Background and literature anchors

- Numbering: erdosproblems.com/97, last edited 2025-10-27.[^erdos97-page]
- Formalized in DeepMind's `formal-conjectures` repository as `ErdosProblems/97.lean`, marked `@[category research open, AMS 52]`, encoding `HasNEquidistantProperty 4`.[^formal97]
- $k = 3$ analogue is FALSE: Danzer (1963) — convex 9-gon with $M(i) = 3$ everywhere (variable radii); Fishburn–Reeds (1992) — convex 20-gon with $M(i) = 3$ at one global radius.[^fishburn-reeds]
- Erdős's 1975 statement asks whether every convex $n$-gon, $n \ge n_0$, has a vertex with at most $k$ others at any single distance, *for every $k$*. The boundary now known is $k = 4$: this is #97. (The "every $k$" framing is recorded on erdosproblems.com[^erdos97-page] as likely mistaken — Erdős did not repeat it later. `PROVENANCE-WARNING`.)
- Distinct-distance bounds from a vertex of a convex polygon: Nivasch–Pach–Pinchasi–Zerbib (2013) give $\ge (13/36 + \varepsilon)n - O(1)$.[^nivasch]
- **Unit-distance bounds in convex position.** *Upper:* $n \log_2 n + O(n)$ (Aggarwal 2010, improving Füredi's earlier $2\pi n \log_2 n + O(n)$).[^aggarwal] *Lower:* there exist convex $n$-gons achieving $\ge 2n - 7$ unit distances (Edelsbrunner--Hajnal 1991).[^edels-hajnal] **Direction-of-bound note:** $2n-7$ is a lower-bound *construction*; it does **not** upper-bound the unit distances in a convex polygon. The Erdős–Fishburn conjecture posits an upper bound of $< 2n$; it is open. (See §5.5 for why this matters to #97.)

---

## §2. The proven lemma library (L1–L10)

These are used everywhere downstream and are not in dispute.

| ID | Statement | Why |
|---|---|---|
| **L1** | Cone containment. All other vertices of $P$ lie in the closed cone spanned by the two incident edges at $v_i$; only adjacent vertices lie on the boundary rays, all non-adjacent vertices lie in the open cone, and the angular span of $W_i$ around $v_i$ is $< \pi$. | Strict convexity + vertex on hull. |
| **L2** | No three polygon vertices are collinear. | Strict convexity. |
| **L3** | Boundary cyclic order matches angular order at any vertex. | L1 + L2. |
| **L4** | Perpendicular-bisector vertex bound. For any unordered pair $\{a, b\}$, at most 2 polygon vertices $v$ satisfy $\|v - a\| = \|v - b\|$. | The locus is one line; intersects a strictly convex polygon in at most 2 points. |
| **L5** | **Two-circle bound.** $\|W_i \cap W_j\| \le 2$ for $i \ne j$. | Two distinct circles intersect in at most 2 points. |
| **L6** | **Perpendicularity lemma.** If $W_i \cap W_j = \{a, b\}$, then $v_iv_j \perp ab$. | Both $v_i, v_j$ lie on the perpendicular bisector of $ab$. |
| **L7** | **Chord formula.** For $a, b$ on a circle of radius $r$ around $c$, $\|a - b\| = 2r \sin(\angle acb / 2)$. Hence on $W_i$, chord length is monotone in angular gap on $(0, \pi)$. | Elementary; needs L1's $< \pi$ span. |
| **L8** | **Semicircle criterion.** $W_i$ is contained in some open semicircle of the circle through it centered at $v_i$. Equivalently, a center $O$ of a circle lies in $\mathrm{int}(\mathrm{conv}(S))$ for $S$ on the circle iff $S$ is *not* contained in any closed semicircle. (Earlier drafts asserted the *negation* — that the center $v_i$ must lie inside $\mathrm{conv}(W_i)$. That is false; see §6.1.) | $v_i$ is an extreme point ⇒ all other vertices lie in one open half-plane through $v_i$. |
| **L9** | **Cyclic polygon subcase.** If all $n$ vertices lie on one circle, then $M(v) \le 2$ for every $v$. | A second circle around $v$ intersects the circumcircle in at most 2 points. |
| **L10** | **Euler/scaling identity.** With constraints $f_{i;u,v} = \|p_i - p_u\|^2 - \|p_i - p_v\|^2$, the system is degree-2 homogeneous, so $R_W(p) \cdot p = 2 F_W(p)$. At any solution $F_W(p) = 0$, the scaling vector $p$ is in $\ker R_W(p)$. Combined with the 3-dim translation/rotation kernel, $\mathrm{rank}\, R_W(p) \le 2n - 4$ at any nondegenerate solution. | Direct differentiation. |

**Triple-sharing corollary (sometimes called L6′).** If three distinct vertices $a, b, c$ lie in $W_i$, then $v_i$ is the unique circumcenter of $\triangle abc$. So $\{a, b, c\} \subset W_i \cap W_j \Rightarrow i = j$.

**Kite corollary (L5 + L6).** If $W_i \cap W_j = \{a, b\}$, the four points $\{v_i, v_j, a, b\}$ form a kite: diagonals $v_i v_j$ and $ab$ perpendicular, with $\|v_i - a\| = \|v_i - b\|$ and $\|v_j - a\| = \|v_j - b\|$.

**Bipartite consequence of L5 (sometimes useful).** If $V = A \sqcup B$ and every vertex of $A$ takes its witness 4-set inside $B$:
- $|B| = 5$: any two 4-subsets of a 5-set share $\ge 3$ points → at most one vertex of $A$ valid.
- $|B| = 6$: 4-subsets are complements of 2-subsets; pairwise intersection $\le 2$ ⇔ complementary pairs disjoint ⇒ at most 3 vertices of $A$ valid.

So simple two-cluster constructions are killed at the combinatorial level. Any candidate must spread witnesses across more than two regions.

---

## §3. Small cases ($n = 5, 6, 7$): proved

### §3.1 $n = 5$ (clean)

Every $W_i = V \setminus \{v_i\}$. For $i \ne j$, $W_i \cap W_j = V \setminus \{v_i, v_j\}$ has size 3, contradicting L5. ∎

(Alternative: by symmetry, all $r_i$ equal, so all 10 distances equal — a regular simplex on 5 points in $\mathbb{R}^2$, which doesn't exist.)

### §3.2 $n = 6$ (clean)

Each $W_i$ omits exactly one other vertex; write $W_i = V \setminus \{v_i, f(i)\}$ for some $f(i) \ne i$. Then

$$W_i \cap W_{f(i)} \supseteq V \setminus \{v_i, v_{f(i)}, v_{f(f(i))}\},$$

a set of size $\ge 3$, contradicting L5. ∎

### §3.3 $n = 7$ (parity / perpendicularity)

Two independent proofs both work; the parity proof is canonical.

**Setup.** $\sum_a d_a = 28$ where $d_a = \#\{i : a \in W_i\}$, and double-counting gives

$$\sum_{i<j} |W_i \cap W_j| = \sum_a \binom{d_a}{2}.$$

**Step 1 — saturation.** From L5, $\sum_{i<j} |W_i \cap W_j| \le 2 \binom{7}{2} = 42$. By Jensen (convexity of $\binom{x}{2}$), $\sum_a \binom{d_a}{2} \ge 7 \binom{4}{2} = 42$, with equality iff every $d_a = 4$. So both bounds are tight: **every $d_a = 4$, every $|W_i \cap W_j| = 2$.**

**Step 2 — pair-multiplicity.** Let $\lambda_{ab} = \#\{i : \{a, b\} \subset W_i\}$. Then $\sum \lambda_{ab} = 7 \binom{4}{2} = 42$, and $\sum \binom{\lambda_{ab}}{2} = \binom{7}{2} = 21$ (the count of pairwise intersections $|W_i \cap W_j|$, all forced to 2 by Step 1, gives $\binom{7}{2} \cdot \binom{2}{2} = 21$). With 21 pairs averaging $\lambda = 2$ and Jensen tightness, every $\lambda_{ab} = 2$.

**Step 3 — bijection.** Define $\phi(\{i, j\}) := W_i \cap W_j$. Step 2 tightness implies $\phi$ is a permutation of the 21 unordered pairs of $V$.

**Step 4 — perpendicularity.** By L6, $\{i, j\} \perp \phi(\{i, j\})$ for every pair.

**Step 5 — parity contradiction.** Along any cycle $\ell_1 \mapsto \ell_2 \mapsto \cdots \mapsto \ell_m \mapsto \ell_1$ of $\phi$, perpendicularity alternates direction by 90°. An odd cycle forces $\ell_1 \perp \ell_1$. So all cycles must be even. But 21 is odd — no permutation of 21 objects has all-even cycles. ∎

**Alternative proof (mutual-witness $K_4$).** Universality argument forces the mutual-witness graph $G_d = K_7$, which by edge count + pigeonhole contains a 4-clique of mutually equidistant vertices in $\mathbb{R}^2$, impossible (no 4 mutually equidistant points exist in the plane; Cayley–Menger determinant on 4 points with all squared distances equal is $4r^6 \ne 0$).

**Both proofs require the strong cocircular witness definition.** The "weak-definition" version of $n = 7$ in some legacy files is *not* a proof and should be discarded.

### §3.4 The forced-double-regularity is special to $n = 7$

The Step 1 conclusion "every $d_a = 4$" is a Jensen-saturation phenomenon: $7 \binom{4}{2} = 42 = 2 \binom{7}{2}$. For $n = 8$ the analogous count is $\sum \lambda_{ab} = 48$ over $\binom{8}{2} = 28$ pairs, average $\approx 1.71$, no tightness. **Forced double regularity is unavailable outside $n = 7$.**

---

## §4. Archived pre-`n=8` state with partial obstructions

This section records the pre-`n=8` snapshot retained for provenance. It is
superseded by the current finite-case artifacts in `RESULTS.md`,
`docs/n8-incidence-enumeration.md`, and `docs/n8-exact-survivors.md`.

Three legacy source files (`erdos_97_complete_notes.md`, `erdos_97_analysis.md`, `erdos_97_summary.md`) claim $n = 8$ is settled. The careful review files catch specific gaps in each. In this archived snapshot, the resolution was to keep $n = 8$ open.

### §4.1 The orthocenter obstruction (real but partial)

If the witness pattern at $n = 8$ is the cube graph $Q_3$ (vertices $= \{0,1\}^3$, $W_v = \{w : d_H(v, w) \in \{2, 3\}\}$), then via L6 the four points $\{p_{000}, p_{011}, p_{101}, p_{110}\}$ satisfy three perpendicularity constraints that are exactly the conditions for $p_{000}$ to be the orthocenter of $\triangle p_{011} p_{101} p_{110}$. In any orthocentric system of 4 points, at least one lies inside the triangle of the other three — contradicting strict convexity. **This proof is correct.**

**What it does NOT prove.** That the cube is the *only* possible $n = 8$ witness pattern. The "uniqueness of triangle-free cubic graph on 8 vertices" claim used in `erdos_97_complete_notes.md` is asserted, not proved; and the underlying double-regularity it requires (every $d_a = 4$) is **not forced at $n = 8$** the way it is at $n = 7$ (§3.4).

### §4.2 The unit-distance-bound argument has the same gap

`erdos_97_analysis.md` argues $u_c(8) = 14 < 16$ to refute $n = 8$. This assumes the mutual-witness graph is connected, which forces all radii equal. That hypothesis is unjustified at $n = 8$; the bidirectional pigeonhole that gave it for free at $n \le 7$ ($\ge 4n - \binom{n}{2}$ guaranteed bidirectional edges) breaks at $n = 8$ (only 4 guaranteed bidirectional edges).

### §4.3 The "$n \le 12$ proven by counting" claim is wrong

`erdos_97_summary.md` claims $n \ge 13$ from $12n \le n(n-1)$. The correct L4-counting bound is $12n \le 2 \cdot n(n-1)$, giving $n \ge 7$. **Use $n \ge 7$, not $n \ge 13$.** (One unordered triple $(i, \{p, q\})$ is at most $2 \binom{n}{2}$ apex assignments by L4, and each $W_i$ contributes $\binom{4}{2} = 6$ such triples; $6n \le n(n-1)$ ⇒ $n \ge 7$.)

### §4.4 Generic Jacobian rank is evidence, not proof

Empirically, at random convex polygons with random witness selections, the Jacobian $R_W$ has rank $2n - 3$ for $k = 4$ and variable rank for $k = 3$. This is a numerical pattern consistent with #97 being true. It is *not* a proof: a counterexample, if any, would by L10 have rank $\le 2n - 4$ at the solution — exactly the rank-deficient locus the random sample never hits. (Toy analogue: $x^2 = 0$ has Jacobian $2x$, rank 1 a.e., yet $x = 0$ is a solution.)

### §4.5 Jacobian rank value at solutions: $\le 2n - 4$, not $2n - 3$

Sources disagree on whether the obstruction is "rank $= 2n-3$" or "rank $\le 2n-4$." The correct statement is: **at a solution, rank $\le 2n - 4$** (translations + rotation + scaling = 4-dim kernel, by L10). The ear-rank theorem (§5.2) proves rank $= 2n - 3$ at *generic* (non-solution) points; combining the two gives the contradiction.

### §4.6 Resolution

At the time of this archived snapshot, $n = 8$ was treated as **open**. The
cube *witness pattern* was provably unrealizable, but that was only a useful
conditional obstruction, not a complete proof.

---

## §5. Active proof programs

Each program has one well-localized open gap. They are not mutually exclusive — settling any one closes #97.

### §5.1 Lemma 12 / endpoint descent

**Setup.** Let $m := \min_i M(i)$, choose $(i^\star, r^\star)$ with $|S_{i^\star}(r^\star)| = m \ge 4$. Set $A := S_{i^\star}(r^\star)$, with angular endpoints $v_-, v_+$ at $v_{i^\star}$ and indices $j^-, j^+$.

**What's proved (using L1, L3, L7):**

1. $A$ is linearly angular-ordered around $v_{i^\star}$, span $< \pi$.
2. Boundary-order endpoints match angular endpoints (L3).
3. **Endpoint chord-length monotonicity:** for $a_1 = v_-$, the distances $\|v_- - a_t\|$ for $t = 2, \dots, m$ are $2r^\star \sin\!\bigl((\phi(a_t) - \phi(a_1))/2\bigr)$, strictly increasing on $(0, \pi)$. (L7 + span $< \pi$.) This is the §3.3-style replacement for the original "bisector ⇒ collinearity" line.
4. Therefore at most 1 vertex of $A \setminus \{v_-\}$ on any circle around $v_-$, plus $v_{i^\star}$ at distance $r^\star$. So $|S_{j^-}(\rho) \cap (A \cup \{i^\star\})| \le 2$ for every $\rho > 0$.

**Reduction.** $M(j^-) \le m - 1$ would follow if $|S_{j^-}(\rho) \setminus (A \cup \{i^\star\})| \le m - 3$ for every $\rho > 0$.

**Auxiliary Endpoint Control Claim (open, the gap):**

> At least one endpoint $j \in \{j^-, j^+\}$ satisfies, for every $\rho > 0$,
> $$|S_j(\rho) \setminus (A \cup \{i^\star\})| \le m - 3.$$

This is a global "outside-of-$A$" control statement. Three sub-questions:

1. Why "at least one" rather than both? Is there a known configuration where one endpoint fails but the other succeeds? The asymmetry hints the proof can't treat $j^-, j^+$ symmetrically.
2. Is $m$ implicitly bounded relative to $n$? The claim is non-vacuous only for $m < (n + 2)/2$. Lemma 11's setup may force this, but it isn't stated.
3. The two boundary chains from $j^-$ to $j^+$ partition $V \setminus A \setminus \{i^\star\}$; the proof likely needs to exploit that partition.

**Suggested attack directions.** Direct attack on the endpoint claim via violation of convexity / collinearity / new descent vertex; reformulation as a boundary-chain intersection bound; counterexample search; tie-breakers in the choice of $(i^\star, r^\star)$.

### §5.2 Ear-elimination + Bridge Lemma A′ (the central bottleneck)

**Ear-orderable witness pattern.** A vertex ordering $(v_1, \dots, v_n)$ such that for every $k \ge 4$, $|W_{v_k} \cap \{v_1, \dots, v_{k-1}\}| \ge 3$.

**Theorem (proved, conditional on the L7-based gauge-fixing repair to the original argument's rigid-motion-matching step; see §6.5).** If $W$ is ear-orderable and $p$ is in general position, then $\mathrm{rank}\, R_W(p) = 2n - 3$.

**Theorem (proved, L10).** At any solution $F_W(p) = 0$, Euler homogeneity gives $p \in \ker R_W$, so $\mathrm{rank}\, R_W(p) \le 2n - 4$.

**Combined:** an ear-orderable witness selection at a solution is a contradiction.

**Bridge Lemma A′ (open, the central bottleneck):**

> Every realizable strictly-convex $k=4$ counterexample admits some ear-orderable witness selection.

**Equivalent: Key Peeling Lemma.**

> For every $S \subseteq V$ with $|S| \ge 4$, there exists $v \in S$ with $|E_v \cap (S \setminus \{v\})| \ge 3$, where $E_v$ is some 4-set of equidistant neighbors of $v$.

**Why this isn't combinatorial.** A 4-out-regular digraph can admit "stuck sets" $S$ where every $v \in S$ has internal outdegree $\le 2$. The geometry must rule these out. **Computational evidence:** the Bridge Lemma holds at $n = 7$, and the combinatorial $n = 7$ patterns lacking ear orderings have no strictly convex realization (least-squares search; see §8.6). So the bridge is *not* a purely combinatorial consequence of L5/L6; it requires deeper geometric/algebraic constraints.

**Stuck-set status.** For every $v \in S$ stuck, can choose $\{a_v, b_v\} \subset E_v \cap (V \setminus S)$, and each unordered outside pair serves at most 2 stuck centers (L5). This is correct but insufficient. Routes proposed: cross-boundary double counting, cyclic-order obstructions, strengthening L5 for repeated outside pairs.

**Suggested attack tools:** circumcenter closure under L5, perpendicularity systems from L6, cross-boundary double counting on stuck sets, cyclic-order obstructions. **Pure graph theory will not work.**

### §5.3 Selection Lemma / noncrossing diagonals

**Goal.** For each bad vertex $i$, assign a chord $\phi(i) = p_i q_i$ with $p_i, q_i \in S_i(r_i)$, such that the assigned chords are pairwise distinct and pairwise noncrossing. If achievable, $|B(P)| \le n - 3$ (max noncrossing diagonals in a convex $n$-gon), contradicting "all bad."

**Proved (short-base lemma).** For bad vertex $i$ with interior angle $\theta_i$, some pair $p, q \in S_i(r_i)$ has angular gap $\le \theta_i / (m - 1) < \pi / 3$, hence $\|p - q\| < r_i$ (chord formula + $\sin < \sin(\pi/6) = 1/2$). So a "short-base witness chord" always exists.

**Failed greedy choices.**

- *Minimal span:* crossings of two minimum-span chords don't auto-produce smaller valid chords for either center.
- *Minimal apex angle:* two narrow isosceles bases can cross.
- *L4 uniqueness:* at most 2 centers can share a chord, giving $|\{\phi(i)\}| \ge |B|/2$ — way too weak.

**Open: canonical-chord-rule injectivity** (e.g. smallest $r_i$, then smallest angular gap). Conjecturally injective; unproved.

### §5.4 Smallest enclosing circle / 3-cap

**Diameter case (proved).** If the smallest enclosing circle of $V$ is determined by two diametrically opposite vertices $p, q$, the cap lemma (Moser, via Dumitrescu's survey) — distances from a chord endpoint to convex-position points inside the cap are all distinct — gives $E(p), E(q) \le 2$. So at least two vertices have $M \le 3$. ∎

**Three-cap case (open).** If the smallest enclosing circle is supported by three vertices $p, q, r$ forming a non-obtuse triangle, the polygon decomposes into caps $K_{pq}, K_{qr}, K_{rp}$. Cap lemma controls distances from $p$ to $K_{pq}$ and $K_{rp}$ (each $\le 1$ contribution to any equal-distance set at $p$), but **not** $K_{qr}$ (since $p$ is not an endpoint of chord $qr$). So if $p$ is bad, $\ge 2$ of its 4 equidistant vertices lie in $K_{qr}$. By symmetry, same for $q$ in $K_{rp}$, $r$ in $K_{pq}$.

**Three-Cap Bridge Lemma (open):** if $p$ is bad, some pair $\{x, y\}$ at equal distance from $p$ both lies in the same cap, with $xy$ a diagonal inside that cap. Then witness-packing inside caps closes the case.

### §5.5 Distance-bound reduction `CONDITIONAL` (both subcases)

**Erdős–Fishburn conjecture.** A convex $n$-gon has fewer than $2n$ pairs at any single distance.[^fishburn-reeds] **Open.**

**Best known bounds (verified externally; see §1.5 footnotes).**
- *Upper:* $n \log_2 n + O(n)$ (Aggarwal 2010), improving Füredi's earlier $2\pi n \log_2 n + O(n)$.[^aggarwal]
- *Lower:* there exist convex $n$-gons with $\ge 2n - 7$ unit distances (Edelsbrunner--Hajnal 1991).[^edels-hajnal]

**Uniform-radius subcase of #97.** If a 4-bad polygon has all $r_i$ equal to a common $r$, then the distance-$r$ graph has $\ge 2n$ edges (each vertex has 4 neighbors at distance $r$, divide by 2). To rule this out via distance bounds, one would need an *upper* bound of the form "convex $n$-gon has $< 2n$ pairs at any single distance" — which is exactly the Erdős–Fishburn conjecture.

**Correction to prior synthesis (`erdos97_final_consolidated.md` §5.5).** The prior synthesis claimed: "Füredi's $2n-7$ already suffices for $n \ge 7$. The uniform-radius subcase of #97 is folklore-resolved by Füredi's bound for all $n \ge 7$." **This is incorrect.** The $2n-7$ result is a lower-bound *construction* — there exist convex $n$-gons achieving at least $2n-7$ unit distances — not an upper bound. Saying the unit-distance graph has $\ge 2n$ edges is *consistent* with the $\ge 2n-7$ lower-bound construction, not in conflict with it. The known general upper bounds ($O(n \log n)$, Aggarwal's $n \log_2 n + O(n)$) do not beat $2n$.

The same error appears in `erdos97_useful_findings.md` §A.11 and `zip/source_notes/17_uniform_radius_related_case.md`. **Both should be treated as `REJECTED` in their proof-of-uniform-radius capacity, retained only as a partial reduction.**

**Net status of the subcase:** the uniform-radius subcase is **`CONDITIONAL` on Erdős–Fishburn**, not folklore-resolved. Direct subcases ($n = 5, 6$) follow from §3.1, §3.2 without needing distance bounds.

**The radius-equality reduction is also limited.** The bidirectional-pigeonhole argument that forces all $r_i$ equal at $n \le 7$ breaks at $n \ge 8$: only 4 guaranteed bidirectional edges remain. So even if Erdős–Fishburn were proved, only the (small) uniform-radius slice of #97 would close. **The variable-radius case is the actual content of #97 for $n \ge 8$.**

**Net status of the program.** Of the five active programs, distance-bound is the **weakest**: it requires both (i) a proof of Erdős–Fishburn at the $< 2n$ level (open since 1992) and (ii) an extension covering variable radii. It is included for completeness, not because it is presently a near-miss.

---

## §6. The morgue: failed routes

Catalogued so they don't get retried. Each entry: failure mode, explicit counterexample (where one exists), the lesson.

### §6.1 Circumcenter-must-be-inside (corrected by L8)

**False claim.** If $W_i$ are 4 vertices of a strictly convex polygon on a circle around $v_i$, then $v_i$ is inside the convex hull of $W_i$.

**Counterexample.** Pentagon with $v_1 = (0, 0)$ and $W_1 = \{(\cos 10°, \sin 10°), (\cos 30°, \sin 30°), (\cos 50°, \sin 50°), (\cos 70°, \sin 70°)\}$ — all in a 60° arc, $v_1$ exterior to their hull.

**Lesson.** Witnesses from a hull vertex live in a semicircle (L8), often a much smaller arc. **The local circumcenter argument can never produce a contradiction. Erdős #97 must be a global statement.** (Concrete coordinates in §7.1.)

### §6.2 Forest lemma

**False claim.** Direct $v \to w$ when $\|vw\| = r_v$. For each center $v$, label the angular endpoints of $S_v(r_v)$ as *end-neighbors* and the rest as *middle-neighbors*. End-edges contribute $\le 2n$ directed edges. The undirected middle-edge graph $M$ was claimed to be a *forest*, hence $\le n - 1$ undirected edges, $\le 2(n - 1)$ directed. Total $\le 4n - 2 < 4n$, contradicting outdegree $\ge 4$.

**Status: FALSE.** $M$ can have cycles. Two explicit counterexamples in §7.2 and §7.3.

**Salvage ideas.** End-edge bound and outdegree-4 lower bound are still valid. A working proof would need either: (i) a charging/weighting on middle edges instead of forest structure; (ii) a sharper bound on middle-edge cycles; (iii) cap-overlap restrictions other than laminarity.

### §6.3 Naive global quadruple count

**False claim.** $N_{\text{quad}}$ = number of ordered tuples $(i; a, b, c, d)$ all four equidistant from $v_i$ satisfies $N_{\text{quad}} < n$.

**Why false.** Place $v_0$ at origin and $v_1, \dots, v_{n-1}$ on a unit-circle arc of angle $< \pi$ around $v_0$. Polygon stays strictly convex; $v_0$ alone contributes $\binom{n-1}{4} \cdot 4! = \Theta(n^4)$ ordered quadruples.

**Replacement (open subproblem).** Count only **rank-critical centered 4-ties.** For center $i$ and radius $r$, define

$$I_i(r) = \#\{j \ne i : \|v_i - v_j\| < r\}, \qquad B_i(r) = \#\{j \ne i : \|v_i - v_j\| = r\}.$$

A *3-critical 4-tie* at $i$ with radius $r$ satisfies $I_i(r) \le 2$ and $B_i(r) \ge 4$.

**Conjecture A (Bridge):** $M(i) \ge 4 \Rightarrow$ some such $r$ exists at $i$.
**Conjecture B (Counting):** the total number of 3-critical 4-ties is $< n$.

Either alone is non-trivial; together they imply #97. **STATUS: both unproved.**

### §6.4 Forced double regularity asserted-not-proved

**False claim.** "In any 4-bad polygon, every vertex appears in *exactly* 4 witness sets."

**Status.** $\sum_j d_j = 4n$ is forced; $d_j = 4$ for all $j$ is an additional symmetry assumption. The Cauchy–Schwarz argument sometimes given for it (using $\sum d_j^2 = 16n$) is **circular**: it assumes the symmetry it wants to deduce.

The clean $n \le 7$ proofs in §3 do *not* require this. They use only L5 directly. Forced double regularity is what makes the orbit-decomposition program in §4.1 fail to actually settle $n = 8$.

### §6.5 Rigid-motion-matching gap in the ear-elimination proof

**Attempted statement.** "Fix the unique infinitesimal Euclidean motion $\dot p^{\rm rig}$ agreeing with $\dot p$ on three noncollinear vertices $v_1, v_2, v_3$."

**Gap.** Infinitesimal Euclidean motions have only 3 d.o.f. ($t \in \mathbb{R}^2, \omega \in \mathbb{R}$); prescribing velocity on 3 vertices is 6 scalar conditions. Existence of a matching motion is not automatic.

**Two repair routes.**
- *Route A (gauge fixing):* impose only 3 scalar gauge conditions (e.g. $\dot p'_{v_1} = 0$ plus one rotation gauge at $v_2$); matches the 3 d.o.f., repairable but the induction has to be re-checked.
- *Route B (explicit minor):* construct a $(2n - 3) \times (2n - 3)$ minor with nonzero determinant directly using the ear ordering. Cleaner.

**Other technical issues in the same route.** Scaling-direction independence from translations/rotations needs a one-line proof. $W_i$ is a set but the constraint map uses an ordering; an arbitrary ordering must be fixed explicitly. Short proofs of L5/L6/L8 should be inlined.

### §6.6 Diameter endpoint can have 4 equidistant

**False claim.** "An endpoint of a diameter of $V$ cannot have 4 equidistant other vertices."

**Status: FALSE.** Hexagon counterexample in §7.4.

**Lesson.** Any proof of #97 must be global. Single-vertex extremality arguments are insufficient.

### §6.7 Rigidity-rank test misses non-generic solutions

**Attempted statement.** Numerically observe $\mathrm{rank}(R_W(p)) = 2n - 3$ at random convex configurations; conclude no solution.

**Status: NOT A PROOF, only NUMERICAL.** Generic rank does not preclude special non-generic solutions. (Toy: $x^2 = 0$ has Jacobian $2x$, rank 1 a.e., yet $x = 0$ is a solution.)

**What it does establish — rank dichotomy (450+ trials):**
- $k = 4$: rank $= 2n - 3$ in every tested polygon, $n \in \{5, 6, 7, 8, 9, 10, 12, 15, 20\}$.
- $k = 3$: rank is configuration-dependent, sometimes drops to $2n - 4$ ($n \in \{7, 9, 10, 12, 15\}$).

Consistent with #97 being true and Danzer's 9-gon being possible. Computational evidence, not proof.

### §6.8 Distance unimodality off cyclic polygons

**False claim.** "From any vertex of a strictly convex polygon, the distances to the other vertices are unimodal as one walks around the boundary."

**Status: FALSE for non-cyclic convex polygons.** True only for inscribed polygons. Elongated convex polygons have multiple local maxima from non-extremal vertices.

### §6.9 Monge property on squared distances

**False claim.** Squared-distance matrices of convex polygons satisfy a strict Monge inequality.

**Status: FALSE.** Direct check on a regular hexagon refutes it. Kalmanson holds for distances (not squared) and only for specific orderings; the Monge form on squared distances does not generally hold.

### §6.10 Symmetric ansatz collapses

**Attempted route.** For $n = 8$ orthocentric setup, place $p_0, p_3, p_4, p_7$ on the y-axis, $p_5, p_6$ on the x-axis, $p_1, p_2$ symmetric in $y$.

**Status: DEGENERATE.** Constraint $p_0 p_4 \perp p_3 p_7$ forces both vectors vertical ⇒ one must be zero ⇒ vertex coincidence. Symmetric witness systems also collapse onto cyclic case (L9), so the ansatz is too strong.

### §6.11 Lattice propagation

**Unproved claim.** Mutual rhombus-witness configurations (from L5 + L6) propagate globally to force the configuration onto a triangular lattice, then a strictly convex subset of a triangular lattice cannot have all hull vertices with 4 lattice neighbors.

**Status: GAP.** The local rhombus lemma is correct (rhombus with sides $r$, diagonals $r$ and $r\sqrt{3}$, angles 60°/120°). The lattice obstruction at hull vertices is correct. **What was never proved:** the existence of mutual witnesses with shared neighbors, and the propagation step from local rhombi to global lattice structure.

### §6.12 Curvature argument

**Attempted statement.** "Triangular-lattice rigidity is 'flat' (zero Gaussian curvature), incompatible with $2\pi$ total turning of a convex polygon."

**Status: HEURISTIC.** Conflates Gaussian curvature (a smooth-surface concept) with polygon turning. No formal connection to the witness-graph constraints was ever made.

### §6.13 Consecutive-witness-class assumption

**False claim.** Equal-distance vertices from a hull vertex form a consecutive cyclic block.

**Status: FALSE.** Numerical 8-vertex example with non-consecutive witnesses (in source notes). The cyclic order from $v_i$ gives angular monotonicity, but witnesses at the same radius can be interleaved with non-witnesses.


---

## §7. Explicit counterexamples (verbatim coordinates preserved)

These are counterexamples to *intermediate lemmas*, not to Erdős #97. Each one kills a specific proof attempt.

### §7.1 Pentagon with $E(v_1) = 4$, witnesses in a semicircle

**Refutes:** §6.1 (the false circumcenter-inside-quadrilateral lemma).

$$v_1 = (0, 0), \quad v_2 = (\cos 20°, \sin 20°) \approx (0.9397, 0.3420),$$
$$v_3 = (\cos 60°, \sin 60°) = (0.5, 0.8660), \quad v_4 = (\cos 120°, \sin 120°) = (-0.5, 0.8660),$$
$$v_5 = (\cos 160°, \sin 160°) \approx (-0.9397, 0.3420).$$

**Verification.** $\|v_1 - v_j\| = 1$ for $j = 2, 3, 4, 5$. The five points form a strictly convex pentagon in cyclic order $v_1, v_2, v_3, v_4, v_5$. The center $v_1 = (0, 0)$ lies *outside* $\mathrm{conv}\{v_2, v_3, v_4, v_5\}$ (which is in the half-plane $y > 0$).

This is consistent with §3.1 (no 4-bad pentagon exists), because the *other* four vertices don't all have $E = 4$ — only $v_1$ does.

### §7.2 9-point forest-lemma counterexample (equilateral + ε-perturbations)

**Refutes:** §6.2 (forest lemma).

Equilateral triangle $A = (0, 0)$, $B = (1, 0)$, $C = (1/2, \sqrt{3}/2)$. Set $\varepsilon = 10°$.

Around $B$, as seen from $A$:
$$B^- = (\cos\varepsilon, -\sin\varepsilon), \qquad B^+ = (\cos\varepsilon, \sin\varepsilon)$$

Around $C$, as seen from $B$:
$$C^- = B + (\cos(120° - \varepsilon), \sin(120° - \varepsilon))$$
$$C^+ = B + (\cos(120° + \varepsilon), \sin(120° + \varepsilon))$$

Around $A$, as seen from $C$:
$$A^- = C + (\cos(240° - \varepsilon), \sin(240° - \varepsilon))$$
$$A^+ = C + (\cos(240° + \varepsilon), \sin(240° + \varepsilon))$$

Cyclic order (for $\varepsilon = 10°$): $A^-, A, A^+, B^-, B, B^+, C^-, C, C^+$. Set $r_A = r_B = r_C = 1$. Then $A \to B$, $B \to C$, $C \to A$ are each *middle* edges (the apex is bracketed by its two siblings on the equal-distance circle of the source). The undirected middle-edge graph contains the cycle $A - B - C - A$.

### §7.3 24-gon forest-lemma counterexample (affine-stretched regular polygon)

**Refutes:** §6.2.

$$P_j = \left( \sqrt{\lambda} \cos\frac{j\pi}{12},\ \sin\frac{j\pi}{12} \right), \quad j = 0, 1, \dots, 23, \qquad \lambda = \frac{2}{\sqrt{3}} - 1.$$

Equal-distance classes:

| $i$ | Equidistant set |
|----|----|
| 0  | $\{4, 10, 14, 20\}$ |
| 1  | $\{5, 10, 11, 22\}$ |
| 11 | $\{14, 1, 2, 7\}$ |
| 12 | $\{16, 22, 2, 8\}$ |
| 13 | $\{17, 22, 23, 10\}$ |
| 23 | $\{2, 13, 14, 19\}$ |

Common squared distance for vertices $0, 12$: $\frac{1}{2} + \frac{\sqrt{3}}{6}$. Common squared distance for vertices $1, 11, 13, 23$: $\frac{\sqrt{3}}{3}$.

Middle-directed edges include $0 \to 10, 0 \to 14, 1 \to 10, 1 \to 11, 11 \to 1, 11 \to 2, 12 \to 22, 12 \to 2, 13 \to 22, 13 \to 23, 23 \to 13, 23 \to 14$. The undirected graph contains the cycle

$$0 - 10 - 1 - 11 - 2 - 12 - 22 - 13 - 23 - 14 - 0.$$

The cap-monotonicity argument fails because the cap of $0 \to 10$ (bounded by 4 and 14) is **larger**, not smaller, than the cap of $1 \to 10$ (bounded by 5 and 11).

Self-contained verification:

```python
import math

n = 24
lam = 2 / math.sqrt(3) - 1
pts = [
    (math.sqrt(lam) * math.cos(j * math.pi / 12),
     math.sin(j * math.pi / 12))
    for j in range(n)
]

def d2(i, j):
    xi, yi = pts[i]; xj, yj = pts[j]
    return (xi - xj) ** 2 + (yi - yj) ** 2

classes = {
    0:  [4, 10, 14, 20],  1:  [5, 10, 11, 22],  11: [14, 1, 2, 7],
    12: [16, 22, 2, 8],   13: [17, 22, 23, 10], 23: [2, 13, 14, 19],
}
for v, neighs in classes.items():
    vals = [d2(v, w) for w in neighs]
    print(v, neighs, vals, "spread =", max(vals) - min(vals))
```

### §7.4 Hexagon counterexample to diameter-endpoint argument

**Refutes:** §6.6.

$$A = (0, 0), \quad D = (0.7286615964,\ 0.2295545885),$$
$$P_{20} = (\cos 20°, \sin 20°), \quad P_{40} = (\cos 40°, \sin 40°),$$
$$P_{60} = (\cos 60°, \sin 60°), \quad P_{80} = (\cos 80°, \sin 80°).$$

Convex hexagon in cyclic order $A, D, P_{20}, P_{40}, P_{60}, P_{80}$. Then $\|A - P_j\| = 1$ for $j = 20, 40, 60, 80$, so $A$ is a diameter endpoint *and* has 4 equidistant other vertices. The other vertices need not have $E \ge 4$, so this is not a #97 counterexample — it just kills the "diameter endpoint is good" route.

### §7.5 32-point general-position counterexample (Pythagorean unit vectors)

**Refutes:** the *non-convex general-position* variant of #97.

Five rational unit vectors:

$$u_1 = \left(\tfrac{132}{157}, \tfrac{85}{157}\right), \quad u_2 = \left(\tfrac{24}{145}, \tfrac{143}{145}\right), \quad u_3 = \left(\tfrac{8}{17}, \tfrac{15}{17}\right),$$
$$u_4 = \left(\tfrac{72}{97}, \tfrac{65}{97}\right), \quad u_5 = \left(\tfrac{195}{197}, \tfrac{28}{197}\right).$$

(All unit because the coordinates come from Pythagorean triples.) Define

$$P = \left\{ \sum_{i=1}^5 \varepsilon_i u_i : \varepsilon_i \in \{0, 1\} \right\}, \qquad |P| = 32.$$

Each point $p = \sum \varepsilon_i u_i$ has 5 unit-distance neighbors $q_i = p \pm u_i$ (sign depending on $\varepsilon_i$). So every point has $E = 5$ in this set. The set has no three collinear (verifiable in exact arithmetic with Fractions).

```python
from fractions import Fraction
from itertools import combinations

u = [
    (Fraction(132,157), Fraction(85,157)),
    (Fraction(24,145),  Fraction(143,145)),
    (Fraction(8,17),    Fraction(15,17)),
    (Fraction(72,97),   Fraction(65,97)),
    (Fraction(195,197), Fraction(28,197)),
]

P = []
for mask in range(1 << 5):
    x = y = Fraction(0, 1)
    for i, (ux, uy) in enumerate(u):
        if (mask >> i) & 1:
            x += ux; y += uy
    P.append((x, y))

def collinear(a, b, c):
    (ax, ay), (bx, by), (cx, cy) = a, b, c
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) == 0

for a, b, c in combinations(P, 3):
    if collinear(a, b, c):
        print("collinear triple found:", a, b, c); break
else:
    print("no three collinear")
```

**Important.** This set is *not* the vertex set of a strictly convex polygon — it just falsifies the general-position variant. **Erdős #97 specifically needs convex position.**

### §7.6 10-point concave configuration with $M(v) \ge 4$ for every vertex

**Refutes:** dropping the convexity hypothesis.

$$n = 10, \quad \Delta = \pi/5, \quad b = (3 - \sqrt 5)/2 \approx 0.381966.$$
$$v_j = \rho_j (\cos(j\Delta), \sin(j\Delta)), \quad \rho_j = \begin{cases} 1, & j \text{ even}, \\ b, & j \text{ odd}. \end{cases}$$

Approximate coordinates:

$$\begin{aligned}
v_0 &= (1.000000, 0.000000), & v_1 &= (0.309017, 0.224514),\\
v_2 &= (0.309017, 0.951057), & v_3 &= (-0.118034, 0.363271),\\
v_4 &= (-0.809017, 0.587785), & v_5 &= (-0.381966, 0.000000),\\
v_6 &= (-0.809017, -0.587785), & v_7 &= (-0.118034, -0.363271),\\
v_8 &= (0.309017, -0.951057), & v_9 &= (0.309017, -0.224514).
\end{aligned}$$

Equal-distance pattern: even $i$ equidistant to offsets $\{\pm 2, \pm 3\}$; odd $i$ to $\{\pm 1, \pm 4\}$. Every vertex has 4 equidistant others. **The polygon is concave**, because strict convexity for the alternating-radius decagon would require $b > \cos(\pi/5) \approx 0.809$, while $b \approx 0.382$.

**Lesson.** The equidistance system is algebraically feasible at $n = 10$; **convexity is the obstruction**.


---

## §8. Computational state

### §8.1 No counterexample found

Across all retained search artifacts. The closest near-misses are degenerate or settle into $k = 3$ structures.

### §8.2 The $n = 39$ circulant — provably impossible

Pattern $S_i = \{i + 18, i - 18, i + 19, i - 19\} \pmod{39}$. Initially the most promising numerical near-solution; the residual diagnostics looked tantalizing.

#### §8.2.1 Best near-miss coordinates

```python
BEST_COORDS = np.array([
    [ 1.011215382989, -0.085596626543], [ 1.011215382989, -0.085586784482],
    [ 0.933513739397,  0.392530635344], [ 0.933510622731,  0.392539970898],
    [ 0.933506048897,  0.392548685611], [ 0.642512416423,  0.779790881685],
    [ 0.642505318304,  0.779797699521], [ 0.642497218446,  0.779803290449],
    [ 0.204874731437,  0.987457742422], [ 0.204865277958,  0.987460480655],
    [ 0.204855507656,  0.987461666985], [-0.279141796035,  0.967957242417],
    [-0.279151439195,  0.967955273752], [-0.279160641682,  0.967951783709],
    [-0.698654812581,  0.725756711217], [-0.698662436291,  0.725750486651],
    [-0.698668962785,  0.725743119762], [-0.957558941793,  0.316341371684],
    [-0.957562799553,  0.316332317190], [-0.957565154912,  0.316322761121],
    [-0.996542367800, -0.166496655884], [-0.996541575843, -0.166506466031],
    [-0.996539220483, -0.166516022100], [-0.806674457503, -0.612144998198],
    [-0.806669197258, -0.612153316610], [-0.806662670764, -0.612160683499],
    [-0.431451660999, -0.918510990678], [-0.431443137524, -0.918515911709],
    [-0.431433935037, -0.918519401752], [ 0.043167000961, -1.015409876561],
    [ 0.043176835041, -1.015410272861], [ 0.043186605343, -1.015409086531],
    [ 0.508452112700, -0.880643288847], [ 0.508461004514, -0.880639069628],
    [ 0.508469104372, -0.880633478700], [ 0.857812462406, -0.545084628668],
    [ 0.857818374948, -0.545076760503], [ 0.857822948782, -0.545068045790],
    [ 1.011213804211, -0.085606341153],
])
```

Verifier diagnostics:

```text
strict convexity:        passes, but barely
minimum signed cross:    1.55384e-11
minimum pair distance:   9.84206e-06
max equality residual:   9.50388e-06
RMS equality residual:   5.87745e-06
```

Per-vertex maximum residuals alternate between $\approx 1.59 \times 10^{-6}$ and $\approx 9.50 \times 10^{-6}$ in a triple-period pattern — the smoking gun of a $13 \times 3$ collapse.

#### §8.2.2 Definitive impossibility proof

Modulo 39: $-18 \equiv 21$, $-19 \equiv 20$. So $S_i = \{i + 18, i + 19, i + 20, i + 21\} \pmod{39}$, giving

$$S_i \cap S_{i+1} = \{i + 19, i + 20, i + 21\}, \qquad |S_i \cap S_{i+1}| = 3.$$

Three points on two distinct circles (centers $p_i \ne p_{i+1}$) ⇒ contradiction with L5. **STATUS: PROVED IMPOSSIBLE** for any strict 39-gon.

#### §8.2.3 First-order blow-up analysis

Setup: $i = 3g + r$, $g \in \mathbb{Z}/13$, $r \in \{0, 1, 2\}$; collapse $p_{3g+r} \approx q_g$ on a regular 13-gon; perturb $p_{3g+r} = q_g + \varepsilon u_{g, r} + O(\varepsilon^2)$.

Result: same-cluster equations from cluster-source $g = h \pm 6$ force $(q_{h \pm 6} - q_h) \cdot (u_{h, 0} - u_{h, 1}) = 0$, $(q_{h \pm 6} - q_h) \cdot (u_{h, 0} - u_{h, 2}) = 0$. The two chord directions $q_{h-6} - q_h$ and $q_{h+6} - q_h$ are not parallel in a regular 13-gon, so $u_{h, 0} = u_{h, 1} = u_{h, 2}$. Same argument repeats at every order. **No formal blow-up of the collapsed regular 13-gon into a genuine strict 39-gon exists.**

Linearized-system numerical confirmation:

```text
Linearized system A shape: (117, 78)
rank(A): 64
nullity(A): 14
cluster-constant subspace dimension: 26
internal separation subspace dimension: 52
rank(A restricted to internal separation subspace): 52
meaningful internal-separation nullity: 0
strict convexity possible at first order: False
```

### §8.3 Two $n = 12$ cyclic configurations

**§8.3.1 Near-convex candidate.** $n = 12$, $D = \{4, 5, 8, 11\}$. Pattern $S_i = \{i + d \mod 12 : d \in D\}$.

Coordinates:
```
( 0.000000,  0.000000)   ( 1.000000,  0.000000)
( 0.499181,  0.864576)   ( 1.66e-06,  0.000976)
( 0.998335, -0.000962)   ( 0.498335,  0.865063)
(-2.38e-07, -0.000947)   ( 0.997489, -0.001449)
( 0.500001,  0.864102)   ( 9.24e-07, -0.001923)
( 0.999156, -0.000489)   ( 0.500845,  0.863613)
```

Squared radii (per vertex): all $\approx 1$ (range $0.99499$ to $1.00000$).

Metrics:
```
max_abs_dist_residual: 1.27e-06
min_pair_distance:     9.47e-04
strictly_convex:       true (extremely small margin)
multiplicities at tol 1e-8: [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
```

**Status: NUMERICAL near-miss only.** Min pair distance $\sim 10^{-4}$ same order as residual ⇒ optimizer near a degeneracy boundary. Actual multiplicity at sane tolerance is only 2, not 4. Not a counterexample. Useful as warm-start or boundary candidate.

**§8.3.2 Degenerate exact configuration.** $n = 12$, $D = \{2, 3, 4, 10\}$. `max_abs_dist_residual = 3.89e-16` (machine precision) but `min_pair_distance = 1.24e-16` and `hull_size = 5` — vertices coincide. Satisfies the equations exactly only because most vertices coincide. **NOT A COUNTEREXAMPLE.** Cautionary value: shows how exact algebraic solutions can be degenerate.

### §8.4 Fishburn–Reeds / Desargues $k = 3$ branch

The original uploaded 20-gon file was diagnosed as corrupted (clustered vertices, bad metadata). A reconstructed numerical $k = 3$ benchmark with 10+10 bipartite structure and offsets $D = \{0, 1, 3\}$ replaces it. Useful for solver regression testing.

The 3-regular equal-distance graph on this 20-vertex seed is identified with the **Desargues graph**. Attempts to upgrade this to $k = 4$ by adding a perfect matching at one global distance plateaued at relative error $\approx 6.3 \times 10^{-3}$. **Important: that branch is stronger than #97** (it requires a globally common distance). The real next computational branch is per-vertex quartets and per-vertex radii.

### §8.5 Rigidity-rank dichotomy (numerical, 450+ trials)

| $n$ | $k = 4$ rank | $k = 3$ rank |
|---|---|---|
| 5–20 (tested: 5, 6, 7, 8, 9, 10, 12, 15, 20) | $2n - 3$ in every trial | configuration-dependent, sometimes drops to $2n - 4$ |

**STATUS: COMPUTATIONAL EVIDENCE only.** See §6.7. Reusable code:

```python
import numpy as np
from scipy.linalg import svd

def build_equidistance_row(vertices, i, a, b):
    """Row for d(v_i, v_a)^2 = d(v_i, v_b)^2"""
    n = len(vertices)
    row = np.zeros(2 * n)
    vi, va, vb = vertices[i], vertices[a], vertices[b]
    row[2*i]     = 2 * (vb[0] - va[0])
    row[2*i + 1] = 2 * (vb[1] - va[1])
    row[2*a]     = 2 * (va[0] - vi[0])
    row[2*a + 1] = 2 * (va[1] - vi[1])
    row[2*b]     = 2 * (vi[0] - vb[0])
    row[2*b + 1] = 2 * (vi[1] - vb[1])
    return row

def build_rigidity_matrix(vertices, k):
    n = len(vertices)
    distances = np.array([[np.linalg.norm(vertices[i] - vertices[j])
                           if i != j else 0
                           for j in range(n)] for i in range(n)])
    rows = []
    for i in range(n):
        nearest = sorted([(j, distances[i, j]) for j in range(n) if j != i],
                         key=lambda x: x[1])
        witness = [d[0] for d in nearest[:k]]
        a = witness[0]
        for j in range(1, k):
            rows.append(build_equidistance_row(vertices, i, a, witness[j]))
    return np.array(rows)

def compute_rank(M, tol=1e-10):
    if M.size == 0: return 0
    _, s, _ = svd(M)
    return int(np.sum(s > tol))
```

### §8.6 Bridge Lemma at $n = 7$ (computational)

For $n = 7$, $k = 4$: 21 pairs, 42 pair-incidences (forces every pair count $= 2$ — matches §3.3 saturation). 6 cyclic starter sets satisfy L5 ∧ L6 ∧ ¬(ear-orderable):

```
{1,2,3,5}, {1,2,3,6}, {1,3,4,5}, {1,4,5,6}, {2,3,4,6}, {2,4,5,6}
```

Geometric realizability (least-squares on 21 equations in 11 d.o.f.):

| Starter | Best residual |
|---|---|
| {1,2,3,5} | 0.797 |
| {1,2,3,6} | 1.041 |
| {1,3,4,5} | 0.821 |
| {1,4,5,6} | 0.936 |
| {2,3,4,6} | 0.609 |
| {2,4,5,6} | 0.739 |

All residuals far from zero ⇒ **algebraically inconsistent ⇒ not geometrically realizable.** Random search of 500K patterns at $n = 7$: best residual 0.78. **STATUS: COMPUTATIONAL evidence that the Bridge Lemma holds at $n = 7$.** Not a proof.

### §8.7 The $n = 8$ golden-ratio cubic

For the symmetric $n = 8$ case with $E(i) = \{i + 1, i + 2, i + 4\} \pmod 8$, after fixing $v_0 = (0, 0)$, $v_1 = (1, 0)$, propagating constraints reduces to the cubic in squared circumradius $r$ from $v_0$:

$$r^3 - 2r^2 - 2r + 1 = 0 \iff (r + 1)(r^2 - 3r + 1) = 0.$$

Roots: $r = -1$ (invalid), $r = (3 - \sqrt{5})/2 \approx 0.382$ (fails auxiliary $3r - 2 \ge 0$), $r = (3 + \sqrt{5})/2 = \varphi^2 \approx 2.618$.

For $r = \varphi^2$: $v_3 = (1/2, \sqrt{\varphi^2 - 1/4}) \approx (0.5, 1.539)$, $v_6 = (\varphi^2/2, \sqrt{\varphi^2(4 - \varphi^2)/4}) \approx (1.309, 0.951)$, $v_7 = (\varphi^2/2, -0.951)$.

Initial checks pass: $d(v_0, v_3) = d(v_0, v_6) = d(v_0, v_7) = \varphi$, $d(v_1, v_6) = d(v_1, v_7) = 1$, $d(v_6, v_3) = 1$. **Full system fails:** $d(v_3, v_2) = 2.227 \ne d(v_3, v_0) = 1.618$, with multiple cascading violations. **NOT a counterexample.** The $\varphi^2$ value hints at pentagonal/continued-fraction structure.

Of the 35 symmetric cyclic assignments $E(i) = \{i + a, i + b, i + c\} \pmod 8$ tested:
- 4 K₄-forced (immediate contradiction)
- 11 with intersection $> 2$ (violates L5)
- 20 marked CHECK with min error $\approx 0.39$ (all infeasible numerically)

Not a complete $n = 8$ proof — only one of many offset patterns.

### §8.8 Candidate pattern families for new search

Designed to avoid the $n = 39$ collapse mode (two-tiny-antipodal-cluster degeneration and quotient degeneracies).

**Family 1: prime cyclic four-offset.** $n = p$ prime; $T = \{a, b, c, d\} \subset \mathbb{Z}/p$ with large cyclic gaps and $|T \cap (T + s)| \le 2$ for all nonzero shifts. Examples: $p = 41,\ T = \{5, 14, 24, 34\}$; $p = 43,\ T = \{6, 15, 27, 36\}$.

**Family 2: prime cyclic symmetric two-chord.** $S_i = \{i \pm a, i \pm b\}$ with $a, b, p - a, p - b$ well separated. Examples: $p = 41, \{a, b\} = \{7, 16\}$; $p = 43, \{8, 17\}$; $p = 47, \{10, 19\}$.

**Family 3: asymmetric cyclic Sidon-type offset sets.** $S_i = i + T$ with $T$ such that pairwise differences have low multiplicity. Examples: $n = 45, T = \{4, 13, 25, 37\}$; $n = 49, T = \{5, 16, 29, 41\}$.

**Family 4: two-lift over a prime quotient.** $n = 2m$, $m$ prime; $i = 2g + r$, $r \in \{0, 1\}$; quotient offsets $a_0, \dots, a_3 \in \mathbb{Z}/m$. $S_{2g+r} = \{2(g + a_t) + ((r + \delta_t) \bmod 2)\}$ for chosen $\delta_t$. Example: $m = 19, (a_0, a_1, a_2, a_3) = (3, 7, 11, 16)$.

**Family 5: three-lift Latin pattern with four distinct quotient targets** (avoids the $n = 39$ mistake). $n = 3m$, $S_{3g+r} = \{3(g + a_t) + ((r + t) \bmod 3) : t = 0, 1, 2, 3\}$. Example: $m = 17, (a_0, a_1, a_2, a_3) = (2, 5, 9, 13), n = 51$.

**Family 6: four-lift residue-rotating.** $n = 4m$, $S_{4g+r} = \{4(g + a_t) + ((r + t) \bmod 4) : t = 0, 1, 2, 3\}$. Example: $m = 11, n = 44, (a_0, a_1, a_2, a_3) = (2, 4, 7, 9)$.

**Block patterns of immediate interest:**
- `B12_3x4_danzer_lift` ($n = 12$): best near-miss documented; likely degenerate.
- `B20_4x5_FR_lift` ($n = 20$): high-priority continuation target.

### §8.9 Required incidence pre-filter (mandatory)

Run **before** any numerical optimization:

```python
def row_overlap_filter(n, pattern):
    """pattern(i) returns the set S_i. Reject if two rows share >= 3 targets."""
    rows = [set(pattern(i)) for i in range(n)]
    bad = []
    for i in range(n):
        for j in range(i + 1, n):
            inter = rows[i].intersection(rows[j])
            if len(inter) >= 3:
                bad.append((i, j, sorted(inter)))
    return bad
```

Any nonempty result is an immediate L5 obstruction. The $n = 39$ pattern fails this maximally.

**Additional combinatorial filters:**
- **Adjacency strengthening:** if pairs $(i, j)$ are forced to be adjacent in the polygon, $|S_i \cap S_j| \le 1$ for those pairs.
- **Triple uniqueness (L6′):** any single triple $\{u, v, w\}$ appears in at most one $S_i$.

### §8.10 Algebraic feasibility via linearization

Before launching a nondegenerate numerical search, run a first-order blow-up around a candidate symmetric configuration. If the linearized system has no meaningful internal-separation nullspace (all null directions are global rigid motions or cluster-preserving), the pattern is degenerate-only. The $n = 39$ case in §8.2.3 is the worked diagnostic template.

### §8.11 Nondegenerate constrained search recipe

Use a scale-invariant objective. Impose:
- diameter normalized to 1
- minimum pair distance $\ge \delta$
- minimum edge length $\ge \delta$
- minimum signed convexity cross-product $\ge c\delta^2$
- no cluster of 3 vertices within radius $\delta$

Scan $\delta \in \{10^{-1}, 5 \cdot 10^{-2}, 10^{-2}, 5 \cdot 10^{-3}, 10^{-3}\}$. For each $\delta$, report residuals **relative to scale**: max residual / diameter², residual / min edge length, residual / min pair distance, residual / min convexity cross-product.

This distinguishes genuine improvement from collapse-driven decay. **Do not reward small absolute residual alone.** A candidate with residual $\approx 10^{-6}$ but degeneracy $\approx 10^{-5}$ is *worse* than one with residual $\approx 10^{-4}$ and degeneracy $\approx 10^{-2}$ — the second may sit in a real nondegenerate basin.

### §8.12 Verification contract for any claimed counterexample

A *certified* counterexample must include:

- exact coordinates *or* exact algebraic parameterization (not floating-point approximations);
- selected witness sets $S_i$;
- exact verification of all distance-equality polynomials $F_{i, a, b} = (x_i - x_a)^2 + (y_i - y_a)^2 - (x_i - x_b)^2 - (y_i - y_b)^2 = 0$;
- exact strict-convexity orientation determinants $O_i = (p_{i+1} - p_i) \times (p_{i+2} - p_{i+1}) > 0$;
- a reproducible script (Sympy / Sage / Lean-compatible);
- *no reliance on floating-point equality.*

A *numerical candidate* (not a proof) must include: coordinates, $S_i$, independent verifier output, max selected-distance spread, RMS residual, convexity margin, min edge length, min pair distance, optimizer + seed, exactification plan.

### §8.13 Useful homogeneity diagnostic

At any actual solution, $J(p) \cdot p_{\text{flat}} = 2 F(p) = 0$ (L10). Useful regression test:

```python
import numpy as np

def constraints(p, triples):
    vals = []
    for i, a, b in triples:
        vals.append(np.sum((p[i] - p[a])**2) - np.sum((p[i] - p[b])**2))
    return np.array(vals)

# At a candidate solution: J(p) @ p.flatten() should approximately equal 2 * F(p),
# which equals 0 when F(p) = 0. Confirms the scaling direction is in the kernel.
```

### §8.14 Machine-readable artifact

`useful_research_findings/machine_readable/erdos97_k4_search_artifacts.json`: near/degenerate search results. Read as search evidence and verifier regression input, **not** as a counterexample. Useful for documenting degeneracy modes.


---

## §9. Open subproblems, ranked by tractability × leverage

| Rank | Task | Why | Tractability |
|---|---|---|---|
| 1 | **Bridge Lemma A′** at $n = 8, 9, 10$ (computational) | Settles whether the ear-elimination program (§5.2) terminates. Same recipe as §8.6: enumerate 4-regular witness patterns satisfying L5 ∧ L6, check ear-orderability, run least-squares geometric realizability. Cost: a few CPU-days per $n$. If the Bridge Lemma fails at any $n$, the §5.2 program is dead. | High — finite cases. |
| 2 | **Independently audit the `n=8` finite artifacts** | The current repo-local claim rests on the incidence-completeness checker, the 15 survivor classes, and exact obstruction certificates. Independent reproduction and alternative certificate checkers would make the result safer to cite. | Medium-high. |
| 3 | **Endpoint Control Auxiliary Claim** (§5.1) | The Lemma 12 program is otherwise complete. Open sub-questions are concrete: asymmetric vs symmetric statement, dependence of $m$ on $n$ ($m \le O(\sqrt n)$ would help), boundary-chain structure. | Medium. |
| 4 | **Three-Cap Bridge Lemma** (§5.4) | Diameter case is done; this is the remaining geometric case. Possibly tractable using cyclic-order arguments inside the opposite cap alone. | Medium. |
| 5 | **Canonical-chord injectivity** (§5.3) | Cleanest reduction; conjecture is sharp. For each bad $i$: take the smallest $r_i$ with $|S_i(r_i)| \ge 4$, then the closest pair in $S_i(r_i)$. Conjecturally injective; no obvious counterexample. | Lower (combinatorial geometry, hard). |
| 6 | **3-critical 4-tie count $< n$** (§6.3) | Replaces the failed naive count. Two subproblems (Conjecture A: bridge; Conjecture B: count), both unsolved. | Lower-medium. |
| 7 | **Stuck-set enumeration** | For the §5.2 program, enumerate stuck-set structures up to small $n$. Each stuck set $S$ requires every $v \in S$ to have $\ge 2$ outside witnesses with the L5 multiplicity bound. Counting against convexity / cyclic-order / perpendicular-bisector restrictions might rule out small stuck sets. | Lower-medium. |
| 8 | **Generalize the orthocenter obstruction** beyond the cube | Could extend §4.1 to more $n = 8$ patterns, eventually all of them. | Lower. |
| 9 | **Compute $N_{\text{crit}}$ on known examples** | Empirical sanity check on the 3-critical 4-tie program. | High. |
| 10 | **Prove $\sum_i M(i) < 4n$** | Most ambitious; would be substantially stronger than #97. No serious attack documented; would likely require new global incidence machinery. | Speculative. |

---

## §10. Reconciliation log

What the prior synthesis documents disagreed about, and what this document adopts.

| Disagreement | Source disagreement | Resolution adopted |
|---|---|---|
| $n = 8$ status | `erdos_97_complete_notes.md` & `erdos_97_analysis.md` claim "proved"; `erdos97_conversation_useful_notes (1).md` & `erdos97_review_notes.md` flag gaps | Archived synthesis resolution: **Open.** This is superseded by the current `n=8` incidence-completeness and exact-obstruction artifacts. (§4.1, §4.6; current status in `RESULTS.md`) |
| $n = 7$ "weak" vs "strong" definition | `vertex_equidistance_complete_analysis.md` §2 explicit; some notes use weak definition silently | **Strong (cocircular) definition only.** The parity proof and $K_4$ proof both require it. (§1.2, §3.3) |
| "$n \le 12$ proven by counting" | `erdos_97_summary.md` "Lemma 6" arithmetic | **Wrong by a factor of 2.** Correct bound is $n \ge 7$. (§4.3) |
| Forced double regularity | Multiple files implicitly assume this; one source's Cauchy–Schwarz argument is circular | **Available only at $n = 7$.** Not generally usable. (§3.4, §6.4) |
| Generic Jacobian rank as proof | Earlier drafts claim it; `erdos97_paper_review_notes.md` corrects | **Numerical evidence, not proof.** The proper rigorization is the rigidity-with-Euler-homogeneity argument with its own gap (Bridge Lemma A′). (§4.4, §6.7) |
| Jacobian rank value at solutions | Some sources say $2n - 3$; correct is $\le 2n - 4$ | **$\le 2n - 4$** (translations + rotation + scaling = 4-dim kernel). The rank $= 2n - 3$ value is *generic* (non-solution). (§4.5, L10) |
| Diameter-endpoint shortcut | Several files informally suggest extremal-vertex argument | **False.** Hexagon counterexample. (§6.6, §7.4) |
| The 1975 Erdős statement on "every $k$" | Contextual ambiguity | $k = 3$ false (Danzer 9-gon, Fishburn–Reeds 20-gon); $k = 4$ is the boundary case = #97. |
| "Erdős Problem #97" name provenance | Various | Numbering from erdosproblems.com; the 4-equidistant problem appears under that label there (last edited 2025-10-27). |
| $n = 6$ status under uniform-radius framing | `erdos97_useful_findings.md` §A.11 appears to suggest $n = 6$ remains open in the variable-radius case | **Closed.** The clean proof in §3.2 uses only L5 directly and works regardless of radius pattern. The useful-findings phrasing is misleading; it conflates the uniform-radius proof method with the actual case status. |
| $k = 3$ "solved" framing | Some sources call it "solved" | More precisely: $k = 3$ has explicit counterexamples (Danzer; Fishburn–Reeds), so the natural conjecture is *false* there. Erdős #97 ($k = 4$) is the boundary and is open. |
| **Uniform-radius case "folklore-resolved by Füredi $2n-7$"** (NEW in canonical merge) | `erdos97_final_consolidated.md` §5.5; `erdos97_useful_findings.md` §A.11; `zip/source_notes/17_uniform_radius_related_case.md` | **Open, not resolved.** The cited $2n-7$ is an Edelsbrunner--Hajnal lower-bound *construction*, not an upper bound; Füredi's separate convex-`n`-gon unit-distance work belongs to the upper-bound side. Saying $\ge 2n$ unit edges is *consistent* with $\ge 2n-7$, not in conflict with it. The needed $< 2n$ upper bound is the Erdős–Fishburn conjecture, still open. Verified externally via Aggarwal arXiv:1009.2216.[^aggarwal][^edels-hajnal] (§5.5.) |

---

## §11. Bookkeeping

### §11.1 The seven prior artifacts and what each is best for

| Document | Lines | Best for |
|---|---|---|
| `erdos97_synthesis.md` | 463 | Meta-synthesis with TL;DR table, reading order, reconciliation log; pointers-to-others style |
| `erdos97_standalone.md` | 832 | Cleanest public-facing version; PROVED/FAILED status tags; full proof writeups |
| `erdos97_useful_findings.md` | 616 | Findings-organized; best-of-N methodology; primitive 4-fan content; bipartite consequence |
| `erdos97_consolidated.md` | 795 | First synthesis with explicit disagreement tracking (§H section) |
| `erdos97_consolidated_private.md` | 1544 | Most detail; private working notes; full prune list and disagreement table |
| `erdos97_research_state.md` | 1194 | Self-contained working state; deepest on lemma library; pattern families and search methodology |
| `useful_research_findings/` (zip) | 18 source notes + 5 generated summaries + 1 JSON | Original source material with caveats; reproducibility artifacts |

### §11.2 What was deliberately not extracted into this final synthesis

- **Repository scaffolding / handoff notes** (`erdos97_github_repo_handoff_notes.md` and similar) — process material, not math.
- **Prompt-engineering files** (`erdos97_gpt52_pro_prompt_notes.md`, `best_of_n_for_erdos_problem.md`) — methodology, useful but not mathematical content.
- **Notes using the weak witness definition without correction** — would propagate invalid claims (notably the weak-definition $n = 7$ argument).
- **Exact duplicates and superseded drafts** — folded into source attribution where unique content survived.
- **The 5 generated summaries from `useful_research_findings/`** — fully subsumed by §1–§10 here; their content lives in this document with corrected framing.

The full classification is preserved in `useful_research_findings/generated_summaries/05_SELECTION_MANIFEST.md`. Of 53 original review files, 18 source notes were kept (preserving 16 unique mathematical/computational threads); the remainder were dedupes, prompt material, or superseded drafts.

### §11.3 The machine-readable artifact

`useful_research_findings/machine_readable/erdos97_k4_search_artifacts.json` contains near/degenerate search results. Read as search evidence and verifier regression input, **not** as a counterexample. Useful for documenting degeneracy modes.

---

## Appendix A: One-page quick reference

**Problem.** Strictly convex polygon, every vertex has $\ge 4$ other vertices on some circle around it — does this exist?

**Status.** Official/global status is open. Repo-local finite-case artifacts rule
out selected-witness counterexamples for `n <= 8`, with independent review
recommended before public theorem-style claims.

**Three workhorse lemmas.**
- **L5:** $|W_i \cap W_j| \le 2$ (two-circle bound).
- **L6:** $W_i \cap W_j = \{a, b\} \Rightarrow v_iv_j \perp ab$ (perpendicularity).
- **L10:** At any solution, $\mathrm{rank}\, R_W(p) \le 2n - 4$ (Euler homogeneity).

**Five open programs, each with one gap.**
1. Lemma 12 — Endpoint Control Auxiliary Claim.
2. Ear-elimination — Bridge Lemma A′ / Key Peeling.
3. Selection lemma — canonical-chord injectivity.
4. 3-cap reduction — three-cap bridge lemma.
5. Distance-bound — both subcases open. Uniform-radius needs Erdős–Fishburn ($< 2n$, open since 1992); variable-radius is the actual problem at $n \ge 8$.

**Highest-leverage next moves.**
- Independently audit the `n=8` incidence and exact-obstruction artifacts.
- Push the finite incidence/exact pipeline toward `n = 9`.

**Hard rules for any new attempt.**
- Strong (cocircular) witness definition only.
- Run row-overlap L5 filter before any numerical optimization.
- No forced double regularity outside $n = 7$.
- Generic Jacobian rank is evidence, not proof.
- Pure graph theory will not close the Bridge Lemma — geometry must do work.
- Single-vertex extremality arguments are insufficient — proofs must be global.
- Local circumcenter argument cannot work — witnesses sit in a semicircle (L8).
- **Do not cite $2n-7$ as an upper bound.** It is a lower-bound construction; the relevant upper bound on unit distances in convex position is the open Erdős–Fishburn conjecture ($< 2n$), or the proved $n \log_2 n + O(n)$ (Aggarwal), neither of which closes the uniform-radius subcase.

---

## Appendix B: Synthesis methodology (Stages 1–4)

This document was produced via the four-stage protocol requested:

**Stage 1 — Inventory.** Catalogued seven inputs:
- Five prior synthesis documents (`erdos97_synthesis.md`, `erdos97_standalone.md`, `erdos97_useful_findings.md`, `erdos97_consolidated.md`, `erdos97_consolidated_private.md`, `erdos97_research_state.md`).
- One curated source bundle (`useful_research_findings.zip`: 18 source notes + 5 generated summaries + 1 machine-readable JSON).

**Stage 2 — Cluster and dedupe.** Identified content clusters across documents:
- Lemma library (in all 5 main docs) — kept one canonical version.
- Small-case proofs $n = 5, 6, 7$ (identical across all) — kept canonical versions.
- Archived/pre-current-artifact $n = 8$ source-corpus status — older source documents treated `n=8` as open or gap-bearing. This is superseded by the current `n=8` incidence-completeness and exact-obstruction artifacts.
- Failed routes (most thorough in `standalone` §C) — kept and supplemented with consensus framings.
- Active proof programs (cleanest in `synthesis` §5; more detail in `standalone` §F) — merged.
- Counterexamples to intermediate claims (most polished in `standalone` §D) — kept verbatim.
- Computational artifacts (most in `research_state` §G; `standalone` §E) — merged.
- Pattern families (unique to `research_state` §H.2) — preserved.
- Search/verification methodology (most complete in `research_state` §I) — preserved.
- Reconciliation log (synthesized from `consolidated` §H, `consolidated_private` §K, `synthesis` §9).

**Stage 3 — Synthesis.** Produced this single self-contained document. Length: ~1000 lines. Structure: TL;DR → problem → lemma library → small cases → $n = 8$ → active programs → failed routes → counterexamples → computational state → open subproblems → reconciliation → bookkeeping.

**Stage 4 — Verification.** Cross-checked critical claims against multiple sources:
- $n = 5, 6, 7$ proofs — consistent across all 5 main docs and source notes (modulo the weak-vs-strong witness distinction at $n = 7$).
- $n = 8$ source-corpus status — the older synthesis corpus predated the current finite-case artifact. Do not use this archived source-corpus status as the current repo-local status.
- L10 rank value at solutions — consistent at $\le 2n - 4$ across `synthesis`, `standalone`, `research_state`, `consolidated_private`.
- Counterexample coordinates — preserved verbatim from `standalone` §D and verified to be cited identically in source notes.
- $n = 39$ circulant impossibility proof — independently confirmed by `source_notes/12_n39_circulant_degeneracy.md` and the linearized-system blow-up in `source_notes/13_n39_raw_search_notes_and_code.md`.
- Selection manifest — confirmed against `useful_research_findings/generated_summaries/05_SELECTION_MANIFEST.md`.

**Known soft spots in the source archive that this synthesis flags but does not resolve:**
- The L7-based gauge-fixing repair to the ear-elimination rank theorem is described as "the better repair" in source notes but a fully written proof using Route B (explicit minor) is not in the archive. The rank theorem is therefore conditional on this repair being executed.
- Conjectures A and B in the 3-critical 4-tie counting framework remain unproved; the framework replaces a known-false count with two precise but unsolved subproblems.
- The Bridge Lemma A′ at $n = 7$ holds computationally (residuals $\ge 0.6$ for non-ear-orderable patterns); a rigorous proof at $n = 7$ — let alone for general $n$ — is not available.

**Stage 5 — Canonical merge (added 2026-04-27).** Reconciled with `erdos97_four_stage_consolidation.md`:
- Imported external citation set as footnotes (Aggarwal, Edelsbrunner–Hajnal, Fishburn–Reeds, Nivasch et al., erdosproblems.com #97 page, DeepMind `formal-conjectures` Lean file).
- **Corrected the uniform-radius / Füredi $2n-7$ direction-of-bound error in §5.5** (and propagated to §1.5, §10, the TL;DR table, Appendix A).
- Added claim taxonomy (Appendix C).
- Added SHA-256 source inventory (Appendix D).
- Kept the long file's L1–L10 lemma numbering (matches more source notes than the four-stage file's L1–L9).

---

## Appendix C: Claim taxonomy

Following the four-stage consolidation, top-level claims in this document carry one of five status tags:

| Tag | Meaning | Handling |
|---|---|---|
| `VERIFIED` | Checked internally or externally enough to reuse in a proof. | Can be used as a step in future arguments. |
| `CONDITIONAL` | Correct if a named missing lemma/conjecture is supplied. | Keep as a proof program; do not cite as theorem. |
| `EVIDENCE` | Numerical or heuristic support without proof. | Use for search prioritization only. |
| `REJECTED` | Proof route or claim is false or fatally incomplete. | Preserve as warning; do not retry without explicit new idea. |
| `PROVENANCE-WARNING` | Historical/source claim may be true but is not enough for math use. | Cite carefully; do not rely on it. |

### C.1 Claim ledger

**`VERIFIED` (safe to reuse):**
- L1–L10 lemma library (§2). Each is elementary and checked.
- $n = 5, 6, 7$ impossibility (§3). The $n = 7$ parity proof relies only on L5, L6, convexity of $\binom{x}{2}$, and a parity argument on a permutation of 21 chords. (Triple-check: §3.3 here, source-note `01_small_cases_and_incidence_review.md`, four-stage Check A.)
- $n = 39$ circulant impossibility (§8.2). $S_i \cap S_{i+1}$ has size 3, contradicting L5. Independently confirmed by linearized-system blow-up (§8.2.3).
- Public status "open / falsifiable / \$100" on erdosproblems.com.[^erdos97-page]
- Formalization status `research open` in DeepMind `formal-conjectures`.[^formal97]
- Counterexamples to intermediate lemmas in §7 (verbatim coordinates verified by independent computation).
- Cube/orthocenter obstruction at $n = 8$ for the cube witness pattern only (§4.1) — an `VERIFIED` partial obstruction, not a proof of $n = 8$.

**`CONDITIONAL` (kept as research programs):**
- Lemma 12 / endpoint descent (§5.1). Conditional on the Endpoint Control Auxiliary Claim.
- Ear-elimination + rigidity rank (§5.2). Conditional on (a) the L7-based gauge-fixing repair to the rank theorem (§6.5), and (b) Bridge Lemma A′.
- Selection lemma / noncrossing diagonals (§5.3). Conditional on canonical-chord injectivity.
- Smallest enclosing circle / 3-cap (§5.4). Conditional on the Three-Cap Bridge Lemma; diameter case is `VERIFIED`.
- Distance-bound reduction (§5.5). Uniform-radius subcase conditional on Erdős–Fishburn ($< 2n$); variable-radius subcase has no current attack.
- 3-critical 4-tie counting (§6.3). Conditional on Conjectures A (bridge) and B (count $< n$).
- $n = 8$ orthocenter beyond cube (§4.1). Conditional on classification of all $n = 8$ witness patterns.
- Bridge Lemma A′ at $n = 7$. `EVIDENCE`-strong (residuals $\ge 0.6$ in least-squares, §8.6) but not rigorously proved.

**`EVIDENCE` (search prioritization only):**
- Rigidity-rank dichotomy at $k = 4$ vs $k = 3$ (§6.7, §8.5). 450+ trials.
- No counterexample found in any retained search (§8.1).
- Numerical Bridge Lemma satisfaction at $n = 7$ (§8.6).

**`REJECTED` (do not retry without new idea):**
- Naive global quadruple count (§6.3). Refuted by $\Theta(n^4)$ from one bad vertex.
- Forest lemma (§6.2). Refuted by the 9-point and 24-gon counterexamples (§7.2, §7.3).
- Circumcenter-must-be-inside (§6.1). Refuted by the pentagon in §7.1.
- Diameter-endpoint shortcut (§6.6). Refuted by the hexagon in §7.4.
- Forced double regularity outside $n = 7$ (§3.4, §6.4). The Cauchy–Schwarz "proof" is circular.
- Generic Jacobian rank as proof (§6.7). $x^2 = 0$ analogue.
- Distance unimodality off cyclic polygons (§6.8).
- Squared-distance Monge property (§6.9). Refuted by regular hexagon.
- Symmetric ansatz collapse (§6.10).
- Lattice propagation (§6.11). Local rhombus + hull obstruction correct; global propagation step never proved.
- Curvature argument (§6.12). Heuristic only; no formal connection.
- Consecutive-witness-class assumption (§6.13). Refuted by 8-vertex example.
- **Uniform-radius case "folklore-resolved by Füredi $2n-7$"** (§5.5). Direction-of-bound error: $2n-7$ is a lower-bound construction, not an upper bound.
- "$n \le 12$ proven by counting" (§4.3). Off by a factor of 2; correct bound is $n \ge 7$.

**`PROVENANCE-WARNING`:**
- Erdős's 1975 "every $k$" framing. Recorded as likely mistaken on erdosproblems.com.[^erdos97-page]
- The 5 generated summaries in `useful_research_findings/`. Subsumed; cite §1–§10 here instead.
- Several legacy notes silently using the weak (non-cocircular) witness definition. Their conclusions, especially the legacy $n = 7$ argument, should not be used.

---

## Appendix D: SHA-256 source inventory

Imported from `erdos97_four_stage_consolidation.md` for traceability. Hashes are over the file contents at the time of the four-stage consolidation (2026-04-26).

| Source | Type | Words | SHA-256 prefix | Role |
|---|---:|---:|---:|---|
| `erdos97_consolidated private.md` | top-level MD | 15,481 | `450603c9828f` | Largest state file; valuable disagreement log; some stale flags. |
| `erdos97_consolidated.md` | top-level MD | 8,363 | `923669cae987` | Public-style consolidated state. |
| `erdos97_research_state.md` | top-level MD | 12,316 | `814f16a9d5e7` | Detailed research ledger; deepest on lemma library. |
| `erdos97_standalone.md` | top-level MD | 7,327 | `7dfa960462be` | Standalone state of play; preserved counterexample coordinates. |
| `erdos97_synthesis.md` | top-level MD | 4,497 | `2a877fce406d` | Cleanest short meta-synthesis. |
| `erdos97_useful_findings.md` | top-level MD | 7,078 | `8d3d24590954` | Curated findings; contains the uniform-radius error. |
| `zip/README.md` | zip MD | 116 | `1e3f8b22ea6e` | Zip package overview. |
| `zip/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md` | zip MD | 1,044 | `ce6b3ab336d4` | Digest of retained results. |
| `zip/generated_summaries/02_SMALL_CASES_N5_N6_N7.md` | zip MD | 501 | `8a771322faab` | Small-case summary. |
| `zip/generated_summaries/03_RANK_AND_BRIDGE_STATUS.md` | zip MD | 393 | `fb0f990c1326` | Rank/ear-orderability + Bridge status. |
| `zip/generated_summaries/04_COMPUTATIONAL_FINDINGS.md` | zip MD | 425 | `96f1d1994991` | Numerical/search artifacts summary. |
| `zip/generated_summaries/05_SELECTION_MANIFEST.md` | zip MD | 1,076 | `86c7eff060bc` | Selection manifest + curation rationale. |
| `zip/source_notes/01_small_cases_and_incidence_review.md` | zip MD | 2,133 | `3c58aac4455c` | n=5,6,7 + incidence counting. |
| `zip/source_notes/02_core_handoff_paraboloid_intersection.md` | zip MD | 3,339 | `0f668200edc8` | Problem statement + paraboloid lift + base lemmas. |
| `zip/source_notes/03_lemma12_review_notes.md` | zip MD | 965 | `f2863842a661` | Endpoint-descent / Lemma 12 review. |
| `zip/source_notes/04_algebraic_and_semicircle_corrections.md` | zip MD | 2,597 | `e1f890869c24` | Algebraic corrections; semicircle criterion; circumcenter-inside refutation. |
| `zip/source_notes/05_rank_scaling_and_verifier_review.md` | zip MD | 2,301 | `f0233d6b317c` | Jacobian/rank scaling; verifier advice. |
| `zip/source_notes/06_ear_elimination_rank_obstruction_review.md` | zip MD | 2,862 | `2b2d371ed4a1` | Ear-elimination rank obstruction. |
| `zip/source_notes/07_critical_review_ear_route_gaps.md` | zip MD | 1,068 | `53f819e8832e` | Critical review of ear-route gaps. |
| `zip/source_notes/08_ear_elimination_proof_draft_read_with_caveat.md` | zip MD | 1,402 | `ded4dc337276` | Ear-elimination draft with caveats. |
| `zip/source_notes/09_bridge_lemma_computational_analysis.md` | zip MD | 1,285 | `00ab00e319c9` | Bridge Lemma computational analysis. |
| `zip/source_notes/10_corrected_global_counting_framework.md` | zip MD | 2,443 | `46f92407c29d` | Corrected critical-circle / 3-critical 4-tie framework. |
| `zip/source_notes/11_forest_lemma_counterexample_review.md` | zip MD | 1,733 | `d0a86671a220` | Forest lemma is false; 24-gon verification. |
| `zip/source_notes/12_n39_circulant_degeneracy.md` | zip MD | 2,150 | `d8b8aa4dac1f` | n=39 circulant collapse + pattern filters. |
| `zip/source_notes/13_n39_raw_search_notes_and_code.md` | zip MD | 2,252 | `041f42854db8` | Raw search notes; best near-miss metrics. |
| `zip/source_notes/14_k3_benchmark_and_solver_notes.md` | zip MD | 1,399 | `2f259424f602` | Fishburn–Reeds k=3 benchmark + solver notes. |
| `zip/source_notes/15_desargues_k3_upgrade_state.md` | zip MD | 3,311 | `55e81b1dd47f` | Desargues/Fishburn k=3 upgrade branch. |
| `zip/source_notes/16_repo_handoff_and_claim_taxonomy.md` | zip MD | 2,806 | `cac84d823c87` | Repo handoff; claim taxonomy; verification contract. |
| `zip/source_notes/17_uniform_radius_related_case.md` | zip MD | 1,720 | `3108424bd7f5` | Uniform-radius case; **contains the $2n-7$ error corrected in §5.5**. |
| `zip/machine_readable/erdos97_k4_search_artifacts.json` | zip JSON | 356 | `ce0221c00815` | n=12 near-miss + degenerate exact solution. |

**No exact duplicates by SHA-256.** Substantial near-duplicates among top-level syntheses: `erdos97_consolidated.md` ↔ `erdos97_standalone.md` (closest pair); `erdos97_consolidated private.md` ↔ `erdos97_research_state.md`.

---

## Appendix E: External references

[^erdos97-page]: T. F. Bloom, "Erdős Problem #97," Erdős Problems, accessed 2026-04-26. Lists the problem as open / falsifiable / \$100 prize; records the $k=3$ Danzer and Fishburn–Reeds background; flags the "every $k$" 1975 statement as likely mistaken. <https://www.erdosproblems.com/97>

[^formal97]: `google-deepmind/formal-conjectures`, `FormalConjectures/ErdosProblems/97.lean`, accessed 2026-04-26. Marks `erdos_97` as `@[category research open, AMS 52]`; encodes `HasNEquidistantProperty 4`. <https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/97.lean>

[^fishburn-reeds]: P. C. Fishburn and J. A. Reeds, "Unit distances between vertices of a convex polygon," *Computational Geometry* 2 (1992), 81–91. Source for the 20-gon $k=3$ counterexample with uniform unit distance, and for the Erdős–Fishburn $< 2n$ conjecture. <https://www.sciencedirect.com/science/article/pii/092577219290026O>

[^aggarwal]: A. Aggarwal, "On Unit Distances in a Convex Polygon," arXiv:1009.2216 (2010). The abstract states Füredi's earlier upper bound of $2\pi n \log_2 n + O(n)$ and Aggarwal's improvement to $n \log_2 n + O(n)$. **This is the relevant external check that the prior synthesis's "Füredi $2n-7$" claim was a direction-of-bound error.** <https://arxiv.org/abs/1009.2216>

[^edels-hajnal]: H. Edelsbrunner and P. Hajnal, "A lower bound on the number of unit distances between the points of a convex polygon," *JCTA* 56 (1991), 312–316. Provides the lower-bound *construction* with $\ge 2n - 7$ unit-distance pairs in some convex $n$-gons. **Not an upper bound.** Füredi's separate convex-`n`-gon unit-distance work is cited under [^aggarwal] on the upper-bound side. <https://pub.ista.ac.at/~edels/Papers/1991-03-UnitDistancesConvexPolygon.pdf>

[^nivasch]: G. Nivasch, J. Pach, R. Pinchasi, and S. Zerbib, "The number of distinct distances from a vertex of a convex polygon," *Journal of Computational Geometry* 4(1):1–12, 2013 / arXiv:1207.1266. Lower bound $\ge (13/36 + \varepsilon)n - O(1)$ on the number of distinct distances from a vertex of a convex polygon. <https://arxiv.org/abs/1207.1266>
