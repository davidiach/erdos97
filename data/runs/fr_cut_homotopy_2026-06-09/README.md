# Fishburn-Reeds cut homotopy imports

These JSON files are selected numerical artifacts from the 2026-06-09
Fishburn--Reeds cut-matrix mixed-radius homotopy session.

They are failed-route diagnostics only. The source archive also contained
earlier same-seed warmup runs, which were not imported because these two files
capture the useful collapse and endpoint-degradation outcomes.

Reproduce fresh runs with:

```bash
python scripts/fr_cut_homotopy.py --seed 97333 --paths 1
python scripts/fr_cut_homotopy.py --seed 97444 --paths 1
```

The checked-in JSONs retain the original session output. Interpret them under
the repository exactification threshold in `docs/exactification-plan.md`.
