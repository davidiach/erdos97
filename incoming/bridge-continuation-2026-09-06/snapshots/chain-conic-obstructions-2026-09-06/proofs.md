# Convex chains, ellipses, and escape tails for Erdős #97

Date: 6 September 2026.

**Status: restricted paper-proof candidates, with exact regression checks; external review pending.**

No proof or counterexample for unrestricted Erdős #97 is claimed. No repository status, accepted finite bound, or prior certificate is changed. Published novelty is not claimed.

For a finite nonempty set of distinct points P in the Euclidean plane, write

\[
 M_P(p)=\max_{r>0}\#\{q\in P\setminus\{p\}:\|p-q\|=r\}.
\]

The maximum is zero when P consists of one point. Erdős #97 asks whether every finite set in strictly convex position contains p with M_P(p) <= 3. All distances below are ordinary Euclidean distances; coordinate changes explicitly used to preserve them are rigid motions.

## 1. A minimum-height theorem for convex graphs

**Theorem 1.** Let f be a real convex function on an interval I, and let T be a finite nonempty subset of I. For

\[
 S=\{(t,f(t)):t\in T\},
\]

any sampled point p=(t_0,f(t_0)) of minimum sampled height satisfies M_S(p) <= 2.

**Proof.** Take two sampled parameters x_1<x_2<t_0. There is a number lambda in (0,1) such that

\[
 x_2=\lambda x_1+(1-\lambda)t_0.
\]

Convexity and the minimum-height choice imply

\[
 f(t_0)\le f(x_2)
 \le\lambda f(x_1)+(1-\lambda)f(t_0)
 \le f(x_1).
\]

Thus

\[
 0<t_0-x_2<t_0-x_1,
 \qquad 0\le f(x_2)-f(t_0)\le f(x_1)-f(t_0).
\]

Squaring and adding gives

\[
 \|(x_2,f(x_2))-p\|^2
 <\|(x_1,f(x_1))-p\|^2.
\]

The corresponding argument on the right of t_0 shows that distance strictly increases as sampled parameters move away from t_0 on either side. A fixed positive distance therefore occurs at most once on each side. QED.

Reflection gives the same statement for concave graphs, using a sampled maximum instead of a minimum. No differentiability, strict curvature, polynomial degree, equal spacing, or prescribed witnesses are required.

**Corollary 1.1 (arbitrary outliers).** If P=S union Z, where S is as in Theorem 1 and Z has at most k additional points, the same p satisfies

\[
 M_P(p)\le 2+k.
\]

In particular, a convex or concave graph together with one arbitrary point cannot be a counterexample to Erdős #97. This conclusion does not require the union itself to be convex.

### Relation to the quartic search family

This theorem applies to every finite sample of a function convex on the interval spanning the sampled parameters, regardless of degree or irregular parameter spacing. It therefore closes the globally convex quartic-graph construction route, not merely an equally spaced finite instance.

This does **not** say that an arbitrary finite convexly independent sample of a polynomial graph lies on a convex function branch. Samples may occupy both boundary chains of their convex hull. Nor does it cover arbitrary implicit quartics or general polynomial parametrizations with both coordinates nonlinear.

The repository's rich-endpoint control is

\[
 g(t)=\frac35t+\frac3{10}t^2-t^3+\frac{13}{10}t^4.
\]

Its second derivative has positive leading coefficient and discriminant -36/25, so g is globally strictly convex. The point (-1,2) has four other points of this graph at squared distance 5. This is compatible with Theorem 1: that endpoint need not be the sampled minimum-height point. For any finite collection containing those five points, the sampled minimum-height point, not the prescribed endpoint, supplies the two-multiplicity conclusion.

The exact verifier checks the original endpoint control by a polynomial identity and a Sturm root count. It does not incorrectly reject a valid rich row.

## 2. Convex chains including vertical end edges

**Theorem 2.** Let Q=(q_0,...,q_m) be a nonempty open polygonal chain whose edge directions rotate strictly counterclockwise and whose total change of edge direction is at most pi. Assume all edges are nonzero. Then some vertex p of Q satisfies M_Q(p) <= 2.

This applies in particular to an inherited open boundary chain of a strictly convex polygon whose sum of turns at its internal vertices is at most pi.

**Proof.** Rotate coordinates so that the first edge has direction -pi/2. All edge directions then lie in [-pi/2,pi/2]. Consequently the x coordinates along the chain are nondecreasing. As the edge directions increase through zero, their y components change from negative to nonnegative at most once. Choose a vertex p of minimum y coordinate.

Along either side of p, when walking away from p, the absolute horizontal displacement from p and the nonnegative vertical displacement above p are both nondecreasing. Each step strictly increases at least one displacement because its edge is nonzero. Squared distance from p therefore strictly increases on each side. A distance can occur at most once on each side, hence at most twice in total. QED.

