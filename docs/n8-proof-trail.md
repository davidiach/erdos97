# n <= 8 Human-auditable Proof Trail

Status: `REVIEW_PACKET_ONLY`.

Claim scope: reviewer map for the repo-local `n <= 8` machine-checked
selected-witness result and the review-pending human-readable small-case
routes.

Source of truth: `README.md`, `STATE.md`, `RESULTS.md`, `docs/claims.md`, and
`metadata/erdos97.yaml`.

Last assembled: 2026-06-04.

## Non-claims

- This trail does not prove Erdos Problem #97.
- This trail does not claim a counterexample.
- This trail does not update the official/global status.
- This trail does not claim that independent external review has happened.
- This trail does not promote review-pending `n=9`, draft `n=10`, or
  fixed-pattern artifacts.

## Purpose

The repository already has two complementary routes for the small cases:

- a compact geometric proof-note route for all bad convex polygons with
  `n <= 8`;
- a repo-local machine-checked selected-witness route for the `n <= 8`
  finite cases, with focused audit helpers for the delicate `n=8` survivor
  certificates.

This file is a reviewer map across those routes. It is meant to make clear
which files to read, which commands validate each artifact layer, and which
review outcomes are safe to record.

## Route A: geometric octagon trap

Primary file: `docs/n8-geometric-proof.md`.

This is the shortest human-readable route. It uses no selected-witness
enumeration and no algebraic certificates.

Proof skeleton:

1. For any unordered base pair `{a,b}`, strict convexity permits at most one
   isosceles apex on each side of line `ab`.
2. Therefore the number `T(A)` of apex-counted isosceles triples satisfies
   `T(A) <= n(n-2)`.
3. A bad polygon contributes at least `binom(4,2)=6` triples at each vertex,
   so `T(A) >= 6n`, forcing `n >= 8`.
4. In the octagon case, equality must hold everywhere. Every vertex has
   distance-class profile `(4,1,1,1)`, every side has exactly one apex, and
   every diagonal has exactly two apices, one on each side.
5. Length-2 diagonal saturation forces all side lengths equal.
6. Length-3 diagonal saturation forces every adjacent exterior-turn pair to
   contain a turn of size `2*pi/3`.
7. Any vertex cover of the 8-cycle has size at least `4`, so the total exterior
   turn would be at least `8*pi/3`, contradicting the strict-convex total
   `2*pi`.

Review burden:

- Check the base-apex lemma's use of strict convexity.
- Check that equality in the global count forces equality in every individual
  base-pair capacity and every vertex contribution.
- Check the length-2 and length-3 diagonal saturation steps.
- Check the exterior-turn formula for equilateral convex polygons.
- Check the final 8-cycle vertex-cover contradiction.

Safe outcome if accepted: this route can serve as the main human-readable
small-case proof note, still with source-of-truth status kept separate from the
official/global problem.

## Route B: selected-witness finite artifact

Primary files:

- `docs/n7-fano-enumeration.md`
- `docs/n8-incidence-enumeration.md`
- `docs/n8-exact-survivors.md`
- `papers/n8-reviewer-packet.md`

This is the current source-of-truth finite-case route in the repository. It
supports the selected-witness `n <= 8` exclusion in a repo-local,
machine-checked finite-case sense.

Artifact skeleton:

1. The two-circle cap and crossing/bisection sharpen the incidence count and
   exclude `n <= 7`; the retained `n=7` Fano enumeration is a reproducible
   equality-case check.
2. For `n=8`, the witness-pair cap forces every witness indegree to equal `4`.
3. The incidence enumerator fixes row `0` to witnesses `{1,2,3,4}` by
   relabeling, enumerates the necessary incidence systems, and reduces them
   to `15` canonical survivor classes.
4. The exact survivor checker kills those `15` classes: one by cyclic-order
   noncrossing, ten by exact rational `y_2` span certificates, class `3` by a
   duplicate vertex, class `4` by collinearity, class `5` by a Groebner
   contradiction, and class `14` by PB+ED Groebner branches with strict
   interior failure.

Core commands:

```bash
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
```

Focused audit commands:

