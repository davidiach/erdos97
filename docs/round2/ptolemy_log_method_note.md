# Ptolemy-log method note and regression artifact

Status: exact fixed-pattern certificate format, retained here as a method note.

This is not the round-two headline result. The C17 certificate is useful because it is small, transparent, and easy to audit, but it does not move live pattern status.

## Idea

For a selected row `i`, let the four selected witnesses be `a,b,c,d` in the cyclic/angular order seen from the center. They lie on a circle centered at `i`, so Ptolemy gives:

```text
d_ac d_bd = d_ab d_cd + d_bc d_da
```

Since all distances are positive, each term on the right is strictly smaller than the diagonal product. In log variables this gives two strict linear inequalities:

```text
log d_ac + log d_bd - log d_ab - log d_cd > 0
log d_ac + log d_bd - log d_bc - log d_da > 0
```

As with Kalmanson, selected row equalities quotient distance variables. A positive integer zero-sum combination yields `0 > 0`.

## Included certificate

```text
File: data/certificates/round2/c17_skew_ptolemy_log_certificate.json
Pattern: C17_skew
Offsets: [-7,-2,4,8]
Cyclic order: natural order 0..16
Support size: 17
Weights: all 1
Distance classes: 85
```

## Verifier improvement in this merged package

The original Ptolemy verifier accepted `selected_witness_sets` as the operative data. The merged verifier still does that, but if `offsets` are present it now verifies that the selected witness sets match the offsets. This prevents a mislabeled certificate from passing as a different circulant pattern.

The `row_order()` docstring now makes explicit the convex-polygon fact being used: angular order around a vertex agrees with boundary cyclic order up to rotation.

## Relationship to Kalmanson

The file

```text
data/certificates/round2/c17_skew_kalmanson_from_ptolemy_method_note.json
```

checks as a Kalmanson certificate with the same 17-row support idea. This supports the careful statement that the current Ptolemy-log zero-sum linear certificate is subsumed by Kalmanson after selected-distance quotienting.

Do not state that all possible Ptolemy arguments are globally redundant. Nonlinear or multiplicative Ptolemy uses could be different.
