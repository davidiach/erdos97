# Kalmanson Two-Certificate Order Search

Status: `EXACT_OBSTRUCTION` for the fixed abstract `C13_sidon_1_2_4_10`
and `C19_skew` selected-witness patterns across all cyclic orders.

No general proof of Erdos Problem #97 is claimed. No counterexample is
claimed.

## Result

For the circulant selected-witness patterns

```text
C13_sidon_1_2_4_10
n = 13
offsets = [1, 2, 4, 10]

C19_skew
n = 19
offsets = [-8, -3, 5, 9]
```

every cyclic order contains an inverse pair of strict Kalmanson inequalities.
After quotienting ordinary pair distances by the selected-distance equalities,
the two inequality coefficient vectors cancel exactly. Summing the two strict
inequalities gives `0 > 0`.

This kills these fixed abstract selected-witness patterns over all cyclic
orders. It does not prove Erdos Problem #97.

## Search Artifact

The original C13 exhaustive DFS artifact is:

```text
data/certificates/c13_sidon_all_orders_kalmanson_two_search.json
```

Summary:

```text
status: EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION
nodes visited: 1496677
branches pruned by completed two-certificate: 6192576
maximum surviving prefix depth: 11
survivor order: none
```

The search fixes label `0` first using the translation symmetry of circulant
selected-witness patterns. It does not quotient reversal.

The checked C19 SMT refinement artifact is:

```text
data/certificates/c19_skew_all_orders_kalmanson_z3.json
```

Summary:

```text
status: EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION
SMT solver: z3
refinement iterations: 142
forbidden inverse-pair order clauses: 7981
solver result after clause replay: unsat
```

Each stored clause forbids one pair of ordered quadrilaterals whose Kalmanson
row vectors are exact inverses after selected-distance quotienting. The verifier
checks every clause against the inverse-vector table and then asks Z3 to prove
that the accumulated exact cyclic-order constraints are unsatisfiable.

The companion clause-template diagnostic is:

```text
reports/c19_kalmanson_z3_clause_diagnostics.json
```

Regenerate and check it with:

```bash
python scripts/analyze_kalmanson_z3_clauses.py \
  --assert-expected \
  --out reports/c19_kalmanson_z3_clause_diagnostics.json

python scripts/analyze_kalmanson_z3_clauses.py \
  --assert-expected \
  --check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json
```

The diagnostic first replays the source Z3 certificate, then summarizes the
7,981 stored clauses by inverse-pair kind, selected-distance quotient table
size, simultaneous cyclic-translation families, modular ordered-quad steps,
label overlap, and label-0 rotation-quotient literals. It is a structural
inspection aid for the fixed abstract `C19_skew` certificate only. It does not
add a proof, search new cyclic orders, transfer the obstruction to any other
pattern, or update the global Erdos #97 status.

## Reproduction

Regenerate the artifact:

```bash
python scripts/check_kalmanson_two_order_search.py \
  --name C13_sidon_1_2_4_10 \
  --n 13 \
  --offsets 1,2,4,10 \
  --assert-obstructed \
  --assert-c13-expected \
  --out data/certificates/c13_sidon_all_orders_kalmanson_two_search.json
```

The exhaustive replay is intentionally not part of the default fast test
suite. The checked JSON artifact is validated by the default tests; rerun the
full search when changing the search code or the C13 artifact.

Verify the C19 SMT certificate:

```bash
python scripts/check_kalmanson_two_order_z3.py \
  --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json \
  --assert-unsat
```

Regenerate the C19 SMT certificate:

```bash
python scripts/check_kalmanson_two_order_z3.py \
  --name C19_skew \
  --n 19 \
  --offsets=-8,-3,5,9 \
  --assert-unsat \
  --out data/certificates/c19_skew_all_orders_kalmanson_z3.json
```

Optional compiled diagnostic:

```bash
rustc -O scripts/check_kalmanson_two_order_search_fast.rs -o kalmanson_fast
./kalmanson_fast \
  --name C19_skew \
  --n 19 \
  --offsets -8,-3,5,9 \
  --node-limit 1000000
```

## Frontier Impact

This completes the current registered C13 and C19 sparse-pattern pilots as
abstract-order obstructions for those fixed selected-witness patterns. The
global problem remains open: a counterexample could use a different incidence
pattern, or a proof could require a bridge from arbitrary counterexamples to a
classified family of selected-witness patterns.
