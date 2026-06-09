# Bootstrap T12 151:6 Outside-Pair Escape Partition

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note partitions the source-`151` row-`6` outside-pair full-neighborhood
vertex-circle packet by the connector role of the row-`6` support pair. It is a
derivative crosswalk over two existing checked packets:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_escape_partition.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_escape_partition.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_151_6_outside_pair_escape_partition.json`.

## Scope

The source packets are:

- `data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`;
- `data/certificates/bootstrap_t12_151_6_outside_pair_connector_contract.json`.

The partition keeps the `151:6` target fixed to the thirteen candidate
bootstrap-core-plus-outside-pair rows from the full-neighborhood packet and
classifies each candidate row as:

- `private_halo_only_connector_avoiding`: contains pair `[3,5]` and avoids
  endpoint `8`;
- `endpoint8_connector_available`: contains `[3,8]` or `[5,8]` and does not
  also contain `[3,5]`;
- `mixed_private_and_endpoint8`: the original row `[0,3,5,8]`, which contains
  both the private pair and endpoint-`8` connector supports.

## Partition Result

| Partition | Candidate rows | Basic survivors | Vertex-circle statuses | Vertex-circle survivors |
| --- | ---: | ---: | --- | ---: |
| `private_halo_only_connector_avoiding` | 4 | 12 | `self_edge: 10`, `strict_cycle: 2` | 0 |
| `endpoint8_connector_available` | 8 | 9 | `self_edge: 7`, `strict_cycle: 2` | 0 |
| `mixed_private_and_endpoint8` | 1 | 7 | `self_edge: 3`, `strict_cycle: 4` | 0 |

Combined:

```text
connector-avoiding basic survivors:   12
connector-available basic survivors:  16
total basic survivors:                28
vertex-circle survivors:               0
```

The named connector-avoiding lane is therefore not killed by the basic
incidence/crossing filters. It is killed only when the stored exact
vertex-circle quotient replay is applied.

## Interpretation

The connector contract already says that endpoint-`8` outside supports
`[3,8]` and `[5,8]` would supply the needed equality connector at center `6`,
while private-halo-only `[3,5]` is the unique connector-avoiding support pair
in the current ledger.

This partition shows where that escape sits inside the full-neighborhood
packet: private-halo-only `[3,5]` rows leave `12` complete basic-filter
assignments, all in the non-original row `[0,3,5,7]`, and all are then
obstructed by vertex-circle replay.

## Remaining Gap

This artifact does not prove outside-pair support existence, does not prove
row forcing, and does not prove that pair `[3,5]` is impossible. The next
proof-facing target is still:

```text
Force an endpoint-8 outside support, or prove that the private-halo-only
[3,5] escape cannot occur under genuine minimal/rich-class hypotheses.
```

## What This Does Not Prove

This artifact does not prove `n=9`, the bootstrap bridge, Erdos Problem #97, or
a counterexample. It is a finite diagnostic crosswalk for one
relation-sufficient outside-pair row target.
