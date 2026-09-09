# Frontier after the two-free closure

9 September 2026. **Review-pending restricted research. No unrestricted solution.**

## Completed new result

For the exact unchanged nine-point seed P, a finite strictly convex rich cap Q
cannot have exactly two points in

    I_P(Q) = {q: every rich radius at q uses at most one point of P}.

The old points are not required to be rich in this exclusion. There is no
symmetry, fixed-radius, carrier, or preselected cap-size assumption.

The geometric reduction has 42 capacity-one old-pair slots and two continuous
free positions. All 4,500 region/support cases close, with 14,621 verified leaves.
Common-radius covers, complete necessary row search, circle-sharing/crossing
constraints, and exact strict-distance cancellations replace the earlier
inconclusive dependency-graph probe. No unresolved case is labelled excluded.

Combining the previous zero- and one-internal-vertex results:

| Internally supported vertices | Rich caps over this fixed seed |
|---|---|
| 0 | Unique next recurrence triangle; six old exceptions stay good |
| 1 | Excluded in the preceding packet |
| 2 | Excluded in this packet |
| 3 | Attained by the known next two recurrence triangles; old exceptions still good |

Therefore an all-rich extension of this seed requires **at least three** such
internally supported new vertices. Their required new witnesses need not
belong to I. This is not a lower bound for arbitrary Erdős97 counterexamples.

## Exact sharpness control

The 15-point control has six new rich vertices, exactly three of which belong
to I. Its full multiplicity census is 3 at maximum 2, 3 at maximum 3, and 9 at
maximum 4. Both checkers certify all 195 supporting signs. It is not all-rich.
The construction was already given by the recurrence; the new contribution
is the two-internal-vertex exclusion and the resulting sharp gap for rich caps.

## Remaining construction obligation

A complete repair must make the old six exceptions rich as well as every
new point. Three internally supported points can exist, but the verified
example does not perform that repair. No exclusion or construction for the
whole class of three-or-more-internally-supported repairs is claimed.

Moving the old coordinates escapes the fixed-seed theorem. No reduction of
an arbitrary all-rich convex polygon to this seed or to these support counts
has been established. The earlier mixed-lens theorem and other restricted
results keep their original scopes; they are not promoted by this packet.

## Trust and publication

Both mathematical replayers pass the complete partition. They are different
implementations written in the same session, not outside expert review or
formalization. Read proof.md and validation.json for exact obligations and
executed commands. The repository baseline is
`047d05149382e48b602b292df4b8fc9e2da560bb`; no repository write, PR, accepted
status change, or published-novelty claim is made.
