# Inversive Incidence Pilot

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This note records a small Mobius/inversion-inspired pilot on the regenerated
`n=9` pre-vertex-circle frontier. It does not claim a proof of `n=9`, a
general proof of Erdos Problem #97, a counterexample, or an independent review
of the exhaustive checker. The official/global status remains falsifiable/open.

## Rule

Fix a pivot vertex `b`. If a selected row centered at `i` contains `b`, then
the selected circle centered at `i` passes through `b`. Inversion around `b`
maps that circle to a line. Therefore the three inverted witnesses in
`S_i - {b}` are collinear.

The pilot keeps only this incidence consequence. It does not construct inverted
coordinates, certify point-line realizability, or translate strict convexity
through inversion.

For each regenerated selected-witness assignment, the checker:

- builds the forced line triples for every pivot;
- merges any two forced lines that share at least two inverted points;
- repeats that merge to closure;
- records whether any pivot produces a larger collinear block or repeated pair.

## Result

Artifact:

```text
data/certificates/n9_inversive_incidence_pilot.json
```

Command:

```bash
python scripts/check_n9_inversive_incidence_pilot.py --assert-expected --write
```

Summary over the 184 regenerated `n=9` assignments:

```text
total pivots:             1656
forced line triples:      6624
closed lines:             6624
compressed pivots:        0
max closed line size:     3
all-collinear pivots:     0
```

Equivalently, every pivot in this frontier has exactly four inversion line
seeds, and no two forced triples for the same pivot share a pair of inverted
points. The line-closure step never produces a line with more than three
points.

## Interpretation

This is useful negative information about the proposed inversion route. The
naive expectation that the `n=9` frontier should become a dense point-line grid
does not show up in the exact selected-witness frontier: the abstract inverted
incidence systems are sparse and pair-disjoint at every pivot.

The pilot therefore does not compete with the vertex-circle or Groebner
obstructions. Its value is as a reusable diagnostic for future frontiers:
larger or less-filtered selected-witness systems with repeated inverted pairs
would be natural candidates for small local collinearity lemmas.

## Guardrails

Do not cite this artifact as:

- a proof of `n=9`;
- a proof of Erdos Problem #97;
- a counterexample or realizability certificate;
- evidence that all inversion approaches fail;
- evidence that point-line incidence bounds apply globally.

The only supported claim is narrower: on the current regenerated `n=9`
pre-vertex-circle frontier, the incidence-only inversion transform produces no
line-compression obstruction.
