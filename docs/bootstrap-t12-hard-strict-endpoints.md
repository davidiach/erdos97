# Bootstrap T12 Hard Strict Endpoints

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the strict-edge endpoint requirements that remain hard in
the joined T12 bridge-target map. It answers a narrower question than row
forcing:

```text
Which strict-edge endpoint sets are still not supplied by the bootstrap core,
deletion closures, or stored support options?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_hard_strict_endpoints.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_hard_strict_endpoints.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_hard_strict_endpoints.json`.

## Scope

The input packets are:

- `data/certificates/bootstrap_t12_activation_requirements.json`;
- `data/certificates/bootstrap_t12_bridge_target_map.json`.

This packet is not full rich-class data. A hard strict endpoint is an unmet
relation requirement inside the stored fixed-row T12/F16 quotient certificate;
it is not a theorem that the endpoint is geometrically forced.

## Results

Both hard strict-edge endpoint requirements occur in source `151`.

| Source | Row | Gap type | Required endpoint set | Current deficit |
|---:|---:|---|---|---|
| `151` | `7` | closure-exposed missing outside endpoint | `[0,1,6]` | exposed closure has `[0,1]` but misses `6` |
| `151` | `8` | singleton supports split strict endpoints | `[1,5,7]` | support `5` misses `7`; support `7` misses `5` |

Headline counts:

```text
hard strict rows: 2
closure-sufficient strict requirements: 0
support-sufficient strict requirements: 0
partial singleton supports: 2
missing endpoint labels: 5, 6, 7
```

## Negative-Control Reading

Row `151:7` is the closure-exposed negative control. It is activation-ready in
the deletion closure for core vertex `2`, but that closure supplies only the
strict-edge endpoints `[0,1]`; the outside endpoint `6` remains private.

Row `151:8` is the singleton-support negative control. The same row has a
support-sufficient equality connector through singleton `5`, but the strict
edge needs `[1,5,7]`. The singleton supports split the strict endpoint set:
`5` supplies `[1,5]` and misses `7`, while `7` supplies `[1,7]` and misses
`5`.

## What This Does Not Prove

This artifact does not prove that any strict endpoint, row center, or rich
class is forced. It does not prove `n=9`, does not prove the bootstrap bridge,
does not independently review the vertex-circle checker, and does not alter
the official/global status of Erdos Problem #97.

## Reviewer Focus

The exact next bridge question is whether strict-edge endpoint sets can be
forced as complete rich-class subsets, rather than one endpoint at a time. A
future lemma would need a genuine geometric reason that rejects both partial
states above without assuming the fixed selected row is already present.
