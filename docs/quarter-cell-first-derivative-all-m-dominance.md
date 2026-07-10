# Quarter-cell first-derivative cells: all-m dominance closure

Trust label: `EXACT_OBSTRUCTION` (symbolic identities + outward-rounded
interval arithmetic + SMT), scoped to the nine first-derivative signed band
cells of the three-orbit quarter-cell program, for every `m >= 8` at once.
Together with the mixed-derivative artifact
(`docs/quarter-cell-mixed-cells-all-m-smt.md`) this closes **all twelve**
signed band cells for every `m >= 8`, so -- conditional on the
review-pending A-row reduction and boundary-band confinement prose
(`docs/quarter-cell-closure.md`) -- every quarter cell with `m = 0 mod 4`,
`m >= 8` is exactly closed; the `m = 4` quarter cell is closed by the
separate SMT artifact `docs/three-square-m4-exact-closure.md`. This is not
a closure of non-quarter three-orbit branches (screen-grade for `m <= 16`,
open beyond), not `n = 9`, not Erdos Problem #97, and not a counterexample.

## What exactly is certified

In the signed-band split (`docs/quarter-cell-signed-band-preflight.md`):
`T = 2h`, `h = pi/m`, band variables `0 < d, e < delta` with
`sin(delta) = omega = sin(h)^2/(2 cos h)`, offsets `beta in {d, T-d}`,
`gamma in {e, T-e}`, radius signs `P(y) = ys sin d`, `P(z) = zs sin e`. The
nine cells whose stored proof rules use a single first derivative are
closed here: for each cell, the killer turn `F` is strictly negative
throughout the strict cell, for every `m >= 8`.

The proof per cell has four machine-checked ingredients and one elementary
glue argument:

**1. Exact corner identity (sympy, m-uniform).** The required derivative
component `F_c` (`F_d` or `F_e` per the stored rule) satisfies, exactly,

```text
F_c(T, 0, 0) = -A   (eight cells with required sign < 0)
F_c(T, 0, 0) = +A   (HH_y-_z-, required sign > 0)
where A = sin T + cos T - 1.
```

Moreover `A = 2 sin(h) (cos h - sin h)` exactly (verified symbolically), so
`A > 0` and `A` is of order `sin h` on `h in (0, pi/8]` -- while the band
radius is of order `sin^2 h`. This scale separation is the whole mechanism.

**2. Certified Lipschitz bound (interval arithmetic).** Over the fixed box
`T in [0, pi/4]`, `d, e in [0, 2/25]` -- a superset of every band square by
ingredient 3 -- outward-rounded mpmath interval evaluation (80-bit, with a
fixed subdivision recorded in the certificate) certifies

```text
sup |dF_c/dd| + sup |dF_c/de| <= M = 4
```

for every cell (largest certified enclosure about `3.27`; the underlying
sum of separate sups is about `3.03` numerically, so `M = 4` absorbs the
interval dependency inflation with real margin). By the
mean value theorem along `(0,0) -> (d,0) -> (d,e)`,

```text
|F_c(T, d, e) - F_c(T, 0, 0)| <= d sup|dF_c/dd| + e sup|dF_c/de|
                              <= delta * M.
```

**3. Band bounds (z3 + exact rationals).** On the polynomial domain
`ch^2 + sh^2 = 1`, `sh > 0`, `ch > 0`, `2ch^2 - 1 >= 2 sh ch` (exactly
`T <= pi/4`, i.e. `m >= 8`), z3 proves the negations unsatisfiable for:
`ch > sh` (hence `A = 2 sh (ch - sh) > 0`); `omega <= 397/5000`; and the
dominance combination

```text
M^2 sh^2 < 4 (ch - sh)^2 (4 ch^2 - sh^4),      M = 4.
```

With `arcsin(x) <= x / sqrt(1 - x^2)` (elementary: `tan(theta) >= theta`
with `theta = arcsin x`), the band radius satisfies
`delta <= delta_bar := omega / sqrt(1 - omega^2)`; the `omega` bound gives
`delta_bar <= 2/25` in exact rational arithmetic (so the band square sits
inside the interval box of ingredient 2), and the dominance combination is
exactly the cleared form of `(M delta_bar)^2 < A^2`, giving

```text
M * delta <= M * delta_bar < A.
```

**4. Vanishing-boundary identities (sympy, m-uniform).** Per the stored
proof rules: `F(0, e) == 0` for the four `F_d` cells, `F(d, 0) == 0` for
the three edge-`F_e` cells, and the diagonal identity `F(d, d) == 0` for
`LL_y-_z-` and `HH_y-_z-` (geometrically: those substitutions collapse two
polygon points, degenerating the turn).

**Glue.** By 1-3, `|F_c - corner| <= M delta < A = |corner|` on the whole
closed band square, so `F_c` keeps the corner's strict sign there, for
every `T in (0, pi/4]`. Integrating `F_c` from the cell's vanishing
boundary (over `[0, d]`, `[0, e]`, or from the diagonal `e = d` -- forward
into the cone `d < e` for `LL_y-_z-`, backward into `e < d` for
`HH_y-_z-`, where the required sign `F_e > 0` makes `F` negative for
`e < d`) gives `F < 0` throughout each strict cell. QED for the nine
cells, all `m >= 8`.

## Controls and self-tests

- z3 `domain_nonempty` is SAT, and the dominance combination with `M = 6`
  is SAT (the inequality genuinely fails past `M ~ 5.2`), so the `M = 4`
  UNSAT is neither vacuous nor slack-free.
- A deterministic finite-difference lattice ties each symbolic `F_c` to the
  raw geometric turns built from the preflight's point coordinates.
- The exact rational checks record `A`'s factorization, the
  band-inside-box bound, and a sample-point verification of the clearing
  identity behind the dominance combination.
- An embedding spot-check confirms the quarter-cell instances
  `m = 0 mod 4, m in [8, 120]` satisfy the shared z3 domain and band-box
  bounds.

## Commands

```bash
python scripts/check_quarter_cell_first_derivative_all_m_dominance.py --assert-clear
python scripts/check_quarter_cell_first_derivative_all_m_dominance.py --assert-clear \
  --check-artifact data/certificates/quarter_cell_first_derivative_all_m_dominance.json
python -m pytest tests/test_quarter_cell_first_derivative_all_m_dominance.py -q -m "not slow and not exhaustive"
```

The finite-`m` interval certificate
(`docs/quarter-cell-derivative-certificate.md`) is now superseded as the
primary closure for all twelve cells (nine here, three by the mixed-cells
artifact) and retained as an independent finite-`m` cross-check.

## Scope and non-claims

- Covers the nine first-derivative signed band cells, all `m >= 8`;
  with the mixed-cells artifact, all twelve cells and hence -- conditional
  on the review-pending A-row reduction and boundary-band confinement --
  every `m = 0 mod 4, m >= 8` quarter cell. The `m = 4` cell has its own
  SMT artifact.
- Trust roots, all disclosed: sympy symbolic algebra (identities and the
  derivative expressions, numerically cross-checked), mpmath
  outward-rounded interval arithmetic (the Lipschitz bound; float endpoint
  extraction is covered by an explicit `1e-12` safety factor against a
  `2^-52` rounding effect), and z3 NRA UNSAT answers (no independent proof
  object stored).
- Nothing here closes the non-quarter three-orbit branches (screen-grade
  for `m <= 16`, entirely open for `m > 16`), `n = 9`, or Erdos Problem
  #97, produces a counterexample, or changes the official/global status.
