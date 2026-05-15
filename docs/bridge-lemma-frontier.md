# Bridge Lemma Frontier Diagnostic

Status: proof-mining diagnostic only. No general proof, no Bridge Lemma A'
proof, and no counterexample are claimed.

Bridge Lemma A' says that every realizable strictly convex `k=4`
counterexample admits an ear-orderable selected-witness pattern. The lemma is
open. This diagnostic makes the current finite frontier around that question
replayable:

- `n=8`: all 15 incidence-completeness survivor classes are rechecked for
  ear-orderability and cross-referenced with exact obstruction certificates.
- `n=9`: all 184 pre-vertex-circle frontier assignments are regenerated from
  the review-pending exhaustive checker, rechecked for ear-orderability, and
  cross-tabulated against the exact vertex-circle obstruction type.
- The four non-ear `n=8` classes and two non-ear `n=9` assignments are emitted
  as explicit proof-mining targets.

The checked artifact is:

```bash
data/certificates/bridge_lemma_frontier.json
```

## Reproduction

Regenerate and compare the checked artifact:

```bash
python scripts/check_bridge_lemma_frontier.py --check --assert-expected --json
```

This check is also registered in the scheduled/manual artifact audit runner
(`make audit-artifacts`).

Rewrite the artifact after an intentional generator change:

```bash
python scripts/check_bridge_lemma_frontier.py --write --assert-expected
```

Run optional numerical smoke probes on the six non-ear targets:

```bash
python scripts/check_bridge_lemma_frontier.py \
  --run-geometry \
  --geometry-restarts 3 \
  --geometry-max-nfev 1000
```

Numerical output is evidence only. A low residual would still require exact
coordinates, interval certificates, SMT certificates, or a formal proof before
supporting any counterexample-style claim.

## Current Counts

| Frontier | total | ear-orderable | non-ear | non-ear ids |
|---|---:|---:|---:|---|
| `n=8` survivor classes | 15 | 11 | 4 | `0, 1, 2, 3` |
| `n=9` frontier assignments | 184 | 182 | 2 | `81, 151` |

For `n=9`, the two non-ear assignments are both killed by strict-cycle
vertex-circle obstructions in the review-pending checker. The full cross-tab is
stored in the artifact summary.

## Usefulness

This is useful because it separates three questions that were easy to blur:

1. Which finite frontier objects are ear-orderable?
2. Which non-ear fixed selections are already killed by exact finite-case
   obstructions?
3. Which small non-ear objects should be studied next when trying to prove or
   refute Bridge Lemma A'?

The diagnostic does not prove the bridge. Its value is that it gives future
work six concrete, reproducible edge cases instead of a vague instruction to
"look at stuck sets."
