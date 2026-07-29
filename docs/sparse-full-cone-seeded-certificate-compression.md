# Sparse full-cone seeded certificate compression

Status: bounded randomized search with exact fixed-pattern, fixed-order
outputs. No general proof, all-order C25/C29 obstruction, geometric
counterexample, or official-status change is claimed.

## Method

The source packet
`data/runs/sparse_full_cone_seeded_cegar_2026-07-23/summary.json` contains
eight newly learned exact full-cone certificates for each sparse pattern,
together with sixteen counterfactual probe orders per pattern.

For each of the sixteen certificates,
`scripts/exploration/compress_sparse_full_cone_seeded_certificates.py` sampled
24 deterministic pseudorandom LP objectives over all fixed-order Kalmanson
rows. A numerical support was retained only after exact positive integer
weights were recovered, its quotient-vector sum checked as zero, and modular
rank certified it as a positive circuit.

Each retained circuit was then expanded through every exact
quotient-preserving affine image. As in the seeded run, only translations are
valid for these two quotients. Coverage was measured both for the direct
compressed clause and for its full translation orbit over all 48 stored fresh
orders: 32 probe orders and 16 seeded models.

## Exact compression result

| Pattern | Source model | Original width | Compressed width | Best trial |
|---|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 0 | 188 | 7 | 20 |
| `C25_sidon_2_5_9_14` | 1 | 202 | 116 | 14 |
| `C25_sidon_2_5_9_14` | 2 | 209 | 8 | 14 |
| `C25_sidon_2_5_9_14` | 3 | 208 | 5 | 0 |
| `C25_sidon_2_5_9_14` | 4 | 204 | 122 | 18 |
| `C25_sidon_2_5_9_14` | 5 | 206 | 119 | 12 |
| `C25_sidon_2_5_9_14` | 6 | 205 | 118 | 20 |
| `C25_sidon_2_5_9_14` | 7 | 208 | 3 | 5 |
| `C29_sidon_1_3_7_15` | 0 | 294 | 5 | 19 |
| `C29_sidon_1_3_7_15` | 1 | 294 | 4 | 8 |
| `C29_sidon_1_3_7_15` | 2 | 291 | 184 | 9 |
| `C29_sidon_1_3_7_15` | 3 | 293 | 181 | 1 |
| `C29_sidon_1_3_7_15` | 4 | 290 | 182 | 22 |
| `C29_sidon_1_3_7_15` | 5 | 289 | 183 | 0 |
| `C29_sidon_1_3_7_15` | 6 | 289 | 190 | 21 |
| `C29_sidon_1_3_7_15` | 7 | 292 | 4 | 23 |

Seven of the sixteen exact circuits have only `3` through `8` ordered
quadrilaterals. The other nine retain widths `116` through `190`. This sharp
split was not assumed by the search.

## Exact cross-order coverage

| Pattern | Stored targets | Probe targets covered | Seeded targets covered | Direct cross-edges | Translation-orbit cross-edges |
|---|---:|---:|---:|---:|---:|
| `C25_sidon_2_5_9_14` | 24 | 0/16 | 8/8 | 11 | 19 |
| `C29_sidon_1_3_7_15` | 24 | 0/16 | 8/8 | 21 | 21 |

No compressed circuit, even after all exact translations, covers any fresh
probe order. Reuse is concentrated inside the seeded-model packets:

- the C25 5-quad circuit from model 3 directly covers seeded models 1 through
  7;
- the C25 3-quad circuit from model 7 covers seeded models 1 through 7 after
  translation expansion;
- the three C29 circuits of widths `5`, `4`, and `4` each directly cover all
  eight seeded models.

Thus small exact circuits recover substantial bounded reuse that was invisible
to the original 188--294-quad clauses. They still do not bridge to the
counterfactual probe stream.

## Quotient-vector reuse

The C25 circuits contain 492 distinct quotient vectors. Only 6 occur in more
than one certificate, no vector occurs in three certificates, and the largest
pairwise overlap is 2 vectors.

The C29 circuits contain 918 distinct quotient vectors. Only 20 occur in more
than one certificate, no vector occurs in three certificates, and the largest
pairwise overlap is 4 vectors.

The observed clause reuse therefore does not come from a large common
quotient-vector core. It comes from a few very small positive circuits whose
ordered-quadrilateral supports recur across the seeded order cluster.

## Scope and next target

The 24-objective search is not exhaustive, and the coverage matrix contains
only the 48 stored orders. The result does not imply all-order coverage for
either abstract pattern.

That target is completed in
`docs/sparse-full-cone-small-template-fresh-stream.md`. The seven circuits were
canonicalized as explicit exact templates and replayed over 64 deterministic
orders dihedrally disjoint from the 48-order source packet. None of the 187
affine template images matched a fresh order, including all 63 fresh
lightweight survivors. The current evidence therefore treats these circuits
as cluster-specific diagnostics. The next target is an exact full-cone screen
of those 63 survivors, not an all-order inference from the zero-hit sample.

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_seeded_certificates.py \
  --check data/runs/sparse_full_cone_seeded_compression_2026-07-29/summary.json
```
