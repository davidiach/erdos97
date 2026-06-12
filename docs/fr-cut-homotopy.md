# Fishburn-Reeds cut-matrix mixed-radius homotopy

Status: `FAILED_APPROACH` / `NUMERICAL_EVIDENCE`.

This note records a 2026-06-09 numerical homotopy probe based on a decimal
transcription of the Fishburn--Reeds 20-point `k=3` table. It is not an exact
Fishburn--Reeds coordinate certificate, not a proof, and not a counterexample
candidate.

The script is:

```bash
python scripts/fr_cut_homotopy.py
```

The imported run artifacts are:

```text
data/runs/fr_cut_homotopy_2026-06-09/FR20_cutmatrix_nearest4_mixed_radius_homotopy_20260609T224640Z_seed97333.json
data/runs/fr_cut_homotopy_2026-06-09/FR20_cutmatrix_nearest4_mixed_radius_homotopy_20260609T224751Z_seed97444.json
```

The larger archive also contained early same-seed warmup runs. They were not
imported because these two artifacts capture the useful outcomes without
duplicating weaker session provenance.

## Setup

The decimal table is interpreted as two 10-point classes

```text
A_i = (-x_i, y_i), labels 0..9
B_i = ( x_i, y_i), labels 10..19
```

using the 30-edge Fishburn--Reeds cut matrix as the `t=0` three-witness seed.
For each center, the `nearest` augmentation adds the closest non-edge across
the cut as a fourth witness. The homotopy then tracks from the three-witness
cut-matrix equations toward a row-wise mixed-radius four-witness system with
independent per-center radii.

At every accepted path point, strict convexity margin, minimum edge length, and
minimum pair distance are checked before residual quality is interpreted.

## Imported Outcomes

The `seed97333` run is the clearest collapse diagnostic. It terminates before
leaving `t=0`:

```text
termination:              convexity_collapse
best full4 RMS residual:  1.1255038974842717e-2
best full4 max spread:    8.21074954883163e-2
convexity margin:         1.5158141958273918e-7
minimum edge length:      4.145366745006794e-3
```

The `seed97444` run reaches `t=1`, but only with poor four-witness residuals:

```text
termination:              reached_t1
final full4 RMS residual: 7.221496028106647e-2
final convexity margin:   2.5536184469754884e-4
```

Neither run approaches the repo exactification threshold from
`docs/exactification-plan.md`:

```text
max selected-distance spread < 1e-10
convexity margin            > 1e-3
minimum edge length         > 1e-3
minimum pair distance       > 1e-3
independent verifier passes
```

No standalone exact verifier was run and no `COUNTEREXAMPLE_CANDIDATE` is
recorded.

## Interpretation

The useful lesson is negative: the decimal Fishburn--Reeds cut-matrix seed is
an excellent three-witness scaffold, but the nearest fourth-witness
mixed-radius continuation either rides the strict-convexity boundary or reaches
the endpoint with residuals far above candidate scale.

This does not obstruct arbitrary fourth-witness choices, arbitrary cyclic
orders, or exact historical Fishburn--Reeds coordinates. It only records that
this specific cut-matrix augmentation is not a productive counterexample path
under the tested numerical homotopy.
