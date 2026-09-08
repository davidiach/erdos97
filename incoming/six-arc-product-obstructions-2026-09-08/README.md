# Six-arc carrier and fixed-product witness obstructions

Research and publication: 8 September 2026.

**REVIEW_PENDING restricted research. No unrestricted proof or counterexample
of Erdős Problem #97, new accepted finite bound, external mathematical review,
or published novelty is claimed.** Retention is not mathematical acceptance.

This packet preserves all **18 delivered files byte-for-byte** in `snapshot/`.
The surrounding publication files supply provenance, corrected current scope,
defensive tests, and an isolated replay. [Provenance](provenance.json) pins
sizes, SHA256 hashes, and Git blob hashes of every original file.

## Findings and boundaries

| Written result | Exact scope | What it does not establish |
|---|---|---|
| [Six-arc carrier theorem](snapshot/proof_attempts/six_arc_carrier.md) | Every nonempty finite subset of the specified six-arc carrier with parameters `0 <= t < 1/3` has a point with every positive-distance multiplicity at most three. No recurrence, subset symmetry, or convexity is assumed. | No statement for off-carrier repairs, parameters at or beyond `1/3`, or arbitrary convex polygons. |
| [Matched-equilateral lemma](snapshot/proof_attempts/matched_equilateral_orientation.md) | Six distinct strict hull points forming two equilateral triples with matched distances equal to the source triangle side must have the same labelled orientation and center. | No reciprocal matching or equality of source and target side lengths is assumed. It is not a statement about arbitrary triples or arbitrary rich centers. |
| [Fixed 27-point witness-system obstruction](snapshot/proof_attempts/product_component.md) | The specified labelled 3-by-3 projective witness system has no strictly convex realization, even with initially arbitrary centers and orientations. | No general 27-point exclusion, ban on every product system, or exclusion of changed witness assignments or longer cycles. |

The 27-point argument uses the matched-equilateral lemma, four-arrow
circle-intersection completion, a mixed-half-plane diamond obstruction, and
the exact three-step projective monodromy. The six-point orientation proof
has 30 rational contradiction certificates. Its six displayed angle identities
and the six symmetry classes are also checked by the publication tests.
Symbolic identities do not by themselves certify the geometric arguments.

An exact **12-point convex same-half-plane diamond** is a falsification control
for the overstrong claim that all such diamonds are nonconvex. It is not an
all-rich counterexample. The exact **27-point all-rich but nonconvex** control
is replayed as a separate negative control; its geometry does not substitute
for a proof excluding other realizations of the fixed witness system.

## Source context

This extends the [unbounded six-exception family](../unbounded-six-exception-family-2026-09-06/README.md)
and investigates the named system in the existing
[27-point metric product control](../../docs/c3-product-27-nonconvex-control.md).
It does not replace those sources or change the accepted
[repository state](../../STATE.md).

The original [research log](snapshot/research_log.md) is chronological and
stale in several places. Read [PUBLICATION_AUDIT.md](PUBLICATION_AUDIT.md)
for corrections, absent exploratory files, unretained commands, and the
separation between paper arguments, exact replays, and numerical diagnostics.
[frontier.md](frontier.md) states the strongest scoped conclusions and missing
unrestricted reduction. No `SOLUTION.md` is appropriate for this packet.

## Replay

Python 3.10+ is sufficient for the source syntax. The rational and algebraic
certificate checkers use only the standard library. The symbolic checker
requires SymPy; publication uses **SymPy 1.14.0**. The integration tests require
pytest. Numerical exploration additionally uses NumPy and SciPy, but is not
needed for any exact replay.

From this packet directory:

```sh
python replay.py --manifest-only
python replay.py --check --output /tmp/six-arc-product-replay.json
python -m pytest -q -o addopts='' test_publication.py
```

The explicit empty pytest `addopts` includes the artifact-marked complete
replay. In ordinary repository fast pytest, that one test is intentionally
excluded; artifact pytest includes it. No root marker, lint, or collection
configuration is changed.

The replay copies the snapshot to a temporary directory, runs all exact
checks without optimization flags, regenerates and compares six outputs,
and checks that all 18 original files remain unchanged. It never overwrites
the archived reports. The packet-local Ruff configuration excludes only the
immutable `snapshot/`; maintained publication code is linted normally.

Individual original commands, run from `snapshot/`, are:

```sh
python verify/check_opposite_triangles.py --check
python verify/symbolic_checks.py --check
python verify/exact_controls.py --which 12 --check
```

The original exact-control CLI defaults to **both** controls, while the source
response supplied only the 12-point generated artifact. Therefore do not run
its default `--check` against the immutable snapshot. The parent `replay.py`
now generates the 27-point control in isolation and compares it against
[generated/product_27_exact_nonconvex.json](generated/product_27_exact_nonconvex.json)
and its [new report](generated/exact_controls_27.json).

## Fresh publication validation

Local publication checks pass all 30 rational certificates, all 49 symbolic
identities, and the 12-point control's 120 strict supporting signs. The
previously unexecuted 27-point routine was now actually run: all 108 named
squared-distance identities and 450 strict supporting signs pass; exactly
18 vertices lie on the hull and nine are interior. All **24 publication tests**
pass, including tampered certificate/manifest rejection, the six printed
identities, complete symmetry coverage, and report regeneration.

The [local replay report](reports/local-publication-replay.json) records the
commands and evidence. The separate [hosted validation](reports/hosted-validation.json) records
a successful Python 3.12 replay, all 24 focused tests, packet Ruff, and the
repository navigation check. Replaying the same code is not external
independent mathematical review.

Repository-wide `make verify-fast`, `make verify-artifacts`, and Ruff were
**not run locally**: GitHub git access failed DNS resolution, so no complete
checkout was available, and Ruff was absent. Focused validation is not a full
repository gate. Ordinary PR CI and expert mathematical/code review remain
separate. The packet does not modify `scripts/audit_commands.json`; its full
replay is covered by the explicit command and artifact-marked test above.
