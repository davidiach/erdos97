# Symmetric two-orbit reduction notes

Trust label: `EXACT_OBSTRUCTION` for the restricted symmetry classes below.
This is not a proof of Erdos Problem #97 and is not a counterexample.

## Scope

This note records a small symmetry-focused reduction. It covers only:

- strictly convex configurations invariant under a full `C_k` rotation with
  `k >= 3`;
- at most two noncentral rotation orbits in the vertex set;
- the separate case of at most three concentric circles whose common center is
  outside the convex hull.

It does not cover `k=2`, mirror-only symmetry, partial orbits, three or more
noncentral orbits, arbitrary perturbations of a symmetric ansatz, or general
Erdos Problem #97.

## Per-circle cap

Fix a center vertex `p`. On any circle centered at the rotation center `O`,
the witnesses at one fixed distance from `p` lie in the intersection of two
circles: the `O`-circle and the circle centered at `p`. That intersection has
at most two points.

Therefore, if a bad row uses vertices from at most two concentric noncentral
rotation orbits, the four equal-distance witnesses must split as `2+2` across
the two orbits. A one-orbit `C_k` configuration is impossible by the same cap.

## Phase alignment

Put the center vertex `p` on the ray angle `0`. Two witnesses on the same
rotation orbit are equidistant from `p` exactly when their angular positions
are symmetric about the line through `p` and `O`. Since orbit angles are spaced
by `2*pi/k`, the phase of a second orbit is forced into one of two classes
modulo `2*pi/k`:

```text
same-ray phase:      delta = 0
half-step phase:     delta = pi/k
```

The same-ray phase cannot give two vertex orbits: the smaller-radius point on
each ray lies on the segment from the rotation center to the larger-radius
point on that ray, hence inside the larger regular orbit's convex hull. Thus a
strictly convex two-orbit candidate must be in the half-step phase class.

So every covered two-orbit candidate reduces to the alternating two-radius
regular family:

```text
p_{2j}   = R exp(2*pi*i*j/k),
p_{2j+1} = S exp(2*pi*i*(j+1/2)/k).
```

For `k >= 4`, `docs/two-orbit-radius-propagation.md` and the checker
`alternating_two_radius_family_summary(k)` prove that this family has strictly
ordered paired offsets throughout the strict convexity interval. No vertex can
have four equal-distance witnesses.

For `k = 3`, the half-step family is an alternating hexagon. With `R=1` and
`b=S/R`, strict convexity requires

```text
1/2 < b < 2.
```

From an even vertex, the same-orbit witness pair has squared distance `3`.
The only possible symmetric pair on the other orbit has squared distance
`1 + b^2 - b`, and

```text
3 - (1 + b^2 - b) = (2 - b)(b + 1).
```

This can vanish only at the non-strict endpoint `b=2` or at the irrelevant
negative value `b=-1`. Thus the `k=3` boundary case is also excluded inside
the strict convexity interval.

## Direct gear-equation certificate

The 2026-06-09 research-pass archive also supplied a direct trigonometric
certificate for the same half-step family. It is worth recording because it
does not rely on scanning every adjacent paired-offset gap.

Scale the larger radius to `1`, write the smaller radius as `rho`, and set

```text
h = pi/k.
```

In the strict alternating gear window,

```text
cos h < rho < 1.
```

For a larger-orbit vertex at angle `0`, a same-orbit symmetric pair has even
angular offset

```text
delta = 2a h,       0 < delta < pi,
```

and a smaller-orbit symmetric pair has odd half-step offset

```text
epsilon = (2b+1)h,  0 < epsilon < pi.
```

Equating those two squared distances gives

```text
rho^2 - 2 rho cos(epsilon) + 2 cos(delta) - 1 = 0.
```

Since `cos h < rho < 1`, write `rho = cos x` with `0 < x < h`. Rearranging
the gear equation gives

```text
cos(delta) - cos(epsilon)
  = (1/2) sin^2 x - cos(epsilon) (1 - cos x).
```

The right-hand side has absolute value strictly less than

```text
(1/2) sin^2 h + (1 - cos h)
  = (1 - cos h)(3 + cos h)/2
  < 2(1 - cos h)
  = 4 sin^2(h/2).
```

The parity of `delta/h` and `epsilon/h` forces
`(delta-epsilon)/2` to be a nonzero odd multiple of `h/2`, while
`(delta+epsilon)/2` lies between `3h/2` and `pi - 3h/2`. Hence

```text
|cos(delta) - cos(epsilon)|
  >= 2 sin(3h/2) sin(h/2).
```

For `k >= 3`, put `t = h/2 <= pi/6`. Then

```text
sin(3t) = sin(t)(3 - 4 sin^2 t) >= 2 sin(t),
```

so

```text
2 sin(3h/2) sin(h/2) >= 4 sin^2(h/2).
```

The same expression would therefore have to be both at least
`4 sin^2(h/2)` and strictly less than `4 sin^2(h/2)`, a contradiction.

## Radius-ratio bound

The half-step reduction also gives a reusable necessary convex-hull bound. If
one orbit has radius `R_max` and a smaller half-step orbit point is still a
strict vertex, then it must lie past the side of the larger regular `k`-gon:

```text
R_min > R_max*cos(pi/k).
```

The checker records the closed necessary form

```text
R_min >= R_max*cos(pi/k).
```

This is only a local vertex-condition bound. It is not sufficient for
realizability and does not imply any global obstruction.

## Exterior-center concentric circles

If the common center `O` of concentric circles lies outside the convex hull,
all vertex rays from `O` lie in an open angular semicircle. Choose an angularly
extreme vertex `p`. If the configuration uses at most three concentric circles,
then four equal-distance witnesses for `p` force two witnesses onto the same
circle by the pigeonhole principle.

But a same-circle equal-distance pair from `p` is symmetric about the line
through `O` and `p`. For an angularly extreme vertex, such a nontrivial pair
would place one witness beyond the extreme ray, contradicting the choice of
`p`.

Hence no configuration in at most three concentric circles with exterior common
center is a counterexample. This says nothing about four or more concentric
circles, or about the case where the common center lies inside the convex hull.

## Reproducible checks

The verifier surface is in
`src/erdos97/two_orbit_radius_propagation.py`.

Useful commands:

```bash
python scripts/check_two_orbit_radius_propagation.py \
  --radius-ratio \
  --k 3 \
  --k-max 12 \
  --assert-radius-ratio

python scripts/check_two_orbit_radius_propagation.py \
  --gear-equation \
  --k 3 \
  --k-max 12 \
  --assert-gear-equation

python scripts/check_two_orbit_radius_propagation.py \
  --two-orbit-reduction \
  --k 3 \
  --k-max 12 \
  --assert-two-orbit-reduction

python scripts/check_two_orbit_radius_propagation.py \
  --concentric-outside \
  --circle-count 3 \
  --assert-concentric-outside
```

The JSON status strings are:

```text
exact_necessary_radius_bound_not_general_proof
exact_gear_equation_obstruction_not_general_proof
exact_reduction_to_alternating_family_obstruction_not_general_proof
exact_exterior_center_obstruction_not_general_proof
```

These status strings are intentionally scoped. They must not be read as an
`n=9` result, a global theorem, or a counterexample claim.
