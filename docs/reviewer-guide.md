# Reviewer guide for Erdos Problem #97 finite-case artifacts

## What this repo claims

- No general proof and no counterexample are claimed.
- The selected-witness method rules out `n <= 8` in a repo-local,
  machine-checked finite-case sense.

## What this repo does not claim

- It does not claim to solve Erdos Problem #97.
- It does not claim that numerical near-misses are counterexamples.
- It does not claim the `n=8` artifact has had independent external review.
- It does not claim that the round-two `C19_skew` Kalmanson certificate kills
  all cyclic orders of the abstract pattern.
- It does not claim that the exact all-order C13 result proves Erdos Problem
  #97; that result is only for one fixed abstract selected-witness pattern.

## Fast reproduction commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make verify-fast
```

If `make` is not available, run:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

## Artifact audit commands

Run these before finite-case, certificate, or public theorem-style updates:

```bash
make verify-artifacts
```

For CI-style audit metadata, run:

```bash
make audit-artifacts
```

The `audit-artifacts` target includes the dated official-status consistency
check, so this audit path is stricter than the default fast tier.

Equivalent raw commands:

```bash
python scripts/check_status_consistency.py --max-official-status-age-days 90
python scripts/check_artifact_provenance.py
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

The default pytest configuration excludes tests marked `artifact`, `slow`, or
`exhaustive`. Use `python -m pytest -q -m ""` when intentionally replaying the
full marker set.

For a version-matched reproduction run, replace `pip install -e .[dev]` with:

```bash
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

## Expected `n=8` outputs

For `python scripts/enumerate_n8_incidence.py --summary`, expected invariants:

- status is `INCIDENCE_COMPLETENESS`;
- `canonical_survivor_class_count` is `15`;
- `matches_existing_reconstructed_survivors` is `true`;
- all necessary incidence survivors are reduced to the 15 canonical classes in
  `data/incidence/n8_incidence_completeness.json` and
  `data/incidence/n8_reconstructed_15_survivors.json`.

For `python scripts/analyze_n8_exact_survivors.py --check --json`, expected
invariants:

- status is `exact_obstruction_artifact_pending_independent_review`;
- `survivor_classes` is `15`;
- `cyclic_order_remaining_count` is `14`, with class `12` killed by cyclic
  order noncrossing;
- classes `3`, `4`, `5`, and `14` report their named exact certificates as
  verified;
- the `pb_y2_span_ids_verified` list contains ten classes;
- the final obstruction pass is exact and does not rely on floating-point
  equality;
- certificate data agrees with `certificates/n8_exact_analysis.json`.

## Files to inspect first

1. `STATE.md`
2. `RESULTS.md`
3. `docs/n7-fano-enumeration.md`
4. `docs/n8-incidence-enumeration.md`
5. `docs/n8-exact-survivors.md`
6. `docs/round2/round2_merged_report.md`
7. `docs/verification-contract.md`
8. `docs/n8-geometric-proof.md`
9. `docs/review-priorities.md`

## Review target A - `n=7`

Primary reference: `docs/n7-fano-enumeration.md`.

Check:

- the Fano/equality reduction;
- the enumeration of labelled/pointed families;
- the cyclic-dihedral reduction;
- the odd-cycle perpendicularity obstruction.

## Review target B - `n=8` incidence completeness

Check:

- derivation of indegree regularity from the column-pair cap;
- exhaustive enumeration assumptions;
- canonicalization under relabeling;
- reproducibility of the 15 survivor classes.

## Review target C - `n=8` exact survivor obstruction

Check:

- the class killed by cyclic-order noncrossing;
- the classes killed by perpendicular-bisector algebra;
- the classes requiring full equal-distance algebra;
- the strict-convexity obstruction cases;
- the archived-ID provenance mapping.

## Review target D - `n=8` geometric proof note

Check:

- the base-apex lemma and its strict-convexity hypothesis;
- the isosceles-triangle count and octagon equality saturation;
- the length-2 diagonal argument forcing equal side lengths;
- the length-3 diagonal argument forcing a cover of adjacent turn-angle pairs;
- the exterior-turn contradiction.

## Review target E - round-two fixed-order Kalmanson certificate

Check:

- that `scripts/check_kalmanson_certificate.py` reconstructs the selected
  distance quotient from the declared `C19_skew` offsets;
- that every listed quadrilateral is in the declared cyclic order;
- that the compact two-inequality certificate has positive integer weights and
  zero total coefficient sum;
- that the earlier 94-inequality certificate remains valid as provenance;
- that the weighted coefficient sum is exactly zero;
- that the result is recorded only as a fixed-order obstruction.

## Review target F - C13 all-order two-certificate search

Check:

- that `scripts/check_kalmanson_two_order_search.py` fixes label `0` only by
  translation symmetry for the circulant pattern;
- that the search result is an all-order statement only for the fixed abstract
  `C13_sidon_1_2_4_10` selected-witness pattern;
- that the result is not described as a general proof of Erdos Problem #97.

## Known weak points / independent review requests

- Independent audit of `scripts/enumerate_n8_incidence.py`.
- Independent audit of exact certificates, especially classes `3`, `4`, and
  `14` if those remain singled out in `RESULTS.md`.
- A minimal standalone class `14` checker would be especially valuable because
  that obstruction combines Groebner reasoning with a strict-interior
  conclusion.
- Independent reproduction of `certificates/n8_exact_analysis.json`.
- A Lean, SMT, interval, or algebraic certificate checker would be high value.

## Reporting review findings

Open an issue or PR that states:

- which artifact was reviewed;
- exact command run;
- environment details;
- whether the result reproduced;
- any mathematical or implementation gap found.
