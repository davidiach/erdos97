---
name: Obstruction lemma proposal
about: Propose a quantitative obstruction lemma that retires a fixed selected pattern
title: "[OBSTRUCTION] <pattern_id> via <obstruction name>"
labels: ["LEMMA", "obstruction"]
assignees: []
---

## Pattern

- pattern id (must match an entry in `data/patterns/candidate_patterns.json`):
- ``n``:
- block / circulant / parity / other:
- selected pattern source: <link to the catalog entry or formula>

## Proposed obstruction

State the lemma in the form

```text
r >= C1 * gamma^alpha
```

or, more generally, a strictly positive lower bound on the RMS equality
residual ``r`` (or the max squared-distance spread) in terms of the
strict convexity margin ``gamma`` and any cluster scale ``rho``.

- proposed exponent ``alpha``:
- proposed coefficient ``C1`` (best honest estimate):
- range of validity (cluster decomposition, orientation regime, ...):
- corollary on zero-residual limits:

## Proof sketch

Fill in the analytic argument.  Compatible structure:

1. **Residual scaling.** How does ``r`` depend on the cluster scale
   ``rho`` (or other geometric scale)?  Linear?  Quadratic?  Cubic?
2. **Convexity bound on the cluster scale.** What is the strongest
   upper bound on ``gamma`` that the cluster geometry forces?
3. **Combination.** Substitute the convexity bound into the residual
   estimate to obtain ``r >= C1 * gamma^alpha``.

State explicitly what the proof does **not** cover (other patterns,
other ``n``, other cluster decompositions).

## Empirical witness

Attach or link:

- a saved JSON config that satisfies the cluster hypotheses (path under
  `data/runs/...` or attached gist);
- a script that runs an SLSQP-style restart sweep at varying
  convex-margin tolerances and records ``(gamma, r, rho, theta)``
  tuples;
- a fit of ``log r`` vs ``log gamma`` (slope, intercept, ``R^2``).

If the empirical fit confirms the analytic exponent within ``0.05``,
propose **LEMMA** trust level.  Otherwise propose **NUMERICAL_EVIDENCE
+ CONJECTURE** for the tight version, and keep the analytic LEMMA at
its proven (looser) exponent.

## Deliverables checklist

- [ ] `docs/lemmas/<pattern>_obstruction.md` LEMMA-tagged document
      (self-contained: definitions, statement, proof sketch,
      explicit constants, range of validity).
- [ ] Cross-reference to the motivating saved run.
- [ ] Note whether the lemma is a candidate for Lean transcription
      (do not attempt the formalization in this issue).
- [ ] `src/erdos97/obstructions.py` extended with a new
      ``ThreeFoldClusterObstruction``-style class (or a documented
      generic version) that stores ``alpha``, ``C1``, applicable
      patterns, and exposes a verifier.
- [ ] `tests/test_obstruction_<pattern>.py` covering: the saved
      run satisfies the bound; randomized restarts at varying
      tolerances satisfy the bound; hand-built synthetic configs at
      known scales satisfy the bound and are tight to a small factor.
- [ ] `scripts/empirical_<pattern>_constants.py` that runs in under
      10 minutes and produces a fit with ``R^2 > 0.95``.
- [ ] Updates to `STATE.md`, `docs/failed-ideas.md`, `docs/claims.md`,
      and the catalog entry's ``"retired_by"`` field.

## Hard constraints

- This issue does **not** propose a proof of Erdős Problem #97; it
  retires a fixed selected pattern.
- Do not modify or delete any saved run.  Add new artifacts alongside.
- Keep the scope tight to one pattern.  Generalizations belong in
  follow-up issues.
- Trust-level taxonomy is enforced.  No floating-point equalities
  presented as exact.
