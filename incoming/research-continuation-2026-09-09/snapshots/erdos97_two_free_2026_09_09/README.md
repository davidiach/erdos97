# Erdős97: exact exclusion of a two-internally-supported-vertex repair

**Restricted computer-assisted proof candidate; independent mathematical
review pending. No unrestricted proof or counterexample is claimed.**

[Mathematical argument](proof.md) · [Current frontier](frontier.md) ·
[Recorded validation](validation.json)

For the specified nine-point seed, a finite strictly convex added set whose
new points are all rich cannot have exactly two new vertices whose every rich
radius uses at most one old point. Together with the preceding results, an
all-rich repair requires at least three such vertices.

An exact 15-point control attains three among a rich cap, but leaves all six
old exceptions good. It is a checked member of the existing recurrence,
not a new counterexample or construction family.

## Reproduce

All maintained code uses the Python standard library. Python 3.10 or newer
is required. Do not run the exact checkers with assertions disabled (`-O`).
No network access or repository checkout is required.

From this directory:

```sh
python -S build_certificate.py --check
python -S verify.py --check
python -S oracle.py --check
python -S last_leaf_audit.py --check
python -S sharpness.py --check
python -S audit_sharpness.py --check
python -S -m unittest -v test_two_free.py
```

The full independent replay can instead be split into four disjoint ranges:

```sh
python -S oracle_parallel.py --jobs 4 --check
```

Its combined report is required to equal the complete sequential report.
Worker ranges and exit codes are retained in `data/oracle_shards/execution.json`.
For a focused diagnostic, `verify.py --cases ...` and `oracle.py --cases ...`
accept indices 0 through 4499. A partial diagnostic cannot overwrite the full
report with `--write` and is not a complete proof replay.

To perform and record the full validation, including the 101 inherited tests:

```sh
python run_validation.py
```

This overwrites current validation logs, not the hash-bound historical input
archive. The file manifest must be regenerated after an intentional new
validation run because timing and command-output records can change.

## What the checks do

`data/certificate.json` contains all 4,500 support/region cases and complete
binary subdivision trees. The generator reconstructs them from retained
exact discovery paths. **The generator checks coverage only**; `verify.py`
and `oracle.py` recompute geometry and exhaust witness-row possibilities at
every leaf. They reject a certificate containing an unresolved leaf.

The complete forest has24,742 nodes,14,621 leaves and maximum depth 36. The
primary performs 1,170,689 exact row-search nodes; the separate search performs
1,069,214. Both test 14,146 surviving necessary row models and leave no survivor.
The 24 last witness systems each have an explicit strict-distance cancellation
in `data/last_leaf_cancellations.json`.

The rich-cap control is checked with two different methods: exact nested-
radical arithmetic, and universal rational polynomial identities plus outward
dyadic interval bounds. The latter does not infer exact equality from a small
interval or residual. Both compute all-radius bounds and 195 strict supporting
signs for the 15-point set.

The 58 new unit tests include positive controls, exhaustive comparisons of
crossing encodings, brute-force checks of small subset searches, and tampered
certificate/input rejection. Unit tests and report-counter comparisons do
not replace the two full mathematical replays.

## Files and provenance

`inputs/internal_support.zip` is the preceding delivered packet, unchanged:

```
dfd032636763cf67c45338c22f24334eb9e5b17367a0de57b00eb074cdfea0e1
```

It includes the nested earlier cap-closure and co-design packets. `prior.py`
checks the archive hash and extracts it into a temporary directory. The
primary imports its earlier primary routines; the separate checker imports
only its separate mathematical implementation. Neither modifies the archive.

`exploratory/` retains the discovery scripts and completed sweep records.
Those historical scripts contain the mounted paths used during discovery;
the authoritative full replayers above do not depend on those paths. A
portable optional fresh discovery implementation is included:

```sh
python -S discover.py --cells 2 5 --old 3 4 --output fresh-case.json
```

Any depth or node guard in discovery produces **unresolved**, not a proof.
The stored generator/replay route needs no discovery optimizer. Exact proofs
use only rational or specified algebraic arithmetic and integer combinatorics.

No repository files were changed, no PR was opened, and repository-wide CI,
Lean, outside expert review, and literature-novelty review were not performed.
The mathematical claim boundary remains restricted to the fixed seed and
support hypothesis stated in proof.md.

To check file integrity or regenerate the manifest after a deliberate new
validation run:

```sh
python tools/package.py --check
python tools/package.py
```

The file-manifest check is an integrity check, not a substitute for the
mathematical replayers. The ZIP builder also reads back and compares every
archived file byte-for-byte.
