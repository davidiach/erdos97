# Sparse full-cone fresh-order screen (2026-07-29)

`summary.json` stores an exact full-Kalmanson-cone classification of the 63
fresh C25/C29 orders that survive all lightweight filters in the source
fresh-stream packet.

For each order, the generator searches the full fixed-order Kalmanson row
family. A conclusive record must contain either an exact positive integer
zero-sum certificate or an exact integer separating potential. Numerical LP
status alone is never promoted.

The checker:

- verifies the source fresh-stream artifact SHA-256;
- reconstructs the exact 31 C25 and 32 C29 survivor identities;
- exact-replays all 63 stored positive-circuit certificates;
- verifies certificate hashes, fixed orders, supports, widths, and modular-rank
  positive-circuit audits;
- would exact-replay any stored separating potential against every strict row;
- recomputes the per-pattern and aggregate classification summaries.

Expected result: 63 verified fresh lightweight survivors, all 63 carrying
exact positive zero-sum certificates, with zero separator cases and zero
unresolved numerical screens.

Artifact SHA-256:

```text
8b215c41179a4a745da5fc9fc8067ca0d8043a8462e94c60db8b86fd45349d32
```

Replay:

```bash
python scripts/exploration/screen_sparse_full_cone_fresh_orders.py \
  --check data/runs/sparse_full_cone_fresh_order_screen_2026-07-29/summary.json
```

This is bounded fixed-pattern, fixed-order evidence. It is not an all-order
obstruction, geometric realization result, counterexample, proof of Erdos
Problem #97, or official/global status update.
