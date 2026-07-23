# Complex two-mode cyclic candidate enumeration

Trust label: `NUMERICAL_EVIDENCE`.

See [`docs/complex-cyclic-construction-screens.md`](../../../docs/complex-cyclic-construction-screens.md)
for the combined two- and three-mode interpretation.

This directory records the floating candidate enumeration for

```text
z_i = w^i + c w^(k i),  w = exp(2 pi i/n),  c complex.
```

For a fixed center, every squared distance is affine in
`(R,x,y) = (|c|^2, Re(c), Im(c))`. The screen enumerates every row-zero
four-set, solves its three affine equality equations, intersects the solution
with `R=x^2+y^2`, and checks each resulting coefficient against all centers,
pairwise distinctness, and strict convexity. Rank-two lines and rank-one
planes receive separate continuation logic.

The retained run used:

```bash
python scripts/exploration/search_complex_two_mode_cyclic.py \
  --min-n 9 --max-n 30 \
  --out data/runs/complex_two_mode_cyclic_2026-07-22/summary.json
```

## Aggregate outcome

- 363 `(n,k)` cells and 3,253,635 row-zero quadruples;
- 2,837,118 nonsingular affine systems, 379,673 rank-two systems, and
  36,844 rank-at-most-one systems;
- no rank-zero identity quadruples and no continuous all-row rank-one planes;
- 128,434 deduplicated candidate coefficients, including 41,207 candidates
  produced by rank-one cross-row intersections;
- zero strictly convex hits at the `2e-8` floating equality tolerance;
- 1,617 exact-looking but invalid coefficients across 61 cells;
- best strictly convex result: `n=15`, `k=7`, relative spread
  `0.0273661273589857`, normalized turn margin `0.00248098061229757`, and
  normalized pair separation `0.128312313256038`.

The screen found no strictly convex coefficient near the exactification
regime. Of the 61 cells with an exact-looking invalid best coefficient, all
have a nonpositive normalized turn and 56 also collapse a pair to numerical
coincidence.

## Exact duplicate degeneration

The prominent `n=12`, `k=7` mirage has

```text
c = i(2+sqrt(3)).
```

Writing `w=exp(i*pi/6)`, one has `w^(7j)=(-1)^j w^j` and

```text
(1+c)/(1-c) = w^5.
```

Therefore `z_e=z_(e+5)` for every even `e` modulo 12. The six coincident
pairs are `(0,5)`, `(1,8)`, `(2,7)`, `(3,10)`, `(4,9)`, and `(6,11)`.
The equality spread is machine-small, but the configuration is a doubled
hexagon rather than a strictly convex 12-gon.

`summary.json` has SHA-256
`bb81f9030782b09428fe70ac2c459889f3b357c02695144bed343f613acbf908`.

This is a tolerance-controlled floating enumeration, not an exact
classification of the complex two-mode family. Zero hits are not an
obstruction, proof, or counterexample.
