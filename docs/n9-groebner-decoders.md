# n = 9 Gröbner-basis Decoders for F07, F08, F09, F13

Status: `REVIEW_PENDING`. This note documents an *added* algebraic check for
the four follow-up dihedral families that the 2026-05-05 Gröbner attack left
without a replayable real-root / non-degeneracy decoder. It does **not** claim
a general proof of Erdős #97. It does **not** promote the n = 9 finite case
past `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`. The official /
global status of #97 (erdosproblems.com/97) remains FALSIFIABLE / OPEN.

The current repo-local n = 9 selected-witness audit target remains the
vertex-circle exhaustive checker
(`docs/n9-vertex-circle-exhaustive.md`,
`data/certificates/n9_vertex_circle_exhaustive.json`). The decoders documented
here are an *independent* algebraic audit artifact for the 16 labelled
selected-witness assignments that vertex-circle already kills via self-edge or
strict-cycle filtering.

## Background

The 2026-05-05 multi-agent attack (`docs/erdos97-attack-2026-05-05.md`,
`data/certificates/2026-05-05/n9_groebner_results.json`) collapsed the 184
labelled n = 9 selected-witness assignments into 16 dihedral families and ran
`sympy.groebner` over `QQ` on the squared-distance equality system for each
representative. The result was

* 11 / 16 families (orbit-sum 150 labelled assignments): grevlex GB = `{1}`,
  no Euclidean realisation.
* 1 / 16 (F12, orbit 18): grevlex GB has 14 generators including the
  univariate relation `y_8^2 + 1/4 = 0`, which has no real root.
* 4 / 16 (F07, F08, F09, F13; orbit sizes 6, 2, 6, 2; covering 16 labelled
  assignments): grevlex GB has 62 generators each, ideal is zero-dimensional,
  but no replayable real-root decoder was committed.

This file documents the decoder for F07, F08, F09, F13.

## What the decoder does

`scripts/decode_n9_groebner_f07_f13.py` regenerates the polynomial system
from each family's witness-incidence rows, recomputes the grevlex Gröbner
basis, computes a univariate elimination polynomial in `y_2` via a lex
Gröbner basis with `y_2` placed last in the lex order, enumerates every real
algebraic configuration consistent with the basis, and checks strict
convexity for each enumerated configuration in the cyclic order `0, ..., 8`.

### Polynomial system

For each witness row `[a, b, c, d]` of vertex `i` we encode the three
squared-distance equalities

```
|p_i - p_a|^2 - |p_i - p_b|^2 = 0
|p_i - p_a|^2 - |p_i - p_c|^2 = 0
|p_i - p_a|^2 - |p_i - p_d|^2 = 0
```

giving 3 × 9 = 27 polynomial generators in 14 free coordinates after the
gauge fix `x_0 = y_0 = 0, x_1 = 1, y_1 = 0`.

### Gröbner basis

