# Complex three-mode cyclic construction screen

Trust label: `NUMERICAL_EVIDENCE`.

See [`docs/complex-cyclic-construction-screens.md`](../../../docs/complex-cyclic-construction-screens.md)
for the combined two- and three-mode interpretation.

This directory records the deterministic seeded construction screen for

```text
z_i = w^i + c w^(k i) + d w^(ell i),  w = exp(2 pi i/n),  c,d complex.
```

The run covered all 560 unordered mode pairs `2 <= k < ell < n` for
`12 <= n <= 18`, with 12 starts per cell and at most 8 alternating witness
selection / least-squares cycles per start. It used this command:

```bash
python scripts/exploration/search_complex_three_mode_cyclic.py \
  --min-n 12 --max-n 18 --restarts 12 --max-cycles 8 --workers 12 \
  --out data/runs/complex_three_mode_cyclic_2026-07-22/summary.json
```

The numerical candidate gate required maximum relative four-distance spread
at most `1e-10`, normalized pair separation at least `2e-3`, and normalized
strict-convexity side margin at least `2e-6`. The run found zero accepted
cells. The strongest robust result was `n=15`, modes `(10,13)`, with maximum
relative spread `0.0198748713248327`, normalized side margin
`0.00267608633453876`, and normalized pair separation `0.128455903709775`.

`summary.json` has SHA-256
`80dfbaa02768fb53bbc7673b0b1ac50c8fec3881e15ed839d53ee21e7c200585`.
It retains every cell's best coefficients, selected witness windows, geometry
margins, restart index, and timing.

This is a finite, seeded heuristic search. Zero hits do not obstruct the
three-mode family, and the run is not a proof or counterexample.
