# Publication audit and corrected ledger

The original 18 files are preserved unchanged under `snapshot/`. This audit
is a later publication record, not an edit to their historical statements.
The archive was not supplied as a ZIP; file-by-file provenance is recorded in
[provenance.json](provenance.json). A container directory or filename is not
an independent source of mathematical authority.

## Corrections to the original ledger

Sections 5 and 6 of `snapshot/research_log.md` predate the completed six-point
orientation argument. The delivered proof notes already contain the stronger
**fixed-witness-system** statement, not merely a same-orientation component
statement. Fresh exact replay accepts all thirty opposite-orientation
certificates, including fifteen with zero contradiction bound, where strict
angle positivity is essential. The parent tests additionally verify all six
printed angle identities and their complete 30-order symmetry coverage.

Section 7 cites `search/other_rotation_diamonds.py` and
`reports/other_rotation_diamonds.json`, but neither was delivered. The cited
rotation-order search is conversation/ledger-reported exploration only. No
code, count verification, or exclusion is supplied for it here. Similarly,
interactive diamond sampling, longer-cycle probes, and projected-arrow counts
in Sections 3 and 6 have no complete replay bundle among the delivered files.
They are not used as finite-exclusion evidence. No missing coordinates or
logs have been invented.

Section 9 ends before the delivered numerical runs. The actual
`reports/nonsymmetric_circulant_probe.json` contains eight cases: four at
`n=12` and four at `n=15`. Every saved hull is incomplete; minimum separations
range from approximately `5.8e-7` to `6.3e-7` after the script's normalization.
No small-residual result is labelled an exact realization. The exact CLI
iteration limit used for these records was not saved; the retained script
is reproducible as a specified new experiment, but a byte-for-byte rerun of
that historical optimization job is not promised.

The original product Jacobian report records numerical ranks 48 and 14 at
threshold `1e-9`, with an 18-vertex floating hull. Those are numerical
diagnostics, not exact rank or realization-space dimension certificates.
The fixed-product written proof does not depend on them.

The off-carrier report contains 100 float64 cap samples and circle-root
residuals. All have incomplete hulls when **all returned supplier orbits** are
included. The script removes apparent aliases using a floating tolerance.
It does not exhaust supplier subsets, exact roots, endpoint gadgets, or
symmetry-breaking repairs. Therefore the response's broad phrasing about a
"needed supplier" being interior must be read only as this recorded sampled
all-root-union failure, not as a theorem that every available repair fails.

## New work performed at publication

The 27-point mode of the delivered `verify/exact_controls.py` had not been run
in the source response. Publication executes it in a temporary copy and stores
its new coordinates and report under `generated/`. It proves exactly the
expected control facts: 27 distinct points, four distinct named witnesses
per point, 108 distance equalities, 18 strict hull vertices, nine strict
interior points, and 450 positive hull-edge/other-point signs. The original
snapshot is not augmented with files it never contained.

The 12-point generated coordinates and all original exact reports are freshly
regenerated and compared. The symbolic comparison ignores only SymPy version
metadata; the mathematical fields must match. New 27-point outputs are
compared byte-for-byte. All original files are hash-checked before and after.

The publication adds 24 tests, including explicit rejection of missing,
duplicated, negatively weighted, coefficient-tampered, malformed and
wrong-bound certificates; manifest corruption; the six printed identities;
symmetry coverage; and the isolated full exact replay. Inventory assertions
on numerical reports are not exact verification of their geometries.

The certificate-generation LP program was not delivered. The rational
certificates themselves and the optimizer-free verifier are delivered, so
verification does not require rerunning the discovery LP. This is a replayable
finite certificate, not a claim of independently reproduced discovery.

## Research scripts and repository policy

The original numerical scripts are immutable research snapshots. They do not
integrate the repository's mandatory exact preflight. Their retention does
not certify that their patterns were viable or exempt future search from
preflight. Any promoted search utility needs that integration, explicit
benchmark handling for obstructed patterns, saved complete invocation metadata,
and the repository's ordinary code review.

No broad numerical search is rerun for publication. The exact checks import
no search implementation. No Lean proof or external expert review is supplied.
No `SOLUTION.md`, claimed unrestricted proof, accepted-bound change, or status
transition is included. Literature and public-status assertions in the source
conversation are not newly verified or promoted by this import.

## Local environment and outstanding gates

Publication uses Python 3.13.5, SymPy 1.14.0, and pytest 9.0.2 locally.
NumPy 2.3.5 and SciPy 1.17.0 are available locally, but the old optimization
jobs are not rerun. GitHub connector reads and branch writes work; direct
`git ls-remote` fails DNS resolution. Consequently repository-wide
`make verify-fast` and `make verify-artifacts` cannot run locally. Ruff is not
installed locally. These are explicit unrun gates, not passes inferred from
the 24 focused tests. No Lean sources are changed.
