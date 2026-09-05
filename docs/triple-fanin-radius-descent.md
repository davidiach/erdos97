# Triple-fan-in radius descent

Status: `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`.

This note strengthens the fan-in analysis in
`docs/sparse-minimum-distance-forest.md`. It proves a quantitative radius
ordering whenever three equal-radius centres share one non-boundary witness.
It is not a proof or disproof of Erdős Problem #97 and not a source-of-truth
status update.

## 1. General asymmetric statement

Let a strictly convex polygon contain four distinct vertices

\[
T,Y_1,Y_2,Y_3
\]

in that cyclic order, after reversing orientation if necessary. Fix `R>0` and
assume

\[
|TY_1|=|TY_2|=|TY_3|=R.                                \tag{1}
\]

Assume also that:

1. `T,Y_1,Y_2,Y_3` are pairwise nonconsecutive on the polygon boundary;
2. the boundary side at `T` entering the arc from `Y_3` to `T` has length
   `a>0`, while the boundary side at `T` leaving toward `Y_1` has length
   `b>0`;
3. the boundary side incident to either side of every `Y_i` has length `R`.

Then:

> **Asymmetric triple-fan-in inequality.**
>
> \[
> \left(\frac{R}{R+a}\right)^2
> +\left(\frac{R}{R+b}\right)^2>1.                     \tag{2}
> \]

In particular, with

\[
c=\sqrt2-1,
\]

at least one of `a,b` is strictly smaller than `cR`.

### Proof

Let

\[
\alpha_1=\angle Y_1TY_2,
\qquad
\alpha_2=\angle Y_2TY_3.
\]

All three rays lie in the open interior-angle cone at the strictly convex
vertex `T`, in boundary order. Hence

\[
\alpha_1>0,\quad \alpha_2>0,\quad
\alpha_1+\alpha_2<\pi.                                 \tag{3}
\]

Let `sigma_0,sigma_1,sigma_2,sigma_3` be the sums of the exterior turns at the
vertices strictly inside the four boundary arcs

\[
T\to Y_1,\quad Y_1\to Y_2,\quad
Y_2\to Y_3,\quad Y_3\to T.
\]

The two middle arcs begin and end with distinct boundary sides of length `R`
by the pairwise nonconsecutiveness hypothesis, so each
has total length at least `2R`. Since the chord `Y_iY_{i+1}` has length

\[
2R\sin(\alpha_i/2),
\]

the standard projection estimate gives

\[
\sigma_i\ge\pi-\alpha_i
\qquad(i=1,2).                                         \tag{4}
\]

The first arc contains one side of length `b` at `T` and one side of length
`R` at `Y_1`; these are distinct because the endpoints are not adjacent.
Thus its total length is at least `R+b`. From the chord equality
`|TY_1|=R`, projection gives

\[
\sigma_0\ge
2\arccos\left(\frac{R}{R+b}\right).                    \tag{5}
\]

Likewise,

\[
\sigma_3\ge
2\arccos\left(\frac{R}{R+a}\right).                    \tag{6}
\]

Equations (4) and (3) imply

\[
\sigma_1+\sigma_2
\ge2\pi-(\alpha_1+\alpha_2)>\pi.                       \tag{7}
\]

The four open-arc turn sums omit the positive exterior turns at
`T,Y_1,Y_2,Y_3`, so their total is strictly less than `2pi`. Combining this
with (5)--(7) yields

\[
\arccos\left(\frac{R}{R+a}\right)
+
\arccos\left(\frac{R}{R+b}\right)
<\frac\pi2.                                            \tag{8}
\]

Put

\[
x=\frac{R}{R+a},\qquad y=\frac{R}{R+b}.
\]

Both numbers lie in `(0,1)`. For such `x,y`, inequality (8) is equivalent to

\[
x^2+y^2>1.
\]

Indeed, the two arccosines lie in `(0,pi/2)`, and positivity of the cosine of
their sum is equivalent to

\[
xy>\sqrt{1-x^2}\sqrt{1-y^2};
\]

