# Kalmanson Two-Certificate Order Search

Status: `EXACT_OBSTRUCTION` for the fixed abstract
`C13_sidon_1_2_4_10` selected-witness pattern across all cyclic orders.

No general proof of Erdos Problem #97 is claimed. No counterexample is
claimed.

## Result

For the circulant selected-witness pattern

```text
C13_sidon_1_2_4_10
n = 13
offsets = [1, 2, 4, 10]
```

every cyclic order contains an inverse pair of strict Kalmanson inequalities.
After quotienting ordinary pair distances by the selected-distance equalities,
the two inequality coefficient vectors cancel exactly. Summing the two strict
inequalities gives `0 > 0`.

This kills the fixed abstract C13 Sidon pattern over all cyclic orders. It does
not kill the larger sparse frontier, and it does not prove Erdos Problem #97.

## Search Artifact

The checked artifact is:

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

## Frontier Impact

This completes the C13 Kalmanson pilot as an abstract-order obstruction for
this one fixed pattern. The analogous `C19_skew` all-order question remains
open, and is the more relevant sparse-overlap wall.
