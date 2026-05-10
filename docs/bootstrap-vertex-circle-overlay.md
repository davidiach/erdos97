# Bootstrap / Vertex-circle Overlay

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note overlays the two tight non-ear-orderable `n=9` rows from
`docs/bootstrap-core-crosswalk.md` with the review-pending vertex-circle
strict-cycle certificate chain. The checked artifact is:

```bash
python scripts/check_bootstrap_vertex_circle_overlay.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_vertex_circle_overlay.py --write --assert-expected
```

to `data/certificates/bootstrap_vertex_circle_overlay.json`.

## Scope

The input bootstrap records are singleton-rich fixed selected-row diagnostics.
They are not full geometric rich-class data, and passing the capacity ledger is
not a Euclidean realization certificate.

The vertex-circle side is also review-pending. The overlay does not reprove the
exhaustive `n=9` checker, and it does not promote any finite-case status. It
only joins existing artifacts by selected-row signature:

- `data/certificates/bootstrap_core_crosswalk.json`;
- `data/certificates/bridge_lemma_frontier.json`;
- `data/certificates/n9_vertex_circle_frontier_motif_classification.json`;
- `data/certificates/n9_vertex_circle_strict_cycle_path_join.json`;
- `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`.

The signature join matters: bridge-frontier source indices `81` and `151`
correspond to vertex-circle classification assignment ids `A082` and `A152`,
respectively.

## Results

Both tight non-ear assignments share the same strict-cycle template bucket:
`T12/F16`, cycle length `3`.

| Bridge source id | Classification id | Offsets | Bootstrap core | Margin | Template | Local cycle rows | Rows outside bootstrap core |
|---:|---|---|---|---:|---|---|---|
| `81` | `A082` | `[1,3,6,7]` | `[0,1,2,4]` | `8` | `T12/F16` | `[0,1,2,3,4,8]` | `[3,8]` |
| `151` | `A152` | `[2,3,6,8]` | `[0,1,2,4]` | `6` | `T12/F16` | `[0,1,5,6,7,8]` | `[5,6,7,8]` |

The overlay conclusion is deliberately narrow:

```text
T12 strict-cycle shared by the two tight non-ear cases,
but not a bootstrap-core-only contradiction.
```

For source id `81`, all three strict-edge rows lie in the bootstrap core, but
the equality connectors still need rows outside the core. For source id `151`,
even the strict-edge rows are not contained in the bootstrap core. Thus the
current data does not support a private-halo-only or core-only contradiction
lemma.

## Reading

The useful bridge signal is that the two tight cases are not two unrelated
vertex-circle phenomena. They are both relabelings of the `T12/F16` strict
cycle. A plausible next proof-mining task is therefore:

```text
bootstrap core [0,1,2,4] + small private-halo margin
  -> force a T12-like six-row strict-cycle core
```

That is still a conjectural bridge target. The current overlay only records the
finite artifact join and the row-center mismatch that any future lemma must
handle.

The follow-up ledger in
[`bootstrap-t12-forcing-targets.md`](bootstrap-t12-forcing-targets.md) breaks
this target into concrete row-center gaps and direct private-pair contacts. It
keeps the same status: proof-mining scaffolding only, not a proof that the
missing rows are forced.