squaring gives `x^2+y^2>1`. This proves (2).

If both `a,b` were at least `(sqrt(2)-1)R`, then both `x,y` would be at most
`1/sqrt(2)`, contradicting their strict squared-sum inequality. `QED`

## 2. Alternating radius-level corollary

Use the alternating boundary-neighbour setup

\[
E_0,Q_0,E_1,Q_1,\ldots,E_{m-1},Q_{m-1},
\]

where the complete rich class at each `E_i` contains its two boundary
neighbours at radius `rho_i`.

Fix a radius value `R`, and suppose one polygon vertex `T` is an extra
radius-`R` witness for three centres in

\[
X_R=\{E_i:\rho_i=R\}.
\]

The three source centres are pairwise nonconsecutive and all have their two
incident sides of length `R`. Since `T` is extra at all three, it is adjacent
to none of them, so the hypotheses above hold.

- If `T=E_j`, both incident sides at `T` have length `rho_j`. Therefore

  \[
  \rho_j<(\sqrt2-1)R.                                  \tag{9}
  \]

- If `T=Q_j`, its incident boundary sides have lengths `rho_j` and
  `rho_{j+1}`. Therefore

  \[
  \min(\rho_j,\rho_{j+1})<(\sqrt2-1)R.                 \tag{10}
  \]

Thus every triple-fan-in target identifies an `E`-centre (the target itself
or a boundary neighbour) whose selected boundary radius drops by the uniform factor `sqrt(2)-1`.

## 3. Consequences

### Minimum-level cap two

If `R` is the minimum selected radius among all `E_i`, equations (9)--(10) are
impossible. Hence no vertex can be an extra radius-`R` witness for three
minimum-level centres. This independently recovers the minimum-level
extra-target cap of two from `docs/radius-level-linear-forest.md`.

### No triple-fan-in radius cycle

Create a directed dependency from a radius level `R` to a radius level `S`
whenever a triple-fan-in target at level `R` selects the target centre itself
or an adjacent centre of radius `S` as supplied by (9) or (10). Every such edge obeys

\[
S<(\sqrt2-1)R.
\]

Therefore the triple-fan-in dependency graph is acyclic. Along a directed path
of length `k`, the radii satisfy

\[
R_k<(\sqrt2-1)^kR_0.
\]

This is a genuine metric descent rather than an incidence-only ordering.

### Capacity interpretation

At a fixed level `R`, the general fan-in lemma permits at most three source
centres per target. The present result divides the targets into two classes:

- targets that neither are nor are adjacent to an `E`-centre of radius below
  `(sqrt(2)-1)R` have capacity at most two;
- capacity three is possible only by paying for a uniformly smaller radius at
  the target centre itself or at an adjacent `E`-centre.

This supplies a natural charging rule for future global counting arguments.

## 4. Boundary of the result

The argument requires all three source incidences to be non-boundary
incidences. If `T` is a boundary neighbour of one source, one end detour may
contain only one side and the coefficient in (2) changes.

The source vertices must also be pairwise nonconsecutive: otherwise a middle
arc can be a single side of length `R`, and the `2R` detour estimate used in
(4) does not follow. Alternating `E`-centres satisfy this automatically.

The result also says nothing directly about targets receiving only one or two
incidences. A global proof still needs to control those low-fan-in exports or
to force enough triple-fan-in targets for the descent to iterate.

Finally, the larger extraction gap remains: an arbitrary hypothetical
counterexample has not been shown to supply an alternating family whose rich
classes all contain both boundary neighbours.

## 5. Exact replay target

The companion arithmetic replay records the equivalent threshold identities

```text
acos(x)+acos(y)<pi/2  iff  x^2+y^2>1,
2/(1+s)^2>1          iff  s<sqrt(2)-1.
```

Run:

```bash
python scripts/check_radius_level_advanced_arithmetic.py \
  --max-cycle-length 512 \
  --assert-expected \
  --summary-json
```

The trigonometric projection and boundary-order argument above remain
review-pending paper mathematics rather than a formal proof object.
