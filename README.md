# Erdos Problem #97 research log

![tests](https://github.com/davidiach/erdos97/actions/workflows/tests.yml/badge.svg)

This repository is a public research log and reproducibility workspace for
Erdos Problem #97. It is intentionally not presented as a solved-proof
repository.

## Status at a glance

- Official/global status: **falsifiable/open**.
- No general proof and no counterexample are claimed.
- Strongest local result: the selected-witness method rules out `n <= 8` in a
  repo-local, machine-checked finite-case sense.
- Independent external review is still recommended before paper-style or
  public theorem-style use of the `n <= 8` computer-assisted artifacts.
- Review-pending `n=9` and draft `n=10` artifacts are recorded for audit, but
  they are not promoted to the source-of-truth strongest local result.
- Canonical status metadata lives in
  [`metadata/erdos97.yaml`](metadata/erdos97.yaml).

## The problem

Given a strictly convex polygon, look at one vertex `v` and ask how many other
vertices can be the same distance from `v`. Erdos Problem #97 asks whether
every convex polygon has at least one vertex for which no distance occurs four
times.

Equivalently: can there be a strictly convex polygon in which **every** vertex
has four other vertices on some circle centered at that vertex?

In the selected-witness language used throughout this repo, a counterexample
would consist of:

```text
n >= 5
strictly convex points p_0,...,p_{n-1}
4-sets S_i subset {0,...,n-1} \ {i}
```

such that, for every center `i`, all squared distances

```text
|p_i - p_j|^2,  j in S_i
```

are equal. The radius may depend on `i`, the selected witness set may depend on
`i`, and the directed incidence graph need not be symmetric.

## Where to start

| If you want... | Read... |
| --- | --- |
| the short working dashboard | [`STATE.md`](STATE.md) |
| the compact results ledger | [`RESULTS.md`](RESULTS.md) |
| the proof-facing claims and caveats | [`docs/claims.md`](docs/claims.md) |
| the full documentation map | [`docs/index.md`](docs/index.md) |
| independent audit instructions | [`docs/reviewer-guide.md`](docs/reviewer-guide.md) |
| current review priorities | [`docs/review-priorities.md`](docs/review-priorities.md) |
| Codex-ready task backlog | [`docs/codex-backlog.md`](docs/codex-backlog.md) |
| the long-form synthesis | [`docs/canonical-synthesis.md`](docs/canonical-synthesis.md) |
| upstream/public status alignment | [`docs/upstream-alignment.md`](docs/upstream-alignment.md) |
| provenance and claim-history notes | [`docs/public-provenance.md`](docs/public-provenance.md), [`CHANGELOG.md`](CHANGELOG.md) |

The live GitHub issue list is here:
[github.com/davidiach/erdos97/issues](https://github.com/davidiach/erdos97/issues).

## What is currently recorded

### Local small cases

The selected-witness incidence pipeline rules out `n <= 8` in the repo-local,
machine-checked finite-case sense.

- `n <= 7`: incidence counting and the crossing/bisection lemma rule out the
  cases. The repo also keeps a reproducible `n=7` Fano enumeration because it
  is structurally useful; see
  [`docs/n7-fano-enumeration.md`](docs/n7-fano-enumeration.md).
- `n=8`: the incidence enumerator reduces all necessary survivors to 15
  canonical classes, and exact cyclic-order / perpendicular-bisector /
  equal-distance checks leave no strictly convex realization. See
  [`docs/n8-incidence-enumeration.md`](docs/n8-incidence-enumeration.md) and
  [`docs/n8-exact-survivors.md`](docs/n8-exact-survivors.md).

There is also a compact human-readable proof-note draft for the small cases in
[`docs/n8-geometric-proof.md`](docs/n8-geometric-proof.md), with an interactive
visualization at [`docs/octagon-trap.html`](docs/octagon-trap.html). That note
is still marked for independent review.

### Fixed-pattern obstructions

Several previously live selected-witness patterns are now exactly obstructed by
local filters such as crossing-bisector, mutual-rhombus, phi 4-cycle,
cyclic-crossing CSP, vertex-circle order, Altman, and Kalmanson/Farkas checks.
These are fixed-pattern or fixed-order results, not a general proof.

Useful entry points:

- [`docs/mutual-rhombus-filter.md`](docs/mutual-rhombus-filter.md)
- [`docs/phi4-rectangle-trap.md`](docs/phi4-rectangle-trap.md)
- [`docs/cyclic-crossing-csp.md`](docs/cyclic-crossing-csp.md)
- [`docs/vertex-circle-order-filter.md`](docs/vertex-circle-order-filter.md)
- [`docs/round2/round2_merged_report.md`](docs/round2/round2_merged_report.md)
- [`docs/kalmanson-two-order-search.md`](docs/kalmanson-two-order-search.md)
- [`docs/sparse-frontier-diagnostic.md`](docs/sparse-frontier-diagnostic.md)

The fixed abstract patterns `C19_skew` and `C13_sidon_1_2_4_10` are killed
across all cyclic orders by exact Kalmanson/Farkas certificate searches. That
does not settle the larger sparse frontier and does not prove Erdos #97.

Restricted symmetry-family diagnostics are also recorded. The two-orbit
circulant family has a review-pending obstruction note, and the three-orbit
program closes the `m = 4` quarter cell exactly and now has a repo-local
interval-derivative certificate for the named `m = 8, 12, 16` quarter-cell
signed-band subcases. This is still a restricted three-orbit finite-`m`
certificate, not an all-`m` obstruction or proof of Erdos #97. See
[`docs/quarter-cell-derivative-certificate.md`](docs/quarter-cell-derivative-certificate.md).

### Review-pending frontier artifacts

The repo records an exhaustive `n=9` vertex-circle checker as a candidate
repo-local finite-case extension. Its cross-check leaves 184 full
selected-witness assignments after pair/crossing/count filters, and the
vertex-circle filter kills all 184 by exact self-edge or strict-cycle
obstructions. This remains review-pending; see
[`docs/n9-vertex-circle-exhaustive.md`](docs/n9-vertex-circle-exhaustive.md).
A companion combined replay now records the same compact frontier accounting
with localized counting and explicit per-assignment obstruction certificates;
it is still audit evidence only, not an `n=9` proof or status promotion.
The Kalmanson self-edge route also has a self-contained frontier-regeneration
replay that reaches the same 184 terminal assignments and finds one strict
Kalmanson self-edge for each; it is corroborating audit evidence only.

A companion closed-descent packet reformulates the 16 compact local-core
quotient obstructions as finite descent regions and extracted strict cycles.
It is diagnostic-only local packet data, not local-lemma completeness, a bridge
proof, or an `n=9` proof; see
[`docs/n9-vertex-circle-quotient-soundness-audit.md`](docs/n9-vertex-circle-quotient-soundness-audit.md).

The `n=9` Groebner decoder follow-up is a second-source algebraic audit target,
not a status promotion; see
[`docs/n9-groebner-decoders.md`](docs/n9-groebner-decoders.md).

Bootstrap/T12 bridge-facing diagnostics are recorded as proof-mining packets
only. The singleton full-neighborhood crosswalk joins the current
one-outside-label singleton-support targets and shows that stored
vertex-circle quotient replays kill all basic-filter survivors in those
selected-row neighborhoods; it does not prove singleton-support existence, row
forcing, `n=9`, or the bridge. See
[`docs/bootstrap-t12-singleton-full-neighborhood-crosswalk.md`](docs/bootstrap-t12-singleton-full-neighborhood-crosswalk.md).
The remaining outside-pair target `151:6` now has the analogous
full-neighborhood vertex-circle packet: basic filters leave `28` complete
assignments and vertex-circle replay kills all `28`, still without proving
outside-pair support existence, row forcing, `n=9`, or the bridge. See
[`docs/bootstrap-t12-151-6-outside-pair-full-neighborhood-vertex-circle.md`](docs/bootstrap-t12-151-6-outside-pair-full-neighborhood-vertex-circle.md).
Its connector contract now isolates the smaller bridge target: an endpoint-`8`
outside support at center `6` would give connector `[0,6]=[8,6]`, while the
private-halo-only pair `[3,5]` is the connector-avoiding escape still open.
See
[`docs/bootstrap-t12-151-6-outside-pair-connector-contract.md`](docs/bootstrap-t12-151-6-outside-pair-connector-contract.md).
The current label-`4` transfer ledger collapses that private lane to six
equal-length segment components, including the unique row-`6` cascade
`D[0,6]=D[4,5]=D[5,6]`; a companion cyclic-arc negative control shows each
component is feasible by itself, so any obstruction must use extra
private-support or rich-class hypotheses. The support-hypothesis ledger then
pins those extra inputs: the cascade needs center `5` with witnesses `[4,6]`
and center `6` with witnesses `[0,5]`, while no label-`4` transfer support
requirement is the exact private pair `[3,5]`. The cascade row-criticality
packet then checks the three auxiliary-center-`5,8` cascade signatures: the
full local row package `{5,6,8}` is strict-cycle obstructed, but every
nonempty proper row truncation is quotient-clean. Thus a bridge proof must
also force the row-`8` strict endpoint row, not only the row-`5`/row-`6`
cascade equalities. A follow-up endpoint-target packet sharpens that row-`8`
requirement: for each stored cascade package, any center-`8` rich class
containing witnesses `[0,4,6]` keeps the quotient replay obstructed. A
center-`8` rich-triple preflight then checks the current support evidence and
records that this target is not yet forced: the label-`4` support ledger has
requirements at centers `5`, `6`, and `7`, with no centered support
requirement at center `8` and no support requirement containing the full
triple `[0,4,6]`. The source-crosswalk follow-up prevents reusing the existing
source-`151` row-`8` singleton packet for that target: its row-`8` activation
family is built from core `[1,2]` and singleton supports `[5,7]`, so no checked
candidate contains even a pair from `[0,4,6]`. A core-route follow-up then
joins the private-lane strict-core split with the endpoint target: `8` of `9`
center-`8` local cores contain `[0,4,6]`, but only `4` of the `32`
label-`8`-visible cores are label-`8`-visible and target-compatible, and `6`
of the `12` private-lane assignments still have no center-`8` target core. The
next useful lemma must force a target-compatible center-`8` local core, not
merely label-`8` visibility. A residual target-row split then shows that four
of those six residual assignments contain `[0,4,6]` only as off-center rows
at centers `2`, `5`, or `7`, while assignments `0` and `11` contain no full
target triple in any strict-core row. Thus the remaining lane asks for either
center migration or a separate target-sparse obstruction. A target-sparse
completion preflight then checks the cheapest repair for assignments `0` and
`11`: all `12` one-row completions of target-pair rows to `[0,4,6]` fail
basic filters before vertex-circle replay. This blocks a one-row repair, but
does not prove those assignments impossible. A repair-extension follow-up then
allows one additional non-completion row replacement after each target
completion; all `6624` such candidates still fail basic filters, so even the
one-completion plus one-repair route is blocked without proving an exact
target-sparse obstruction. A depth-two repair packet then allows two
additional non-completion row replacements after the target completion; all
`1599696` one-completion plus two-repair candidates still fail basic filters,
so this selected-row repair route is blocked through two arbitrary extra rows
without proving a geometric target-sparse obstruction. A support-cone follow-up
then adds the cascade support equalities center `5` with `[4,6]` and center
`6` with `[0,5]`; target-pair and completion probes still have no bounded
one- or two-row Kalmanson/Altman cone certificate, while center-`8`
endpoint-augmented probes are covered in `27` of `30` cases and leave exactly
three assignment-`0` endpoint rows as next certificate targets. A full-cone
miss follow-up then probes those three quotients with arbitrary nonnegative
weights over the same `255` natural-order Kalmanson/Altman strict rows; HiGHS
reports both normalized zero-sum and nonpositive LP screens infeasible, but no
exact dual infeasibility certificate is stored. The dual-certificate follow-up
then stores exact nonnegative integer separating potentials for those same
three quotients, with minimum strict-row dot `1` and potential weight sums
`250`, `253`, and `243`; this certifies only that the current row family
cannot produce either normalized screen. A fixed alternate-order follow-up for
cyclic order `[0,1,2,3,4,5,7,8,6]` then gives tiny exact Kalmanson zero-sum
certificates for the same three quotients, with row counts `10`, `10`, and
`9`; this is a fixed-order obstruction only. An order-sensitivity crosswalk
then records the route decision: the current certificate evidence needs order
forcing, a stronger row family, or endpoint geometry before it can become an
all-order target-sparse obstruction. This is still route-pruning
bookkeeping, not a proof that assignments `0` and `11` are impossible. See
[`docs/bootstrap-t12-151-6-label4-transfer-length-components.md`](docs/bootstrap-t12-151-6-label4-transfer-length-components.md)
and
[`docs/bootstrap-t12-151-6-label4-transfer-component-feasibility.md`](docs/bootstrap-t12-151-6-label4-transfer-component-feasibility.md),
plus
[`docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md`](docs/bootstrap-t12-151-6-label4-support-hypothesis-ledger.md)
and
[`docs/bootstrap-t12-151-6-label4-cascade-row-criticality.md`](docs/bootstrap-t12-151-6-label4-cascade-row-criticality.md),
with
[`docs/bootstrap-t12-151-6-label4-cascade-endpoint8-targets.md`](docs/bootstrap-t12-151-6-label4-cascade-endpoint8-targets.md)
and
[`docs/bootstrap-t12-151-6-label4-center8-rich-triple-preflight.md`](docs/bootstrap-t12-151-6-label4-center8-rich-triple-preflight.md)
plus
[`docs/bootstrap-t12-151-6-label4-center8-source-crosswalk.md`](docs/bootstrap-t12-151-6-label4-center8-source-crosswalk.md)
and
[`docs/bootstrap-t12-151-6-label4-center8-core-route.md`](docs/bootstrap-t12-151-6-label4-center8-core-route.md),
plus
[`docs/bootstrap-t12-151-6-label4-center8-residual-target-rows.md`](docs/bootstrap-t12-151-6-label4-center8-residual-target-rows.md)
and
[`docs/bootstrap-t12-151-6-label4-center8-target-sparse-completions.md`](docs/bootstrap-t12-151-6-label4-center8-target-sparse-completions.md),
plus
[`docs/bootstrap-t12-151-6-label4-center8-target-sparse-two-row-repairs.md`](docs/bootstrap-t12-151-6-label4-center8-target-sparse-two-row-repairs.md)
and
[`docs/bootstrap-t12-151-6-label4-center8-target-sparse-three-row-repairs.md`](docs/bootstrap-t12-151-6-label4-center8-target-sparse-three-row-repairs.md),
plus
[`docs/bootstrap-t12-151-6-label4-target-sparse-support-cone.md`](docs/bootstrap-t12-151-6-label4-target-sparse-support-cone.md)
and
[`docs/bootstrap-t12-151-6-label4-target-sparse-full-cone-misses.md`](docs/bootstrap-t12-151-6-label4-target-sparse-full-cone-misses.md),
with
[`docs/bootstrap-t12-151-6-label4-target-sparse-full-cone-dual-certificates.md`](docs/bootstrap-t12-151-6-label4-target-sparse-full-cone-dual-certificates.md)
and
[`docs/bootstrap-t12-151-6-label4-target-sparse-alt-order-kalmanson.md`](docs/bootstrap-t12-151-6-label4-target-sparse-alt-order-kalmanson.md),
plus
[`docs/bootstrap-t12-151-6-label4-target-sparse-order-sensitivity-crosswalk.md`](docs/bootstrap-t12-151-6-label4-target-sparse-order-sensitivity-crosswalk.md).
On the source-`81` side, the `81:3` ordered chain-closure, one-layer
repeated-support, two-repeated-support, and repeated-support saturation packets
close the current bounded support-chain continuations under basic
incidence/crossing filters, but still do not prove support existence, row
forcing, genuine rich-class order, `n=9`, or the bridge. See
[`docs/bootstrap-t12-81-3-chain-closure-csp.md`](docs/bootstrap-t12-81-3-chain-closure-csp.md)
and
[`docs/bootstrap-t12-81-3-repeated-support-catalogue-audit.md`](docs/bootstrap-t12-81-3-repeated-support-catalogue-audit.md),
plus
[`docs/bootstrap-t12-81-3-two-repeated-support-catalogue-audit.md`](docs/bootstrap-t12-81-3-two-repeated-support-catalogue-audit.md)
and
[`docs/bootstrap-t12-81-3-repeated-support-saturation-audit.md`](docs/bootstrap-t12-81-3-repeated-support-saturation-audit.md).

An incoming `n=10` singleton-slice continuation is recorded as a finite-case
draft review target only; see
[`docs/n10-vertex-circle-singleton-slices.md`](docs/n10-vertex-circle-singleton-slices.md).
It now has a portable C++ second-source replay that matches all 126 stored
singleton rows, still as review evidence only and not an `n=10` proof.

### Numerical near-misses

The historical best saved near-miss is `B12_3x4_danzer_lift`. It is useful as
a degeneration diagnostic, but it is **not** a counterexample. Its fixed
selected pattern is now exactly killed by the mutual-rhombus midpoint filter,
and the saved floating-point artifact is retained only as provenance for a
failed route.

```text
n: 12
pattern: B12_3x4_danzer_lift
max squared-distance spread: 0.006806368780585714
RMS equality residual:       0.0019599509549614457
convexity margin:            9.999999943508973e-07
minimum edge length:         0.0007465865604262556
status: numerical artifact only; fixed selected pattern exactly killed
```

Any proposed counterexample needs exact coordinates, an exact algebraic
certificate, an interval certificate, an SMT certificate, or a formal proof
covering both the distance equalities and strict convexity. Numerical
near-misses are not counterexamples.

## Trust labels

The repo uses explicit labels so that proof, computation, and exploration do
not blur together:

- `THEOREM` / `LEMMA`: proved local statements.
- `MACHINE_CHECKED_FINITE_CASE_ARTIFACT`: checked finite-case result in the
  repo-local sense.
- `EXACT_OBSTRUCTION`: exact arithmetic, algebraic, interval, SMT, or formal
  certificate killing a stated pattern or class.
- `NUMERICAL_EVIDENCE`: floating-point evidence only.
- `HEURISTIC` / `CONJECTURE`: search guidance or plausible but unproved
  mathematics.
- `COUNTEREXAMPLE_CANDIDATE`: requires independent verification and is not a
  counterexample claim.

See [`docs/claims.md`](docs/claims.md) and
[`docs/verification-contract.md`](docs/verification-contract.md) for the
proof-facing standard.

## Repository map

```text
.
|-- README.md
|-- STATE.md                  # short working dashboard
|-- RESULTS.md                # compact results ledger
|-- metadata/
|   `-- erdos97.yaml          # canonical status metadata snapshot
|-- docs/                     # proofs, audits, provenance, and planning notes
|-- src/erdos97/              # reusable search and verification code
|-- scripts/                  # command-line checkers and generators
|-- tests/                    # pytest coverage for code and artifacts
|-- data/                     # checked JSON artifacts and numerical runs
`-- certificates/             # legacy n=8 certificate paths
```

New generated checked certificates should normally live under
`data/certificates/`. The top-level `certificates/` directory is retained for
legacy n=8 artifacts and manual templates whose paths are already referenced by
docs, tests, and manifests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make verify-fast
```

If `make` is not available, run the fast tier directly:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

`make verify-lint` runs the sub-minute text/status/provenance/ruff tier without
pytest. The default pytest configuration excludes tests marked `artifact`,
`slow`, or `exhaustive`; run `python -m pytest -q -m ""` only when you
intentionally want the full marker set.

For a version-matched reproduction environment, install the checked dependency
snapshot before installing this package:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

## Artifact checks

Run the artifact tier before finite-case, certificate, or public
theorem-style updates:

```bash
make verify-artifacts
```

For CI-style metadata capture, run:

```bash
make audit-artifacts
```

Both targets use the command registry in
[`scripts/run_artifact_audit.py`](scripts/run_artifact_audit.py): `verify-artifacts`
runs the registry without metadata capture, while `audit-artifacts` records
per-command stdout/stderr and environment metadata. If `make` is unavailable,
use `python scripts/run_artifact_audit.py --verify-only` for the same raw
artifact command set.

Useful exploratory commands:

```bash
erdos97-search --list-patterns
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
python scripts/interval_verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
python scripts/check_mutual_rhombus_filter.py --assert-expected
python scripts/check_vertex_circle_order_filter.py --pattern P18_parity_balanced --search --assert-obstructed
python scripts/check_min_radius_filter.py --pattern C19_skew --assert-pass
```

Optional dependencies for selected exactification paths:

```bash
pip install sympy z3-solver
```

## Research hygiene

1. Do not present floating-point equalities as exact.
2. Keep search heuristics separate from necessary mathematical constraints.
3. Record failed approaches clearly enough that future work avoids repeating
   them.
4. Prefer small reproducible JSON artifacts over screenshots or prose-only
   claims.
5. Do not prepare OEIS submissions from AI-generated output.

## Nearby examples

The 3-neighbor version is false: Danzer produced a 9-point convex polygon
where every vertex has 3 equidistant vertices, and Fishburn-Reeds produced a
20-point convex polygon where every vertex has 3 equidistant vertices at a
common radius. These examples do not automatically extend to the 4-neighbor
target.

A 1975 Erdos paper reports an unpublished all-`k` Danzer claim, but the
official #97 page says this was not repeated later and was presumably
mistaken. This repository treats that statement as unverified literature risk,
not as a `k=4` counterexample; see
[`docs/literature-risk.md`](docs/literature-risk.md).

## Contribution policy

Contributions are welcome if they are reproducible and clearly labelled.
Especially useful contributions include:

- independent verification scripts;
- exact obstruction lemmas;
- interval, SOS, SMT, or formal certificates for restricted classes;
- new incidence patterns satisfying known necessary filters;
- numerical candidates with robust convexity margins and residual below
  `1e-10`.

Please avoid presenting numerical near-equalities as counterexamples.

## License and citation

Code is licensed under the MIT License. Research notes, documentation, data
artifacts, issue templates, and certificate templates are licensed under
CC-BY-4.0. See [`LICENSE.md`](LICENSE.md).

If you use this repository, please cite it using
[`CITATION.cff`](CITATION.cff).

## Maintenance checklist

- Run `make verify-fast` or the equivalent raw fast-tier commands after code or
  documentation changes.
- Run `make verify-artifacts` before finite-case, certificate, or public
  theorem-style updates, or record exactly why a command could not be run.
- Keep `README.md`, `STATE.md`, `RESULTS.md`, and
  `metadata/erdos97.yaml` aligned when a source-of-truth status changes.
- Confirm this README still says no general proof and no counterexample are
  claimed.
- Keep current-work pointers aligned with
  [`docs/review-priorities.md`](docs/review-priorities.md),
  [`docs/codex-backlog.md`](docs/codex-backlog.md), and the live GitHub issue
  list.
