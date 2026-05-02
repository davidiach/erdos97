# Two-orbit radius-propagation obstruction

Trust label: `EXACT_OBSTRUCTION` for this ansatz only. This is not a proof of
Erdos Problem #97 and is not a counterexample.

## Pattern

Fix `t >= 1`, set

```text
m = 4t,   h = pi/m.
```

Consider two concentric regular `m`-gons with half-step offset:

```text
A_j = R exp(2ijh),
B_j = S exp((2j+1)ih),
```

listed in the alternating order

```text
A_0, B_0, A_1, B_1, ..., A_{m-1}, B_{m-1}.
```

The selected four-neighbor pattern is

```text
A_j: A_{j+t}, A_{j-t}, B_{j+t}, B_{j-t-1},
B_j: B_{j+t}, B_{j-t}, A_{j+t}, A_{j-t+1}.
```

This gives `n = 2m = 8t` points.

## Distance equations

By scaling, set `R = 1` and write

```text
x = S/R,   s = sin h.
```

The same-orbit selected vertices are quarter-turns apart, so

```text
|A_j - A_{j +/- t}|^2 = 2,
|B_j - B_{j +/- t}|^2 = 2x^2.
```

For an `A_j` row, the cross-orbit angular offsets are
`+/- (pi/2 + h)`, hence

```text
|A_j - B_{j+t}|^2 = |A_j - B_{j-t-1}|^2
                  = 1 + x^2 + 2x sin h.
```

Matching these to the same-orbit value gives

```text
x^2 + 2x sin h = 1.
```

For a `B_j` row, the cross-orbit angular offsets are `+/- (pi/2 - h)`, hence

```text
|B_j - A_{j+t}|^2 = |B_j - A_{j-t+1}|^2
                  = 1 + x^2 - 2x sin h.
```

Matching these to `2x^2` gives the same equation:

```text
x^2 + 2x sin h = 1.
```

The positive solution is

```text
x = sqrt(1 + sin^2 h) - sin h.
```

Thus the four-distance condition is satisfied exactly inside this ansatz.

## Convexity obstruction

The two alternating signed turns are

```text
det(B_j - A_j, A_{j+1} - B_j) = 2 sin h (x - cos h),
det(A_{j+1} - B_j, B_{j+1} - A_{j+1}) = 2x sin h (1 - x cos h).
```

So strict convexity of the alternating polygon requires

```text
cos h < x < sec h.
```

But the forced ratio satisfies `x < cos h`. Indeed,

```text
x < cos h
<=> sqrt(1 + sin^2 h) < sin h + cos h,
```

and both sides are positive while

```text
(sin h + cos h)^2 - (1 + sin^2 h)
  = 2 sin h cos h
  > 0
```

for `0 < h <= pi/4`.

Therefore the distance equations force every `B_j` turn to be negative. The
inner orbit lies below the convexity threshold; the exact failure mode is
concavity/inliers caused by radius propagation.

As `t -> infinity`,

```text
x = 1 - h + O(h^2),
cos h = 1 - h^2/2 + O(h^4).
```

The first-order inward term in `x` is the obstruction. Convexity needs only a
quadratic radial drop, while the equality equations force a linear radial drop.

## Reproducible checker

The exact checker is implemented in
`src/erdos97/two_orbit_radius_propagation.py`.

Useful commands:

```bash
python scripts/check_two_orbit_radius_propagation.py --t 2 --assert-expected
python scripts/check_two_orbit_radius_propagation.py --t 2 --assert-expected --verify-all-rows
python scripts/check_two_orbit_radius_propagation.py --t 3 --json
```

The checker reports `status: exact_ansatz_obstruction_not_general_proof`.

## Next perturbative test

The exact ansatz is dead, but it is still a good deformation base. The useful
next computation is local, not random:

1. Let `A_j = r_j exp(i alpha_j)` and `B_j = rho_j exp(i beta_j)` near the
   symmetric solution above.
2. Keep the same selected equal-distance equations.
3. Compute the Jacobian of those equations at the symmetric solution.
4. Intersect its kernel with the linearized cone that increases the negative
   `B_j` turns.
5. Look for a rational or algebraic Farkas/stress certificate proving that no
   first-order deformation can make all `B_j` turns positive.

If this first-order obstruction exists, it becomes a reusable
radius-propagation-versus-convexity filter. If it fails, the escaping tangent
direction gives a much better perturbative ansatz than another symmetric
guess.

## Linearized escape diagnostic

The first-order Farkas obstruction does not appear in the checked small
two-orbit cases. The command

```bash
python scripts/check_two_orbit_radius_propagation.py \
  --linearized-escape \
  --t 1 \
  --t-max 5 \
  --assert-linearized-escape
```

solves the numerical LP

```text
J v = 0,
d(turn_q)(v) >= 1 for every currently concave alternating turn q,
minimize ||v||_1.
```

Here `J` is the selected squared-distance equality Jacobian at the exact
symmetric ansatz. The reproducible snapshot is:

```text
t  n   status                   rank  kernel  concave turns
1  8   LINEARIZED_ESCAPE_FOUND  12    4       4
2  16  LINEARIZED_ESCAPE_FOUND  26    6       8
3  24  LINEARIZED_ESCAPE_FOUND  40    8       12
4  32  LINEARIZED_ESCAPE_FOUND  54    10      16
5  40  LINEARIZED_ESCAPE_FOUND  68    12      20
```

This is a `NUMERICAL_LINEARIZED_DIAGNOSTIC`, not an exact proof certificate and
not a counterexample. Its useful interpretation is negative: the symmetric
two-orbit ansatz is not blocked by a first-order tangent-cone certificate of
the simplest kind. Any proof route based on this ansatz needs second-order
information, a stronger convexity cone, or an exact nonlinear obstruction. Any
counterexample route should treat the LP direction as a targeted perturbative
seed rather than as evidence of realizability.
