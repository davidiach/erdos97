# Repository maintenance

Status: workflow guidance only; no mathematical status change.

## Stable boundaries

- `src/erdos97/`: reusable code. Group new or actively refactored families in
  subpackages such as `finite_cases/n9/`; preserve old imports where used.
- `scripts/`: command entry points and standalone independent checkers. Shared
  validation belongs in the package; independent mathematical implementations
  remain independent.
- `tests/`: existing regression paths remain valid. New grouped tests can live
  beside the matching family, for example `tests/finite_cases/n9/`.
- `data/certificates/`: new exact artifacts; `certificates/` retains legacy paths.
- `docs/`: topic maps, authored proofs, review notes, and generated inventory.
- `incoming/`: retained imported packets with explicit review boundaries.
- `reports/`: dated research records and the generated session index.

The first grouped module is `erdos97.finite_cases.n9.local_core_packet`.
Its historical script API and command path remain available. Continue by family,
checking command output, artifact bytes, old imports, and existing tests before
moving more modules. File-count reduction is not a reason to merge independent
proof algorithms.

## Shared plumbing

Use `erdos97.json_io` for stable JSON. `write_json(payload, path)` is the main
interface; `write_artifact(path, payload)` preserves the historical CLI argument
order. Use `erdos97.path_display.display_path(path, root)` for display paths.
Keep mathematical predicates and certificate logic out of generic CLI helpers.

## Generated navigation

```bash
python scripts/generate_navigation.py --write
python scripts/generate_navigation.py --check
```

This generates `docs/inventory.md` from documentation paths and
`reports/research-log-index.md` from session headings. The index is navigation,
not evidence. `docs/index.md` and `docs/topics/` are concise authored entry maps;
`docs/catalogue.md` retains earlier annotations. Old map anchors remain as
forwarding links. Do not hand-edit generated lists.

Keep `STATE.md` short: accepted scope, live obligations, and links. Detailed
pre-cleanup prose is retained in `docs/research-state-detail-2026-09-06.md`.
`RESULTS.md` and proof notes remain authored ledgers. Canonical claim status
continues to live in `metadata/erdos97.yaml`, with existing consistency checks.

For new long research sessions, prefer `reports/research-log/YYYY-MM-DD.md`,
with `## Session YYYY-MM-DD - topic` headings; the generator indexes these too.
The historical log is preserved without rewriting its content or anchors.
Do not delete failed approaches to make the tree look smaller.

## CI and merge gates

`ci_scope.py` selects expensive artifact and compatibility collection jobs from
changed paths. Every PR reports aggregate gates even when a lane is unnecessary;
failed scope detection or required jobs cannot become a successful gate.
Dependency declarations use package environment markers instead of manual lists
in workflows. The declared 3.12 snapshot remains separate reproducibility data.

Main's intended ruleset requires PRs, resolved threads, `pytest (3.12)`,
`artifact checks`, and `compatibility collection`, and blocks force pushes and
branch deletion. No minimum approval count is imposed for a sole maintainer;
this does not replace independent mathematical review. Changes to the source
snapshot referenced by a release require a generated bundle refresh and a merge
that preserves the source commit. [Contributor contract](../CONTRIBUTING.md).