The argument intentionally permits vertical first or last edges. Thus total turn equal to pi is included; there is no unproved limiting step at equality. Chains with one vertex or one edge are immediate.

### A radius-independent necessary condition for any counterexample

Let p_0,...,p_{n-1} be a strictly convex polygon in counterclockwise order, with exterior turns tau_i in (0,pi). Indices are modulo n.

**Corollary 2.1.** If, for some i,

\[
 \tau_{i-1}+\tau_i+\tau_{i+1}\ge\pi,
\]

then P contains a vertex p with M_P(p) <= 3.

**Proof.** The cases with at most three vertices are immediate. Delete p_i, and consider the remaining original-boundary chain

\[
 p_{i+1},p_{i+2},\ldots,p_{i-1}.
\]

Its internal turns are precisely those of P except at the three labels i-1,i,i+1. Its total turn is

\[
 2\pi-(\tau_{i-1}+\tau_i+\tau_{i+1})\le\pi.
\]

Theorem 2 provides a point p with multiplicity at most two among the remaining vertices. Restoring p_i increases any distance multiplicity at p by at most one. QED.

Consequently every hypothetical counterexample must satisfy

\[
 \boxed{\tau_{i-1}+\tau_i+\tau_{i+1}<\pi\quad\text{for every }i.}
\]

This is an all-size necessary condition. It is not a new general lower bound beyond the repository's accepted n <= 8 result. Averaging these inequalities alone only excludes n <= 6.

### Exact determinant implementation

Set e_j=p_{j+1}-p_j. For n>=4 the total positive turn between e_{i+1} and e_{i-2}, through the complementary chain, lies strictly between zero and 2pi. It is at most pi exactly when

\[
 \det(e_{i+1},e_{i-2})\ge0.
\]

Thus a hypothetical counterexample necessarily has

\[
 \boxed{\det(e_{i+1},e_{i-2})<0\quad\text{for every }i.}
\]

The unwrapped turn interval matters: a determinant sign is not, in general, an unrestricted angle comparison. Here strict convexity and the specified complementary boundary chain provide that interval.

## 3. A two-multiplicity theorem for Euclidean ellipses

**Theorem 3.** Every finite nonempty set S on a nondegenerate Euclidean ellipse contains a point p with M_S(p) <= 2. One may choose a point maximizing the absolute major-axis coordinate relative to the ellipse center.

The repository's prior Vieta argument gave only M_S(p) <= 3. The stronger conclusion here allows one arbitrary point to be added.

**Proof.** A rigid motion puts the ellipse in the form

\[
 E(t)=(a\cos t,b\sin t),\qquad a\ge b>0.
\]

Choose p maximizing |x| over S. If this maximum is zero, S has at most two points and the claim is immediate. By reflections in the two coordinate axes, assume

\[
 p=E(\tau),\qquad 0\le\tau<\frac\pi2.
\]

Every other sampled point has x coordinate at most a cos(tau), and therefore has a parameter in the arc

\[
 [\tau,2\pi-\tau].
\]

It suffices to show that squared distance from p is strictly increasing and then strictly decreasing on this arc. Define

\[
 D(t)=a^2(\cos t-\cos\tau)^2+b^2(\sin t-\sin\tau)^2,
\]

and put G(t)=D'(t)/2. Direct differentiation gives

\[
 G(t)=(b^2-a^2)\sin t\cos t
       +a^2\cos\tau\sin t-b^2\sin\tau\cos t. \tag{1}
\]

On tau<t<=pi/2, an equivalent form is

\[
 G(t)=a^2\sin t(\cos\tau-\cos t)
       +b^2\cos t(\sin t-\sin\tau)>0.
\]

On pi/2<=t<pi, all three terms of (1) are nonnegative and the middle term is positive. At t=pi, G(pi)=b^2 sin(tau).

For t=pi+s with 0<s<pi/2, write

\[
 G(\pi+s)=\cos s\,B(s),
\]

where

\[
 B(s)=b^2\sin\tau-(a^2-b^2)\sin s-a^2\cos\tau\tan s.
\]

Since a>=b and cos(tau)>0,

\[
 B'(s)=-(a^2-b^2)\cos s-a^2\cos\tau\sec^2s<0. \tag{2}
\]

When tau>0, B starts positive and tends to negative infinity, so G changes sign exactly once from positive to negative in (pi,3pi/2). When tau=0, B is negative for s>0, and the unique maximum of D is at t=pi.

Finally, on 3pi/2<=t<2pi-tau, put v=-sin(t)>=0 and c=cos(t), so 0<=c<=cos(tau). Then

\[
 G(t)=-a^2v(\cos\tau-c)-b^2c(v+\sin\tau)<0
\]

in the interior under consideration. Endpoint values do not disturb strict monotonicity on the two open branches.

