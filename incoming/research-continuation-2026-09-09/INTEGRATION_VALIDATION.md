# Complete-checkout integration, 9 September 2026

This is repository integration evidence, not independent mathematical review.
No general proof, counterexample, accepted finite-bound promotion, or change to
the canonical status is claimed.

The import is based on `047d05149382e48b602b292df4b8fc9e2da560bb` (PR #942).
The six continuation packets are additional retained research; the previously
merged packets remain in place. All 325 snapshot files match their original
SHA256 and Git blob hashes, including nine historical logs normally ignored by
the root log rule. All 319 original manifest entries and five nested archive
links verify. Original snapshot files and preparation reports are unchanged.

## Integration fixes

- Disable Git text conversion within the immutable snapshots.
- Force UTF-8 for replay subprocesses and captured output on Windows.
- Report unittest skip events explicitly. A skipped test class is one event,
  not necessarily one omitted test method.
- Add real-subprocess regression tests for Unicode, failure exit codes, and
  skipped test classes. The focused publication suite now has eleven tests.
- Link the mixed-lens proof and two-free reduction as separate review targets.

## Fresh scoped replay

On Windows with Python 3.12.2, the following command completed all 30 commands
and all six packets, preserving the original source hashes before and after:

```sh
python publication.py --scoped --output continuation-scoped-windows.json
```

The [execution record](reports/integration-scoped-windows.json) reports **258
unit tests run**, not the preparation session's 262. The four methods in the
final-push C++ test class were not run because `g++` is unavailable. unittest
reports that class-level omission as one skip event. The
[final-push rerun](reports/integration-final-push-windows.json) verifies the
updated wrapper exposes that event: 62 tests run, one skip event. The other
five packet counts are 31, 30, 40, 37, and 58.

The eleven focused publication tests pass. The six complete packet replays
also collect successfully under the artifact marker. The scoped run does not
replace the complete two-free or exhaustive C++ metric replays.

## Repository checks and remaining gates

Text cleanliness, status consistency, artifact provenance, generated navigation,
documentation index coverage, generated Make targets, Ruff, and staged diff
whitespace checks pass.

The fast pytest run with four workers initially recorded 2,167 passes, 27
skips, and four failures. Two failures are the existing Bash gate tests, which
also fail on files copied directly from the unmodified base: Windows resolves
`bash` to an inaccessible WSL launcher. Another is the existing multiprocessing
test, blocked by Windows named-pipe permissions. The release-packet check
requires a clean committed worktree and rejected the staged import. These
failures must be distinguished from a successful full fast-tier run.

The current registry-wide command `python scripts/run_artifact_audit.py
--verify-only` was attempted. Its first nine commands passed; it was interrupted
during command 10, `python
scripts/sweep_c19_kalmanson_prefix_windows_catalog_prefilter.py --json
--assert-expected`, a prolonged unchanged C19 search. The 306-command tier is
not reported as passed. The shorter artifact tier supplied with the task is
checked separately; it is not a substitute for the current full registry.

The command `python publication.py --full --packet final-push` requires `g++`
and GMP and cannot complete in this environment. The historical exhaustive
metric reports remain preserved. Hosted checks and expert review remain
separate gates. No Lean sources changed.
