# Erdős #97: two-closer minimum-layer escape

6 September 2026. **Restricted paper-proof candidates; review pending.**
No unrestricted solution or counterexample, no full variable-radius rank-two
impossibility, no accepted finite-case promotion, and no published novelty
claim.

## Result

For assigned radii with at most two strictly closer vertices at each center,
a fully four-rich minimum-radius layer forces **at least four distinct higher-
radius witness vertices**, each with assigned radius strictly between r and 2r.
When the minimum layer has at least two vertices, it exports at least six
witness incidences. The exact strengthened count is

    U >= 6 + 2*(nontrivial short paths) + 4*(short cycles)

inside that layer.

The proof uses a fixed-radius edge theorem valid at arbitrary size:

    e_r <= 2n-3-p-2c,

where each vertex has at most two neighbors strictly closer than r, and p,c
are the path/cycle component counts of the short-edge graph. It decomposes
edges using empty closed diameter disks and charges two triangulation-ear
resources per nontriangular short cycle. It never assumes that the whole
threshold graph is planar or that its short graph is a forest.

This closes the common-radius two-closer case and the stated variable-radius
symmetric-closeness restriction. It does not close arbitrary variable radii.

## Exact obstruction to naive iteration

A new rational nine-point control has an entirely rich minimum layer and a
higher-radius four-rich center that uses that layer as an essential witness.
Deleting the minimum layer changes the higher center's ALL-RADIUS maximum
multiplicity from four to three. Every assigned radius is an actual third-
nearest distance. Seven vertices of this control are not rich, so it does
not refute a bridge that uses universal four-richness.

See [the complete proof](proofs.md), [the exact return control](return_control.json),
and [all controls](exact_controls.json).

## Replay

Python 3.10+; standard library only:

```sh
python verify.py --check
python oracle.py
python -m unittest -v test_bridge.py
```

To regenerate deterministic data:

```sh
python verify.py --write
```

The main exact regression covers 639 fixture instances, 5,873 fixed-radius
checks, 6,429 deduplicated-per-fixture radius assignments, and 20,379 convex
quadrilaterals. There are 129 fully rich minimum-layer checks, including 33
with multiple minimum centers. All 51 unit tests pass.

A separate combinatorial audit checks 624 triangulations and 259,890 injective
blocked-base assignments through nine cycle vertices. `oracle.py` is a second
representation on the named controls only. These are finite controls, not
independent external mathematical review or a formal all-real proof.

## Files

- `proofs.md`: complete mathematical arguments, controls, and precise gap.
- `geometry.py`: exact rational geometric implementation.
- `fixtures.py`: exact coordinate and radius definitions.
- `verify.py`: deterministic regression and JSON regeneration.
- `combinatorial.py`: separate finite ear-resource audit.
- `oracle.py`: second-representation checks of named controls.
- `test_bridge.py`: defensive and regression tests.
- `verification.json`, `exact_controls.json`, `return_control.json`: generated results.
- `oracle_report.json`, `test_output.txt`, `validation.json`: validation record.
- `PROVENANCE.md`, `manifest.json`: provenance and integrity.

No repository-wide CI, GitHub write, PR, or accepted-status change was made.
