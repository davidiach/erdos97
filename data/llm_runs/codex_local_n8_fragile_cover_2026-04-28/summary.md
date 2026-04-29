# n=8 fragile-cover follow-up, 2026-04-28

Status: research artifact only. This is an incidence-level finite check, not a
metric realization certificate and not a proof of the global problem.

## Main result

The repaired fragile-cover lemma does not add a new incidence-only obstruction
to the existing n=8 survivor classes.

For each of the 15 reconstructed n=8 selected-row survivor classes, there is a
subset of rows that covers all eight vertices. If those rows are allowed to be
the fragile centers, the fragile-cover condition is satisfied.

The minimum number of fragile centers needed to cover is:

```text
2 fragile centers: 6 classes
3 fragile centers: 9 classes
```

No class requires more than three possible fragile rows at the incidence level.

## Added tooling

`scripts/analyze_n8_fragile_covers.py` loads
`data/incidence/n8_reconstructed_15_survivors.json` and computes row-subset
cover statistics for every survivor class.

This answers a narrow question:

```text
Does fragile-cover eliminate any n=8 full selected-row incidence survivor if
any selected row is eligible to be fragile?
```

The answer is no.

## Interpretation

Actual fragility is metric data: a center has a unique rich radius and exact
cohort size four. The selected-row incidence matrix records only one chosen
four-cohort per center, so it cannot certify or refute actual fragility.

The next useful condition must therefore involve metric facts about uniqueness
of a rich radius, not merely the existence of a covering subset of selected
rows.
