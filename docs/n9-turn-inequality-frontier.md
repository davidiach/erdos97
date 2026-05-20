# n=9 Turn-Inequality Frontier Replay

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records a replayable check of the latest GPT Pro n=9 route. It is
not a proof of Erdos Problem #97, not a counterexample, not an official/global
status update, and not an independently reviewed theorem. The geometric turn
lemma below is the review bottleneck. See `docs/turn-inequality-lemma.md` for
the proof-facing lemma note and `docs/turn-packing-bridge.md` for the
review-pending certificate principle extracted from the replay.

## Scope

The checker regenerates the 184 complete selected-witness assignments that
survive the existing n=9 pair/crossing/count filters before vertex-circle
pruning, in the natural cyclic order. For each assignment it builds the weak
linear turn system suggested by the proposed geometry argument and stores an
integer dual certificate. Z3 is still replayed as a cross-check, but the stored
certificate layer is verified by arithmetic alone.

The generated artifact is:

```bash
data/certificates/n9_turn_inequality_frontier.json
```

The generator and checker are:

```bash
python scripts/check_n9_turn_inequality_frontier.py --assert-expected --write
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --json
```

The check command is also registered in `scripts/run_artifact_audit.py` and
listed in the raw audit command set in `README.md`.

## Candidate Turn Lemma

Let `tau_i` be exterior turns and set `t_i = 2*tau_i/pi`, so
`sum_i t_i = 4`. If center `i` selects two targets with cyclic offsets
`1 <= a < b <= 8`, the proposed lemma gives the strict inequalities

```text
sum_{h=1}^{b-1} t_{i+h} > 1
sum_{h=a+1}^{8} t_{i+h} > 1
```

The replay uses the weaker rational inequalities with `>= 1`. Therefore an
`unsat` result for the weak system is stronger than what the geometric argument
would need, assuming the lemma and indexing are correct.

## Current Replay Counts

The artifact currently records:

- regenerated source-frontier assignments: `184`;
- source-frontier SHA-256:
  `d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01`;
- indegree distribution: all assignments have indegrees `(4,4,4,4,4,4,4,4,4)`;
- side-sensitive pair-cap violation count: `0` for all 184 assignments;
- turn inequalities per assignment: `108`;
- Farkas/dual certificates: `184`;
- Farkas certificate SHA-256:
  `1aed1b1f78178b967f93a3894e67cf9a0c314441a94423c8f24f2e0b8cb9bf89`;
- Farkas lambda histogram: `lambda=1` for 180 assignments and `lambda=2`
  for 4 assignments;
- Farkas term-count histogram: 5 selected interval inequalities for 180
  assignments and 9 selected interval inequalities for 4 assignments;
- Z3 exact linear-arithmetic status: `unsat` for all 184 assignments.

Each stored certificate lists interval-inequality indices. If its bound is
`lambda`, every normalized turn variable has total coefficient at most
`lambda`, while the number of selected inequalities is greater than
`4*lambda`. Summing the selected weak inequalities gives

```text
left side >= rhs_sum > 4*lambda,
```

but nonnegativity and `sum_i t_i = 4` give

```text
left side <= lambda * sum_i t_i = 4*lambda.
```

That is the recorded arithmetic contradiction.

The side-cap benchmark pattern from the GPT Pro continuation is included as a
negative-control-style benchmark. It is assignment `4` in the regenerated
frontier, has natural-order status `accepted_frontier`, has vertex-circle
status `self_edge`, and is also `unsat` under the weak turn system.

## Review Requirements

Before this can support a theorem-style n=9 claim, reviewers should check:

- the geometric turn lemma and all offset/index conventions;
- that the regenerated 184-assignment frontier is the intended source frontier
  and is not hiding symmetry quotient assumptions;
- the stored integer dual certificates and their arithmetic verifier;
- the Z3 linear-arithmetic replay as an independent cross-check, not as the
  primary stored certificate;
- that no source-of-truth status file is promoted until the above review is
  complete.

## Fast Reproduction

```bash
python scripts/check_n9_turn_inequality_frontier.py --assert-expected --json
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --json
python -m pytest tests/test_n9_turn_inequality_frontier.py -q
```
