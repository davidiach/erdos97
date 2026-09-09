# Erdős97 research continuation: six retained packets

Research: 8–9 September 2026. Import preparation: 9 September 2026.

**REVIEW_PENDING / restricted research. No unrestricted proof or counterexample,
accepted finite-bound promotion, external mathematical review, or published
novelty is claimed. Retention does not constitute mathematical acceptance.**

This directory retains all **325 source files from six delivered research ZIPs**,
byte-for-byte under `snapshots/`. The six original manifests remain unchanged.
[Provenance](provenance.json) records the ZIP hashes, exact archive membership,
file sizes, SHA256 hashes, and Git blob hashes. Five embedded preceding-packet
ZIPs match the corresponding separately delivered archives exactly.

## Contents and claim boundaries

| Retained packet | Source files | Principal written results and controls | Essential restriction |
|---|---:|---|---|
| [Co-design](snapshots/erdos97_codesign_packet_2026_09_08/README.md) | 21 | Old-vertex repair lemma; exact nine-point addition repairing the fixed seed's six old exceptions; old-support cap; four-witness middle-edge cycle control | The added vertices are good; nine-addition optimality fixes the seed and prescribed old radii |
| [Cap closure](snapshots/erdos97_cap_closure_packet_2026_09_08/README.md) | 21 | All two-old-supported finite rich caps over the fixed seed are the next recurrence triangle | Not arbitrary old coordinates or internally supported caps; old exceptions remain good |
| [Internal support](snapshots/erdos97_internal_support_2026_09_08/README.md) | 63 | One-internally-supported-vertex exclusion; two-copy obstruction; tripled-pattern certificates; different-seed positive control | Fixed seed for the cap theorem; consecutive clusters and inherited witness pools for doubling |
| [Final push](snapshots/erdos97_final_push_2026_09_09/README.md) | 90 | Parallel-parabola closure, exact locally planar/globally nonplanar rich metric controls, restricted three-block theorem, median-pattern exclusions | Deterministic target part per source part for parallel parabolas; metric controls are not planar polygons; three-block hypothesis is essential |
| [Mixed parabolic lens](snapshots/erdos97_mixed_support_2026_09_09/README.md) | 51 | Arbitrary-size mixed-witness theorem on the specified symmetric parabolic lens; exact selector controls; historical coarse two-free probe | The fixed lens geometry, not arbitrary convex boundaries |
| [Two-free closure](snapshots/erdos97_two_free_2026_09_09/README.md) | 79 | Complete fixed-seed exactly-two-internally-supported-vertex exclusion and exact three-internal-support rich-cap control | The original seed is unchanged; the positive control leaves the six old exceptions good |

These files are archival research, not an additional accepted result produced
by this import. See [publication scope and audit](PUBLICATION_AUDIT.md) and the
[current combined frontier](frontier.md) before relying on a dated snapshot's
statement that a later-resolved restricted case was still open.

For focused mathematical review, start with the mixed-lens packet's
[distance-polynomial proof](snapshots/erdos97_mixed_support_2026_09_09/proof.md).
Review the two-free packet's
[geometric reduction and certificate coverage](snapshots/erdos97_two_free_2026_09_09/proof.md)
separately: in particular, insertion-cell coverage, slot capacity, all-rich-radius
quantifiers, and witness-closed search completeness. Passing replays do not
discharge these mathematical review obligations.

## Current fixed-seed conclusion

For the unchanged nine-point seed P, assume P union Q is strictly convex and
all added vertices are rich. A vertex of Q is internally supported when **every**
radius making it rich uses at most one old point. Its witnesses need not all
belong to the internally supported subset.

The retained written results classify zero such vertices (only the next
recurrence triangle) and exclude exactly one or exactly two. A rich cap with
exactly three exists, but does not repair the six original good vertices.
Thus a complete all-rich repair of this seed needs at least three internally
supported vertices; no result here excludes all such repairs or moving seeds.
All these stronger research claims remain review-pending.

## Replay

Python 3.10+; the scoped checks also require SymPy and the repository development
dependencies. The exhaustive metric check additionally requires g++ and GMP.
Run from this directory:

```sh
# Hashes, exact inventories, all original manifest entries, nested ZIP linkage:
python publication.py

# All 262 original unit tests and bounded exact checks, in temporary copies:
python publication.py --scoped --output /tmp/erdos97-continuation-scoped.json

# Also repeat the complete two-free primary/oracle and exhaustive C++ metrics:
python publication.py --full --output /tmp/erdos97-continuation-full.json

# A single packet, with its own isolated imports:
python publication.py --scoped --packet two-free --output /tmp/two-free-scoped.json

# Fast publication tests; no heavy mathematical replay:
python -m pytest -q -o addopts='' -m 'not artifact' test_research_continuation_publication.py

# Includes the complete replay for every packet:
python -m pytest -q -o addopts='' test_research_continuation_publication.py
```

`--scoped` is **not** a full two-free exclusion replay: it checks the complete
partition generator, terminal cancellations, both sharpness implementations,
and all 58 two-free unit tests, but not geometry at every leaf through both
full mathematical replayers. It also does not repeat the exhaustive C++ metric
scans. `--full` includes both expensive obligations. The original historical
complete-run reports remain preserved and are not counted as fresh executions.

`conftest.py` excludes only `snapshots/` from direct pytest collection. The
artifact-marked tests invoke the mathematical checks in temporary subprocesses,
preventing collisions between historical names such as `verify.py`, `oracle.py`,
and `exact.py`. No root test configuration or workflow is changed. The local
Ruff exclusion likewise applies only to immutable snapshots.

The import wrapper forces UTF-8 for child processes and captured output,
including on Windows. Snapshot files have Git text conversion disabled so
checkout and staging preserve their hash-pinned bytes. The original snapshot
code is unchanged. See [integration validation](INTEGRATION_VALIDATION.md) for
checks performed in the complete checkout after the preparation session below.

## Import-preparation validation

**All 262 original unit tests and eight new publication tests passed.**
The scoped run also completed 30 exact-check/test commands with original
snapshot hashes unchanged. Fresh execution records are in [publication-validation.json](publication-validation.json)
and [reports/](reports/). They are separate from each snapshot's original
`validation.json`. Thirty-six separately attached files were compared with their
ZIP members and matched exactly. The publication harness checks every source
file before and after replay.

Repository-wide `make verify-fast`, `make verify-artifacts`, root Ruff, and
navigation generation were not executed during import preparation because a
complete checkout could not be obtained: direct GitHub access failed DNS
resolution. This is not a full CI pass. No Lean source was changed and no Lean
formalization is claimed. Ordinary PR checks, a full replay, and expert
mathematical review remain separate requirements.

Base inspected through the GitHub connector:
`047d05149382e48b602b292df4b8fc9e2da560bb` (merged PR #942).
At preparation, GitHub reads were available, but no write action was exposed;
no remote branch, commit, or PR was created by this preparation session.
