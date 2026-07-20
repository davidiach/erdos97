# Five-orbit `C3` regular-tournament obstruction

Status: `LEMMA` draft / exact restricted-pattern obstruction (review pending).

This note exactly rules out the natural reciprocal-free continuation of the
four-orbit construction in `docs/four-c3-generic-orbit-obstruction.md`.  It is
not a proof of Erdos Problem #97, not a counterexample, and not an exclusion
of all configurations made from five equilateral-triangle orbits.

## Statement

Let `omega = exp(2*pi*I/3)`.  For five nonzero complex numbers `z_i`, indexed
modulo `5`, define five concentric equilateral-triangle orbits

```text
T_i = {z_i, omega*z_i, omega^2*z_i}.
```

Assume the five orbits are pairwise distinct.  Suppose that, at a
representative `z_i`, a selected four-tie consists of

- the two other points of `T_i`;
- one point of `T_{i+1}`;
- one point of `T_{i+2}`.

The witness rotations may be chosen independently in every row.  Then the ten
selected singleton equalities cannot all hold.

Equivalently, the reciprocal-free regular tournament on five orbit labels is
not realizable by own-pair rows.  The proof uses no convexity: it is a metric
obstruction for this selected pattern.

## Gain normalization

The two orbit-mates of `z_i` are at squared distance `3*abs(z_i)^2`.  Hence a
singleton witness `omega^g z_j` is in the same row exactly when

```text
abs(1 - omega^g*z_j/z_i)^2 = 3.                 (1)
```

Let

```text
C = {x in C : abs(1-x)^2 = 3},
q_i = z_{i+1}/z_i.
```

Write `a_i` for the gain on the step-1 arc `i -> i+1`, and put

```text
x_i = omega^a_i q_i.
```

Equation (1) says `x_i in C`.  Since `product(q_i)=1`,

```text
product(x_i) = Omega,                            (2)
```

where `Omega` is a cube root of unity.  In particular its modulus is one.

After absorbing the two adjacent step-1 gains, the step-2 arc `i -> i+2`
has an adjusted gain `c_i in {0,1,2}` and says

```text
omega^c_i x_i x_{i+1} in C.                     (3)
```

Thus the usual `3^6` gain quotient is represented by the five adjusted gains
`c_i` and the product gain `Omega`.  We will not need to enumerate them.

## Circle-product lemmas

### Zero-gain lemma

If `x,z,xz` all belong to `C`, then

```text
abs(xz) >= 1.
```

Equality forces `x,z` to be cube roots of unity.

Proof.  The circle equation gives the exact conjugation rule

```text
conj(w) = (w+2)/(w-1),  w in C.                 (4)
```

Apply (4) to `x`, `z`, and `p=xz`.  Comparing
`conj(p)=conj(x)conj(z)` and clearing denominators gives

```text
p*(x+z) = 2.                                    (5)
```

Put `R=abs(p)>0`.  From the circle equation for `x,z`, equation (5), and the
circle equation for `p`,

```text
abs(x)^2 + abs(z)^2
  = 2*Re(x+z) + 4
  = 4*Re(1/p) + 4
  = 6 - 4/R^2.
```

The arithmetic-geometric mean inequality gives

```text
6 - 4/R^2 >= 2*abs(x)*abs(z) = 2R,
```

so

```text
R^3 - 3R^2 + 2
  = (R-1)*(R^2-2R-2) <= 0.                      (6)
```

Also `p in C` implies `R <= 1+sqrt(3)`.  If `0<R<1`, both factors in (6) are
negative, contradicting (6).  Hence `R>=1`.

If `R=1`, the equations `p in C` and `abs(p)=1` give
`p in {omega,omega^2}`.  The quadratic with roots `x,z`, using (5), is

```text
lambda^2 - (2/p)*lambda + p = 0.
```

For `p=omega` this is `(lambda-omega^2)^2`, and for `p=omega^2` it is
`(lambda-omega)^2`.  This proves the equality statement.

### Primitive-gain lemma

Let `x,z in C`, and let `eta` be `omega` or `omega^2`.  If `eta*x*z in C`,
then either one of `x,z` is a cube root of unity, or

