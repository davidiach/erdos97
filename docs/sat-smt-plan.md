# SAT / SMT / ILP finite abstraction plan

## Base incidence SAT

Boolean variable:

```text
x[i,j] = 1 iff vertex j is selected by center i.
```

Mandatory necessary constraints:

```text
x[i,i] = 0
sum_j x[i,j] = 4                  for every i
sum_j (x[a,j] AND x[b,j]) <= 2    for every a != b
```

The last condition is the circle-intersection cap and should be run before
every numerical optimization.[^repo]

## Row-overlap filter

For a concrete pattern, reject immediately if any pair of rows shares three or
more selected targets:

```python
def row_overlap_filter(n, pattern):
    rows = [set(pattern(i)) for i in range(n)]
    bad = []
    for i in range(n):
        for j in range(i + 1, n):
            inter = rows[i].intersection(rows[j])
            if len(inter) >= 3:
                bad.append((i, j, sorted(inter)))
    return bad
```

The archived `n=39` circulant branch is killed exactly by this filter.[^comp]

## What UNSAT proves

If only necessary constraints are used, UNSAT for a fixed `n` proves that no
counterexample of that size exists at the incidence level.[^repo]

## What SAT proves

SAT gives only an incidence pattern. It says nothing by itself about strict
convex Euclidean realizability or exact distance equality.[^repo]

## What restricted UNSAT does not prove

UNSAT after adding balance, cyclic-spread, symmetry, common-radius, or
search-convenience constraints only rules out that restricted class.[^repo]

## Next strengthening ideas

- Add the pair-sharing and triple-sharing bounds as finite filters.[^digest]
- Add radical-axis perpendicularity templates for row pairs sharing exactly two
  selected witnesses.[^small]
- Add order-type or oriented-matroid constraints only when they are proved
  necessary.[^comp]
- Keep heuristic balance and symmetry filters in a separate namespace from
  necessary constraints.[^comp]
- Use SAT patterns as inputs to exactification, not as candidates by
  themselves.[^repo]

[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^comp]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/04_COMPUTATIONAL_FINDINGS.md`.
[^digest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md`.
[^small]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/02_SMALL_CASES_N5_N6_N7.md`.
