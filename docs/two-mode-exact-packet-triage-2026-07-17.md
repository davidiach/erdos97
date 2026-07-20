# Two-mode exact packet triage (2026-07-17)

Status: provenance and intake decision record, not mathematical evidence.

## Source packet

- archive: `erdos97_two_mode_exact_repo_packet_2026-07-17.zip`
- archive SHA-256:
  `f421abbf148adc6df170f537858e2aa6141fef98b777015e2a7ceeb902232d2e`
- packet inventory: all 21 files matched the packet's `SHA256SUMS`
- target repository: this repository at the 2026-07-17 intake

The source archive remains external to the repository. This note records what
was accepted; it does not make the packet itself a repository dependency.

## Accepted

The following material was useful and was integrated after review:

- the exact verifier in `src/erdos97/two_mode_cyclic_exact.py`;
- its repository CLI wrapper and focused tests;
- the retained generated certificate
  `data/certificates/two_mode_cyclic_exact_n80.json`;
- a cleaned and repository-scoped proof note;
- dependency pins, generated-artifact provenance, and the slow audit command;
- conservative source-of-truth and navigation updates.

Before import, the retained certificate was independently replayed under
CPython 3.12.2, SymPy 1.14.0, python-flint 0.8.0, and mpmath 1.3.0. The replay
covered all 2,988 `(n,k)` cases, matched the stored payload and case digest,
classified all 1,865,543 real collision-root occurrences, and left zero
unresolved occurrences. The artifact SHA-256 is
`c24f6394145ea68272e024f703aada5a5d9d8410747c29587682ce71698b4268`.

## Rewritten rather than copied

The packet contained a repository-shaped overlay and semantic integration
snippets written for a generic target tree. The mathematical proof note was
cleaned semantically, and source-of-truth updates were adapted to the live
repository. No damaged prose was retained verbatim.

## Discarded

The packet-level README, file map, integration prompt, standalone source
material, duplicate metadata snippets, validation transcript, and proposed
patch fragments were not imported. They duplicate the integrated verifier,
certificate, tests, documentation, or this decision record and would create
two sources of truth.

## Claim boundary

The accepted result is a review-pending exact certificate diagnostic for the
real two-mode family
`z_i = w^i + t w^(k i)`, with `9 <= n <= 80`,
`2 <= k <= n-2`, and real `t`. It says nothing about arbitrary point
configurations, unbounded `n`, complex coefficients, or additional modes.
It is not a proof or counterexample for Erdos Problem #97, does not change the
official/global open status, and does not replace the repository's strongest
local `n <= 8` result.
