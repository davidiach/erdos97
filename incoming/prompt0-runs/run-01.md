# Prompt 0 Run 01

I do **not** have a complete proof or counterexample for the original statement. Rather than give a false proof, I will state precisely what I can prove. The argument below gives a rigorous reduction, proves several necessary structural lemmas, and gives an exact near-counterexample showing why the strict-convexity hypothesis is doing real work.

Let me call a vertex `(p_i)` **good** if

`N_i(r) <= 3` for every `r > 0`,

and **bad** otherwise. Thus `(p_i)` is bad exactly when there are four distinct other vertices lying on one circle centered at `(p_i)`.

The desired statement is:

Every finite strictly convex planar vertex set has at least one good vertex.

I cannot honestly claim to have settled this. The strongest rigorous facts I obtained are the following.

---

## 1. A basic angular lemma for a bad vertex

Let `P={p_1,...,p_n}` be the vertex set of a strictly convex polygon, listed in cyclic order. Fix a vertex `p in P`. Let the two polygonal edges incident to `p` determine the interior angle

`alpha_p in (0, pi)`.

All other vertices of the polygon lie strictly inside the open cone of angle `alpha_p` with apex `p`.

### Lemma 1

Suppose `p` is bad. Then there exist four distinct vertices

`q_1,q_2,q_3,q_4 in P\{p}`

lying on a common circle centered at `p`, and in their cyclic order around the polygon their polar angles around `p` also occur in the same order. Moreover they lie on an arc of angular length `< pi`.

### Proof

Since `p` is bad, there is some `r>0` such that at least four vertices of `P\{p}` lie on the circle

`C(p,r)={x:|x-p|=r}`.

Choose four of them and label them `q_1,q_2,q_3,q_4` according to the cyclic order of the polygon after deleting `p`.

Because the polygon is strictly convex, all vertices different from `p` lie strictly inside the interior tangent cone at `p`. This cone has opening angle `alpha_p<pi`. Hence the four rays

`p q_1, p q_2, p q_3, p q_4`

are contained in an angular interval of length `alpha_p<pi`. In particular, the four points `q_1,q_2,q_3,q_4` lie on an open semicircle of `C(p,r)`.

Strict convexity also prevents two distinct vertices from lying on the same ray from `p`, because then `p` and those two vertices would force a collinearity incompatible with all vertices being extreme. Thus the polar angles are distinct. Along the boundary chain opposite `p`, the radial projection from `p` preserves order, because two chords from `p` to boundary vertices cannot cross in the interior of a convex polygon. Therefore the cyclic order and polar order agree.

---

## 2. A quantitative angle constraint

For a vertex `x`, write

`epsilon_x := pi - alpha_x`

for its exterior angle. Thus `epsilon_x > 0`, and

`sum_{x in P} epsilon_x = 2pi`.

### Lemma 2

Let `p` be bad, and let `q_1,q_2,q_3,q_4` be four vertices lying on a circle centered at `p`, in the order given by Lemma 1. Define the angular gaps at `p` by

`delta_1 = angle q_1 p q_2`, `delta_2 = angle q_2 p q_3`, `delta_3 = angle q_3 p q_4`.

Then

`delta_1 + delta_2 + delta_3 < alpha_p < pi`.

Moreover the two middle vertices satisfy

`epsilon_{q_2} <= (delta_1+delta_2)/2`,

`epsilon_{q_3} <= (delta_2+delta_3)/2`.

Equivalently,

`alpha_{q_2} >= pi - (delta_1+delta_2)/2`,

`alpha_{q_3} >= pi - (delta_2+delta_3)/2`.

### Proof

Because `q_1,q_2,q_3,q_4` lie in the interior cone at `p`, their total angular spread is less than `alpha_p`, so

`delta_1 + delta_2 + delta_3 < alpha_p < pi`.

Now consider `q_2`. The two vertices `q_1` and `q_3` lie on opposite sides of `q_2` along the boundary chain of the polygon. Since the polygon is convex, the diagonal rays

`q_2 q_1`, `q_2 q_3`

lie inside the interior angle at `q_2`. Therefore

`alpha_{q_2} >= angle q_1 q_2 q_3`.

The four points `q_1,q_2,q_3` lie on a circle centered at `p`. The central angle subtending the chord `q_1 q_3` is

`angle q_1 p q_3 = delta_1 + delta_2`.

Since `q_2` lies on the minor arc from `q_1` to `q_3`, the inscribed angle `angle q_1 q_2 q_3` subtends the complementary major arc. Hence

`angle q_1 q_2 q_3 = pi - (delta_1+delta_2)/2`.

Thus

`alpha_{q_2} >= pi - (delta_1+delta_2)/2`,

