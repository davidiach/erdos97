# An exact 66-point structured partial construction for Erdős Problem 97

**Date:** 4 September 2026
**Status:** `EXACT_CERTIFICATE_DIAGNOSTIC` / review pending. **Not a counterexample. Not a solution of Erdős Problem 97.**

> **Claim boundary.** This note records one exact partial construction. It does
> not update `README.md`, `STATE.md`, `RESULTS.md`, `docs/claims.md`, or
> `metadata/erdos97.yaml`; the repository-wide status remains open, with no
> counterexample claimed. The 192-, 256-, and 384-bit runs cited below are
> repeated executions of one verifier, not independent implementations.

## 1. Result obtained

Let

\[
M_P(p)=\max_{r>0}|\{q\in P\setminus\{p\}:|p-q|=r\}|.
\]

The explicit radical construction below produces 66 distinct points in
strictly convex position, with the exact distribution

| Maximum multiplicity | Number of vertices |
|---:|---:|
| 2 | 3 |
| 3 | 3 |
| 4 | 60 |

Thus exactly 60 vertices have four equidistant other vertices. The other six
do not. This configuration satisfies, rather than disproves, the conclusion of
Erdős Problem 97.

This is a result of the present construction and verifier. No claim is made
that this partial construction is new in the published literature or that it
approaches a counterexample in a mathematically controlled limit.

## 2. Exact coordinates

Identify the Euclidean plane with the complex numbers and put

\[
\omega=\frac{-1+i\sqrt3}{2},\qquad
P=\{\omega^k z_j:0\le j<22,\ 0\le k<3\}.
\]

The seeds are

\[
z_0=2i,\qquad
z_1=\frac{-8991\sqrt3-26503i}{10927},\qquad
z_2=\frac{-10753\sqrt3-44665i}{18529}.
\]

Every orbit is an equilateral triangle centered at the origin. The two other
members of the orbit of \(z_j\) are both at squared distance

\[
\rho_j^2=3|z_j|^2
\]

from \(z_j\). Four-fold ties at this radius therefore require two additional witnesses from other orbits.

The three initial cross-orbit equalities are

\[
|z_0-\omega z_1|^2=3|z_0|^2,\qquad
|z_1-\omega z_2|^2=3|z_1|^2,\qquad
|z_2-z_0|^2=3|z_2|^2.
\]

These are checked by rational arithmetic after writing every seed as \((\sqrt3 X,Y)\).

### Two types of constraint circle

An **incoming** constraint based at \(p\) is

\[
\mathcal I(p):\quad |z-p|^2=3|p|^2.
\]

It gives an extra witness \(z\) to the existing center \(p\).

An **outgoing** constraint based at \(p\) is

\[
\mathcal O(p):\quad |z+p/2|^2=\frac34|p|^2.
\]

Expanding shows that this is equivalent to

\[
|z-p|^2=3|z|^2.
\]

It therefore gives the existing point \(p\) as an extra witness to the new center \(z\).

### Circle intersection formula

For circles with centers \(a,b\), squared radii \(u,v\), and \(a\ne b\), define

\[
\Delta=b-a,\quad D=|\Delta|^2,\quad
 t=\frac{u-v+D}{2D},\quad H=\frac uD-t^2.
\]

Their two intersection points are

\[
\operatorname{CI}_{\pm}(a,u;b,v)
 =a+t\Delta\pm i\Delta\sqrt H.
\]

Every use below has \(D>0\) and \(H>0\). The square root is the positive real square root.

### Complete construction history

In each row, intersect the indicated constraint based at \(z_a\) with the
indicated constraint based at \(\omega^k z_b\), and choose the displayed sign
in the formula above. This table, together with the seeds, specifies every
coordinate exactly; it does not use rounded decimal coordinates.

| New index | a | b | k | First constraint | Second constraint | Sign |
|---:|---:|---:|---:|---|---|:---:|
| 3 | 1 | 2 | 1 | in | in | + |
| 4 | 0 | 3 | 0 | out | out | − |
| 5 | 3 | 4 | 0 | out | out | − |
| 6 | 2 | 5 | 2 | out | out | + |
| 7 | 0 | 6 | 0 | in | out | + |
| 8 | 3 | 7 | 1 | out | out | + |
| 9 | 1 | 8 | 0 | out | out | + |
| 10 | 3 | 7 | 2 | out | out | − |
| 11 | 3 | 6 | 0 | out | out | − |
| 12 | 2 | 11 | 2 | out | out | − |
| 13 | 5 | 11 | 0 | out | out | − |
| 14 | 9 | 10 | 0 | out | out | − |
| 15 | 8 | 14 | 1 | out | out | − |
| 16 | 1 | 15 | 2 | out | out | + |
| 17 | 3 | 16 | 2 | out | out | − |
| 18 | 11 | 17 | 0 | out | out | + |
| 19 | 0 | 10 | 1 | out | out | − |
| 20 | 2 | 19 | 1 | out | out | − |
| 21 | 11 | 20 | 2 | out | out | + |

