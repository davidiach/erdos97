# Dumitrescu Isosceles Shortcut For n <= 8

Status: `LITERATURE_BACKED_PROOF_NOTE` / `REVIEW_PENDING`.

This note records a short literature-backed route to the same small-case wall
as the repository's machine-checked selected-witness artifacts. It does not
change the source-of-truth status: no general proof and no counterexample are
claimed, and the repo-local `n <= 8` result remains grounded in the checked
finite-case pipeline until independent review promotes any paper-style proof.

## Counting Convention

For a finite strictly convex point set `P`, let

```text
Z(P) = sum_{p in P} sum_delta binom(m_p(delta), 2),
```

where `m_p(delta)` is the number of other vertices at distance `delta` from
`p`. Equivalently, `Z(P)` counts unordered equal-leg pairs at an apex `p`.
With this convention an equilateral triangle is counted three times, once for
each possible apex. This is the same apex-counted convention used by
Nivasch--Pach--Pinchasi--Zerbib and by Dumitrescu's isosceles-triangle bound.

Dumitrescu's convex-position bound is

```text
Z(P) <= (11 n^2 - 18 n) / 12.
```

The exact expression is the only external input in this shortcut.

## Shortcut

Suppose `P` is 4-bad: every vertex has at least four other vertices at one
common distance. Then each apex contributes at least

```text
binom(4,2) = 6
```

apex-counted isosceles triangles, so

```text
Z(P) >= 6n.
```

Combining with Dumitrescu's upper bound gives

```text
6n <= (11 n^2 - 18 n) / 12.
```

For `n > 0`, this is equivalent to

```text
72n <= 11 n^2 - 18n,
90n <= 11 n^2,
n >= 90/11 > 8.
```

Therefore no strictly convex 4-bad polygon exists with `n <= 8`.

## n = 9 Slack

For `n = 9`, Dumitrescu's bound gives

```text
Z(P) <= (11*9^2 - 18*9) / 12 = 729/12 = 60.75.
```

Since `Z(P)` is integral, `Z(P) <= 60`. The 4-bad lower bound gives only
`Z(P) >= 54`, leaving slack `6`. Thus this shortcut stops exactly before the
`n = 9` frontier and does not promote any `n = 9` artifact.

## Review Notes

- This note is independent of the selected-witness enumeration, but it uses an
  external literature bound and should be reviewed against the cited counting
  convention before being treated as a paper-style proof.
- It does not update `README.md`, `STATE.md`, `RESULTS.md`, or
  `metadata/erdos97.yaml`.
- It is consistent with the repository's existing `n <= 8` artifacts and gives
  a compact human-readable shortcut, not a new global claim.

## References

- A. Dumitrescu, "On Distinct Distances from a Vertex of a Convex Polygon."
  Accessible copy:
  <https://www.academia.edu/118624932/On_Distinct_Distances_from_a_Vertex_of_a_Convex_Polygon>.
- G. Nivasch, J. Pach, R. Pinchasi, and S. Zerbib, "The number of distinct
  distances from a vertex of a convex polygon." Accessible JoCG copy:
  <https://jocg.org/index.php/jocg/article/download/2937/2631/7290>.