or equivalently,

`epsilon_{q_2} <= (delta_1+delta_2)/2`.

The proof for `q_3` is identical, using the triangle `q_2 q_3 q_4`.

### Corollary 3

If `p` is bad and

`alpha_p < 2pi/3`,

then at least one of the four equal-distance witnesses has interior angle strictly larger than `alpha_p`. In fact, both middle witnesses `q_2,q_3` in Lemma 2 satisfy

`alpha_{q_2} > alpha_p`, `alpha_{q_3} > alpha_p`.

### Proof

Since

`delta_1 + delta_2 < alpha_p`,

Lemma 2 gives

`alpha_{q_2} >= pi - (delta_1+delta_2)/2 > pi - alpha_p/2`.

If `alpha_p < 2pi/3`, then

`pi - alpha_p/2 > alpha_p`.

Thus `alpha_{q_2} > alpha_p`. The same argument applies to `q_3`.

This gives a genuine obstruction to local badness, but it does not by itself prove the theorem. In a hypothetical counterexample in which every vertex is bad, the maximum interior angle must be at least `2pi/3`, which is compatible with convex polygons.

---

## 3. A strong intersection restriction

For each bad vertex `p_i`, choose one radius `r_i` for which

`N_i(r_i) >= 4`,

and choose a set

`S_i subseteq P\{p_i}`, `|S_i|=4`,

such that every point of `S_i` lies on the circle `C(p_i,r_i)`.

### Lemma 4

If `p_i != p_j` are two bad vertices, then

`|S_i cap S_j| <= 2`.

### Proof

Suppose, toward a contradiction, that

`|S_i cap S_j| >= 3`.

Choose three distinct vertices

`a,b,c in S_i cap S_j`.

Because `a,b,c in S_i`, we have

`|a-p_i|=|b-p_i|=|c-p_i|=r_i`.

Because `a,b,c in S_j`, we also have

`|a-p_j|=|b-p_j|=|c-p_j|=r_j`.

Hence each of `a,b,c` lies on both circles

`C(p_i,r_i)`, `C(p_j,r_j)`.

Equivalently, subtracting squared-distance equations,

`|x-p_i|^2-|x-p_j|^2=r_i^2-r_j^2`.

This is a linear equation in `x`, so the common points of the two circles lie on a single line, namely the radical axis of the two circles. Thus `a,b,c` are collinear.

But three collinear vertices cannot occur in a strictly convex polygon. Contradiction. Therefore

`|S_i cap S_j| <= 2`.

This lemma is quite restrictive: a putative all-bad configuration must carry four-element witness sets `S_i` with pairwise intersections at most `2`, and these sets must also satisfy the angular inequalities of Lemma 2.

---

## 4. An exact near-counterexample when convex position is dropped

The strict-convexity hypothesis is highly load-bearing. If we merely take a finite planar point set and do not require every point to be a vertex of its convex hull, the corresponding statement is false.

Let

`phi=(1+sqrt(5))/2`, `rho=phi^{-2}=(3-sqrt(5))/2`.

Let

`zeta=e^{2pi i/5}`, `eta=e^{pi i/5}`.

Define ten points in the complex plane by

`A_k=zeta^k`, `0<=k<=4`,

and

`B_k=rho eta zeta^k`, `0<=k<=4`.

Thus the `A_k` form a regular pentagon of radius `1`, while the `B_k` form a smaller regular pentagon of radius `rho`, rotated by `36` degrees.

### Proposition 5

For the ten-point set

`Q={A_0,...,A_4,B_0,...,B_4}`,

every point has four other points at the same distance.

### Proof

By fivefold rotational symmetry, it suffices to check `A_0` and `B_0`.

First consider `A_0=1`. Its four equal-distance neighbors are

`A_1, A_4, B_1, B_3`.

Indeed,

`|A_0-A_1|^2 = |1-zeta|^2 = 2-2 cos(2pi/5)`.

Since

`cos(2pi/5)=1/(2phi)`,

this equals

`2-1/phi`.

On the other hand,

`|A_0-B_1|^2 = |1-rho e^{3pi i/5}|^2 = 1+rho^2-2rho cos(3pi/5)`.

Using

`cos(3pi/5)=-1/(2phi)`,

we get

`|A_0-B_1|^2 = 1+rho^2+rho/phi`.

Since `rho=phi^{-2}`, this is

`1+phi^{-4}+phi^{-3}`.

Using `phi^2=phi+1`, one checks that

`1+phi^{-3}+phi^{-4} = 2-phi^{-1}`.

Thus

`|A_0-B_1|=|A_0-A_1|`.

By symmetry,