The grevlex basis is computed first with `sympy.groebner(..., order='grevlex',
domain=QQ)`. For F07/F08/F09/F13 it is identical across the four families
(62 polynomials including the simple linear / quadratic relations

```
x_2 = 1/2,  x_5 = 1/2,  x_8 = 1/2
y_2^2 - 3/4 = 0,  y_5^2 - 3/4 = 0,  y_8^2 - 3/4 = 0
x_3^2 - (3/2) x_3 = 0,  x_6^2 - (3/2) x_6 = 0
x_4^2 - x_4/2 - 1/2 = 0,  x_7^2 - x_7/2 - 1/2 = 0
```

plus four linear binders

```
x_3 y_2 - (3/2) y_3 = 0      (so y_3 = (2/3) x_3 y_2)
x_4 y_2 - y_2 + (3/2) y_4 = 0 (so y_4 = (2/3) y_2 (1 - x_4))
x_6 y_2 - (3/2) y_6 = 0      (so y_6 = (2/3) x_6 y_2)
x_7 y_2 - y_2 + (3/2) y_7 = 0 (so y_7 = (2/3) y_2 (1 - x_7)).
```

The remaining 51 generators are consistency relations among the seven free
roots `(y_2, y_5, y_8, x_3, x_6, x_4, x_7)`. The variety is
zero-dimensional and lives entirely in `Q(sqrt(3))`.

### Univariate elimination polynomial

A lex Gröbner basis with `y_2` placed last in the lex order yields the
univariate elimination polynomial

```
y_2^2 - 3/4 = 0
```

with real roots `y_2 = ±sqrt(3)/2` for each of the four families. (The lex
basis is small — 26 polynomials for F07 — and finishes in about 6 s in
sympy 1.14.)

### Real-root enumeration

The decoder enumerates every assignment of

```
y_2 ∈ {±sqrt(3)/2}        y_5 ∈ {±sqrt(3)/2}        y_8 ∈ {±sqrt(3)/2}
x_3 ∈ {0, 3/2}             x_6 ∈ {0, 3/2}             x_4 ∈ {1, -1/2}
x_7 ∈ {1, -1/2}
```

(2^3 × 2^2 × 2^2 = 128 candidates), derives `y_3, y_4, y_6, y_7` from the
linear binders, and verifies that every generator of the original 27-polynomial
system evaluates to zero. Each accepted tuple is a real point of the variety.

### Strict convexity audit

For each accepted configuration we check whether all 9 consecutive cross
products `(p_{i+1} - p_i) × (p_{i+2} - p_i)` are strictly positive (or all
strictly negative); equivalently, whether the polygon `p_0, p_1, ..., p_8` is
strictly convex in cyclic order. Configurations with coincident vertices are
recorded as `degenerate_coincident_vertices`.

## Reproducible numbers

Running

```bash
python3 scripts/decode_n9_groebner_f07_f13.py
```

with sympy 1.14.0 (the version pinned in `requirements-lock.txt`) writes
`data/certificates/n9_groebner_real_root_decoders.json` and prints

```
[F07] grevlex GB: 62 polys, zero-dim=True
[F07] real algebraic solutions: 20
[F08] grevlex GB: 62 polys, zero-dim=True
[F08] real algebraic solutions: 20
[F09] grevlex GB: 62 polys, zero-dim=True
[F09] real algebraic solutions: 20
[F13] grevlex GB: 62 polys, zero-dim=True
[F13] real algebraic solutions: 20

total real solutions across F07/F08/F09/F13: 80
strictly convex configurations: 0
```

Total wall-clock under sympy 1.14.0 on Python 3.11: ~2 minutes (dominated by
the four lex Gröbner runs, ~5 s each, plus ~30 s of grevlex recomputation and
~30 s of substitution / strict-convexity checks).

For every one of the 80 accepted real configurations the convexity audit
returns `degenerate_coincident_vertices`: the 9 labelled vertices collapse
onto only 3 or 4 distinct points among `{(0,0), (1,0), (1/2, ±sqrt(3)/2),
(-1/2, ±sqrt(3)/2), (3/2, ±sqrt(3)/2)}`. Hence **no strictly convex 9-gon**
exists in the variety of any of the four families.

## Verifier instructions

1. Confirm `requirements-lock.txt` lists `sympy==1.14.0` and install it.
2. Run `python3 scripts/decode_n9_groebner_f07_f13.py`.
3. Diff the output JSON against the committed
   `data/certificates/n9_groebner_real_root_decoders.json`. The artifact
   should reproduce bit-for-bit modulo wall-clock fields
   (`grevlex_basis_seconds`, `wall_time_seconds`,
   `univariate_elimination.lex_basis_seconds`).
4. Sanity-check the polynomial system in the artifact against the witness
   rows in `data/certificates/2026-05-05/n9_groebner_results.json`: every
   `polys[k]` should be the difference of two squared-distance polynomials
   between vertex `i` and the four witnesses listed in `rows[i]`.
5. For each family, verify that every entry of `convexity_audit` reports
   `degenerate_coincident_vertices` and that `any_strictly_convex == false`.
6. As an independent spot-check, manually substitute one of the listed real
   solutions (e.g. F07 solution 0) into one of the original 27 polynomials
   and confirm it evaluates to 0.

## Relation to the existing n = 9 finite-case artifacts

This decoder strictly complements:

* `data/certificates/n9_vertex_circle_exhaustive.json` (the
  vertex-circle exhaustive checker, which already kills these 16 labelled
  assignments via 158 / 184 self-edge and 26 / 184 strict-cycle obstructions);
* `data/certificates/2026-05-05/n9_groebner_results.json` (the
  2026-05-05 grevlex Gröbner sweep, which left F07/F08/F09/F13 as decoder
  follow-up).

The decoder does **not** independently reduce the 184 labelled assignments to
the 16 dihedral representatives — it consumes the dihedral-family rows from
the 2026-05-05 artifact directly. A reviewer wanting a chain of independent
checks should additionally re-derive the 16 families from
`data/certificates/n9_vertex_circle_motif_families.json`.

## Honest caveats

* **Not a proof of #97.** The decoder closes 16 / 184 labelled assignments at
  n = 9 — the same 16 already closed by vertex-circle. It is a review-pending
  algebraic check, not a source-of-truth obstruction.
* **Gauge dependence.** A different gauge fix (different choice of three
  rigid-motion + scale constants) would change the GB and the univariate
  elimination polynomial. The decoder only proves the chosen gauge has no
  strictly convex realization; the full gauge-invariant statement follows
  because rigid motions and uniform scaling preserve strict convexity.
* **Sympy 1.x.** Computed and verified under sympy 1.14.0. Different sympy
  versions may produce different but equivalent grevlex / lex bases (the
  reduced Gröbner basis with respect to a fixed monomial order is unique up
  to scaling, but sympy's coefficient normalisation has changed across
  versions).
* **No general n.** The structural shape of the real variety
  (`Q(sqrt(3))`, vertices on a hexagonal lattice) is specific to these four
  families at n = 9. There is no claim of an analogous algebraic structure at
  larger n.
