# Threefold Pair-Lift Obstruction

Status: `LEMMA` / `FAILED_SEARCH_MECHANISM`.

This note records a narrow obstruction for a natural Danzer-style 3-fold
rotational lift mechanism. It does not rule out all 3-fold symmetric
constructions, does not prove Erdos Problem #97, and does not produce a
counterexample.

## Mechanism

Let

```text
omega = exp(2*pi*i/3).
```

A nondegenerate 3-fold orbit is

```text
O_p = {p, omega*p, omega^2*p},  p != 0.
```

The mechanism considered here tries to make a 4-witness row at each point by
using:

1. the two same-orbit mates, and
2. two points from one other full 3-fold orbit.

Thus for `p = r*exp(i*theta)`, the selected radius is forced to be
`sqrt(3)*r`, the distance from `p` to its two same-orbit mates.

## Lemma

No finite nondegenerate union of 3-fold orbits can be 4-bad by this mechanism.

## Proof

Let

```text
p = r*exp(i*theta),       r > 0,
q = rho*exp(i*phi),       rho > 0.
```

Suppose two points of the orbit `O_q` are both at distance `sqrt(3)*r` from
`p`. If two points of `O_q` are equidistant from `p`, then `p` lies on the
perpendicular bisector of the chord joining those two orbit points. In an
equilateral orbit centered at the origin, the three perpendicular bisectors of
the orbit chords are exactly the three radial lines through the remaining
orbit point. Therefore, after relabeling the orbit `O_q`, either

```text
phi = theta mod 2*pi/3
```

or

```text
phi = theta + pi mod 2*pi/3.
```

In the first case, the two non-corresponding points of `O_q` have squared
distance

```text
r^2 + rho^2 + r*rho
```

from `p`. Setting this equal to the same-orbit squared distance `3*r^2` gives

```text
rho^2 + r*rho - 2*r^2 = 0.
```

The only positive solution is `rho = r`, which means `O_q = O_p`, not a
distinct extra orbit.

In the second case, the two contributing points lie in the opposite radial
orientation, and their squared distance from `p` is

```text
r^2 + rho^2 - r*rho.
```

Setting this equal to `3*r^2` gives

```text
rho^2 - r*rho - 2*r^2 = 0.
```

The only positive solution is `rho = 2*r`.

Thus any distinct orbit that supplies the extra pair for `O_p` under this
mechanism must be the opposite-phase orbit with twice the radius.

In a finite configuration where every orbit uses this mechanism, each orbit
has an outgoing edge to a distinct orbit with twice its radius. Following
outgoing edges in a finite directed graph eventually gives a directed cycle.
Along that cycle the radii are multiplied by `2` at each step:

```text
r -> 2*r -> 4*r -> ... -> 2^k*r.
```

Returning to the original orbit would force `2^k*r = r`, impossible for
`r > 0`.

Therefore this 3-fold same-orbit-plus-one-orbit-pair lift mechanism cannot
produce a counterexample.

## Scope

This obstruction does not rule out every 3-fold symmetric construction. It
only rules out the mechanism where each selected row includes the two
same-orbit mates and gets the two remaining witnesses as an equidistant pair
from one other full 3-fold orbit at that same radius. A different selected
radius, two singleton witnesses from two different orbits, or a non-full-orbit
construction lies outside this note.
