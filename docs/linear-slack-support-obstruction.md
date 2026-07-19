# Linear slack support obstruction

Status: `LEMMA_DRAFT` / `REVIEW_PENDING`. This note does not claim a proof of
Erdos Problem #97, a proof of any finite case beyond the stated counting
lemma, or a counterexample. Independent proof review is requested before
theorem-style use.

## Statement

Let `v_0,...,v_{n-1}` be the vertices of a strictly convex polygon in cyclic
order, with `n >= 8`. At each center `i`, choose one same-radius support
`R_i subset V \ {v_i}`. Define the usage of an unordered vertex pair by

```text
u({x,y}) = #{i : {x,y} subset R_i}.
```

Hull-edge pairs have capacity one and diagonal pairs have capacity two. The
edge-sensitive raw budget and its unused capacity are therefore

```text
sum_i binom(|R_i|,2) = sum_pairs u({x,y}) <= n(n-2),
d = n(n-2) - sum_i binom(|R_i|,2).
```

The claimed strengthening is

```text
d >= ceil((n-4)/2) = floor((n-3)/2),
```

or equivalently

```text
sum_i binom(|R_i|,2)
    <= n(n-2) - ceil((n-4)/2).
```

For `n=8` this recovers the earlier two-unit near-saturation bound. It is
strictly stronger for every `n >= 9`.

## Proof

Write `s_i = |v_i v_{i+1}|` for the side lengths and let `tau_i in (0,pi)` be
the exterior turns, with indices modulo `n` and

```text
sum_i tau_i = 2*pi.
```

Let `B` be the set of indices `i` for which the gap-2 diagonal
`{v_i,v_{i+2}}` is not saturated, and let `G` be the analogous set for the
gap-3 diagonal `{v_i,v_{i+3}}`. The two short-diagonal families contain `2n`
distinct pairs when `n >= 8`. Every member of `B` or `G` consumes at least one
unit of pair-capacity slack, so

```text
|B| + |G| <= d.                                      (1)
```

### Local side equalities

If gap-2 diagonal `i` is saturated, its two using centers lie on opposite
sides of its line. The short side contains only `v_{i+1}`, so that vertex is
one of the centers and

```text
s_i = s_{i+1}.                                       (2)
```

The earlier near-saturation proof chained these equalities around the entire
polygon. That global step fails after two distinct gap-2 deficits. The key
point here is that only a local chain of two equalities is needed.

Fix a gap-3 index `i` such that

```text
i notin G,   i notin B,   i+1 notin B.               (3)
```

The last two conditions and (2) give

```text
s_i = s_{i+1} = s_{i+2}.
```

The saturated gap-3 diagonal has one using center on its short side, which is
either `v_{i+1}` or `v_{i+2}`. If it is `v_{i+1}`, the equal-radius condition
and the equilateral local side triple force `tau_{i+2}=2*pi/3`. If it is
`v_{i+2}`, the symmetric argument forces `tau_{i+1}=2*pi/3`. Thus every index
satisfying (3) gives the turn clause

```text
tau_{i+1} = 2*pi/3  or  tau_{i+2} = 2*pi/3.           (4)
```

### Clause count

Let `M={j : tau_j=2*pi/3}`. A bad gap-3 index removes at most its own clause.
A bad gap-2 index can remove only the clauses at indices `i-1` and `i`.
Consequently at least

```text
h >= n - (2|B| + |G|)                                (5)
```

distinct edges of the turn-index cycle must meet `M`.

There cannot be three members of `M`: three turns of `2*pi/3` already sum to
`2*pi`, while every remaining exterior turn is strictly positive. Hence
`|M| <= 2`. Two vertices of a cycle meet at most four distinct cycle edges, so
`h <= 4`. Combining this with (5) gives

```text
n - 4 <= 2|B| + |G|
      <= 2(|B|+|G|)
      <= 2d,                                          (6)
```

where the last inequality is (1). Since `d` is an integer,

```text
d >= ceil((n-4)/2).
```

This proves the draft statement.

## What changed relative to the two-unit proof

`docs/near-saturation-support-obstruction.md` stopped at `d>=2` because two
distinct gap-2 deficits disconnect the global side-equality chain. That
diagnosis is correct for the global-equilateral argument but is not a boundary
for the local turn clauses. Away from the at most four clause indices touched
by those two deficits, the three consecutive sides needed for (4) are still
equal. This closes slack `2` for `n>=9`, slack `3` for `n>=11`, and in general
gives the linear bound above.

The local clause condition already appears in the finite `n=9` base-apex
diagnostic (`docs/n9-base-apex-frontier.md`). Its exhaustive escape search for
`n=8,...,12` reports minimum deficits `2,3,3,4,4`, exactly matching
`ceil((n-4)/2)`. That finite search is an independent cross-check, not an input
to the general proof.

## Consequences and scope

The first budgets are

| `n` | slack lower bound | support-pair budget |
|---:|---:|---:|
| 8 | 2 | 46 |
| 9 | 3 | 60 |
| 10 | 3 | 77 |
| 11 | 4 | 95 |
| 12 | 4 | 116 |

For hypothetical 4-bad polygons, integer rounding means this does not improve
the previously recorded floors of six exact-four centers at `n=10`, four at
`n=11`, and one at `n=12`; it strengthens the underlying mixed-profile budget
and excludes every support-size profile whose raw slack is below the displayed
linear threshold.

This is a support-pair counting lemma only. It does not classify the surviving
support systems, force a selected row, prove `n=9`, `n=10`, or any larger
finite case, or prove Erdos Problem #97.

## Verification

Run

```bash
python scripts/check_linear_slack_support_obstruction.py --check --json
```

The checker verifies the arithmetic rows and independently enumerates every
gap-2/gap-3 unit-deficit placement up to the first escape for `n=8,...,12`.
It checks the minimum deficits `2,3,3,4,4`. This validates the finite cyclic
bookkeeping; it does not replace review of the geometric saturation lemmas.
