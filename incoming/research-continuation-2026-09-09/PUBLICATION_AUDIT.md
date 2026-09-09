# Publication audit: scope, chronology, and evidence

Prepared 9 September 2026 from six delivered ZIP files and 36 separate
attachments. **This is a retention/publication task, not new mathematical
research or independent expert review.**

## Preservation

All 325 original archive members are retained byte-for-byte, including source
code, proofs, exploratory runs, historical reports, manifests, and embedded
preceding-packet ZIPs. All 319 entries in the original manifests match. The
six manifests exclude themselves; the outer provenance also hashes them.
All 36 separate attachments match their corresponding archive members.

Five embedded ZIPs match separately delivered predecessor archives: cap closure
contains co-design, internal support contains cap closure, and final push,
mixed lens, and two-free closure each contain internal support. These binary
inputs are intentionally retained: their original replayers hash and extract
them. They are not replaced with imports from a mutable neighboring directory.
The outer provenance links them without modifying the archived evidence.

No accepted mathematical-status file is changed. The only existing repository
file edited is the navigation inventory `incoming/README.md`; it gains one
entry and an updated entry count. Previously merged PRs #940–#942 are not
republished as new findings. Embedded historical inputs retain their original
bytes and names.

## Chronological statements are not current claims

The cap-closure packet's one-free relaxation and mixed-lens packet's two-free
probe are coarse historical relaxations. The later exact one-free and two-free
packets close those cases under their fixed-seed hypotheses. All old survivor
counts and "open" statements remain as dated provenance, not current claims.
The combined frontier records the later conclusions without editing snapshots.

Likewise, the final-push opposite-chain parabola theorem is not a mixed-witness
theorem. The mixed-lens packet later treats arbitrary mixed witnesses only for
the stated symmetric lens. Its scope must not be inflated to all parallel
parabolas. The all-size metric control is not globally planar. The three-block
bound is not an accepted or general n <= 16 result.

The exact three-internal-support cap is an existing recurrence continuation,
checked as a sharpness control. It leaves all six old exceptions good. It is
not a counterexample, an all-rich repair, or a reason to exclude size three.

## Fresh checks versus retained reports

Fresh scoped executions are recorded separately in `publication-validation.json`
and `reports/`. They run every original unit suite exactly once at its own
packet location (262 tests total), along with the commands named by the
publication harness. They do not invoke nested predecessor suites a second
time and then count those duplicate executions as additional tests.

The complete two-free primary and separate geometry replayers, and the two
exhaustive C++ metric scans, are retained as original reports but are not
represented as newly executed by the scoped run. `publication.py --full`
provides that repeatable path and fails on command errors or timeouts.
Partition generation alone proves neither geometry nor witness realizability.
The existing checkers still validate only their stated certificate models;
the human geometric reduction remains a separate obligation.

No original validation record is overwritten to make publication appear to
have happened earlier. Fields such as `pull_request_opened: false` and mounted
paths in discovery scripts are preparation-session provenance. The portable
mathematical replayers, not ad hoc exploratory scripts, are the authoritative
execution entry points.

## Test collection and code boundaries

Many original scripts intentionally use the same flat module names. Direct
repository-wide collection would mix those modules. A new packet-local
`conftest.py` ignores only immutable `snapshots/`; the uniquely named
`test_research_continuation_publication.py` supplies publication tests and
artifact-marked complete subprocess replays. This preserves original code
and avoids the collection collision previously encountered in PR #942.
No root pytest policy, workflow, or accepted-certificate checker is weakened.

The new wrapper checks safe paths, symlink rejection, complete membership,
SHA256/Git-blob identity, predecessor linkage, subprocess return codes, and
post-replay preservation. It does not alter the mathematics. Temporary copies
isolate regenerated files from archived proofs and certificates.

## Publication status and unperformed gates

The current default ref was read through GitHub and resolved to
`047d05149382e48b602b292df4b8fc9e2da560bb`. The exposed GitHub actions provide
reads but no repository-write or PR-create action. A direct Git probe failed:
`fatal: unable to access 'https://github.com/davidiach/erdos97.git/': Could not resolve host: github.com`.
There was no authenticated GitHub CLI available. No remote write or PR was made
by this preparation session. A binary-safe patch and a draft-PR publisher were
prepared for use from an authenticated checkout instead.

Repository-wide `make verify-fast`, `make verify-artifacts`, and root Ruff were
not run because no complete checkout was available. No hosted CI was triggered.
No Lean source changed; Lean compilation, mathematical formalization, external
expert review, and literature-novelty review were not performed. None is
inferred from passing isolated publication checks. The PR should remain draft
until the relevant repository gates and review obligations are addressed.

The cap-closure source proof has two intentional trailing-double-space Markdown
hard breaks in its date/status header. Exact-path `.gitattributes` rules permit those two hard breaks and terminal
blank lines in 19 retained stdout files, without changing any archived bytes.
The exception list is explicit; it does not exempt mathematical Python/C++
sources, future files, or files outside the snapshot. All other whitespace
checks remain active.
