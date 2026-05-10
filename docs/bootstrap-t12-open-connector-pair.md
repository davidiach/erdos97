# Bootstrap T12 Open Connector Pair

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the equality-connector pair requirement that remains open
in the joined T12 bridge-target map. It answers a narrower question than row
forcing:

```text
Which connector pair is still not supplied by the bootstrap core, deletion
closures, or stored singleton support options?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_open_connector_pair.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_open_connector_pair.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_open_connector_pair.json`.

## Scope

The input packets are:

- `data/certificates/bootstrap_t12_activation_requirements.json`;
- `data/certificates/bootstrap_t12_bridge_target_map.json`.

This packet is not full rich-class data. An open connector pair is an unmet
relation requirement inside the stored fixed-row T12/F16 quotient certificate;
it is not a theorem that the pair is geometrically forced.

## Results

There is one open equality-connector requirement:

| Source | Row | Requirement | Required connector pair | Current deficit |
|---:|---:|---|---|---|
| `151` | `5` | `151:5:connector:1:0` | `[7,8]` | singleton `7` misses `8`; singleton `8` misses `7` |

Headline counts:

```text
open connector rows: 1
closure-sufficient connector requirements: 0
support-sufficient connector requirements: 0
partial deletion closures: 1
partial singleton supports: 2
missing connector endpoint labels: 7, 8
```

## Negative-Control Reading

Row `151:5` is the open connector-pair negative control. Its bootstrap core
contains row witnesses `[2,4]`, while the stored equality connector needs the
outside pair `[7,8]`.

The deletion closure for core vertex `2` sees endpoint `7`, but not endpoint
`8`, and the row center `5` is not in that closure. The singleton support
options also split the connector pair: support `7` supplies only `[7]` and
misses `8`, while support `8` supplies only `[8]` and misses `7`.

## What This Does Not Prove

This artifact does not prove that any connector endpoint, row center, or rich
class is forced. It does not prove `n=9`, does not prove the bootstrap bridge,
does not independently review the vertex-circle checker, and does not alter
the official/global status of Erdos Problem #97.

## Reviewer Focus

The exact next bridge question is whether a singleton-activated row can be
forced to carry both outside endpoints of an equality-connector pair, rather
than only one endpoint at a time. A future lemma would need a genuine
geometric reason that rejects the split-support state above without assuming
the fixed selected row is already present.
