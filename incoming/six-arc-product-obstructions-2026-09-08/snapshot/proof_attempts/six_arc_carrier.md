# A good point in every finite subset of the six-arc carrier

**Status:** self-contained restricted paper proof; independent review pending.
This is not a solution of unrestricted Erdős #97. The carrier comes from the
repository's unbounded six-exception construction. The statement below does
not assume its recurrence, rotational invariance of the finite set, or the
choice of an own-side witness radius.

## Theorem

Put

\[
\omega=(-1+i\sqrt3)/2,\qquad D(t)=1+3t^2,
\qquad z(t)=-\tfrac12+\frac{3t}{D(t)}
  +i\sqrt3\frac{1-3t^2}{2D(t)}.
\]

For \(0<s<1/3\), define

\[
\mathcal C_s=\{\omega^kz(t),\ \omega^k\overline{z(t)}:
                  k=0,1,2,\ 0\le t\le s\}.
\]

Every circle of positive radius centered at \(z(s)\) meets
\(\mathcal C_s\) in at most three **distinct** points.

Consequently every nonempty finite subset of
\(\mathcal C_{<1/3}=\bigcup_{0<s<1/3}\mathcal C_s\) has a point from which
every positive distance occurs at most three times. Convexity of the finite
subset is not required for this last assertion.

## Six distance functions

Fix \(0<s<1/3\), write \(D=1+3s^2\), and put

\[
F_{+,k}(t)=|z(s)-\omega^kz(t)|^2,
\qquad
F_{-,k}(t)=|z(s)-\omega^k\overline{z(t)}|^2.
\]

Their common denominator is \(D(1+3t^2)\). Their numerators are

| Function | Numerator |
|---|---|
| \(F_{+,0}\) | \(9(s-t)^2\) |
| \(F_{+,1}\) | \(3(9s^2t^2-9st^2+3st+3t^2-3t+1)\) |
| \(F_{+,2}\) | \(3(9s^2t^2-9s^2t+3s^2+3st-3s+1)\) |
| \(F_{-,0}\) | \(3(3st-1)^2\) |
| \(F_{-,1}\) | \(3(3s^2+3st-3s+3t^2-3t+1)\) |
| \(F_{-,2}\) | \(9(3s^2t^2-3s^2t+s^2-3st^2+st+t^2)\) |

After differentiation and multiplication by the positive denominator
\(D(1+3t^2)^2\), the six derivative numerators are, respectively,

\[
\begin{split}
&-18(s-t)(3st+1),\\
&9(s-1)(6st-3t^2+1),\\
&9(3s-1)(3st^2-s+2t),\\
&18(s+t)(3st-1),\\
&-9(s-1)(6st+3t^2-1),\\
&9(3s-1)(3st^2-s-2t).
\end{split}
\]

On \([0,s]\), the first, second, fourth and fifth functions are strictly
decreasing and the sixth is strictly increasing. For example,
\(6st+3t^2\le9s^2<1\), and
\(3st^2-s-2t<0\). The third derivative changes sign exactly once, from
positive to negative: \(3st^2-s+2t\) is strictly increasing, is negative at
zero, and equals \(s(3s^2+1)>0\) at \(t=s\). Thus \(F_{+,2}\) has exactly
one interior maximum, denoted \(V\), and no level has more than two preimages
under this function.

## Separation of the ranges

Set

\[
\begin{array}{lll}
 L=9s^2/D,& R=3(3s^2-3s+1)/D,& H=3/D,\\
 S=27s^2(1-s)^2/D^2,& T=3(1-3s^2)^2/D^2,
 &U=3(1-3s)^2/D^2.
\end{array}
\]

Direct endpoint substitution and the preceding monotonicity give

| Function | Range | Maximum number of parameter preimages |
|---|---|---|
| \(F_{+,0}\) | \([0,L]\) | 1 |
| \(F_{-,2}\) | \([L,S]\) | 1 |
| \(F_{-,1}\) | \([U,R]\) | 1 |
| \(F_{+,1}\) | \([R,H]\) | 1 |
| \(F_{-,0}\) | \([T,H]\) | 1 |
| \(F_{+,2}\) | \([R,V]\) | 2 |

Here

\[
0<L<S<R<V<T<H,
\qquad 0<U<R.
\]

The only non-immediate separation is \(V<T\). We verify all the other
necessary strict inequalities using

