# Corrected search reporting (schema 2)

Use `search_cli.cpp` for new interactive searches. It compiles the exact same
`Search` implementation from the hash-pinned `exact_search.cpp` but replaces
its command-line and JSON-reporting layer. No pruning rule or branch order is
changed. The original source, manifests, replay programs, and recorded reports
remain unchanged for historical reproduction.

The archived CLI's `complete` field meant only that no node-limit abort occurred.
It could be true after the first survivor even though enumeration stopped early.
The archived exclusion acceptance condition (`complete && !survivor`) is not
invalidated by that ambiguity. Do not use the old `complete` field alone to claim
exhaustive enumeration, and do not rewrite historical reports as schema 2.

## Run the maintained reporting CLI

From the repository root:

```sh
c++ -std=c++17 -O2 -DSEARCH_N=9 \
  incoming/radius-descent-n11-2026-09-05/search_cli.cpp -o /tmp/erdos97-search
/tmp/erdos97-search --no-turn --no-kalmanson
/tmp/erdos97-search --no-turn --no-kalmanson --enumerate-all
/tmp/erdos97-search --limit 1
```

`SEARCH_N` defaults to 11 and retains the original compile-time 5..16 bound.
A positional nonnegative integer selects one center-0 slice; omitting it searches
unsliced. `--no-turn`, `--no-kalmanson`, and `--limit` preserve their meanings.
`--enumerate-all` enables the existing engine's full enumeration option and may
retain many survivors in memory. A zero node limit means unlimited, as before.
Malformed arguments exit 2 without emitting a search result. Aborts exit 3,
even when a previously found survivor already decides existence.

The new JSON reports:

| Field | Meaning |
|---|---|
| `schema` | 2 |
| `exhausted` | No node-limit abort and no first-survivor early termination |
| `complete` | Deprecated alias for `exhausted`, not the archived meaning |
| `decision_complete` | A survivor was found, or the search was exhausted |
| `termination_reason` | `survivor_found`, `node_limit`, or `exhausted` |
| `relaxation_unsat` | `exhausted && !survivor` |
| `solution_count` | Survivors retained by this run, not necessarily the total |

A first-survivor run conservatively withholds exhaustion even if that survivor
happened to be the final leaf. An aborted enumeration can have
`decision_complete=true` and `exhausted=false` after finding a survivor.
A survivor is only a selected-witness relaxation assignment, not a Euclidean
realization or a counterexample. A slice result only covers that slice.

## Regression checks

```sh
python -m pytest -q tests/test_radius_descent_search_reporting.py
```

The tests recompile n=9, check the archived source hash, and reproduce:

- first-survivor incidence search: 2,265 nodes, one retained survivor, not exhausted;
- full incidence frontier: 100,818 nodes, 184 survivors, exhausted;
- full metric/turn search: 18,472 nodes, zero survivors, exhausted;
- node-limit exits before and after a survivor, with distinct decision/exhaustion flags;
- malformed arguments fail without a misleading result.

These reporting tests are not an independent solver, an all-n result, a new
full n=11 replay, or external geometric review. They do not change the accepted
finite-case bound. Existing historical validation remains a separate command.
