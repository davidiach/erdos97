# n=8 Exact Survivor Obstruction Artifact

Status: `EXACT_OBSTRUCTION`.

This note records an exact obstruction pass over a reconstructed canonical list of
15 `n=8` selected-witness incidence classes. The list was reconstructed from the
known incidence filters:

- zero diagonal;
- row sums 4;
- column sums 4;
- row-pair dot products at most 2;
- column-pair dot products at most 2;
- no odd forced-perpendicularity cycle;
- no same-color forced-parallel chords sharing an endpoint.

The reconstruction produced exactly 15 simultaneous-relabeling classes. In this
workspace, these classes were compared against the archived
`erd archive/outputs/data/n8_exact_geometry_filter_results.json` artifact and
matched exactly up to simultaneous relabeling. The independent incidence
enumerator in `docs/n8-incidence-enumeration.md` now reproduces the same 15
classes from the strong selected-witness convention and necessary incidence
filters.

The archived IDs map to reconstructed IDs as follows:

| archived ID | reconstructed ID |
| ---: | ---: |
| 2 | 12 |
| 7 | 11 |
| 8 | 10 |
| 9 | 14 |
| 19 | 7 |
| 28 | 9 |
| 51 | 5 |
| 70 | 6 |
| 88 | 8 |
| 92 | 2 |
| 117 | 4 |
| 120 | 1 |
| 134 | 13 |
| 138 | 3 |
| 139 | 0 |

## Exact filters applied

For each class, write `W_i` for the selected witness set in row `i`. Whenever

```text
|W_i cap W_j| = 2,
```

define

```text
phi({i,j}) = W_i cap W_j.
```

The source chord `{i,j}` and target chord `phi({i,j})` are forced perpendicular,
because the two centers lie on the perpendicular bisector of the common witness
chord.

The forced-perpendicularity graph is built on the 28 unordered chords. Each
bipartite component has two color classes; chords in the same color class are
forced parallel.

The new cyclic-order filter enumerates all cyclic orders of the 8 labels modulo
rotation and reversal, normalized by

```text
order[0] = 0,
order[1] < order[-1].
```

For every order, every same-color forced-parallel class must be a noncrossing
matching. This kills class `12`.

The new perpendicular-bisector filter uses the full implication for every phi edge

```text
{i,j} -> {a,b}.
```

With coordinates `p_k = (x_k,y_k)`, the equations are

```text
(p_i - p_j) dot (p_a - p_b) = 0,
det(p_j - p_i, p_a + p_b - 2 p_i) = 0.
```

The second equation is twice the midpoint-line condition, so no denominators are
introduced.

The gauge is

```text
p_0 = (0,0),
p_1 = (1,0),
y_2 != 0.
```

The optional full equal-distance equations are also generated:

```text
|p_i - p_other|^2 - |p_i - p_base|^2 = 0,
other in W_i \ {base}.
```

## Result summary

For the reconstructed 15-class list:

```text
cyclic-order noncrossing kills: 1 class
remaining after cyclic-order filter: 14 classes
final survivors after exact geometry: 0 classes
```

Compatible cyclic-order counts:

| class | compatible cyclic orders |
| ---: | ---: |
| 0 | 2520 |
| 1 | 280 |
| 2 | 21 |
| 3 | 2520 |
| 4 | 280 |
| 5 | 4 |
| 6 | 280 |
| 7 | 50 |
| 8 | 538 |
| 9 | 100 |
| 10 | 74 |
| 11 | 44 |
| 12 | 0 |
| 13 | 280 |
| 14 | 72 |

Class `12` has no compatible cyclic order.

Classes `0,1,2,6,7,8,9,10,11,13` are killed by exact rational linear algebra:
`y2` lies in the rational linear span of the perpendicular-bisector equations, so
every solution has `y2 = 0`, contradicting the gauge.

Class `3` is killed by duplicate vertices. The perpendicular-bisector equations
force, on the nondegenerate branch,

```text
p_2 = (1/2,t),
p_3 = (1/2,-t),
p_4 = (-1/2,t),
t^2 = 3/4,
p_7 = p_0.
```

Class `4` is killed by three collinear vertices. The equations force

```text
p_2 = (1/2,t),
p_3 = (1/2,-t),
p_4 = (1/2, y_4),
4t^2 = 3,
```

so `p_2,p_3,p_4` are collinear.

Class `5` is killed by an exact Groebner contradiction. After the exact
substitutions forced by early perpendicular-bisector equations,

```text
x3 = x2,
y3 = -y2,
x6 = 2*x2 - x4,
y6 = y4,
```

the Groebner basis over `QQ` contains `y2`, contradicting `y2 != 0`.

Class `14` is killed by the full perpendicular-bisector plus equal-distance
system. Its exact Groebner basis exposes four real algebraic branches. In every
branch, exactly four labels are convex-hull vertices and the other four labels
are strict interior points, so no strictly convex realization exists.

## Reproduction

Run from the repository root after installing the development dependencies:

```bash
pip install -e .[dev]
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/analyze_n8_exact_survivors.py --check --json --check-compatible-orders-data data/incidence/n8_compatible_orders.json --check-exact-analysis-data certificates/n8_exact_analysis.json
pytest -q
```

When the archive artifact is available, also run:

```bash
python scripts/analyze_n8_exact_survivors.py --check --json --provenance-json "<path-to-archive>/n8_exact_geometry_filter_results.json"
```

The script performs no numerical optimization and uses no floating-point equality.
It recomputes the cyclic-order counts, the rational linear-span kills, the class
`3` duplicate-vertex certificate, the class `4` collinearity certificate, the
class `5` Groebner contradiction, the class `14` Groebner and strict-interior
certificate, and the optional archived-ID mapping.

The expanded polynomial systems and full compatible cyclic-order lists are stored
as reproducibility artifacts:

```text
data/incidence/n8_reconstructed_15_survivors.json
data/incidence/n8_compatible_orders.json
certificates/n8_exact_analysis.json
certificates/n8_polynomial_systems.txt
```

## Remaining review gap

The incidence-completeness gap is closed in this repository by
`data/incidence/n8_incidence_completeness.json`. The remaining risk is ordinary
computer-assisted-proof review: independently review the class `3`, `4`, and
`14` exact certificates and the checker implementation before making an
external theorem claim.
