# Kalmanson/Farkas Template Loop

Status: `EXACT_CERTIFICATE_DIAGNOSTIC` / template-extraction research note.

No general proof of Erdos Problem #97 is claimed. No counterexample is
claimed. The C13 and C19 entries discussed below are fixed abstract
selected-witness pattern obstructions. The C29 entry is one fixed-order
obstruction only.

## Scope

Task bridge: extract reusable Kalmanson/Farkas order-search templates from the
retired sparse leads, then test whether the same viewpoint explains the larger
C29 full-cone certificate.

Inputs read first:

- `AGENTS.md`
- `README.md`, `STATE.md`, `RESULTS.md`, `metadata/erdos97.yaml`
- `docs/claims.md`, `docs/review-priorities.md`, `docs/codex-backlog.md`
- `docs/codex-strategy-instructions.md`
- `docs/kalmanson-two-order-search.md`
- `docs/kalmanson-certificate-diagnostics.md`
- `docs/round2/kalmanson_distance_filter.md`
- `data/certificates/c13_sidon_all_orders_kalmanson_two_search.json`
- `data/certificates/c19_skew_all_orders_kalmanson_z3.json`
- `data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`
- existing diagnostics under `reports/c19_kalmanson_z3_clause_diagnostics.json`

Verifier commands run during this loop:

```bash
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/check_kalmanson_certificate.py data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json --summary-json
python scripts/analyze_kalmanson_z3_clauses.py --assert-expected --check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json
python scripts/analyze_kalmanson_certificates.py data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json --top 20 --json
python scripts/analyze_kalmanson_certificates.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --top 8 --json
python scripts/find_kalmanson_two_certificate.py --name C29_sidon_1_3_7_15 --n 29 --offsets 1,3,7,15 --order 0,27,11,4,19,5,26,12,6,21,13,28,14,2,20,18,7,24,10,25,17,3,9,15,1,22,8,23,16 --summary-json
```

The C13 all-order checker replayed `1496677` nodes, pruned `6192576`
branches, and found no survivor order. The C19 Z3 checker replayed UNSAT with
`7981` clauses. The C29 fixed-order checker verified `165` positive
inequalities, `319` quotient distance classes, and zero weighted sum.

## Cycle 1 - Inverse-Pair Proposal

Propose:

A reusable template family is the support-two quotient-edge inverse pair. Let
`[xy]` denote the selected-distance quotient class of ordinary pair-distance
variable `d(x,y)`. For a quadrilateral `a,b,c,d` in cyclic order, a Kalmanson
row is a signed vector in these quotient classes. If quotienting cancels one
positive and one negative term inside the same row, the row reduces to a
directed edge

```text
[A] - [B].
```

Two strict Kalmanson rows whose reduced quotient edges are opposite,

```text
[A] - [B]  and  +[B] - [A],
```

sum to `0 > 0`. This is a reusable fixed-order obstruction template. It is
not tied to C13 or C19 labels; those patterns are only benchmarks showing the
template in action.

Audit:

The compact C13 fixed-order certificate has two `K2_diag_gt_other` rows:

```text
K2 [5,0,9,3]    -> class 17 - class 6
K2 [5,10,8,9]   -> class 6 - class 17
```

The compact C19 fixed-order certificate has the same quotient-edge shape:

```text
K2 [18,10,7,2]  -> class 54 - class 33
K2 [7,5,2,16]   -> class 33 - class 54
```

The class IDs are checker-local identifiers, but the cancellation statement is
not: each class is a selected-distance quotient class. The stored C19
all-order clause diagnostic confirms that this small support family dominates
the Z3 certificate: `7780` of `7981` stored clauses use inverse vector pairs
with support size `2`; the remaining `201` use support size `4`.

Refine:

Template record `QE2`:

- Object: two strict Kalmanson rows available in one fixed cyclic order.
- Hypotheses: after selected-distance quotienting, row 1 reduces to
  `+[A]-[B]` and row 2 reduces to `+[B]-[A]`.