```text
x*z = -2.                                       (7)
```

Proof.  Use the real-projective parametrization

```text
X(t) = 1 + sqrt(3)*(1+I*t)/(1-I*t),
t in R union {infinity},
```

of `C`, and put `a=2+sqrt(3)`.  Direct substitution and exact factorization
give, up to nonzero factors,

```text
omega*X(t)*X(u) in C
  iff (t+a)*(u+a)*(t*u-a) = 0,

omega^2*X(t)*X(u) in C
  iff (t-a)*(u-a)*(t*u-a) = 0.                  (8)
```

Here

```text
X(a)=omega,  X(-a)=omega^2,
X(t)*X(a/t)=-2.                                 (9)
```

Equations (8)-(9), with the projective limiting convention when a parameter
is zero or infinity, prove the lemma.

## Product contradiction

Put

```text
p_i = x_i*x_{i+1}.
```

If `c_i=0`, the zero-gain lemma gives `abs(p_i)>=1`.  Equality would make an
`x_i` a cube root of unity.  Since `x_i` differs from
`q_i=z_{i+1}/z_i` only by a cube root, this would make `T_i=T_{i+1}`.
Pairwise distinctness therefore strengthens the conclusion to

```text
abs(p_i) > 1.
```

If `c_i` is primitive, the primitive-gain lemma and the same distinctness
argument force `p_i=-2`, so `abs(p_i)=2>1`.

Every one of the five factors consequently has modulus greater than one.  On
the other hand, equation (2) gives

```text
product(p_i) = product(x_i)^2 = Omega^2,
```

whose modulus is one.  This contradiction proves the statement for every
gain assignment at once.

## Consequence for five generic orbits

Suppose five pairwise distinct generic `C3` orbits have own-pair rich rows,
each completed by singleton witnesses from two distinct supplier orbits.
Choose two suppliers per orbit.  The resulting directed graph has outdegree
two at every label.

If it contains a reciprocal pair, the reciprocal-supplier lemma in
`docs/four-c3-generic-orbit-obstruction.md` forces the two orbits to coincide.
If it has no reciprocal pair, its ten arcs orient all ten unordered pairs on
five labels.  It is therefore a regular tournament on five vertices, which is
isomorphic to the cyclic tournament used above.  The product obstruction
kills this case too.

Consequently a 4-bad union of five generic `C3` orbits, if one exists, must
use a four-cross-singleton row at least one orbit.  This is the precise row
shape not covered by the two `C3` obstruction notes.

The strongest version of that escape, in which all five rows are
four-cross-singleton rows and all ten mutual gain-pairs are nonreciprocal, is
ruled out in `docs/five-c3-all-cross-nonreciprocal-obstruction.md`.  Systems
with a reciprocal mutual gain-pair and mixed own-pair/all-cross systems
remain open.

## Relation to the convex-body 15-gon

The Barany--Roldan-Pensado boundary construction discussed in
`docs/brp-boundary-vertexization-probe.md` starts with four concentric `C3`
orbits and inserts a fifth, so it motivates exactly this symmetry class.  Its
centered circles are rich in intersections with polygon **edges**, however;
the intersections need not be vertices.  The present product obstruction
therefore neither contradicts that construction nor extracts a finite
counterexample from it.  It says instead that a direct five-orbit
vertexization cannot give every orbit an own-pair-plus-two-singletons row.  A
successful discrete extraction would have to enter one of the row shapes
left open below.

## Exact replay

The companion checker verifies the conjugation factor, the two primitive
factorizations, the special parameter values, and the product identity:

```bash
python scripts/check_five_c3_tournament_obstruction.py --assert-expected --json
```

The checker is an exact algebra replay of the proof, not a numerical search.

## Scope boundary

For five generic `C3` orbits, a four-tie need not contain the center's own
pair: four singleton witnesses can come from the four other orbits.  This
note does not cover that row shape.  It also does not cover half-step
cross-pair rows, partial orbits, different rotation centers, or arbitrary
strictly convex polygons.
