# n=9 Regular-Tournament Kalmanson Audit

Status: `EXACT_N9_NO_RECIPROCAL_SUBCASE_AUDIT`.

This note records a narrow exact subcase audit for selected-witness systems on
nine cyclically ordered labels. It does not prove `n=9`, does not prove Erdos
Problem #97, and does not change the repository source-of-truth status. The
review-pending exhaustive `n=9` vertex-circle checker remains the stronger
finite-case artifact.

Replay:

```bash
python scripts/check_n9_regular_tournament_kalmanson.py --assert-expected --json
```

The full replay enumerates `3,230,080` labelled regular tournaments and checks
`252` strict Kalmanson inequalities per cyclic order.

## Subcase

Consider a selected-witness system on cyclic labels `0,1,...,8` in which no
unordered pair is selected in both directions. Since each of the nine rows has
four selected witnesses, there are `9 * 4 = 36` directed selections. This equals
the number of unordered pairs `binom(9,2)`. Therefore every unordered pair is
selected in exactly one direction, and the selected incidence data is exactly a
labelled regular tournament: every vertex has outdegree `4`.

For such a tournament, let `rho_i` denote the selected row radius at center
`i`. If the unordered pair `{a,b}` is selected by `a`, then its ordinary
distance is represented by `rho_a`; if it is selected by `b`, it is represented
by `rho_b`.

## Strict Kalmanson Implications

For cyclic labels `i < j < k < l`, strict convexity gives the two strict
Kalmanson inequalities

```text
d_ij + d_kl < d_ik + d_jl,
d_il + d_jk < d_ik + d_jl.
```

After substituting row-radius variables from the tournament orientation, some
inequalities have one equal row variable on both sides. Cancelling that common
term gives a strict implication

```text
rho_a < rho_b.
```

The checker builds the directed implication graph on the nine row-radius
variables. Any directed cycle is impossible, since it would imply
`rho_i < rho_i` after summing strict inequalities.

## Checked Result

The replay reports:

```json
{
  "acyclic_implication_failures": 0,
  "checked_all": true,
  "kalmanson_inequalities": 252,
  "n": 9,
  "status": "EXACT_N9_NO_RECIPROCAL_SUBCASE_AUDIT",
  "strong_connectivity_failures": 0,
  "target_outdegree": 4,
  "total_regular_tournaments": 3230080
}
```

In fact, every enumerated regular tournament has a strongly connected strict
implication graph, which is stronger than merely having a directed cycle.

Consequently, under the fixed cyclic order on the nine labels, every
no-reciprocal selected-witness system is obstructed by strict Kalmanson
inequalities. Equivalently, any genuine `n=9` selected-witness candidate must
contain at least one reciprocal selected pair.

## Scope

This is not a full `n=9` obstruction. The reciprocal-pair cases remain outside
this audit and require the existing selected-distance quotient,
vertex-circle, same-distance clique, `K4-e`, or other exact filters. The result
is best used as a cheap exact branch cut before heavier `n=9` frontier tools.
