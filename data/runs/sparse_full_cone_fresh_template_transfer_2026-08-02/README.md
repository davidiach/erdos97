# Sparse full-cone fresh-template transfer audit

Status: bounded exact-template transfer diagnostic over fixed C25/C29 order
packets. No all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This run canonicalizes four exact circuits from
`data/runs/sparse_full_cone_fresh_compression_2026-08-01/summary.json`:
the three circuits of width at most 12 and the C25 width-14 circuit whose
affine orbit covers at least 24 source targets.

The four templates are replayed against:

1. the prior 48-order packet; and
2. a second 64-order inverse-pair-escape stream that is dihedrally disjoint
   from both the prior packet and the first 64-order fresh stream.

Templates are not asserted as solver blockers during second-stream
generation. All 104 affine images and all stored coverage matches are replayed
exactly.

## Result

| Pattern | Templates | Source covered | Prior covered | Second-stream covered | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `C25_sidon_2_5_9_14` | 3 | 31/31 | 16/24 | 16/32 | continue exact transfer |
| `C29_sidon_1_3_7_15` | 1 | 6/32 | 0/24 | 0/32 | stop packet-specific mining |

Generate:

```bash
python scripts/exploration/probe_sparse_full_cone_fresh_template_transfer.py \
  --out data/runs/sparse_full_cone_fresh_template_transfer_2026-08-02/summary.json
```

Replay without rerunning Z3:

```bash
python scripts/exploration/probe_sparse_full_cone_fresh_template_transfer.py \
  --check data/runs/sparse_full_cone_fresh_template_transfer_2026-08-02/summary.json
```

SHA-256 of `summary.json`:

`406a2dab8f84c673a710353509d00466192df23d4aa320180fc40598a6f00175`
