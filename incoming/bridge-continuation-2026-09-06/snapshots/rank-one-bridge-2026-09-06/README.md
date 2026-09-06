# One-closer-point bridge for Erdős 97

6 September 2026 · Restricted paper-proof candidate · Independent review pending

**No unrestricted proof or counterexample is claimed.** This packet excludes
an arbitrary-size, variable-radius family and records exact controls for the
next unresolved regime. It does not promote a repository bound or status.

## Result

Let X be a finite strictly convex set. Assign each x a radius rho_x with at
most one other point strictly closer than rho_x. It is impossible for every
x to have four equidistant witnesses at its assigned radius.

More strongly, if Y is the group with smallest assigned radius and m=|Y|,
at most max(0,m-2) members of Y can be four-rich at that radius, even when
witnesses are counted in all of X. The deficit of two is attained in an
exact five-point example with three minimum-radius vertices.

The proof extracts a short pair from four hull witnesses, forces that pair
into the minimum-radius group, proves noncrossing for the resulting
threshold graph, and injects rich centers into its at most m-2 triangular
faces. No conic, symmetry, common-radius, incident-side, independence, or
minimal-counterexample assumption is used.

A consequence is that some vertex has no four-rich radius at or below its
second-nearest distance, with distances counted with multiplicity. This is
not an all-radius conclusion.

## Exact boundary controls

A five-point example refutes the minimum-layer conclusion once two strictly
closer points are allowed. A separate rational eight-point example has two
genuinely four-rich centers, at squared radii 1 and 16/13. Its short-pair
propagation can move to the larger radius. The other six vertices have
maximum multiplicity one, so it is not a counterexample to Erdős 97.

The complete arguments, controls, and quantifier boundaries are in
[proofs.md](proofs.md).

## Replay

Python 3.10 or later. No third-party modules or network access are needed.
Run from this directory:

```sh
python verify.py --check
python -m unittest -v test_bridge.py
```

To regenerate the retained report intentionally:

```sh
python verify.py --write
```

`--check` regenerates the report in memory and requires exact byte equality
with `verification.json`. It does not overwrite the retained report.

## Contents

- `proofs.md`: complete arbitrary-size mathematical arguments and limits.
- `checker.py`: exact rational geometry, radius counts, threshold graph, and
  minimum-layer certificate checks; rejects floating-point geometric input.
- `fixtures.py`: exact rational/algebraic fixture constructors.
- `verify.py`: deterministic geometric and combinatorial regressions.
- `test_bridge.py`: 33 unit tests, including failure and boundary controls.
- `verification.json`: generated certificates, all-distance classifications,
  and regression counters.
- `rank_two_exact_control.json`: retained exact eight-point coordinates.
- `test_output.txt`: recorded test run.
- `validation.json`: final standalone validation record.
- `PROVENANCE.md`: source context, discovery, and review boundaries.
- `MANIFEST.sha256`: SHA-256 digest of each other delivered file.

## Verification scope

The retained report covers 381 geometric fixtures and 12,902 permitted
radius assignments, including 130 assignments with a rich minimum-radius
center. It also checks 861 common-scale threshold graphs and 3,207 convex
crossing quadrilaterals. A separate abstract routine covers 196
triangulations with all 15,726 matching choices for polygon sizes 3–8.

These finite checks do not prove the arbitrary-size theorem; its proof is
in `proofs.md`. The combinatorial routine is a different validation layer,
not independent mathematical review or a second full geometric verifier.
The written geometry has not been formalized. No claim of published novelty
is made.

## Remaining problem

A full counterexample has not been shown to admit one-closer-point rich
radii at every vertex. In fact this packet proves it cannot. Any full
counterexample must have a vertex at which every four-rich radius contains
at least two strictly closer vertices. The exact controls show why simply
relaxing the hypothesis from one closer point to two does not extend the
present proof.
