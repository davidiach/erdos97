# n=9 Reviewer Dossier

Status: `REVIEW_DOSSIER_ONLY`.

This note explains `metadata/n9_review_dossier.yaml` and
`scripts/check_n9_review_dossier.py`. The dossier is a checked review worksheet
for the compact `n=9` harness. It does not prove Erdos Problem #97, does not
prove `n=9`, does not claim a counterexample, does not complete independent
review, and does not update the official/global status.

## Purpose

The route manifest, review-gate ledger, and evidence matrix are useful as
machine-readable contracts, but a reviewer also needs one coherent worksheet.
The dossier checker assembles those contracts into a single view:

- the compact command surface;
- the open mathematical and infrastructure gates;
- the output-invariant evidence records;
- the allowed acceptance outcomes;
- the decision fields a written review should fill in.

## Commands

Validate the dossier contract:

```bash
python scripts/check_n9_review_dossier.py --check --summary-json
```

Render the Markdown worksheet to stdout:

```bash
python scripts/check_n9_review_dossier.py --markdown
```

The Markdown renderer does not write a generated artifact. It is an on-demand
review aid so the source contracts remain the source of truth.

## Boundary

The dossier can make a review easier to run, but it cannot replace the review.
In particular, the worksheet keeps all of these open until a human reviewer
accepts or rejects them in writing:

- A6/A7 source-frontier enumeration;
- A8 vertex-circle strict-edge geometry;
- A10 quotient obstruction replay;
- B1/B2 exterior-turn geometry;
- B3/B4 turn-packing arithmetic replay;
- stored-input Kalmanson corroboration;
- Lean compilation on a machine with Lake installed;
- independent review itself.

Only `accepted_vertex_circle_route` or `accepted_turn_route`, recorded in a
separate source-of-truth PR after review, could support a repo-local finite-case
`n=9` status update. Neither outcome would prove the general problem.
