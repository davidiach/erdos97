# Candidate incidence patterns

Each pattern assigns a 4-set `S_i` to each center `i`. These are incidence
designs only; geometric realization is a separate problem.

## Live ranked and numerical patterns

| Rank | Name | n | Formula | Type | Current status |
|---:|---|---:|---|---|---|
| 1 | `C19_skew` | 19 | offsets `{-8,-3,5,9}` | skew circulant | natural-order status: exactly killed by Altman diagonal-order sums; abstract-incidence status: live/sparse, with no `phi` edges and no mutual-rhombus, forced-perpendicularity, vertex-circle, or minimum-radius obstruction currently known[^repo] |
| 11 | `C13_sidon_1_2_4_10` | 13 | offsets `{1,2,4,10}` | Sidon circulant | natural-order status: exactly killed by Altman linear certificate; abstract-incidence status: Sidon sparse-overlap lead, not settled by current filters; SLSQP evidence plateaus at `eq_rms ~ 0.84` under strict convexity margins |
| 12 | `C25_sidon_2_5_9_14` | 25 | offsets `{2,5,9,14}` | Sidon circulant | natural-order status: exactly killed by Altman linear certificate; abstract-incidence status: Sidon sparse-overlap lead, not settled by current filters; cataloged but not yet run numerically |
| 13 | `C29_sidon_1_3_7_15` | 29 | offsets `{1,3,7,15}` | Sidon circulant | natural-order status: exactly killed by Altman linear certificate; abstract-incidence status: Sidon sparse-overlap lead, not settled by current filters; cataloged but not yet run numerically |

The live abstract-incidence patterns above pass the row-overlap filter
`|S_i cap S_j| <= 2` before numerical optimization. `C19_skew`'s natural-order
realization is already exactly obstructed; its abstract-order status is tracked
separately.[^comp] The Sidon natural orders are also exactly obstructed by
Altman linear certificates, but their arbitrary abstract-order status remains
separate. A registered non-natural `C13_sidon_1_2_4_10` order survives the
current fixed-order exact filters; see `docs/sparse-frontier-diagnostic.md`.
The Sidon entries are incidence-pattern leads, not geometric realizability
claims. The minimum-radius short-chord filter is also
recorded as a weak exact necessary test, but it does not kill `C19_skew` in
natural order or as currently implemented; see `docs/minimum-radius-filter.md`.
For the first fixed-selection stuck-set/radius/fragile-cover pass over this
frontier, see `docs/stuck-frontier-snapshot.md`.

## Natural-order killed / abstract-order status patterns

These patterns are killed if the natural label order `0,1,...,n-1` is the
cyclic order. Their abstract-incidence status is tracked separately when
arbitrary cyclic orders are allowed.

| Rank | Name | n | Formula | Type | Current status |
|---:|---|---:|---|---|---|
| U1 | `P18_parity_balanced` | 18 | even: `{-7,-2,4,8}`, odd: `{-8,-4,2,7}` | period-2 | natural-order status: killed by adjacent-row two-overlap via crossing-bisector; abstract-incidence status: killed by exact crossing plus vertex-circle order strict-cycle search |
| U2 | `P24_parity_balanced` | 24 | even: `{-10,-3,5,11}`, odd: `{-11,-5,3,10}` | period-2 | natural-order status: killed by adjacent-row two-overlap via crossing-bisector; abstract-incidence status: killed by exact finite crossing-CSP; no cyclic order satisfies all 36 required crossings |

## Speculative extensions

These came from the n=39 degeneracy review. They are not claims of geometric
realizability; they are examples of incidence families designed to avoid the
row-overlap failure that killed the n=39 branch.[^n39]

| Rank | Name | n | Formula | Type | Current status |
|---:|---|---:|---|---|---|
| 11 | `C41_offsets_5_14_24_34` | 41 | offsets `{5,14,24,34}` | prime cyclic | speculative incidence source |
| 12 | `C43_offsets_6_15_27_36` | 43 | offsets `{6,15,27,36}` | prime cyclic | speculative incidence source |
| 13 | `C45_offsets_4_13_25_37` | 45 | offsets `{4,13,25,37}` | Sidon-type cyclic | speculative incidence source |
| 14 | `C49_offsets_5_16_29_41` | 49 | offsets `{5,16,29,41}` | Sidon-type cyclic | speculative incidence source |
| 15 | `R44_four_lift_2_4_7_9` | 44 | `S_{4g+r}={4(g+a_t)+((r+t) mod 4): t=0..3}`, `a=(2,4,7,9)` | residue-rotating | speculative incidence source |

## Archived / killed patterns

| Rank | Name | n | Formula | Type | Current status |
|---:|---|---:|---|---|---|
| A1 | `Q8_cube_witness` | 8 | vertices `{0,1}^3`, witnesses at Hamming distance at least 2 | cube pattern | unrealizable by orthocenter obstruction; the full `n=8` case is now covered by the incidence/exact pipeline |
| A2 | `C39_pm_18_19` | 39 | `S_i={i+18,i-18,i+19,i-19}` mod 39 | circulant | impossible: adjacent rows share three targets, violating the two-circle cap[^n39] |
| A3 | `B12_3x4_danzer_lift` | 12 | `(a,b) -> {(a+1,b),(a+2,b),(a+1,b+1),(a+2,b-1)}` mod `(3,4)` | block/symmetric | exactly killed as a fixed selected pattern by mutual-rhombus midpoint equations; numerical near-miss remains useful as a degeneration diagnostic |
| A4 | `B20_4x5_FR_lift` | 20 | `(a,b) -> {(a+1,b),(a+3,b),(a+1,b+2),(a+3,b-2)}` mod `(4,5)` | block/symmetric | exactly killed as a fixed selected pattern by mutual-rhombus midpoint equations |
| A5 | `C17_skew` | 17 | offsets `{-7,-2,4,8}` | skew circulant | exactly killed by an odd forced-perpendicularity cycle |
| A6 | `C20_pm_4_9` | 20 | offsets `{-9,-4,4,9}` | palindromic circulant | exactly killed by mutual-rhombus midpoint equations; residue mod 4 collapse |
| A7 | `C16_pm_1_6` | 16 | offsets `{-6,-1,1,6}` | palindromic circulant | exactly killed by mutual-rhombus midpoint equations; parity collapse |
| A8 | `C13_pm_3_5` | 13 | offsets `{-5,-3,3,5}` | palindromic circulant | exactly killed by mutual-rhombus midpoint equations; all labels collapse |
| A9 | `C9_pm_2_4` | 9 | offsets `{-4,-2,2,4}` | palindromic circulant | exactly killed by mutual-rhombus midpoint equations; all labels collapse |

[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^comp]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/04_COMPUTATIONAL_FINDINGS.md`.
[^n39]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/12_n39_circulant_degeneracy.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
