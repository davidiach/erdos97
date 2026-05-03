# C13 Kalmanson Order Pilot

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This is a bounded fixed-order pilot for `C13_sidon_1_2_4_10`. It is not an
all-order cyclic-order search and does not prove that the abstract C13 Sidon
pattern is impossible across all cyclic orders.

## Artifact

```text
data/certificates/c13_kalmanson_bounded_order_pilot.json
```

Regenerate it with:

```bash
python scripts/pilot_c13_kalmanson_orders.py \
  --assert-expected \
  --summary-only \
  --out data/certificates/c13_kalmanson_bounded_order_pilot.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

The committed artifact is a compact summary. Omit `--summary-only` to emit the
full exact certificate objects for independent inspection.

## Scope

The pilot normalizes seven explicitly pinned cyclic orders by rotation and
reflection, removes dihedral duplicates, and runs the fixed-order
Kalmanson/Farkas certificate finder on each unique order.

The pinned orders include:

- the natural order;
- the registered non-natural sparse-frontier survivor order already documented
  in `docs/kalmanson-c13-pilot.md`;
- five deterministic non-natural probe orders.

All seven unique fixed orders close by exact positive-integer
Kalmanson/Farkas certificates. The script checks each generated certificate
with `scripts/check_kalmanson_certificate.py`; the committed artifact records
the checked summaries and branch accounting.

## Current Counts

| Count | Value |
|---|---:|
| Raw orders | 7 |
| Unique dihedral-normalized orders | 7 |
| Dihedral duplicates pruned | 0 |
| Closed by exact Kalmanson certificate | 7 |
| Unclosed orders | 0 |

This is useful search-pipeline evidence: the fixed-order Kalmanson certificate
machinery can close several non-natural C13 orders quickly and reproducibly.
It is not evidence of geometric realizability, and it is not a proof that all
C13 cyclic orders close.

## Next Step

The next exact extension is a true bounded brancher: normalize partial cyclic
orders, add cheap pruning before LP calls, run dual checks only on closed
branches, and emit exact integer certificates for each closure. Until every
normalized cyclic order is covered, the abstract C13 Sidon pattern remains
unsettled.

A first bounded prefix-branch follow-up is recorded in
`docs/c13-kalmanson-prefix-branch-pilot.md` and
`data/certificates/c13_kalmanson_prefix_branch_pilot.json`. It adds
reflection pruning before LP calls and closes twelve sampled fixed completions,
but it is still not an all-order search.
