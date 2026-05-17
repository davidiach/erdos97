# Open Issue Resolution Crosswalk

Status: `ISSUE_ACCEPTANCE_CROSSWALK_ONLY`.

This note is repository bookkeeping. It does not prove Erdos Problem #97, does
not claim a counterexample, and does not change the official/global status.

## Checker

Run the crosswalk with:

```bash
python scripts/check_open_issue_resolution_crosswalk.py --assert-expected --json
```

The checker verifies that the four currently open legacy GitHub issues are now
covered by scoped, reproducible repository entrypoints. Its safe-closure
recommendation is only about each issue's stated engineering or research-log
acceptance criteria, not about the global problem.

## Issue Rows

| Issue | Crosswalk status | Main evidence | Claim boundary |
|---:|---|---|---|
| #5 | Interval verifier is implemented and guarded | `src/erdos97/interval_verify.py`, `scripts/interval_verify_candidate.py`, `tests/test_interval_verify.py` | The saved B12 floating near-miss is rejected as a counterexample. |
| #81 | C13 cyclic-order pilot is covered | `data/certificates/c13_sidon_all_orders_kalmanson_two_search.json` | The all-order obstruction is only for fixed abstract `C13_sidon_1_2_4_10`. |
| #82 | Low-excess ledger attack is covered as bookkeeping | `data/certificates/n9_base_apex_low_excess_ledgers.json`, `data/certificates/n9_base_apex_low_excess_escape_crosswalk.json`, D=3 packets | Remaining low-excess ledgers are enumerated; realizability and incidence states remain unknown where marked. |
| #83 | C19 certificate decomposition is covered | `reports/kalmanson_certificate_diagnostics.json`, `reports/c19_kalmanson_compact_vs_legacy.json`, `reports/c19_kalmanson_z3_clause_diagnostics.json` | Fixed-order support diagnostics and fixed-pattern all-order C19 obstruction remain separate. |

## Safe Closure Recommendation

The checker recommends closing issues `#5`, `#81`, `#82`, and `#83` after this
crosswalk is merged, because their acceptance criteria now have explicit
scripts, artifacts, tests, and documentation.

The recommendation is deliberately narrow:

- #5 is closed as an interval-verifier implementation and B12 rejection guard,
  not as a new exact candidate certificate.
- #81 is closed as a C13 fixed-pattern cyclic-order pilot, not as evidence that
  the method transfers to C19 or to Erdos Problem #97.
- #82 is closed as a low-excess ledger attack and enumeration, not as a proof
  of `n=9`.
- #83 is closed as fixed-order C19 certificate decomposition and all-order
  guardrail documentation, not as a sparse-frontier closure.

The next technical work should continue from `docs/codex-backlog.md` and
`docs/review-priorities.md`, especially the bridge and review-pending artifact
items that remain open after the GitHub issue cleanup.
