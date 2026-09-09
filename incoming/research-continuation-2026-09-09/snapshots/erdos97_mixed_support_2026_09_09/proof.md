# Every finite symmetric parabolic-lens sample has a good vertex

Research date: 9 September 2026. **Written proof; independent mathematical
review pending.** This is an all-size theorem for a specified geometric family,
not a solution of unrestricted Erdős Problem #97. No published novelty or
formalization is claimed.

## 1. Statement and the improvement over the preceding packet

For H>0, put

    K_H = {(x,y): x^2 <= y <= H-x^2},    b = sqrt(H/2).

Its boundary consists of the lower arc L(t)=(t,t^2) and the upper arc
U(t)=(t,H-t^2), -b<=t<=b. The arcs coincide only at their two endpoints.

**Theorem.** Every finite nonempty set P of distinct points on the boundary of
K_H contains p such that every positive-radius circle centered at p contains
at most three other points of P. More precisely:

* If 0<H<=3/2, **every** point of P maximizing |x| has every positive-distance
  multiplicity at most **two** (a stronger conclusion).
* If H>=3/2, **every** point of P minimizing |x| is good.

At H=3/2 both assertions apply. Witnesses can mix the arcs in any proportion;
radii and witness assignments can differ at every vertex. The sample need not
be symmetric, and there is no size cutoff.

Every finite boundary sample with at least three points is strictly convex:
the tangent to either containing parabola supports K_H and meets that parabola
only at the tangency point. Thus all its distinct sampled points are exposed.
The one- and two-point cases are harmless.

This closes the **mixed-witness symmetric lens family**, not just the earlier
opposite-chain witness scaffold. The previous Vieta/averaging theorem required
all four witnesses of a row on one specified target parabola. That assumption
is not used here. Conversely the present theorem assumes the points are on the
bounded lens boundary; it does not cover arbitrary samples outside that lens,
unequal curvatures, shifted axes, or arbitrary convex polygons.

## 2. Reductions and distance polynomials

Reflection in x=0 and reflection in y=H/2 preserve the lens, distances, and |x|.
We may therefore take the selected center as p=L(c), 0<=c<=b. Write

    A(t) = |L(t)-p|^2 = (t-c)^2+(t^2-c^2)^2,
    B(t) = |U(t)-p|^2 = (t-c)^2+(H-t^2-c^2)^2,
    ell = H-2c^2 >= 0.

Their relevant derivatives are

    A'(t) = 2(t-c)[1+2t(t+c)],
    B'(t) = 2 C(t),
    C(t) = 2t^3+(1-2H+2c^2)t-c.

For s>=0 also write

    F(s)=B(-s)=(s+c)^2+(H-c^2-s^2)^2,
    g(s)=2s^3+(1-2H+2c^2)s+c,
    F'(s)=2g(s).

All counts below are counts of DISTINCT geometric points, not polynomial-root
multiplicities. The common arc endpoints are counted only once.

## 3. Shallow lenses: a largest-|x| point is good

Assume H<=3/2 and c>0. All witnesses in P have t in [-c,c], and c^2<=H/2<=3/4.
On this interval t(t+c)>=-c^2/4, so

    1+2t(t+c) >= 1-c^2/2 > 0.

Consequently A is strictly decreasing on [-c,c]; at most one lower witness
can lie at a given positive distance.

We show B takes every value at most twice on [-c,c]. First, C is convex on
[0,c], because C''(t)=12t>=0, and

    C(0)=-c<0,    C(c)=2c(2c^2-H)<=0.

Thus C(t)<0 for 0<=t<c. No positive-interior stationary point of B occurs.
On the negative half, its stationary points correspond to roots of g in (0,c).
There is at most one such root:

**Case c<=1/2.** At any root s in (0,c),

    s g'(s)-g(s)=4s^3-c < 4c^3-c <=0.

Thus every such root is a strict downward crossing. Two downward crossings
would require an intervening upward crossing or tangency. This is impossible
because every root in this interval has negative derivative. So there is at
most one root.