\[
\begin{split}
S-L&=\frac{-18s^2(3s-1)}{D^2}>0,\\
R-S&=\frac{3(3s-1)(3s^2-1)}{D^2}>0,\\
T-R&=\frac{9s(s-1)(3s-1)}{D^2}>0,\\
H-T&=\frac{-27s^2(s-1)(s+1)}{D^2}>0.
\end{split}
\]

The strict inequality \(U<R\) also follows from strict decrease of
\(F_{-,1}\). The single interior maximum of \(F_{+,2}\), whose two endpoint
values are \(R\), gives \(V>R\).

To prove \(V<T\), direct subtraction gives

\[
D^2(1+3t^2)(T-F_{+,2}(t))=9(3s-1)Q(s,t),
\]
where
\[
Q(s,t)=(3s^3+s)t+s^2-s-(3s+1)t^2.
\]

For \(0\le t\le s<1/3\),

\[
Q(s,t)\le (3s^3+s)s+s^2-s
       =s(3s^3+2s-1)<0.
\]

Indeed \(3s^3+2s<1/9+2/3<1\). Both \(3s-1\) and \(Q(s,t)\) are strictly
negative, so \(T-F_{+,2}(t)>0\) everywhere in the parameter interval.

## Counting points, including the shared arc endpoints

A circle centered at \(z(s)\) with squared radius \(d>0\) meets the carrier
at the solutions of the six level equations \(F_{\pm,k}(t)=d\). We must
count points rather than arc parametrizations.

For \(d<R\), the first and sixth ranges, \([0,L]\) and \([L,S]\), contribute
at most one distinct point together. Their sole possible common level is
\(L\); at that level both parameter values are \(t=0\) and both describe the
same point \(\omega\). The fifth function contributes at most one more
point. All other ranges lie above or at \(R\). Thus there are at most two
points.

At \(d=R\), the possible points are precisely among

\[
\omega z(s),\quad \omega^2z(s),\quad 1.
\]

The point \(1\) is described twice: by \(F_{+,2}(0)\) and by
\(F_{-,1}(0)\). The other endpoint of \(F_{+,2}\) is \(t=s\), while
\(F_{+,1}(s)=R\). No other function contributes at this level.

For \(R<d\le V\), only \(F_{+,1}\) and \(F_{+,2}\) can contribute, giving
at most one plus two points. For \(V<d<T\), only \(F_{+,1}\) contributes.
For \(T\le d\le H\), only \(F_{+,1}\) and \(F_{-,0}\) contribute, giving
at most two. For \(d>H\), there are no intersections. This proves the circle
intersection assertion, including every critical and shared-endpoint level.

## Passing to an arbitrary finite subset

For each point of a finite subset \(P\subset\mathcal C_{<1/3}\), choose a
representation with parameter \(t\in[0,1/3)\). If all chosen parameters are
zero, then \(P\subset\{1,\omega,\omega^2\}\), and the conclusion is
immediate. Otherwise choose a point with largest chosen parameter \(s>0\).
A rotation by a power of \(\omega\), followed if necessary by conjugation,
sends this point to \(z(s)\) and sends all the chosen representations into
\(\mathcal C_s\). Apply the circle intersection assertion. These isometries
do not change distance multiplicities.

This completes the restricted proof. No recurrence, density, limiting
configuration, or assumed symmetry of \(P\) has been used.

## Scope and boundary audit

The parameter range is strict. At \(s=1/3\), the derivative formulas become
degenerate and this proof does not give the assertion. No assertion at or
beyond that parameter is included.

The original six-exception family uses \(0<t\le1/10\), so every finite union
of any number of its carrier arcs is covered, even with independently chosen
parameters on different arcs. In particular, adding points **on this same
carrier**, splicing chains on it, removing its rotational symmetry, and
changing the radius selected at the endpoint cannot yield an all-rich set.

This does not rule out a point added off the carrier, a change of the carrier
itself, a different incidence assignment in the plane, or any general convex
polygon. An unrestricted extraction theorem that would place a hypothetical
counterexample in this carrier is neither proved nor assumed.

## Replay

`python verify/symbolic_checks.py` independently expands the coordinates,
checks the six distance and derivative formulas, the endpoint identities,
and the polynomial factorizations used above. Its algebra checks are not a
substitute for the written interval inequalities and endpoint counting.

Provenance: the definition of \(z(t)\) and the original recurrence are in
`davidiach/erdos97`,
`incoming/unbounded-six-exception-family-2026-09-06/README.md`.
