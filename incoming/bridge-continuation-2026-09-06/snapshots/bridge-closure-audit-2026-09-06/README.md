# Erdős #97: closure-step audit, 6 September 2026

**No solution is claimed.** This packet records the outcome of an attempt to finish the return-dependency bridge. It deliberately separates what is proved from what remains missing.

Read [proofs.md](proofs.md) for a shorter proof of the existing common-radius two-closer obstruction, a conditional local radius-descent corollary, and three exact counterexamples to stronger intermediate statements.

The most consequential negative control is a strictly convex rational 15-point set with at most two closer points at every assigned radius, but **36 assigned witness incidences versus 32 total Gabriel degrees**. A second rational control shows that deleting a rich degree-two Delaunay ear can make another rich vertex good at every radius. A six-point control rejects a middle-edge forest shortcut for three-witness rows only.

None has every vertex four-rich. None refutes an all-rich-specific lemma. The global two-closer bridge and the reduction from unrestricted radii remain unproved.

## Replay

Python 3.10 or later, standard library only:

```sh
python verify.py --check
python -m unittest -v test_audit.py
```

To regenerate the exact report:

```sh
python verify.py --write
```

Coordinates are reconstructed from rational formulas; input floats are rejected. The Gabriel convention uses **closed** diameter disks. Tests are bounded regression, not independent review or formalization of the paper arguments.

## Files

`proofs.md` contains the mathematical argument and claim boundaries. `verify.py` reconstructs all evidence. `verification.json` is its generated exact output. `test_audit.py` and `test_output.txt` contain the tests and recorded result. `manifest.json` records the file hashes.

The repository and previous research packets were not modified, and no PR was opened for this audit.