`|A_0-B_3|=|A_0-B_1|`, `|A_0-A_4|=|A_0-A_1|`.

Therefore `A_0` has four equidistant neighbors.

Now consider `B_0=rho e^{pi i/5}`. Its four equal-distance neighbors are

`A_0, A_1, B_2, B_3`.

We have

`|B_0-A_0|^2 = 1+rho^2-2rho cos(pi/5)`.

Since

`cos(pi/5)=phi/2`,

this becomes

`|B_0-A_0|^2 = 1+rho^2-rho phi`.

Because `rho=phi^{-2}`, this is

`1+phi^{-4}-phi^{-1}`.

Next,

`|B_0-B_2|^2 = rho^2 |e^{pi i/5}-e^{5pi i/5}|^2`.

The angle difference is `4pi/5`, so

`|B_0-B_2|^2 = 2rho^2(1-cos(4pi/5))`.

Using

`cos(4pi/5)=-phi/2`,

we obtain

`|B_0-B_2|^2 = rho^2(2+phi)`.

Since `rho=phi^{-2}`, this is

`phi^{-4}(2+phi)`.

Again using `phi^2=phi+1`, one checks that

`phi^{-4}(2+phi) = 1+phi^{-4}-phi^{-1}`.

Hence

`|B_0-B_2|=|B_0-A_0|`.

By symmetry,

`|B_0-A_1|=|B_0-A_0|`, `|B_0-B_3|=|B_0-B_2|`.

Thus `B_0` also has four equidistant neighbors. Rotating the whole construction proves the same for every `A_k` and every `B_k`.

However, this is **not** a counterexample to the original problem. The points `B_k` lie strictly inside the regular pentagon with vertices `A_0,...,A_4`. Indeed, the inradius of the outer regular pentagon is

`cos(pi/5)=phi/2`,

whereas

`rho=phi^{-2} < phi/2`.

So `Q` is not the vertex set of a strictly convex polygon. This example shows that the convex-position assumption cannot simply be discarded.

---

## 5. What the proved lemmas reduce the problem to

A genuine counterexample to the original problem would have to be a strictly convex polygon in which every vertex `p_i` is bad. For each `p_i`, choose four equal-distance witnesses `S_i`. Then the following conditions are forced:

1. Each `S_i` lies on an open semicircle of the circle centered at `p_i`.
2. If `S_i={q_1,q_2,q_3,q_4}` is written in cyclic order around the polygon, and `delta_1=angle q_1 p_i q_2`, `delta_2=angle q_2 p_i q_3`, `delta_3=angle q_3 p_i q_4`, then
   `epsilon_{q_2} <= (delta_1+delta_2)/2` and
   `epsilon_{q_3} <= (delta_2+delta_3)/2`.
3. For distinct centers `p_i,p_j`, `|S_i cap S_j| <= 2`.

The exact obstruction I could not overcome is this:

I do not know how to rule out, or realize, a strictly convex configuration satisfying all these constraints simultaneously.

The local angle inequalities are strong, but they do not immediately force an infinite descent, because once `alpha_p >= 2pi/3`, Lemma 2 no longer guarantees a witness of strictly larger interior angle. The intersection bound is also strong, but by itself it is only combinatorial and does not contradict the possible existence of `n` four-element witness sets with pairwise intersections at most `2`.

---

## 6. Role of the hypotheses

The most load-bearing hypothesis is **strict convexity**.

It is used in two essential places:

1. To ensure that all other vertices lie inside an open cone of angle `<pi` at a chosen vertex. This is what makes the four equal-distance witnesses lie on an open semicircle and makes Lemma 2 possible.
2. To forbid three collinear vertices. This is what proves the intersection bound `|S_i cap S_j| <= 2`.

The exact ten-point construction above shows that if one drops the requirement that all points be vertices of a strictly convex polygon, the analogous statement is false.

The hypothesis of **planarity** is also essential. In higher dimensions, the analogue is false in a very simple way: in `R^4`, the five vertices of a regular simplex have the property that every vertex is equidistant from the other four. Thus every vertex has a radius `r` with `N_i(r)=4`.

The **centered-on-vertex condition** is also crucial. Lemma 1 and Lemma 2 both rely on the fact that the center of the relevant circle is itself one of the polygon vertices, so that the interior cone at that vertex controls the angular spread of the witnesses.

The hypothesis of **finiteness** is needed for extremal arguments involving angles and for the witness-set formulation. Without finiteness, one can no longer reduce the problem to finitely many four-point witness configurations.

So the status of my work is:

No complete proof or disproof; the original statement remains unresolved by the argument above.

But the strongest established local statement is Lemma 2, and the strongest established global restriction is Lemma 4.
