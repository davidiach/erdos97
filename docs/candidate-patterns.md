# Candidate incidence patterns

Each pattern assigns a 4-set `S_i` to each center `i`. These are incidence designs only; geometric realization is a separate problem.

| Rank | Name | n | Formula | Type | Current status |
|---:|---|---:|---|---|---|
| 1 | `B12_3x4_danzer_lift` | 12 | `(a,b) -> {(a+1,b),(a+2,b),(a+1,b+1),(a+2,b-1)}` mod `(3,4)` | block/symmetric | best near-miss, degenerates to 3 clusters |
| 2 | `B20_4x5_FR_lift` | 20 | `(a,b) -> {(a+1,b),(a+3,b),(a+1,b+2),(a+3,b-2)}` mod `(4,5)` | block/symmetric | promising next margin sweep |
| 3 | `P18_parity_balanced` | 18 | even: `{-7,-2,4,8}`, odd: `{-8,-4,2,7}` | period-2 | worth basin-hopping / DE |
| 4 | `P24_parity_balanced` | 24 | even: `{-10,-3,5,11}`, odd: `{-11,-5,3,10}` | period-2 | more variables, harder search |
| 5 | `C19_skew` | 19 | offsets `{-8,-3,5,9}` | skew circulant | sparse common-neighbor overlap |
| 6 | `C17_skew` | 17 | offsets `{-7,-2,4,8}` | skew circulant | overdetermined but useful |
| 7 | `C20_pm_4_9` | 20 | offsets `{-9,-4,4,9}` | palindromic circulant | do not impose coordinate symmetry |
| 8 | `C16_pm_1_6` | 16 | offsets `{-6,-1,1,6}` | palindromic circulant | may encourage local edge collapse |
| 9 | `C13_pm_3_5` | 13 | offsets `{-5,-3,3,5}` | palindromic circulant | small smoke test |
| 10 | `C9_pm_2_4` | 9 | offsets `{-4,-2,2,4}` | palindromic circulant | likely too constrained |

All listed patterns satisfy the known pairwise common-selected-neighbor cap `<= 2`.