```bash
python scripts/independent_n8_obstruction_recheck.py --check --json
python scripts/check_n8_class14_certificate.py --check --json
python scripts/check_n8_residual_certificates.py --check --json
```

Expected invariants:

- incidence completeness records `117072` balanced cap matrices with row `0`
  fixed, `4560` forced-perpendicular survivors with row `0` fixed, and `15`
  canonical survivor classes;
- the exact survivor pass rejects all `15` reconstructed classes;
- class `12` has zero compatible cyclic orders;
- ten classes are killed by exact rational `y_2` span certificates;
- classes `3`, `4`, `5`, and `14` report their named exact certificates as
  verified;
- the SymPy-free independent recheck kills classes
  `[0,1,2,6,7,8,9,10,11,12,13]` and explicitly leaves
  `[3,4,5,14]` to Groebner-dependent review.

Safe outcome if accepted: this route supports the existing repo-local
machine-checked `n <= 8` selected-witness artifact. Public theorem-style use
still needs independent review of the incidence assumptions, exact
certificates, and source-of-truth wording.

## Route C: literature-backed shortcut

Primary file: `docs/dumitrescu-isosceles-n8-shortcut.md`.

This is a compact external-bound route. Dumitrescu's convex-position bound for
apex-counted isosceles triangles gives

```text
Z(P) <= (11 n^2 - 18 n) / 12.
```

A 4-bad polygon gives `Z(P) >= 6n`, hence `n >= 90/11 > 8`.

Review burden:

- Check the cited bound and its counting convention.
- Check that the repository's `Z(P)` convention matches the literature
  convention.
- Keep this route separate from the selected-witness source-of-truth artifact
  unless an independent review explicitly accepts the literature dependency.

Safe outcome if accepted: this route gives a short paper-facing shortcut for
the small cases, but it does not move the official/global status or promote
any `n=9` result.

## Evidence matrix

| Layer | Covers | Does not cover |
| --- | --- | --- |
| `docs/n8-geometric-proof.md` | Human geometric route for `n <= 8` | Independent review, `n >= 9`, source-of-truth status update |
| `docs/dumitrescu-isosceles-n8-shortcut.md` | Literature-backed `n <= 8` shortcut | Literature audit, `n >= 9`, selected-witness artifact review |
| `scripts/enumerate_n8_incidence.py` | Regenerates the 15 `n=8` incidence survivor classes | Exact survivor obstructions, public theorem review |
| `scripts/independent_check_n8_artifacts.py` | Checks stored survivor, completeness, compatible-order, and exact-analysis artifacts as inputs | Full independent incidence regeneration |
| `scripts/independent_n8_obstruction_recheck.py` | SymPy-free cyclic-order counts and 11 survivor-class kills | Groebner-dependent classes `3`, `4`, `5`, `14` |
| `scripts/check_n8_residual_certificates.py` | Focused classes `3`, `4`, `5` replay | Class `14`, incidence regeneration |
| `scripts/check_n8_class14_certificate.py` | Focused class `14` PB+ED Groebner and strict-interior replay | Other survivor classes, incidence regeneration |

## Review outcomes

- `accepted_geometric_route`: the proof note is accepted as a human-readable
  small-case proof route.
- `accepted_selected_witness_artifact`: the machine-checked selected-witness
  `n <= 8` artifact is accepted as repo-local finite-case evidence.
- `accepted_literature_shortcut`: the external Dumitrescu-bound shortcut is
  accepted with its counting convention.
- `gap_found`: record the exact failed step, affected route, command output if
  applicable, and whether source-of-truth wording needs qualification.
- `no_status_change`: the safe default for this file; review notes can improve
  without changing the official/global status.

## Known weak points

- The geometric octagon trap is intentionally short and needs independent
  line-by-line geometry review before public theorem-style use.
- The selected-witness artifact is machine-checked and exact, but the aggregate
  `n=8` exclusion remains a repo-local finite-case artifact pending external
  review.
- The SymPy-free recheck is deliberately partial; Groebner-dependent classes
  `3`, `4`, `5`, and `14` are covered by focused checkers but still use SymPy.
- The literature-backed shortcut depends on an external theorem and matching
  counting convention.
- None of these routes says anything about `n >= 9` beyond preserving the
  current open/review-pending boundaries.
