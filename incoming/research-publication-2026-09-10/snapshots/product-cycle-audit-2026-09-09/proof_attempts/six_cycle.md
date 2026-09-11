# Exact same-upper-half-plane six-cycle: closure succeeds, convexity fails

**Exact nonconvex control, not an Erdos counterexample.** This replaces the
previous six-cycle monodromy experiment's numerical existence evidence with
a specified algebraic example. It is not a theorem that every six-cycle fails.

Let s be the unique real root in (536/1000,537/1000) of

    7s^4-24s^3+44s^2-42s+13=0.

Endpoint signs are opposite and the derivative is strictly negative throughout
that rational interval. The standard-library checker verifies these facts
with rational interval arithmetic, specifying the root without decimals.
Set

    v=(s-2)/2 + i*sqrt(3)*(-5s^2+6s-2)/(6(s-2)),
    zeta=(1+i*sqrt(3))/2,    u=zeta/v^2.

Exact quotient-ring arithmetic at the isolated root verifies

    |v|^2=s, |v-1|^2=3, |u-1|^2=3,
    Im(v)>0, Im(u)>0, |u|^2=1/s^2.

The six multipliers (u,v,v,u,v,v) multiply to zeta^2=omega. The orbit
representatives are

    1, u, uv, zeta, zeta*u, zeta*uv.

Their union contains 18 distinct points, each having its two orbit mates and
the next matched orbit point at its own-side distance (the last edge has gain
one). The checker reconstructs every distance partition: each vertex's actual
maximum multiplicity is exactly THREE, not four.

There are three regular hexagons, of radii 1, 1/s and 1/sqrt(s). The outer
hexagon has radius 1/s. Its inradius is sqrt(3)/(2s); both other radii are
strictly smaller, since 1/2<s<3/4. Thus all twelve remaining points are strictly
interior regardless of their phases. The six actual hull edges have 96
strict supporting-halfplane inequalities against the other sixteen points.
These signs and all 153 distinct pairs are separately checked.

The quotient arithmetic does not assume an unproved irreducibility statement.
Every asserted zero is an exact polynomial reduction modulo the displayed
polynomial, hence vanishes at its root. Every asserted nonzero/sign is separated
by rational interval evaluation in that root's specified real embedding.
Different stored distance classes are explicitly checked to be unequal in the
embedding. No floating residual certifies a zero or a sign.

The original numerical six-by-six product is a separate historical input.
Its factors already have six hull vertices out of eighteen, so its hull
collapse cannot be attributed solely to the product operation. Neither that
observation nor this special algebraic six-cycle excludes other phase choices,
longer cycles, or altered witness graphs.
