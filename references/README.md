# References Workspace

Status: bibliography and annotation workflow scaffold only; not mathematical
evidence.

This directory tracks external sources, citation risks, and negative search
results for Erdos Problem #97 work. It complements `docs/literature-risk.md`
and `metadata/erdos97.yaml`; it does not replace either file as a source of
claim status.

## Files

- `source_manifest.yml`: canonical local ledger for external sources, nearby
  examples, literature risks, and planned searches.

Future additions may include:

- `erdos97.bib`: BibTeX entries for pinned primary references.
- `annotation_index.md`: human-readable extracted annotations and negative
  search notes.
- `literature_sweeps/`: dated summaries of search queries, databases, and
  results.

## Workflow

For each source or search target:

1. Add or update an entry in `source_manifest.yml`.
2. Link to the local note that explains how the source is used.
3. Mark whether the source is primary, secondary, official status metadata, or
   a negative search result.
4. Record caveats before using the source in proof-facing prose.
5. Update `docs/literature-risk.md` only when the risk summary changes.
6. Update `metadata/erdos97.yaml` only when canonical status metadata changes.

## Claim Discipline

- A reference entry never proves a mathematical claim by itself.
- A nearby `k=3`, common-radius, or unit-distance construction is not a
  `k=4` variable-radius counterexample.
- A negative search result is useful provenance, but it is not a theorem.
- Recheck the official Erdos Problems page before any public solution or
  counterexample announcement.
