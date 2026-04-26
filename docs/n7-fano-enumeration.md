# n=7 Fano-incidence enumeration

Status: **THEOREM / EXACTIFICATION** for the selected-witness `n=7` equality case only. This does **not** prove the full Erdős #97 problem and does **not** give a counterexample.

This note supports issue #2, “Enumerate all n=7 Fano-incidence cyclic labelings up to dihedral symmetry.” It gives a deterministic, dependency-free enumerator and a checked-in JSON artifact containing canonical representatives and their induced perpendicularity constraints.

## Why n=7 reduces to Fano incidence

Let `W_i` be a selected witness 4-set for center `i`, and assume the pairwise circle-intersection cap

```text
|W_i ∩ W_j| <= 2    for i != j.
```

For `n=7`, the standard counting argument is tight. Every vertex has selected indegree `4`, and every pair of selected rows intersects in exactly two vertices. Define the complement triples

```text
T_i = {0, ..., 6} \ W_i.
```

Then each `T_i` is a 3-set containing `i`, and every two triples `T_i,T_j` intersect in exactly one point. The seven triples therefore form a labelled Fano plane, with a row assignment `i -> T_i` that is incident point-to-line.

## What was enumerated

The script `scripts/enumerate_n7_fano.py` enumerates:

```text
30   labelled Fano planes on labels 0..6
720  row-indexed equality families T_0,...,T_6 with i in T_i
54   canonical representatives modulo the cyclic dihedral action x -> ±x + shift mod 7
```

The dihedral orbit-size distribution is:

```text
orbit size 14: 51 representatives
orbit size  2:  3 representatives
```

The machine-readable artifact is checked in as:

```text
data/incidence/n7_fano_dihedral_representatives.json
```

Each representative records:

- complement triples `T_i`;
- witness rows `W_i`;
- the 21 induced radical-axis perpendicularity constraints;
- the chord-cycle decomposition.

## Perpendicularity obstruction

For a pair of centers `{i,j}`, the two shared selected targets

```text
W_i ∩ W_j = {a,b}
```

force the chord `p_i p_j` to be perpendicular to the chord `p_a p_b`: both centers lie on the perpendicular bisector of the target chord.

Thus every n=7 equality family induces a map on the 21 unordered chords:

```text
{i,j} -> W_i ∩ W_j.
```

The enumerator verifies that, for every one of the 720 labelled equality families, this chord map is a permutation with cycle lengths

```text
7, 7, 7
```

Every family therefore has an odd perpendicularity cycle. Alternating perpendicularity around an odd cycle is impossible in the Euclidean plane: after an odd number of quarter-turn constraints, the initial nonzero chord direction would have to be perpendicular to itself. Since a strictly convex polygon has distinct vertices, all chords are nonzero.

Therefore no `n=7` selected-witness equality family survives the radical-axis perpendicularity check.

## Reproduce

From the repository root:

```bash
python scripts/enumerate_n7_fano.py --summary
python scripts/enumerate_n7_fano.py --check-data data/incidence/n7_fano_dihedral_representatives.json --summary
pytest -q tests/test_n7_fano.py
```

Expected summary counts:

```json
{
  "labelled_fano_planes": 30,
  "pointed_fano_patterns": 720,
  "dihedral_classes": 54,
  "dihedral_orbit_size_distribution": {"2": 3, "14": 51},
  "cycle_type_counts": {"7+7+7": 54},
  "all_pattern_cycle_type_counts": {"7+7+7": 720},
  "classes_with_odd_perpendicularity_cycle": 54,
  "all_classes_obstructed": true
}
```

## Scope and caveats

This is a finite exact obstruction for `n=7`. It does not address larger `n`, and it relies on the selected-witness convention where each bad vertex contributes one chosen 4-set `W_i`. That convention is safe for proving impossibility: any true `E(i) >= 4` counterexample would allow such a selected witness subfamily.