## 3. Witness graph and the remaining failure

Write an arrow \(i\to(j,k)\) for

\[
|z_i-\omega^k z_j|^2=3|z_i|^2.
\]

Every row also has its two same-orbit witnesses \(\omega z_i\) and
\(\omega^2z_i\). The exact verification gives:

| Orbit | Exact maximum multiplicity | Selected cross-orbit witnesses (j,k) |
|---:|---:|---|
| 0 | 4 | (1, 1), (7, 0) |
| 1 | 4 | (2, 1), (3, 0) |
| 2 | 4 | (0, 0), (3, 2) |
| 3 | 2 |  |
| 4 | 4 | (0, 0), (3, 0) |
| 5 | 4 | (3, 0), (4, 0) |
| 6 | 4 | (2, 0), (5, 2) |
| 7 | 3 | (6, 0) |
| 8 | 4 | (3, 0), (7, 1) |
| 9 | 4 | (1, 0), (8, 0) |
| 10 | 4 | (3, 0), (7, 2) |
| 11 | 4 | (3, 0), (6, 0) |
| 12 | 4 | (2, 0), (11, 2) |
| 13 | 4 | (5, 0), (11, 0) |
| 14 | 4 | (9, 0), (10, 0) |
| 15 | 4 | (8, 0), (14, 1) |
| 16 | 4 | (1, 0), (15, 2) |
| 17 | 4 | (3, 0), (16, 2) |
| 18 | 4 | (11, 0), (17, 0) |
| 19 | 4 | (0, 0), (10, 1) |
| 20 | 4 | (2, 0), (19, 1) |
| 21 | 4 | (11, 0), (20, 2) |

For vertex indices \(j+22k\), the six exceptional vertices are

\[
3,25,47\quad\text{(maximum multiplicity 2)},
\]

and

\[
7,29,51\quad\text{(maximum multiplicity 3)}.
\]

Within the selected side-radius construction, orbit 3 lacks two cross-orbit
witnesses and orbit 7 lacks one. No choice of a different existing radius fixes
these six vertices: the verifier upper-bounds multiplicity over **all** their
distances, not just the selected side radius.

### Important bookkeeping limitation

The seed has three selected cross-orbit arrows. Each subsequent orbit is
constructed from two constraints and adds two selected arrows. With \(m=22\)
orbits, the construction therefore explicitly supplies

\[
3+2(m-3)=2m-3=41
\]

arrows. Supplying two at every orbit would require at least 44. The three missing arrows have not been obtained.

Increasing the number of already-good orbits can raise the proportion of
four-bad vertices without decreasing this deficit. Consequently, the 60/66
fraction is **not** a percentage completion of a disproof. A valid completion
would need additional identities, altered incidence structure, or another
construction—not merely further two-constraint growth with no new
coincidences.

## 4. Exactness and verification

The selected equalities are algebraic identities of the seeds, rotations, and circle-intersection formula. Small numerical residuals are not used to prove an equality.

The standalone verifier `scripts/check_orbit66_exact_partial.py` uses only Python's standard library. It encloses each coordinate in an interval whose endpoints are integers divided by \(2^b\). Addition, multiplication, division, squaring, and square roots round outward using integer and rational arithmetic. Square roots use integer square-root bounds.

The verifier checks:

1. All construction denominators and intersection radicands are strictly positive.
2. All 2,145 point pairs are distinct.
3. For every directed edge of the supplied cyclic order, every other point is strictly to its left: 4,224 strictly positive determinant checks.
4. Every selected witness is distinct and its equality follows from the defining identities.
5. The maximum multiplicity at every orbit representative is exactly 2, 3, or 4 as stated.

For the last check, all squared-distance intervals in a row are partitioned into overlap components. Any collection of exactly equal distances must lie in one such component. The largest component is therefore an upper bound on multiplicity. It equals the lower bound supplied by the exact selected witnesses in every row. Rotation gives the same conclusion at the other two vertices of each orbit.

The smallest certified edge-point determinant is larger than

