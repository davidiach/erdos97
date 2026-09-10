# Repository integration - September 10, 2026

Status: research retention and reproducibility only. No general proof,
counterexample, accepted-bound change, or independent mathematical review.

## Source and preservation

- Base: `9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7` (main after PR #943).
- Supplied archive: `erdos97_all_useful_research_pr_ready_2026_09_10.zip`.
- Archive SHA256: `c41caa6d8ed0de5edd254bc5467580b5b8665c7da7446e9474f4ce87c2e67b18`.
- All 168 original snapshot contents retain their recorded hashes. One historical
  numerical script remains losslessly stored as a single-member ZIP.
- The five mirrored diamond-core files retain draft #944's source version;
  importing the archive does not accept or merge that separate draft.

The incoming inventory and packet README provide curated entry points. Parent
documentation distinguishes export-time validation from integration checks.
The packet's Ruff configuration inherits the repository rules and excludes only
immutable snapshots; their tests run in isolated subprocesses through the full
replay. The export's remote publisher and draft PR template are not imported.
Canonical mathematical status, existing certificates, and root CI remain unchanged.

## Integration validation

The isolated integration checkout uses Python 3.11.15. The packet pytest command
passes all 20 items: 19 importer tests plus the artifact-marked full replay. That
replay runs the 50 original tests, verifies 2,531 stored contradiction records,
1,354 positive rational angle vectors and nine geometric controls, and compares
five regenerated reports with their retained JSON. All 168 original snapshot
contents pass integrity checks. This is replay of stored cases, not a new search
or proof of enumeration completeness.

Repository text, status, provenance, generated navigation, Make targets and Ruff
checks pass. A local `make verify-fast` attempt also reaches an existing Apple
Clang 21 compile error in
`incoming/c3-own-side-eight-orbits-2026-09-05/search.cpp:45`:
`-Werror,-Wmisleading-indentation`. That source is byte-identical to the base
commit and is outside this import. No compiler warning or test is disabled.
Hosted Linux checks remain required. The historical `validation.json` and
`reports/` describe earlier export runs, not those hosted results.

Required commands from the repository root:

```sh
make verify-fast
make verify-artifacts
python -m pytest -q -o addopts='' incoming/research-publication-2026-09-10
```

The full 306-command artifact registry can also be run in four supported shards:

```sh
python scripts/run_artifact_audit.py --verify-only --shard-count 4 --shard-index 0
python scripts/run_artifact_audit.py --verify-only --shard-count 4 --shard-index 1
python scripts/run_artifact_audit.py --verify-only --shard-count 4 --shard-index 2
python scripts/run_artifact_audit.py --verify-only --shard-count 4 --shard-index 3
```

Every shard must pass; one shard is not a complete artifact-tier result.

Passing these commands establishes the stated replay and integration contracts.
It does not establish completeness of missing searches, Euclidean realization
of positive relaxations, or acceptance of the written all-size arguments.
