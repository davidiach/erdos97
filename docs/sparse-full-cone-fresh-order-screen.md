# Sparse full-cone fresh-order screen

Status: exact fixed-order full-cone certificates over a bounded
history-disjoint C25/C29 packet. No general proof, all-order C25/C29
obstruction, geometric counterexample, or official-status change is claimed.

## Target

The canonical-template transfer probe in
`docs/sparse-full-cone-small-template-fresh-stream.md` produced 64 orders
dihedrally disjoint from its 48-order source packet. Sixty-three also survive
the vertex-circle and both Altman lightweight filters, and none matches any of
the seven previously extracted tiny certificate templates.

A zero template hit does not imply escape from the full Kalmanson cone. This
follow-up runs the complete fixed-order Kalmanson row family on those 63
survivors.

## Exact classification protocol

`scripts/exploration/screen_sparse_full_cone_fresh_orders.py` uses Gordan's
theorem of alternatives. A conclusive fixed-order record contains exactly one
of:

1. an exact positive integer combination of strict Kalmanson row vectors whose
   quotient-vector sum is zero; or
2. an exact integer potential whose dot product with every strict row vector
   is positive, proving that no nonzero nonnegative zero sum exists for that
   row family.

The LP is only a witness finder. Stored positive circuits are checked by exact
integer arithmetic and a modular-rank audit. A separating potential would
likewise be replayed against every row by exact integer arithmetic. If neither
exact object can be recovered, the record remains unresolved rather than
being called a full-cone escape.

## Result

| Pattern | Selected survivors | Exact positive certificates | Exact separators | Unresolved | Support range | Quad-width range |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `C25_sidon_2_5_9_14` | 31 | 31 | 0 | 0 | 197–217 | 197–217 |
| `C29_sidon_1_3_7_15` | 32 | 32 | 0 | 0 | 282–304 | 282–304 |
| **Total** | **63** | **63** | **0** | **0** |  |  |

All 63 zero-objective LP basic supports exactified directly; the deterministic
random-objective fallback was never needed. Five certificates contain two
inequality kinds on one ordered quadrilateral, so support and quad width differ
by one in those records.

Thus none of the 63 fresh lightweight survivors is a full-cone escape: every
one has an exact fixed-pattern, fixed-order Kalmanson/Farkas obstruction.
This closes only the bounded 63-order screen. It does not classify all cyclic
orders of either abstract pattern.

## Limitations and next target

The bounded follow-up is completed in
`docs/sparse-full-cone-fresh-certificate-compression.md`. Six deterministic
alternative objectives per source recover three new width-`3`, width-`5`, and
width-`7` circuits plus exact fresh-packet reuse. The strongest C25 width-`3`
affine orbit covers all 31 C25 targets, so the predeclared stopping rule does
not fire. The next target is a transfer audit against prior and second-stream
orders, not a larger same-packet objective budget.

No coordinate search is warranted for these 63 orders because each is already
exactly inconsistent with its selected-distance quotient and fixed cyclic
order. This says nothing about other selected-witness patterns or orders.

Replay:

```bash
python scripts/exploration/screen_sparse_full_cone_fresh_orders.py \
  --check data/runs/sparse_full_cone_fresh_order_screen_2026-07-29/summary.json
```