**Case c>=1/2.** The exact identity

    g(s) = 2(s+1)(s-1/2)^2
           +2(c^2-1/4)s +(c-1/2)+(3-2H)s

is a sum of nonnegative terms for s>=0. It is strictly positive except possibly
when c=1/2, H=3/2, s=1/2, which is not in (0,c). There is no interior root.

Therefore B has at most one stationary point in (-c,c). If one exists, the
signs just established show it is a MAXIMUM, not a minimum: g starts positive
at s=0 and can cross downward only, so B' crosses from positive to negative
as t increases. Thus B is decreasing, or increases and then decreases.

This gives the sharper count two. The lower distances range from 0 to 4c^2,
whereas B(-c)=4c^2+ell^2. For R<=4c^2 with ell>0, the left endpoint of B
is above R and the possible turning point is a maximum, so B takes R at most
once. This gives at most one lower plus one upper witness. For R>4c^2, there
are no lower witnesses and at most two upper witnesses.

If ell=0, then c=b. At the one extra boundary level R=4c^2, the lower witness
L(-c) is the same geometric point as the upper endpoint U(-c). Even if B has
one more occurrence of that level, the distinct-point total is still at most
two. The other levels obey the preceding count. If c=0, all of P is on x=0
and contains at most two points. This completes the shallow case.

## 4. Deep lenses: a smallest-|x| point is good

Assume H>=3/2. If c=b, all of P lies at the two common endpoints; the result is
immediate. First take 0<c<b. The allowed witness parameters lie in
[-b,-c] union [c,b].

### 4.1 The right boundary contributes at most one witness

On [c,b], A is strictly increasing. C is convex and

    C(c)=2c(2c^2-H)<0,
    C(b)=(b-c)(1-H-2bc)<0.

Thus B is strictly decreasing on [c,b]. Traverse the boundary from L(c)
through L(b)=U(b) to U(c). Squared distance increases strictly from 0 to
ell^2, since A(b)=B(b). This entire right arc contributes at most one point
at any radius, and contributes none when the squared radius R>ell^2.

### 4.2 The left lower arc contributes at most one

For t in [-b,-c], t(t+c)>=0 and t-c<0, so A'(t)<0. There is at most one
left lower witness at any squared radius R.

### 4.3 The left upper arc contributes at most two

Since g'(s)=6s^2+1-2H+2c^2 is strictly increasing for s>0, g decreases and then
increases, or is increasing throughout. If g(c)<0, it has at most one root in
(c,b). If g(c)>=0, use

    g(c)=2c(1-H+2c^2)>=0.

Then H<=1+2c^2 and, as H>=3/2, c^2>=1/4. Hence

    g'(c) >= 4c^2-1 >=0.

The derivative increases beyond c, so g has no root in (c,b). Thus F has at most
one stationary point in (c,b), and every level has at most two points there.

### 4.4 Its possible double intersection is too far away to combine with the right arc

We need the stronger assertion that F(s)=R has at most one solution in [c,b]
when R<=ell^2. Every INTERIOR stationary point s in (c,b) satisfies

    H = c^2+s^2+1/2+c/(2s).                           (1)

Set v=c/s, so 0<v<1. Since s<b, (1) and 2s^2<H give

    2s(s-c)<1,
    H(s-c)<s.                                       (2)

For completeness, these follow from the identities, with
D=2s(s-c)-1,

    H-2s^2 = -(c+s)D/(2s),
    H(s-c)-s = (c^2+s^2)D/(2s).

From H>=3/2 and (2), 1-v<1/H<=2/3, hence v>1/3. Also

    (s-c)^2 < (s-c)/(2s)=(1-v)/2 < v.

At this same stationary point, direct substitution yields

    F(s)-ell^2 = (s+c)^2 [v-(s-c)^2] > 0.            (3)

