# GPT-5.5 bridge-output triage, 2026-05-10

Status: `PROVENANCE` / triage note. No general proof and no counterexample are
claimed.

This note records the triage of ten GPT-5.5 Pro outputs aimed at the missing
bridge from minimal fragile-cover structure to selected-witness machinery.
The raw outputs should be treated as AI-generated provenance only. The only
material extracted into proof-facing form is the adaptive radius-blocker fork
and a small set of exact negative controls.

## Triage table

| Output | Verdict | Action |
|---|---|---|
| 1 | Mostly correct abstract C13 Sidon negative control. | Subsumed by `docs/bridge-negative-controls.md`. |
| 2 | Correct projective-plane incidence idea, but the no-ear proof uses a stuck set where a forward-ear argument is needed. | Quarantine as redundant with Output 3. |
| 3 | Best abstract obstruction: linear selected systems are phi-silent and not forward-ear-orderable. | Extract as the C13 linear negative control. |
| 4 | Valid finite C9 symbolic certificate: no forward ear and vertex-circle killed. | Keep as optional future regression fixture, not central. |
| 5 | Exact six-label fragile block geometry checks out. | Extract as the block-6 geometric atom. |
| 6 | Best route worth pursuing: adaptive peeling versus radius-blocker alternative. | Extract as `docs/adaptive-radius-blocker-bridge.md`. |
| 7 | Abstract two-block full extension has no forward ear and passes pair/crossing checks. | Keep as an incidence negative control. |
| 8 | Six-block part is fine, but the 12-row no-ear claim is false. | Record correction only. |
| 9 | Six-block geometry and forced dependency cycle are good. | Subsumed by the block-6 geometric atom. |
| 10 | Six-block coordinates are good, but it repeats the false 12-row no-ear claim from Output 8. | Use the six-block atom; reject the full-extension conclusion. |

## Extracted work

The useful extracted artifacts are:

- `docs/adaptive-radius-blocker-bridge.md`: a proof-facing fork lemma. Either
  adaptive selected-witness peeling gives an ear-orderable selection, or a
  radius-blocker remains.
- `docs/bridge-negative-controls.md`: exact guardrails for bridge work:
  the C13 linear/Sidon fixed pattern, the exact geometric block-6 fragile atom,
  and the two-block incidence no-forward-ear control.
- `scripts/check_bridge_negative_controls.py`: replayable checks for the
  extracted finite claims.

## Non-overclaiming guardrails

The extracted material does not prove Erdos Problem #97. It does not produce a
counterexample. It does not promote `n=9`, `n=10`, or any fixed sparse pattern.

The C13 Sidon pattern is already retired as a fixed selected-witness pattern
across all cyclic orders by the exact Kalmanson/Farkas order search. Its role
here is only to show that incidence-only bridge claims can fail.

The block-6 geometric atom realizes only fragile rows. Its non-fragile centers
are not bad, so it is not a selected-witness counterexample.

The adaptive radius-blocker fork is a bridge target, not a finished proof:
future work must rule out radius-blockers using genuinely geometric input, or
construct an exact blocker escape mechanism that survives all current filters.
