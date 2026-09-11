# Exact failures of two extremal selection shortcuts

Status: **exact geometric negative controls**, with written interpretation;
independent external review pending. Neither set is an Erdős #97 counterexample.
All coordinates lie in Q(sqrt(3)). The field checkers compare signs exactly;
there is no floating hull or equality tolerance in the certificate contract.

## A. Every minimum-enclosing-disk support can be rich

Let omega=(-1+i sqrt(3))/2 and

    u = 1-99 sqrt(3)/101 + 20 i sqrt(3)/101.
    P = {omega^k, omega^k u, omega^k conjugate(u): k=0,1,2}.

Label the three anchors 0,1,2, the rotations of u by 3,4,5, and its conjugate
by 6,7,8. Counterclockwise order is

    [0,5,8,1,3,6,2,4,7].

The exact checker verifies 36 distinct pairs and all 63 global supporting
inequalities. Their minimum is

    11880/10201 - 60 sqrt(3)/101 > 0.

At each anchor, its two anchor mates and its two matching rotated u-points
are at squared distance 3. The complete maximum-multiplicity vector is

    [4,4,4,2,2,2,2,2,2].

The six nonanchors have norm squared 4-198 sqrt(3)/101, strictly between zero
and one. Only the anchors are on the unit circle. Their centroid is zero, so
for any proposed disk center c their squared distances from c average to
1+|c|². Thus no disk of radius below one contains the anchors, and a disk of
radius one containing them must have center zero. The unit disk is therefore
the unique minimum enclosing disk, and every one of its support vertices is
rich.

This refutes "one of the minimum-enclosing-circle supports is good" even
when the disk and its three-point support set are unique. It does not refute
a theorem using additional hypotheses, or the existence of a good vertex
elsewhere: the other six vertices are good.

The six nonanchors are genuinely outside the old six-arc carrier associated
with these anchors. Every point x on that carrier satisfies
|x-a|²=3|x|² for some anchor a. The independent supplemental checker verifies
that none of the six nonanchors satisfies any of these three equalities.

Replay:

    python verify/geometry_control.py candidate_counterexamples/mec_support_control_9.json \
        --output /tmp/mec9.json

## B. A maximum-rich-radius root can have four nonlarger-rich witnesses

Use complex coordinates and define

    c=(99-20i)/101,
    a=((1-i sqrt(3))/2)c,
    b_1=c(1-(15+8i)/17),
    b_2=c(1-(4+3i)/5).

For rational t define U(t)=(1-t²+2it)/(1+t²), which has norm one.
Let epsilon=1/10, let

    (t_1,t_2,t_3,t_4)=(-9/20,-11/25,-43/100,-21/50),
    f_j=a+epsilon U(t_j).

The seventeen labelled points are

    p0=0, p1=a, p2=c, p3=conjugate(c), p4=conjugate(a),
    p5=b1, p6=b2, p7=conjugate(b1), p8=conjugate(b2),
    p9,...,p12=f1,...,f4,
    p13,...,p16=conjugate(f1),...,conjugate(f4).

Counterclockwise order:

    [0,5,6,1,9,10,11,12,2,3,16,15,14,13,4,8,7].

The independent verifier reconstructs all 136 distinct pair distances and
all 255 global supporting inequalities. The minimum support determinant is

    100/2125864637 > 0.

There are exactly five rich centers, with the following complete rich classes:

| center | witnesses | squared radius |
|---|---|---|
| 0 | 1,2,3,4 | 1 |
| 1 | 9,10,11,12 | 1/100 |
| 2 | 0,1,5,6 | 1 |
| 3 | 0,4,7,8 | 1 |
| 4 | 13,14,15,16 | 1/100 |

Every distance at each of the other twelve vertices is distinct. In particular,
1 is the largest *actual rich squared radius anywhere in the set*, not just
the largest radius in an arbitrarily chosen list of witness rows. The root
0 has four rich witnesses; each of their unique rich radii is no larger than
the root's. The middle witnesses have the same radius, and the two outer
witnesses have strictly smaller radii.

Thus the following proposed local route is false:

> A rich vertex at the global maximum rich radius has a good witness, or a
> witness whose rich radius is necessarily larger.

This control is complementary to the preceding session's 21-point control,
whose root has four witnesses at strictly larger rich radii. Together they
show that neither a radius-increasing nor a radius-decreasing rule can be
forced solely from a rich root and richness of its four witnesses.

**Scope:** the seventeen-point set has twelve good vertices. It does not
refute a descent or ascent theorem whose derivation genuinely uses every
vertex of the whole polygon being rich, or a closed multi-step region.

A second retained version uses epsilon=1/10000. It has the same exact
multiplicity distribution. The primary control above uses 1/10 to avoid
unnecessarily small geometric margins.

Replay:

    python verify/star_control.py candidate_counterexamples/nonincreasing_star_control_17_robust.json \
        --output /tmp/star17.json

The verifier imports field arithmetic, not the construction script. It
recomputes every actual distance class and checks the global-maximum-radius
claim. It does not trust named witness rows or a stored numerical hull.
