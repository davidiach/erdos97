# Quarter-cell signed-band preflight

Trust label: `REVIEW_PENDING_DIAGNOSTIC`.

This note is a follow-up to `docs/quarter-cell-closure.md`. It records a
sharper target for the missing exact turn-sign proof. By itself it does not
close the `m = 8, 12, 16` quarter cells; the successor interval certificate in
`docs/quarter-cell-derivative-certificate.md` closes those named finite-m
signed-band cells in the repo-local interval-arithmetic sense.

## Split

In the remaining `m = 0 mod 4` three-orbit quarter cells, the A-row reduction
forces the B- and C-orbit offsets into the boundary bands. Write

```text
T = 2*pi/m,
beta in {d, T-d},
gamma in {e, T-e},
P(r) = (r^2 - 1)/(2r).
```

The radius signs are

```text
P(y) = +/- sin(d),   P(z) = +/- sin(e).
```

The angular order `0 < beta < gamma < T` leaves exactly three band-order cases:

```text
LL: beta=d,   gamma=e,   0 < d < e
LH: beta=d,   gamma=T-e, d,e>0 and d+e<T
HH: beta=T-d, gamma=T-e, 0 < e < d
```

Together with the two radius signs this gives `12` signed cells.

## Boundary killer table

Let

```text
A = sin(T) + cos(T) - 1,
D = 1 - sin(T) - cos(T).
```

For `m >= 8`, so `0 < T <= pi/4`, one has `A > 0` and `D < 0`. Expanding the
three per-period turn determinants at the orbit-coincidence boundary gives a
fixed negative leading term in every signed cell:

| cell | killer turn | leading term |
| --- | ---: | --- |
| `LL_y+_z+` | 1 | `-d*A` |
| `LL_y+_z-` | 1 | `-d*A` |
| `LL_y-_z+` | 2 | `-2*d*e` |
| `LL_y-_z-` | 3 | `(d-e)*A` |
| `LH_y+_z+` | 1 | `-2*d*e` |
| `LH_y+_z-` | 3 | `e*D` |
| `LH_y-_z+` | 2 | `-d*A` |
| `LH_y-_z-` | 2 | `-d*A` |
| `HH_y+_z+` | 1 | `-e*A` |
| `HH_y+_z-` | 3 | `-2*d*e` |
| `HH_y-_z+` | 1 | `-e*A` |
| `HH_y-_z-` | 2 | `(d-e)*D` |

Thus every signed cell approaches the degenerate orbit-coincidence boundary
from the non-convex side at first nonzero order.

## What remains open

The table is only a boundary/tangency statement. The exact missing lemma is:

```text
In each signed boundary-band cell, the listed killer turn is negative
throughout the full strict window.
```

A deterministic floating grid in
`data/certificates/quarter_cell_signed_band_preflight.json` checks that same
fixed killer turn over sampled interiors for `m = 8, 12, 16, 20, 40, 100`; no
sampled violation is found. This is useful evidence and a precise exact target,
not a certificate.

The follow-up certificate
`data/certificates/quarter_cell_derivative_certificate.json` verifies the
required derivative signs over interval boxes for `m = 8, 12, 16`, using this
table's fixed killer turns.

The three mixed-derivative cells of that table (`LL_y-_z+`, `LH_y+_z+`,
`HH_y+_z-`) are now closed for all `m >= 8` at once by
`docs/quarter-cell-mixed-cells-all-m-smt.md`, and the nine
first-derivative cells are closed for all `m >= 8` by the dominance
argument of `docs/quarter-cell-first-derivative-all-m-dominance.md`
(exact corner identities `F_c(T,0,0) = +/-A`, a certified interval
Lipschitz bound, and the scale separation `A ~ sin h` versus band radius
`~ sin^2 h`). The exact missing lemma above is therefore closed in all
twelve signed cells for every `m >= 8`, still conditional on this note's
band split and the A-row reduction remaining review-pending prose.

## Reproduce

```bash
python scripts/check_quarter_cell_signed_band_preflight.py --check --assert-expected --json
```

Regenerate the artifact with:

```bash
python scripts/check_quarter_cell_signed_band_preflight.py --write --assert-expected
```

## Non-claims

- This preflight artifact does not close the `m = 8, 12, 16` quarter cells.
- This preflight artifact does not, by itself, provide an exact certificate for
  `m >= 8`.
- Does not prove an all-`m` quarter-cell obstruction.
- Does not prove Erdos Problem #97 and does not give a counterexample.
