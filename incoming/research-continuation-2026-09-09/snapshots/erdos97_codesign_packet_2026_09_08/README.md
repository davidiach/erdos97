# Erdős 97: exact off-carrier repair and the cap's own witness burden

**8 September 2026 — research packet, review pending.**

This packet contains a written general extension lemma, two exact
seed-specific cap theorems, an explicit off-carrier construction, and a new
negative control for a proposed proof shortcut. **It does not prove or
disprove unrestricted Erdős Problem #97.** No external mathematical review,
formal Lean proof, published novelty, or accepted repository status change is
claimed.

Repository baseline: `davidiach/erdos97` at
`047d05149382e48b602b292df4b8fc9e2da560bb` (merged PR #942).

## Results

1. **Any finite set of old vertices can be repaired.** In a finite strictly
   convex polygon, any chosen `k` old vertices can be made four-rich by adding
   at most `3k` vertices while retaining every old vertex in strict convex
   position. The new vertices need not be rich. This is an all-size written
   lemma, not an extrapolation from numerical samples.
2. **A sharp nine-point repair for the nine-point seed.** Keep the exact
   nine-point member of the six-exception family fixed. Repair its six good
   vertices at their existing maximum-multiplicity radii. At least nine new
   vertices are necessary, even allowing arbitrary off-carrier positions.
   The explicit 18-point construction attains that bound: all nine old
   vertices have maximum multiplicity four; all nine new vertices have
   maximum multiplicity two. Every added point is off the old carrier.
3. **Every new rich cap vertex needs at least two cap witnesses.** For that
   fixed seed, any genuinely new point in a strictly convex extension has at
   most two old vertices at any one distance. This applies to caps of any
   finite size, without symmetry or prescribed radii for their new vertices.
   The certificate exhausts all 84 old triples and their 64 distinct
   circumcenters.
4. **Four-rich middle-witness rows can have a cycle, even with two closer
   points.** A second exact convex nine-point set has three four-rich
   centers whose middle-witness arrows contain a directed triangle. At
   radius one, every one of its nine vertices has exactly two strictly
   closer points. The other six vertices have maximum multiplicity two.
   Thus the control does not refute a lemma that truly requires every
   vertex to be rich.

The number of good vertices in Result 2 increases from six to nine. It is
not an improvement in exception count and not an all-rich counterexample.
Its contribution is a sharp, exactly checked repair operation and a precise
constraint on what the added vertices must do themselves.

Read **[proofs.md](proofs.md)** for the statements, full extension argument,
explicit coordinates, certificate interpretation, and logical limitations.
Read **[frontier.md](frontier.md)** for the resulting research boundary.

## Exact replay

Python 3.10+; the following commands use only the standard library:

```sh
python generate_certificates.py
python verify.py
python oracle.py
python -m unittest -v test_research.py
```

The generator's default mode checks byte-for-byte reproducibility without
writing. Use `--write` only for intentional regeneration. The two exact
checkers do not invoke the numerical search.

The primary checker uses exact arithmetic in `Q(sqrt(721))` and quadratic
extensions. The separate oracle uses flattened polynomial arithmetic and
rational square-root enclosures. It imports none of the primary arithmetic,
geometry, generator, or verifier modules. These are separate implementations
from the same research session, **not external independent review**.

Fresh checks pass 31 tests, all 84 circumcenter cases, all 30 real branches
from 15 circle pairs, and 414 strict supporting-half-plane signs across the
three principal configurations. See `data/verification.json`,
`data/oracle_report.json`, and `validation.json`.

## Numerical co-design attempt

`exploratory/` preserves eight bounded searches at 12, 15, and 18 vertices.
Two begin at independently perturbed versions of the exact 18-point repair.
All coordinates can move, and witness tables can change between stages.
Integer-label preflight rejects three-common-witness and direct strict
Kalmanson contradictions before optimization. Hard convexity, separation,
centroid, and scale constraints are included in the final search version.

No near-zero all-rich realization was obtained. This is neither an
infeasibility certificate nor an exhaustive search. Exact mathematical
results above do not depend on those runs.

## Repository scope

This is a standalone packet. No repository files, accepted claims, or branch
refs were changed, and no PR was opened. Repository-wide `make verify-fast`,
`make verify-artifacts`, and Lean builds were not run. Direct Git access
failed DNS resolution; connected GitHub reads succeeded. The scoped checks
above are not a substitute for those repository gates.
