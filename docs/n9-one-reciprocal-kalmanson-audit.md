# n=9 One-Reciprocal Kalmanson Audit

Status: `EXACT_N9_ONE_RECIPROCAL_SUBCASE_AUDIT`.

This note records a narrow exact subcase audit for selected-witness systems on
nine cyclically ordered labels. It extends the regular-tournament/no-reciprocal
branch cut by one reciprocal pair. It does not prove `n=9`, does not prove Erdős
Problem #97, and does not change the repository source-of-truth status. The
review-pending exhaustive `n=9` vertex-circle checker remains the stronger
finite-case artifact.

Replay:

```bash
python scripts/check_n9_one_reciprocal_kalmanson.py --assert-expected --json
```

The replay checks `76` cyclic-dihedral status representatives, covering all
`36 * 35 = 1,260` labelled choices of one reciprocal selected unordered pair
and one absent unordered pair. For each representative it searches all degree-4
orientations of the remaining `34` unordered pairs.

## Subcase

For `n=9`, every selected-witness row has size `4`, so there are `9 * 4 = 36`
directed selections. There are also `binom(9,2) = 36` unordered pairs.

If exactly one unordered pair is selected reciprocally, then the count forces
exactly one unordered pair to be unselected. Every other unordered pair is
selected in exactly one direction. Thus the subcase is determined by:

- one reciprocal pair `{a,b}` contributing both selections `a -> b` and
  `b -> a`;
- one absent pair `{c,d}` contributing no selected direction;
- an orientation of every other unordered pair;
- outdegree `4` at every label.

The reciprocal pair identifies the two corresponding row-radius variables. The
absent pair remains an ordinary distance variable. Every singly selected pair
is represented by the row-radius variable at its selected tail.

## Strict Kalmanson implications

For cyclic labels `i < j < k < l`, strict convexity gives the two strict
Kalmanson inequalities

```text
d_ij + d_kl < d_ik + d_jl,
d_il + d_jk < d_ik + d_jl.
```

After substituting selected-distance quotient variables, a common quotient
class on the left and right can be cancelled. Each one-term cancellation gives
a strict implication between quotient classes. The checker maintains the
transitive closure of these implications and prunes as soon as it creates a
strict cycle.

The pruning is monotone: orienting more selected pairs can only assign more
edge terms and add more strict implications; it never removes an already found
strict cycle.

## Checked result

The replay reports:

```json
{
  "absent_pair_count": 1,
  "checked_all": true,
  "checked_representatives": 76,
  "dihedral_orbits": 76,
  "first_survivor": null,
  "kalmanson_acyclic_survivors_found": 0,
  "kalmanson_inequalities": 252,
  "labelled_status_pairs": 1260,
  "limit_representatives": null,
  "max_search_nodes": 12770,
  "max_search_status": {
    "absent_edge": [2, 5],
    "orbit_multiplicity": 18,
    "reciprocal_edge": [0, 4]
  },
  "n": 9,
  "reciprocal_pair_count": 1,
  "status": "EXACT_N9_ONE_RECIPROCAL_SUBCASE_AUDIT",
  "target_outdegree": 4,
  "total_search_nodes": 404189,
  "unordered_pairs": 36,
  "use_dihedral_reduction": true
}
```

Consequently, under the fixed cyclic order on nine labels, every
exactly-one-reciprocal selected-witness system is obstructed by strict
Kalmanson implication cycles.

Combined with the no-reciprocal regular-tournament audit, this gives the
following branch cut for `n=9` proof search: any selected-witness candidate must
have at least two reciprocal selected unordered pairs. Since the selected-edge
count balances reciprocal and absent unordered pairs, it must also have at
least two absent unordered pairs.

## Scope

This is not a full `n=9` obstruction. The cases with two or more reciprocal
selected pairs remain outside this audit and still require the existing
selected-distance quotient, vertex-circle, same-distance clique, `K4-e`,
Kalmanson/Farkas, or other exact filters. The result is best used as a cheap
exact branch cut before heavier `n=9` frontier tools.