- Conclusion: the fixed selected-witness pattern and fixed cyclic order are
  impossible.
- Verifier pattern: reuse `all_kalmanson_rows`, quotient row vectors, and
  `inverse_pairs` from `scripts/find_kalmanson_two_certificate.py`.
- Scope limit: this does not say every cyclic order contains such a pair
  unless an all-order order search or SMT replay proves that separately.

## Cycle 2 - C29 Audit

Propose:

Try to transfer `QE2` directly to the recorded C29 Sidon fixed order. If the
larger sparse order only needed the same support-two inverse edge, the
two-certificate finder should produce a weight-`1,1` certificate.

Audit:

The direct transfer fails cleanly. The fixed C29 order returns:

```text
NO_TWO_INEQUALITY_KALMANSON_CERTIFICATE_FOUND
```

The full C29 certificate still contains some small rows, but they do not pair
off as inverse rows:

```text
quotient row support sizes: 17 rows of size 2, 148 rows of size 4
support weights by size:    56,593,811 on size 2, 447,706,983 on size 4
kind/support split:         K1 size 2: 10; K1 size 4: 55; K2 size 2: 7; K2 size 4: 93
```

The checked full certificate is a one-dimensional positive dependency over
the listed support rows: rank `164` for `165` rows over each checked prime,
with nullity `1`. Its top repeated cyclic gap patterns are weakly repeated:
the largest observed normalized row-gap count is only `3`.

Refine:

The C29 blocker is precise: support-two quotient edges exist, but no opposite
edge pair occurs in the fixed order. The obstruction needs a full positive
Farkas circuit mixing support-two and support-four Kalmanson rows. Treating
C29 as another inverse-pair order-search clause would lose the actual
certificate structure.

## Cycle 3 - Full-Cone Template Attempt

Propose:

Extract a reusable full-cone family from C29 by grouping the 165 rows by
normalized cyclic gap signatures and quotient support size.

Audit:

The current C29 certificate does not yet expose a compact reusable family.
The repeated row-gap signatures are too sparse, the weights have large spread
(`gcd 1`, max weight `15835921`, total weight `504300794`), and the positive
dependency is global across many distance classes rather than a visible small
translation orbit. This is evidence of a real exact obstruction for the fixed
order, but not yet a reusable all-order clause family.

Refine:

Next tiny script target: `scripts/analyze_kalmanson_template_families.py`.
It should be diagnostic-only and should not generate new mathematical claims.
Minimum useful output:

- for each supplied fixed-order certificate, compute every quotient row vector;
- classify rows by `K1/K2`, quotient support size, internal cancellation type,
  normalized cyclic gap signature, and simultaneous cyclic label translate;
- detect `QE2` inverse-pair clauses as a named family;
- build the directed support-two quotient-edge graph and report missing
  opposite edges;
- for full-cone certificates, compute the positive circuit support projected
  to support-two edges plus support-four hyperedges;
- emit the smallest exact subcircuits if any are found, otherwise report the
  current certificate as a full-support blocker.

The immediate acceptance check for that script should be: it rediscovers the
C13/C19 compact inverse-pair family, reports no C29 two-row inverse pair for
the recorded order, and reproduces the C29 `165`-row nullity-`1` full-cone
dependency without claiming an all-order C29 obstruction.

## Outcome

Classified reusable family: `QE2`, the support-two quotient-edge inverse-pair
template. It is a fixed-order obstruction template and becomes all-order only
when paired with an exhaustive order search or SMT certificate.

Precise blocker beyond the retired sparse leads: the recorded C29 fixed order
has support-two rows but no two-inequality inverse pair. The existing
obstruction is a full-cone positive circuit with one-dimensional support
dependency, large weights, and weak repeated gap patterns. The next useful
work is a diagnostic script that separates support-two inverse-pair templates
from larger full-cone circuit structure.