Therefore D is strictly increasing up to one maximum and strictly decreasing after it. A fixed positive value has at most two preimages on the allowed arc. Every sampled point lies on that arc, so M_S(p)<=2. QED.

**Corollary 3.1.** A finite subset of a Euclidean ellipse, together with one arbitrary additional point, cannot be a counterexample to Erdős #97. More generally, k arbitrary additional points give M_P(p)<=2+k at the same chosen ellipse point.

### Sharpness and a necessary distinction

For S={(2,0),(0,1),(0,-1)} on x^2/4+y^2=1, the chosen point p=(2,0) has two witnesses at squared distance 5. Adding z=(1,2) gives three witnesses at that same distance, while all four points remain strictly convex. Thus the +1 allowance is actually used.

Theorem 3 guarantees a suitable point; it does not say every ellipse point is good. The exact five-point set

\[
 (0,0),\quad(3/5,4/5),\quad(3/5,-4/5),
 \quad(5/13,12/13),\quad(5/13,-12/13)
\]

lies on the ellipse

\[
 80x^2+15y^2-64x=0.
\]

Its origin has four witnesses at distance one. Its exact maximum-multiplicity profile is (4,1,1,1,1). The verifier checks all 15 strict supporting-line inequalities.

## 4. Escape tails and both branches of a hyperbola

**Lemma 4 (escape tail).** Let C be a planar curve, let P be a finite subset, and let p be a point of P. Assume:

1. every positive-radius circle centered at p meets C in at most m distinct points;
2. C contains a continuous injective path gamma:[0,infinity)->C with gamma(0)=p, with gamma(t) not in P for t>0, and with ||gamma(t)-p|| tending to infinity.

Then M_P(p)<=m-1.

**Proof.** For every r>0, continuity and the intermediate value theorem give a point gamma(t) at distance r from p. It is not in P, and consumes one of the at most m distinct circle-curve intersections. The remaining intersections can contribute at most m-1 witnesses in P. QED.

**Theorem 4.1.** Every finite nonempty point set on a real nondegenerate hyperbola has a point p with M_P(p)<=3, even when P meets both branches and even without convexity.

**Proof.** After a rigid motion a hyperbola can be written

\[
 x^2/a^2-y^2/b^2=1,\qquad a,b>0.
\]

Use the bijective real parametrization

\[
 x(t)=\frac a2(t+t^{-1}),\qquad
 y(t)=\frac b2(t-t^{-1}),\qquad t\ne0.
\]

Substitution into an arbitrary circle equation, followed by multiplication by t^2, gives a polynomial of degree exactly four: its leading and constant coefficients are both (a^2+b^2)/4>0. Hence a circle has at most four distinct intersections with the entire hyperbola, across both branches together.

Choose any occupied branch and a point p of maximum y coordinate among the sampled points on that branch. Continuing upward on that branch gives a continuous unbounded path containing no other point of P. Points on the other branch cannot lie on this path. Apply Lemma 4 with m=4. QED.

The proof does not assume that the selected witness circle has four intersections on one branch. The total intersection bound and the unused escape-tail intersection are global across both branches.

### A four-rich hyperbola control

The five strictly convex points

\[
 (0,0),\quad(9/41,-40/41),\quad(3/5,4/5),
 \quad(5/13,12/13),\quad(7/25,24/25)
\]

lie on the nondegenerate hyperbola

\[
 192x^2+220xy+57y^2-288x-48y=0.
\]

Its quadratic discriminant is 4624>0. All four nonzero points are on the unit circle centered at the origin. Again the exact multiplicity profile is (4,1,1,1,1); the conclusion is existential, not a claim that every hyperbola point is three-good.

## 5. Every real conic

**Corollary 5.** Every finite nonempty subset of the zero set of a nonzero real polynomial of degree at most two contains p with M_P(p)<=3, provided that zero set is not the whole plane.

**Proof.** A nondegenerate real conic is, after a rigid motion, an ellipse, parabola, or hyperbola. Ellipses are covered by Theorem 3. Parabolas are convex or concave graphs after an orthogonal change of coordinates and are covered by Theorem 1. Hyperbolas are covered by Theorem 4.1, including both branches.

The remaining nonempty real loci are a point, one line, or a union of two lines, including parallel or coincident lines. For two distinct lines, choose an occupied line and an endpoint of the finite sample on that line. A circle centered there meets that same line in at most one other sampled point, because only one of its two rays contains other sampled points. The other line contributes at most two points. Any intersection-point double counting can only lower the total. One-line and one-point cases are immediate. Empty loci contain no nonempty P. QED.

The escape-tail proof alone gives three, not two, on a general both-branch hyperbola. Convexity supplies the following separate strengthening.

### Convexly independent conic sets have the stronger bound two

