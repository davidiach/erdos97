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

## Canonical trust classes

`scripts/check_artifact_provenance.py` accepts exactly the twelve values below
and rejects every other `trust_class`. This list is the documented form of that
closed set; `KNOWN_TRUST_CLASSES` in the checker remains the authority, and the
checker fails if the two ever disagree. Each gloss below describes how the value
is used in the manifest today. None of them, alone or together, proves Erdos
Problem #97, claims a counterexample, or changes the official/global status.

Exact certificates:

- `EXACT_OBSTRUCTION`: exact arithmetic, algebraic, interval, SMT, or formal
  certificate ruling out a stated pattern, order, or restricted class.
- `EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN`: exact obstruction covering
  every cyclic order of one fixed abstract pattern, and nothing wider.
- `SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN`: the same all-order scope,
  reached by an SMT certificate.
- `EXACT_ROUTE_PRUNING_CERTIFICATE`: exact certificate that prunes a search
  route or index window; route pruning only, not an obstruction for the class.
- `EXACT_CERTIFICATE_DIAGNOSTIC`: exact diagnostic evidence, including
  certificate analysis, constructions, negative controls, and review-pending
  bounded obstructions. The artifact's `claim_scope` supplies its precise
  mathematical scope and review qualifications; this category alone does not
  establish acceptance as a theorem.

Finite-case artifacts:

- `INCIDENCE_COMPLETENESS`: repo-local enumeration recording that a finite
  incidence search is complete at its stated size.
- `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`: checked finite-case
  checker output offered as a candidate repo-local result, with independent
  review still open.
- `MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING`: the same, at draft
  maturity rather than candidate maturity.
- `MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING_SECONDARY`: an independent
  second-source replay of such a draft, used to cross-check a primary artifact.
- `FINITE_BOOKKEEPING_NOT_A_PROOF`: exact finite counting or ledger output that
  is bookkeeping for a route, explicitly not a proof of its case.

Provenance and open diagnostics:

- `REVIEW_PENDING_DIAGNOSTIC`: the default and by far the most common class -
  a checked diagnostic whose mathematical reading is not yet reviewed.
- `REVIEW_PENDING_PROVENANCE`: retained as the record of a superseded or
  negative-control route, not as a live frontier.

## How the trust vocabularies relate

Three distinct vocabularies appear in this repository, and they are not
interchangeable:

1. The reader-facing labels in `README.md` are a deliberately coarse summary
   for someone orienting in the repository. They are not manifest values.
2. The canonical `trust_class` values above are the machine-enforced review
   categories for generated artifacts. They are the authority for what a
   checked artifact claims.
3. The `Status:` header on an individual note in `docs/` is free-form prose.
   Notes routinely combine labels, qualify them, or coin a label for one note,
   so a header is a human summary of that note's scope and is not validated
   against the canonical set.

When the two disagree in substance, the manifest `trust_class` and the
artifact's `claim_scope` govern; a note's prose header never promotes an
artifact. Deciding whether note headers should stay free-form or be constrained
to the canonical set is an open maintainer question, deliberately left open
here.

Run `python scripts/check_artifact_provenance.py` for the integrity-only check.
It does not regenerate expensive artifacts; managed replay commands are stored
separately when available.
