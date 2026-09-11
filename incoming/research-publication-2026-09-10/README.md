# Retained continuation: general stars, Gabriel defects, and product-cycle audit

Research: September 9, 2026. Import preparation: September 10, 2026.

**Restricted research, review pending. No unrestricted proof or counterexample
to Erdős #97, accepted finite-bound promotion, or external mathematical review.**

This package preserves the supplied continuation research after the six packets
already merged in #943. Its 168 original
files remain byte-for-byte under `snapshots/`. All 133 members of the complete
product-cycle ZIP are present. Earlier incomplete exports are retained as such,
not misrepresented as complete historical source trees.

The small diamond-phase core already exists in draft PR #944, at head
`832fe620583488b5c4a1169c75b486b2debf4bad`. The five files in the latest snapshot's
`publication_core/` match that PR's five core Git blobs; they are archival mirrors,
not a second proposed version of the live packet. This import neither edits that
PR's branch nor depends on its merge. The full archive adds the evidence that
PR #944 explicitly left out, and earlier useful general-polygon controls.

## Useful results and their limits

Start with these notes rather than the historical search logs:

| Result | Research value | Scope and next obligation |
|---|---|---|
| [Diamond-phase obstruction](snapshots/product-cycle-audit-2026-09-09/proof_attempts/diamond_phase.md) | Circle completion gives phase identities that reject three systems passing separate angle and distance relaxations | Specified gain-aligned diamonds and sector order in own-side C3 geometry; independent proof review and a global extraction argument remain open |
| [Supplier-arc radial lifting](snapshots/product-cycle-audit-2026-09-09/proof_attempts/supplier_arc.md) | A written geometric lemma and exact non-vacuous control isolate a forbidden three-arrow configuration | Concentric equilateral-triangle orbits with their own-side radii and stated order; not arbitrary rich vertices |
| [Extremal-selection controls](snapshots/global-bridge-stress-2026-09-09/proof_attempts/extremal_selection_controls.md) | Exact 9- and 17-point examples refute simple minimum-enclosing-circle and one-step radius shortcuts | The examples have good vertices; they do not refute a theorem using richness at every vertex |
| [General-star angle evidence](snapshots/unrestricted-angle-bridge-2026-09-09/frontier.md) | Stored exact contradictions and positive rational angle vectors can be replayed independently of the missing search generators | Enumeration completeness is unverified; positive angle vectors are not Euclidean realizations |
| [Gabriel defect argument](snapshots/global-bridge-stress-2026-09-09/proof_attempts/gabriel_defect.md) | Written local inequality, slack identity, and obstruction to treating the defect as a bounded index | Review-pending proof candidate; two named regression scripts were not supplied |

The import's value is reproducibility, restricted geometric lemmas, and exact
negative controls. It does not establish a bridge from arbitrary all-rich
polygons to these obstructions. See [frontier.md](frontier.md) for that missing
implication and [INTEGRATION.md](INTEGRATION.md) for repository validation.

## Contents

| Snapshot | Original files | Useful contents | Claim boundary |
|---|---:|---|---|
| [Product-cycle audit](snapshots/product-cycle-audit-2026-09-09/README.md) | 133 | 333 exact fixed-system certificates; positive angle/distance relaxations; diamond-phase and supplier-arc proofs; four exact controls; bounded searches; 50 defensive tests | Own-side C3/order hypotheses; not exhaustive nine-orbit coverage |
| [General-star frontier](snapshots/unrestricted-angle-bridge-2026-09-09/frontier.md) | 19 | Two-star angle catalogue, 20/30-label certificate records, three rational geometric controls, higher-product exploratory records | Stored cases can be checked; original enumeration/search generators are incomplete |
| [Global-bridge proof notes](snapshots/global-bridge-stress-2026-09-09/proof_attempts/extremal_selection_controls.md) | 14 | Exact 9/17-point controls; 84-triple circumcenter scan; Gabriel inequality/slack/cubic-growth written argument; changed-witness diagnostics | Local controls are not all-rich; two promised Gabriel replay modules are absent |
| Loose attachments | 2 | Original ZIP-download validation and the earlier empty `circ24.json` | Historical provenance only; the empty list does not certify enumeration counts |

See [PUBLICATION_AUDIT.md](PUBLICATION_AUDIT.md) for corrections and missing
source obligations; [frontier.md](frontier.md) for the mathematical checkpoint;
[claims.json](claims.json) for claim/evidence boundaries; and
[provenance.json](provenance.json) for original byte hashes and duplicate links.

## Verification recorded during export preparation

The new isolated replay completed on Python 3.13.5, using only the standard
library. It checks 2,531 stored contradiction certificate records
(333 + 912 + 799 + 487), 1,354 positive rational two-star angle vectors, nine
exact geometric controls, and the original 50 product-cycle/core tests. It
regenerates five earlier exact reports and compares their full JSON content.
All 168 original files are hash-checked before and after.

These are stored-case certificates, not a new exhaustive search, all-order
proof, or accepted cardinality bound. The positive vectors certify necessary
relaxations, not Euclidean coordinates. Search histories, numerical ranks and
solver statuses retain their original diagnostic evidence level.

The maintained importer adds 19 defensive tests, including a second sparse
reconstruction of the earlier dense angle checker, coefficient mutation,
missing strictness, exact-rational input validation, provenance corruption,
Unicode I/O, nonzero process exits, and disabled-assertion rejection.

From this directory:

```sh
python -S publication.py
python -S publication.py --scoped --output /tmp/erdos97-publication-replay.json
python -S -m unittest -v test_research_publication_20260910.py
python -m pytest -q -o addopts='' test_research_publication_20260910.py test_research_publication_replay_20260910.py
```

The last command also executes the artifact-marked full replay. Standard pytest
collection skips immutable snapshots; the replay runs their original tests in
isolated processes. There are no root workflow or test-configuration changes.
Do not write fresh outputs under `snapshots/` or run exact checks with `-O`.

## Historical preparation status

Prepared against `main` at `9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7`.
At preparation, connected GitHub reads succeeded and the account had repository
admin permission. No branch/commit/PR-writing action was exposed in this turn;
direct Git failed DNS resolution. **No new remote branch, commit, or PR was
created.** This remains a prepared import, not a claimed completed publication.

At export preparation, repository-wide `make verify-fast`, `make verify-artifacts`, and compatibility
collection were not run locally: no complete checkout could be retrieved.
Ruff was absent in that environment. Packet tests are not those full gates. No Lean source,
accepted-status file, secret, permission, or existing certificate was changed.
These paragraphs and the retained `validation.json` describe the export session;
the subsequent repository integration is recorded in [INTEGRATION.md](INTEGRATION.md).

## Lossless storage of one historical script

The original `global-bridge-stress-2026-09-09/search/angle_hole_walk.py` has two
trailing spaces on historical lines 13 and 53. Its exact original bytes are
retained in `snapshots/global-bridge-stress-2026-09-09/search/angle_hole_walk.py.zip`
as the single member `angle_hole_walk.py`. It is not rewritten, and no whitespace
check is disabled. The parent provenance and replay verify the decoded original
bytes; the transport manifest also binds the physical ZIP. Thus 168 original
source files are preserved, with one stored losslessly as a ZIP member. This
numerical discovery script is not imported by the exact replay.
