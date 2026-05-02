# n=9 Incidence Frontier Scan

Status: `BOUNDED_INCIDENCE_CSP_DIAGNOSTIC`.

This note records a bounded selected-witness incidence/CSP scan at the `n=9`
frontier. It does not claim an `n=9` completeness theorem, a general proof of
Erdos Problem #97, or a counterexample.

## Scope

The generated artifact is
`data/certificates/n9_incidence_frontier_bounded.json`.

The scan fixes the natural cyclic order

```text
0,1,2,3,4,5,6,7,8
```

and fixes row `0` to the registered rectangle-trap seed row

```text
S0 = {1,2,3,8}.
```

Within that row0-fixed slice, the search is deterministic and bounded by
explicit node and full-pattern limits. The default run is seed-prioritized by
the registered `n=9` rectangle-trap pattern; it completed before either limit.
This is not a lossless quotient of all fixed-order `n=9` selected-witness
systems, because the cyclic order is held fixed.

## Filters

The backtracker applies these exact necessary incidence/order filters as early
as possible:

- row-pair intersections have size at most `2`;
- adjacent source pairs in the cyclic order cannot have a two-overlap;
- every two-overlap source chord must cross its witness chord;
- each witness label has indegree at most `5`, by `3d <= 2(n-1) = 16`;
- every witness pair occurs together in at most two rows.

At full patterns it also applies:

- odd forced-perpendicularity cycles;
- mutual-rhombus midpoint collapse;
- phi 4-cycle rectangle-trap certificates.

## Current Result

The default run completed its row0-fixed slice:

```text
nodes visited:          6793
row options considered: 475231
full patterns checked:  3
truncated:              false
```

Partial rejection counts:

```text
row-pair cap:          215140
adjacent two-overlap:   20362
crossing-bisector:     232937
indegree upper:             0
column-pair cap:            0
```

The three full patterns split as follows:

```text
odd forced-perpendicularity cycle: 1
phi4 rectangle trap:              1
accepted frontier:                1
```

Here `accepted_frontier` means only that the listed exact necessary filters did
not obstruct the fixed incidence/order pattern. It is not evidence of geometric
realizability.

The surviving fixed-order incidence pattern is:

```text
S0 = {1,2,3,8}
S1 = {0,3,4,7}
S2 = {1,3,5,6}
S3 = {2,4,5,8}
S4 = {0,3,6,8}
S5 = {2,4,6,7}
S6 = {1,5,7,8}
S7 = {0,1,4,6}
S8 = {0,2,5,7}
```

It has balanced witness indegrees `[4,4,4,4,4,4,4,4,4]`, `18` phi edges, no
directed phi 4-cycle, no odd forced-perpendicularity cycle, and no forced
midpoint equality classes under the current mutual-rhombus filter.

## Reproduction

```bash
python scripts/check_n9_incidence_frontier.py --assert-expected
python scripts/check_n9_incidence_frontier.py --assert-expected --write
python -m pytest tests/test_n9_incidence_frontier.py -q
```

The `--write` command regenerates
`data/certificates/n9_incidence_frontier_bounded.json`.

## Next Use

The immediate value of the artifact is that it reduces this row0-fixed natural
order slice to one current filter survivor. Good next checks for that survivor
are the row-circle/Ptolemy equations, radius-propagation diagnostics, interval
verification attempts, and an even-cycle certificate search beyond the phi4
rectangle-trap shape.
