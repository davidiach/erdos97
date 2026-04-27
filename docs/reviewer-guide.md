# Reviewer guide for Erdos Problem #97 finite-case artifacts

## What this repo claims

- No general proof and no counterexample are claimed.
- The selected-witness method rules out `n <= 8` in a repo-local,
  machine-checked finite-case sense.

## What this repo does not claim

- It does not claim to solve Erdos Problem #97.
- It does not claim that numerical near-misses are counterexamples.
- It does not claim the `n=8` artifact has had independent external review.

## Minimal reproduction commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
pytest -q
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
```

## Files to inspect first

1. `STATE.md`
2. `RESULTS.md`
3. `docs/n7-fano-enumeration.md`
4. `docs/n8-incidence-enumeration.md`
5. `docs/n8-exact-survivors.md`
6. `docs/verification-contract.md`

## Review target A - `n=7`

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

## Known weak points / independent review requests

- Independent audit of `scripts/enumerate_n8_incidence.py`.
- Independent audit of exact certificates, especially classes `3`, `4`, and
  `14` if those remain singled out in `RESULTS.md`.
- Independent reproduction of `certificates/n8_exact_analysis.json`.
- A Lean, SMT, interval, or algebraic certificate checker would be high value.

## Reporting review findings

Open an issue or PR that states:

- which artifact was reviewed;
- exact command run;
- environment details;
- whether the result reproduced;
- any mathematical or implementation gap found.