But F(c)=4c^2+ell^2>ell^2. Two distinct solutions of F(s)=R<=ell^2, starting
from this larger left-end value, would force an interior local minimum with
value at most R. Equation (3) excludes that. Tangency does not create an
exception, because it too would be a stationary point at a forbidden level.
So there is at most one such left upper witness.

### 4.5 Count the witnesses

For R<=ell^2, the right boundary contributes at most one, the left lower at
most one, and the left upper at most one: total at most three.

For R>ell^2, the right boundary contributes none, the left lower at most one,
and the left upper at most two: again at most three.

Common endpoints may have been counted twice in these upper bounds; identifying
them can only reduce the count.

If c=0, the right-arc monotonicity in 4.1 still holds (strict away from its
initial endpoint). Reflection in x=0 makes the left arc identical in its
radial behavior. Each half contributes at most one, with the point U(0)
counted only once. Thus there are at most two witnesses. The deep case, and
hence the theorem, is proved.

## 5. Similarity-invariant formulation

For a>0 and H>0, consider the lens

    k+a(x-h)^2 <= y <= k+H-a(x-h)^2.

After the Euclidean similarity X=a(x-h), Y=a(y-k), it becomes K_(aH).
The same theorem applies, choosing maximum |x-h| for aH<=3/2 and minimum
|x-h| for aH>=3/2. Rigid motions preserve the statement. The switch value
3/2 is a sufficient common cutoff in this proof; no optimality of either
selector's full validity range is asserted.

## 6. Why the switch of extremal vertex is substantive

Two exact five-point controls are included. They are not all-rich polygons.
One has H<3/2 and its UNIQUE minimum-|x| vertex is rich via one lower and
three upper witnesses. The other has H>3/2 and its UNIQUE maximum-|x| vertex
is rich with the same mixed distribution. Thus neither proposed selector
works uniformly for all heights.

The controls are specified by rational upper parameters t1,t2,t3 and the
fourth formal circle/parabola root t4=-t1-t2-t3. Put

    c=e3(t1,t2,t3,t4)/2,
    H=c^2+(1-e2(t1,t2,t3,t4))/2.

Then p=(c,c^2) is the exact circumcenter of the four formal upper points.
Only the first three are kept; the fourth lies outside the lens. The remaining
witness is L(z), where z is the uniquely isolated real root in the supplied
rational interval of

    (z-c)^2+(z^2-c^2)^2-R=0,
    R=(t1-c)^2+(H-t1^2-c^2)^2.

All five retained points lie strictly inside their respective lens arcs.
The verifier checks all 15 strict supporting signs, every squared-distance
class, the selector property, the isolation, and both arc memberships exactly.
The chosen extremal center has multiplicity four; each other point is good.
The source parameters and root intervals are in data/controls.json.

The deep selector's bound of three is attained in a further exact level-count
control. Set c=3/5, H=7907/3800, R=44468521/14440000, and restrict both arcs
to |t|<=1019/1000 (which is strictly within the lens). In |t|>=c, there is
exactly one lower witness and exactly two upper witnesses, at the rational
parameters -9/10 and -1. The lower witness is uniquely specified by its
quartic and its negative-interval isolation. Taking these three witnesses and
L(c) gives a finite convex sample whose unique minimum-|x| point has distance
multiplicity three. This does not claim that every point of that sample has
multiplicity three, nor that the family's optimal guaranteed-good bound is
three.

## 7. Verification and remaining gap

The proof above, not a numerical scan, supplies the arbitrary-size and
arbitrary-real conclusion. verify.py uses rational polynomial arithmetic,
Sturm root counts and rational interval signs for controls and a finite
regression suite. oracle.py derives the formulas with SymPy, uses its own
root-count machinery, and checks control signs with Bernstein bounds rather
than the primary Horner interval evaluation. Both were created in this run;
this is not independent external review or a formal proof assistant check.

This theorem does not settle an arbitrary strictly convex polygon, the fixed
nine-point seed's two-internally-supported-vertex escape, general unequal or
offset parabolic carriers, or configurations outside the specified lens.
