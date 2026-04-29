# Run B: obstruction audit

Status: no counter-scenario survives the fixed-distance check.

## Candidate obstruction

The only apparent way for minimality to fail to imply fragility is:

```text
u has two different rich radii r and s in P,
deleting v drops both rich cohorts below size 4.
```

For deletion of v to drop the cohort at radius r, v must lie in C_P(u,r). For
deletion of v to drop the cohort at radius s, v must lie in C_P(u,s). These two
conditions imply

```text
r = |p_v-p_u| = s.
```

Therefore r and s are the same radius. The obstruction is not geometrically
possible, independent of convexity.

## Other edge cases

1. Could a radius with five or more points drop below four after deleting v?

No. Deleting one point can reduce a fixed-radius cohort by at most one. If the
original size were at least five, the remaining size would be at least four,
contradicting m_u(P-v) <= 3.

2. Could the maximizing radius for u change after deleting v?

Yes, but that does not matter. The proof compares every rich radius of u in P
against the same radius in P-v. It does not assume the maximum radius is
preserved.

3. Does strict convexity enter the fragile-cover proof?

Not directly, except as part of the ambient class and to ensure the deletion is
still interpreted as a convex-position subpolygon. The proof itself is a
finite metric argument.

4. Does the lemma require u to be unique for v?

No. For each v, minimality guarantees at least one witness u. There may be
several.

## Audit conclusion

The fragile-cover lemma is valid as stated. The earlier pilot's fatal-gap claim
was an error caused by overlooking that a fixed deleted vertex has a unique
distance to a fixed center.
