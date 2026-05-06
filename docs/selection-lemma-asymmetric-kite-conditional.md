# Selection Lemma asymmetric-kite conditional memo

Status: `CONDITIONAL_REVIEW_PENDING`.

This memo records the salvageable asymmetric-kite algebra from the 2026-05-06
attack drafts. It is not a proof of Erdős Problem #97, not a counterexample,
and not a source-of-truth promotion. The official/global status remains
falsifiable/open, and the strongest local finite-case result remains the
repo-local `n <= 8` selected-witness artifact.

The intended scope is narrower: if the cyclic-order assumptions below are
validated, the recorded cross-product identities obstruct the asymmetric-kite
case of canonical-chord-rule injectivity. The symmetric-kite case and the
separate noncrossing claim remain outside this memo.

## Setup

Assume two distinct bad vertices `v_i` and `v_j` select the same canonical
chord `{p, q}` with witness radii `r_i != r_j`. By the two-overlap
perpendicular-bisector rule, the line `v_i v_j` is perpendicular to `pq` and
passes through the midpoint of `pq`.

Use coordinates

```text
p = (-c, 0),  q = (c, 0),  v_i = (0, h_i),  v_j = (0, -h_j)
```

with `c, h_i, h_j > 0`. Let

```text
r_i = c / sin(alpha_i),  r_j = c / sin(alpha_j)
```

and take `0 < alpha_j <= alpha_i < pi/6` after swapping `i,j` if needed. The
extra witnesses of `v_i` and `v_j` are parameterized by signed angles from the
axis through the shared chord.

The key audit assumption is cyclic-order completeness: the local predecessor
and successor cases at `p` (and the reflected cases at `q`) must follow from
the canonical-chord setup without losing an interleaving possibility.

## Checked Algebra

For the four local predecessor/successor cases at `p`, the left-turn
cross-products factor as:

```text
LT_X1 =
  -4 c^2 sin((B-alpha_j)/2) sin((A-alpha_i)/2)
      sin((A+B+alpha_i+alpha_j)/2)
    / (sin(alpha_i) sin(alpha_j))

LT_X2 =
  -2 c^2 cos((A+alpha_i+2 alpha_j)/2) sin((A-alpha_i)/2)
    / (sin(alpha_i) sin(alpha_j))

LT_X3 =
  -4 c^2 sin((B_2-B_1)/2) sin((B_2-alpha_j)/2)
      sin((B_1-alpha_j)/2)
    / sin(alpha_j)^2

LT_X4 =
  -c^2 sin(B-alpha_j) / sin(alpha_j)^2
```

The script `scripts/check_asymmetric_kite_conditional.py` verifies these
identities symbolically with SymPy by checking `raw - factored == 0`. It also
runs a deterministic sign sweep in the strict interior of the assumed
parameter box and records no sampled violations.

Run:

```bash
python scripts/check_asymmetric_kite_conditional.py --json
```

The script deliberately reports `CONDITIONAL_REVIEW_PENDING`; it does not
claim that the geometric assumptions are fully discharged.

## Why The Signs Matter

Under the assumed box, the sine factors above are positive. The only delicate
factor is

```text
cos((A + alpha_i + 2 alpha_j) / 2),
```

which is positive throughout the interior when `alpha_i >= alpha_j`. This is
the WLOG smaller-radius-side convention. Therefore each displayed `LT_Xk` is
strictly negative in the corresponding local case, contradicting the expected
left-turn sign for a strictly convex CCW cyclic order.

## Remaining Audit Items

The memo is blocked on these points before any theorem-style use:

- prove the cyclic-order completeness statement for all interleavings of the
  extra witnesses around `p` and `q`;
- audit the reflection/mirror reduction for the all-on-one-side case without
  relying on numerical samples;
- keep this injectivity subclaim separate from the noncrossing claim in the
  Selection Lemma program;
- re-audit the canonical-chord tie-breaking assumptions used to define the
  shared chord.

Until those items close, this branch is an exact-algebra and audit-target
record only.
