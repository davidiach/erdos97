# Artifact provenance and trust policy

`metadata/generated_artifacts.yaml` separates tracked certificate JSON into
managed and archived inventories. Managed artifacts carry byte hashes, JSON
shape, conservative claim scope, canonical `trust_class`, and replay metadata
when available. Archived legacy/exploratory artifacts remain byte-pinned and
are covered by a sorted aggregate inventory digest, but carry no live claim.

The checker rejects an archived artifact cited by `README.md`, `STATE.md`,
`RESULTS.md`, `docs/claims.md`, or `metadata/erdos97.yaml`; such a file must be
promoted to a managed entry first. It also rejects tracked certificate JSON
that appears in neither inventory.

`trust_class` is the repository's canonical review category. A payload's
native `trust` and `status` remain producer-owned metadata. Every disagreement
or missing top-level native `trust` is mapped explicitly and conservatively in
`native_trust_policy`; stale mappings fail validation and no mapping promotes a
diagnostic into a proof.

Run `python scripts/check_artifact_provenance.py` for the integrity-only check.
It does not regenerate expensive artifacts; managed replay commands are stored
separately when available.
