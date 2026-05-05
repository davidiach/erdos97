# n=8 Independent SymPy-Free Obstruction Recheck

Status: `REPO_LOCAL_INDEPENDENT_CROSS_CHECK_PENDING_EXTERNAL_REVIEW`.

This note records a SymPy-free cross-check of the `n=8` obstruction
certificates documented in `docs/n8-exact-survivors.md`.  The cross-check
is repo-local and does not turn the `n <= 8` finite-case result into a
public theorem-style claim.

## Goal

The existing `n=8` obstruction artifact (see
`docs/n8-exact-survivors.md`) uses SymPy for rational linear-span checks
and Groebner-basis substitution chains.  This note records an
independent reproduction of as much of that obstruction set as is
feasible in pure-Python rational arithmetic, with no SymPy import and
no shared code path.

The independent verifier is intended as a defensive cross-check: if a
SymPy bug or a regression in `scripts/analyze_n8_exact_survivors.py`
were to affect the existing checker, this independent verifier would
still flag mismatches in the parts it covers.

## Method

The verifier in `src/erdos97/n8_independent_obstruction.py`
reimplements the obstruction tests using only the Python standard
library and `fractions.Fraction` for exact rational arithmetic:

- A from-scratch sparse multivariate polynomial type
  (`dict[monomial_tuple, Fraction]`).
- A from-scratch sparse Gauss-Jordan rank routine over `QQ`.
- An independent cyclic-order enumeration loop with its own
  forced-perpendicularity bipartite-coloring step.
- An auxiliary squared-distance / Cayley-Menger linear stage that
  treats `PB` and `ED` equations as linear identities in the 28
  squared-distance variables `d_{ij}` and reports the resulting rank
  and free-variable count for each class.

The Cartesian gauge matches the existing checker
(`p_0 = (0, 0)`, `p_1 = (1, 0)`, twelve free coordinates
`x_2, y_2, ..., x_7, y_7`).  Each phi-edge `(i, j) -> (a, b)`
contributes both forms of the perpendicular-bisector polynomial: the
dot-product form `(p_i - p_j) . (p_a - p_b)` and the bisector
determinant form `det(p_j - p_i, p_a + p_b - 2 p_i)`.

## Coverage

| class | independent kill | mechanism |
| ---: | :--- | :--- |
| 0  | yes | `y_2 in PB span` |
| 1  | yes | `y_2 in PB span` |
| 2  | yes | `y_2 in PB span` |
| 3  | no  | requires Groebner substitution chain |
| 4  | no  | requires Groebner substitution chain |
| 5  | no  | requires Groebner substitution chain |
| 6  | yes | `y_2 in PB span` |
| 7  | yes | `y_2 in PB span` |
| 8  | yes | `y_2 in PB span` |
| 9  | yes | `y_2 in PB span` |
| 10 | yes | `y_2 in PB span` |
| 11 | yes | `y_2 in PB span` |
| 12 | yes | cyclic-order kill |
| 13 | yes | `y_2 in PB span` |
| 14 | no  | requires Groebner substitution chain |

The independent verifier kills 11 of 15 reconstructed classes.  The
remaining four classes (3, 4, 5, 14) require nonlinear substitution
chains that go beyond the Q-linear span of the PB polynomials.  They
are explicitly out of scope here and remain covered by the
SymPy/Groebner-based existing checker.

The independent verifier additionally re-derives the compatible
cyclic-order count for every class.  All 15 counts match the values
recorded in `data/incidence/n8_compatible_orders.json` and listed in
`docs/n8-exact-survivors.md`.  This is a stronger check than a
single-class kill: it independently reconstructs the full
forced-perpendicularity bipartite structure for every class.

## Reproduction

```bash
python scripts/independent_n8_obstruction_recheck.py --check --json
python -m pytest tests/test_n8_independent_obstruction.py -q
```

## Remaining gap

The independent verifier does not cover classes 3, 4, 5, 14.  Closing
that gap would require either implementing multivariate Groebner
bases over `QQ` from scratch (substantial), or using a fundamentally
different obstruction route (e.g., interval-arithmetic certified
nonexistence on the polynomial system, or an SOS/positivstellensatz
certificate).  These remain on the backlog as conditional follow-ups
and are not preconditions for the existing repo-local result.

## Provenance

- Implementation: `src/erdos97/n8_independent_obstruction.py`.
- CLI entrypoint: `scripts/independent_n8_obstruction_recheck.py`.
- Tests: `tests/test_n8_independent_obstruction.py`.
- Existing checker (cross-checked against): `scripts/analyze_n8_exact_survivors.py`.
- Survivor data (input): `data/incidence/n8_reconstructed_15_survivors.json`.
