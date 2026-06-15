# n=9 parallel-endpoint combinatorial closure

Status / trust label: `REVIEW_PENDING_DIAGNOSTIC`. This is a lighter, second-source
closure of the review-pending `n=9` pre-vertex-circle frontier. **No general proof
of Erdos Problem #97, no proof of the `n=9` finite case, and no counterexample are
claimed, and the official/global falsifiable-open status is unchanged.**

## Summary

The review-pending `n=9` selected-witness pipeline reduces every hypothetical 4-bad
nonagon to `184` pre-vertex-circle frontier assignments, then kills all `184` with
the **vertex-circle quotient** filter (`158` self-edges, `26` strict cycles).

This note records that the same `184` assignments are already killed by two
**purely combinatorial** necessary-condition filters, with **no** vertex-circle or
metric reasoning:

| filter | assignments killed |
| --- | ---: |
| parity (odd forced-perpendicular cycle) | 22 |
| parallel-endpoint | 162 |
| survive both | 0 |
| **total** | **184** |

By the stored vertex-circle status the split is: of the `158` self-edge assignments,
`22` fall to parity and `136` to parallel-endpoint; all `26` strict-cycle assignments
fall to parallel-endpoint.

## The two filters and why they are sound necessary conditions

Both filters are consequences of repository lemmas and use strict convexity.

**Forced perpendicularity (lemma L6).** If centers `i, j` share exactly two selected
witnesses `S_i cap S_j = {a, b}`, then both centers lie on the perpendicular bisector
of segment `ab`, so the chord `p_i p_j` is perpendicular to the chord `p_a p_b`. Build
the forced-perpendicularity graph `G` on unordered vertex-chords with an edge
`{i,j} -- {a,b}` for every such two-overlap.

1. **Parity.** A slope in `RP^1` (angle mod `pi`) flips by `pi/2` along each
   perpendicularity edge. Around an odd closed walk this would force
   `theta = theta + pi/2`, impossible for a nonzero chord. Strict convexity supplies
   the nonzero chord via lemma L2 (distinct vertices), so a realizable system must have
   `G` bipartite (no odd cycle). This is the `n`-independent generalization of the
   `n=7` perpendicularity-cycle argument. Checker:
   `erdos97.incidence_filters.odd_forced_perpendicular_cycle`.

2. **Parallel-endpoint.** Within a connected component of a bipartite `G`, a proper
   2-coloring assigns each chord a slope class; two chords of the **same** color in the
   same component are forced **parallel**. Two forced-parallel chords sharing a polygon
   vertex would place three vertices on a line, forbidden by strict convexity (L2). The
   presence of such a same-color, shared-endpoint pair is therefore a sound obstruction.
   Checker: `erdos97.incidence_filters.forced_parallel_endpoint_violation`.

Apply parity first; the parallel-endpoint refinement is meaningful on the bipartite
systems that pass it.

## Provenance gap this surfaces

The parity filter is already available in the `n=9` pipeline
(`odd_forced_perpendicular_cycle`), but the **parallel-endpoint** filter previously
lived only in the `n=8` enumerator (`src/erdos97/n8_incidence.py`) and in the
`reports/explorations/2026-06-14/A6-topological-parity.md` exploration. It was **not**
wired into `src/erdos97/n9_incidence_frontier.py`. Promoting it to a first-class,
tested filter in `src/erdos97/incidence_filters.py` (this change) makes the lighter
closure reproducible and reusable, and documents that `162/184` frontier assignments
admit a combinatorial obstruction that the `n=9` enumerator did not previously test.

## What this does and does not establish

- It **does** give an independent, lighter combinatorial closure of the *stored* `184`
  frontier assignments, with an exact reproducible certificate.
- It is **necessary-only**: all `15` `n=8` survivor classes pass both filters (they die
  only to exact metric/orthocenter algebra), so this route cannot settle even `n=8`, let
  alone the global problem.
- It **does not** independently prove the `n=9` finite case: the `184` frontier is itself
  the output of the review-pending incidence enumerator (its pair/crossing/count filtering
  and completeness remain review-pending). This note re-closes that same stored frontier
  by a lighter argument; it does not re-derive the frontier.
- It **does not** prove Erdos Problem #97, exhibit a counterexample, or change the
  official/global status.

## Reproduction

```bash
python scripts/check_n9_parallel_endpoint_closure.py --check --assert-expected
python scripts/check_n9_parallel_endpoint_closure.py --json   # full per-assignment record
python -m pytest -q tests/test_n9_parallel_endpoint_closure.py
```

Checked artifact: `data/certificates/n9_parallel_endpoint_closure.json` (managed in
`metadata/generated_artifacts.yaml`). Exploration provenance:
`reports/explorations/2026-06-14/A6-topological-parity.md`.

## Suggested follow-up

A separately reviewed change could apply the parallel-endpoint necessary filter inside
`src/erdos97/n9_incidence_frontier.py` so the frontier closes at the incidence layer.
That touches review-pending source and should be made under its own review, not bundled
with this additive second-source diagnostic.