\[
8.13\times10^{-6},
\]

and the smallest certified squared separation is larger than

\[
2.85\times10^{-5}.
\]

The output JSON contains the full dyadic lower bounds, coordinate enclosures, and expanded witness table. These decimal summaries are not used in the proof.

The same verifier passed at 192, 256, and 384 bits of dyadic precision. These are repeated runs of one implementation, not three independent implementations or external peer review.

### Reproduce

```sh
python scripts/check_orbit66_exact_partial.py --assert-expected --summary-json
python scripts/check_orbit66_exact_partial.py --bits 384 --assert-expected
```

No third-party packages or internet access are needed for verification.

## 5. A useful cubic identity for this family

For arbitrary complex \(a,b\), write \(s=|a|^2\), \(t=|b|^2\). Then

\[
\boxed{
\prod_{k=0}^2\left(|a-\omega^k b|^2-3s\right)
 =|a^3-b^3|^2-9s(s-t)^2.
}
\]

One derivation is to put \(U=\Re(a^3\overline{b^3})\). The three squared distances are the roots of

\[
f(x)=(x-s-t)^3-3st(x-s-t)+2U.
\]

Evaluate \(-f(3s)\), and use \(|a^3-b^3|^2=s^3+t^3-2U\).

Consequently, an arrow from the orbit of \(a\) to the orbit of \(b\), at the source's own triangle-side radius, exists exactly when

\[
|a^3-b^3|^2=9s(s-t)^2.
\]

If arrows exist in both directions, subtraction gives

\[
9(s-t)^3=0.
\]

Thus \(s=t\), and the identity then forces \(a^3=b^3\): the two orbits are the same. Therefore **distinct orbits in this side-radius family cannot have arrows in both directions**, even without assuming convexity. Distinct equal-radius orbits cannot have an arrow in either direction.

This is also a practical warning about nearly coincident orbits: the forward/reverse identity difference is cubic in \(s-t\). Very small floating-point residuals can therefore mimic a forbidden reverse arrow. Such an apparent coincidence occurred in an earlier 18-point numerical branch and was not used in the exact certificate.

For a strictly convex union, one target orbit can supply at most one extra
witness at the source's triangle-side radius. To see this, suppose two target
vertices are equidistant witnesses. After rotating labels, write them as
\(b,\omega b\). Their perpendicular bisector is the symmetry axis through
\(\omega^2b\), so the source has the form \(a=t\omega^2b\) with real \(t\).
The radius equation becomes

\[
|a-b|^2=|b|^2(t^2+t+1)=3t^2|b|^2,
\]

hence \((t-1)(2t+1)=0\). The case \(t=1\) identifies the two orbits, while
\(t=-1/2\) makes \(a=(b+\omega b)/2\), a side midpoint and therefore not a
strict hull vertex. Thus distinct strict-hull orbits contribute at most one
witness per target orbit. Together with the no-reciprocal-arrow identity, a
side-radius counterexample in this family would require an oriented graph of
minimum outdegree at least two. Since such a graph has at most
\(\binom{m}{2}\) arrows, it requires \(2m\le\binom{m}{2}\), hence at least five
orbits. This is a necessary condition, not a sufficiency claim.

## 6. Search scope and outcome

The construction was discovered by a bounded floating-point beam search over incoming/outgoing circle constraints. That search was not exhaustive and is not evidence of nonexistence or optimality. The checked claim in this note depends only on the embedded exact construction and the standard-library verifier.

**Final outcome:** an exact, auditable 66-point partial construction and a family-specific cubic identity. No complete counterexample to Erdős Problem 97 was obtained.

## Appendix: certified cyclic order

The verifier certifies strict convexity in the following counterclockwise order.
Vertex `j + 22k` denotes `omega^k z_j`.

```text
22, 4, 19, 60, 53, 8, 36, 59, 51, 1, 25, 54, 61, 42, 49, 2, 55,
18, 28, 21, 13, 34, 44, 26, 41, 16, 9, 30, 58, 15, 7, 23, 47, 10,
17, 64, 5, 24, 11, 40, 50, 43, 35, 56, 0, 48, 63, 38, 31, 52, 14,
37, 29, 45, 3, 32, 39, 20, 27, 46, 33, 62, 6, 65, 57, 12
```

A reviewer can regenerate the full coordinate enclosures and expanded witness
table without committing a generated JSON artifact:

```bash
python scripts/check_orbit66_exact_partial.py \
  --assert-expected \
  --output /tmp/orbit66_exact_partial.json
```
