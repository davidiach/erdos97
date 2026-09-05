# Radius descent and exact n=11 research packet

Date: 2026-09-05. Repository base:
`2aae1262af21a2487e2f534f36968bfa1a3c1002`.

**No general proof and no counterexample to Erdos Problem #97 are claimed.**
This is an isolated, review-pending research packet. It does not change the
repository's source-of-truth status or accepted finite-case bound.

## Results

The complete paper argument in `proofs.md` excludes any nonempty
boundary-independent center set in which each center has two witnesses in the
set at a radius no larger than either incident side of the original polygon.
An equal-leg two-star forces a strictly smaller-radius witness at every center,
contradicting the minimum radius. This closes the whole variable-radius
alternating-center branch, not merely its reciprocal or common-radius cases.
A separate theorem shows that all endpoint-dominated short chords form a
noncrossing forest, with a matching at each individual edge length.

The independently written finite search exhausts all 210 n=11 center-0
slices with zero survivors in 114,344,315 DFS nodes. It also reproduces the
n=9 and n=10 exclusions and the 184-system n=9 incidence frontier.
This is computer-assisted finite-case review evidence, not a general proof,
external review, or an automatic promotion of n=11.

## Files and replay

- `proofs.md`: geometric proofs, exact controls and the remaining extraction gap.
- `finite-search.md`: exhaustive domain, pruning soundness, counters and limitations.
- `exact_search.cpp`: the byte-preserved C++17 source of the complete n=11 run.
- `oracle.cpp`: different-representation predicate checks and n=9 calibration.
- `results.json`: all 210 per-slice integer records, aggregate and provenance.
- `validate.py`: exact artifact, coefficient-identity and rational-control checks.
- `replay.py`: compile, execute and compare checks without third-party Python packages.
- `validation.json`: actual quick replay and undefined-behavior-sanitizer report.
- `full-validation.json`: second full n=11 regeneration report, when present.

Run in this directory with Python 3.10+ and a C++17 compiler:

```sh
python validate.py
python replay.py --quick --sanitize
python replay.py --full-n11 --jobs 8
```

The original full run and a later full regeneration are executions of the same
search source, not independent search implementations. The predicate oracle is
a second representation of local tests, not a second complete n=11 solver.
No full repository checkout was available locally, so repository-wide fast and
artifact CI were not run. Standalone validation must not be called full CI.

## Mathematical gap

An arbitrary hypothetical counterexample has not been shown to provide a
nonempty independent center set whose selected radii are bounded by both
original incident sides and whose rows retain two witnesses inside that set.
The new theorem closes that branch conditional on extraction; it does not
supply the extraction. The 66-point partial construction on main is neither
completed nor ruled out by this packet.