**Lemma 5.1 (opposite-branch interior point).** Three points on one branch of a hyperbola and one point on the other branch cannot all be in strictly convex position. The middle parameter point of the three lies strictly inside the triangle of the other three points.

**Proof.** Use the hyperbola parametrization in Theorem 4.1. Its exact orientation determinant is

\[
 \det(H(v)-H(u),H(w)-H(u))
 =-\frac{ab(v-u)(w-u)(w-v)}{2uvw}. \tag{3}
\]

By a half-turn if necessary, take three right-branch parameters 0<u<v<w, and let h<0 parametrize the opposite-branch point. Write A=H(u), B=H(v), C=H(w), D=H(h).

Equation (3) gives orient(A,B,C)<0 and gives orient(A,B,D)>0, orient(A,C,D)>0, and orient(B,C,D)>0. In the counterclockwise triangle A,C,D, the point B therefore lies strictly to the left of each of its three oriented sides:

\[
 \operatorname{orient}(A,C,B)>0,\qquad
 \operatorname{orient}(C,D,B)>0,\qquad
 \operatorname{orient}(D,A,B)>0.
\]

Thus B is strictly inside that triangle. QED.

Consequently a convexly independent set meeting both hyperbola branches contains at most two points on each branch, hence at most four points total.

**Theorem 5.2.** Every nonempty finite set S in strictly convex position lying on a real conic contains a point p with M_S(p)<=2.

**Proof.** Ellipses and parabolas were covered by Theorems 3 and 1. One branch of a hyperbola is, after swapping the orthogonal coordinate axes, the graph of the convex function x=a sqrt(1+y^2/b^2) or its concave negative, so Theorem 1 applies. Both-branch sets have at most four points by Lemma 5.1. A degenerate union of two lines also has at most four points under strict convexity, because three collinear points are forbidden.

For completeness, every set of at most four distinct planar points has some point with multiplicity at most two. Only a four-point set could violate this: then every point would be equidistant from the other three, forcing all six pair distances equal. Three would form an equilateral triangle of side r, while the fourth would have to be its circumcenter at distance r from all three. Its actual circumradius is r/sqrt(3), a contradiction. Single-line and point conics are immediate. QED.

**Corollary 5.3 (a conic plus one point).** A strictly convex polygon for which all but at most one vertex lie on any nonzero real conic satisfies Erdős #97.

Indeed its conic subset is itself convexly independent. Choose p supplied by Theorem 5.2 and restore the one possible outlier. Then M_P(p)<=3.

The convexity hypothesis here is essential to the proof of the two-multiplicity strengthening on both hyperbola branches and on degenerate conics. It is not silently inserted into the earlier, convexity-free three-multiplicity theorem.

## 6. The general gap is not removed

These theorems do not prove that every convex polygon lies on a conic, or that deleting one vertex leaves a convex graph chain. Both unconditional reductions are false.

An exact strictly convex control is

\[
 (5,0),(3,4),(0,51/10),(-3,4),
 (-5,0),(-3,-41/10),(0,-5),(3,-4).
\]

For every one-point deletion, the 7-by-6 conic evaluation matrix with rows

\[
 (x^2,xy,y^2,x,y,1)
\]

has rank six. Consequently none of those seven-point subsets lies on any nonzero conic. The verifier also checks every possible boundary cut of every one-point deletion and finds no convex graph chain, even allowing the weak endpoint case in Theorem 2.

This polygon has M-profile (2,1,2,1,2,1,2,1), so it is **not a counterexample**. It demonstrates only that a conic/chain reduction would have to use the additional all-rich hypothesis, not strict convexity alone.

No argument here derives such a reduction from the assumption that every vertex has four equidistant witnesses. Nor does this packet establish the separate boundary-independent, incident-side-bounded extraction required by the repository's radius-descent theorem. The unrestricted Erdős #97 problem remains unresolved by this work.

## 7. What the computation verifies

`verify.py` checks rational finite instances with exact Fraction arithmetic and checks algebraic identities, root counts, and matrix ranks with SymPy. Its purpose is to catch sign, endpoint, quantifier, and indexing errors in the written arguments. The finite tests are not substitutes for the proofs for arbitrary real inputs.

The saved run includes 1,533 convex-graph subsets, 5,115 ellipse subsets, the corresponding isometry and +1-point checks, 765 hyperbola subsets (675 meeting both branches, including 300 convexly independent subsets subject to the four-point cap), 511 two-line subsets, 11,540 weak convex chains, and 763 applicable three-turn certificates. Nested counts are not independent tests. Four-rich conic controls, a +1 sharpness control, and the eight-point bridge control are retained.

The quartic control's four roots are certified by exact root counts, not numerical residuals. No floating-point comparison supports an equality or a nonexistence claim in the delivered verifier. There is no exhaustive search over arbitrary polygons, no external mathematical review, and no Lean formalization in this packet.
