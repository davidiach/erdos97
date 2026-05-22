# n=9 Base-apex D=3 P20 Residue Obstruction

Status: `EXACT_FINITE_PROFILE_CAPACITY_OBSTRUCTION` for the P20 rows of the
D=3 profile-capacity packet only.

This note closes the second eight representative rows `R008..R015` of
`data/certificates/n9_base_apex_d3_incidence_capacity_packet.json`. It does not
prove `n=9`, does not claim a counterexample, does not test Euclidean
realizability, and does not update the official/global status of Erdos Problem
#97.

## Packet slice

The D=3 packet has `88` representative profile/escape rows, arranged as the
`11` profile multisets `P19..P29` crossed with the `8` escape classes
`X00..X07`. The P20 multiset is

```text
[0,0,0,0,0,0,0,1,5].
```

In distance-profile terms, this means seven centers have profile
`[4,1,1,1,1]`, one center has profile `[4,2,1,1]`, and one center has profile
`[5,2,1]`.

## Incident-residue support count

Work modulo `3` with incident base-pair counts at each vertex.

A `[4,1,1,1,1]` profile contributes either `3` to a vertex if the vertex lies
in the 4-class, or `0` otherwise. Hence the seven excess-0 rows contribute only
zero residues modulo `3`.

A `[4,2,1,1]` profile contributes residue `1` exactly at the two vertices in
its 2-class. A `[5,2,1]` profile contributes residue `1` at the five vertices
in its 5-class and at the two vertices in its 2-class, hence at exactly seven
vertices. Therefore the P20 profile side can produce residue `2` only where
those two residue-1 supports overlap, so at at most two vertices.

In a nonagon, the full base-apex incident capacity at a fixed vertex is

```text
2 side capacities + 6 diagonal capacities = 2*1 + 6*2 = 14.
```

A D=3 escape row subtracts one unit from each endpoint of its three deficient
length-2 or length-3 base chords. If `delta_v` is the deficient-chord endpoint
degree at vertex `v`, the target incident count at `v` is

```text
14 - delta_v.
```

Every vertex missed by the three deficient chords has `delta_v = 0`, and thus
has target residue

```text
14 = 2 mod 3.
```

Three chords touch at most six vertices, so at least three vertices have
`delta_v = 0`. The target side therefore needs residue `2` at at least three
vertices, while the P20 profile side can supply residue `2` at at most two
vertices. This contradiction is independent of the escape class and independent
of which centers carry the excess-1 and excess-5 profiles.

## Checker

The checker treats the checked-in D=3 packet as input data and verifies this
obstruction row-by-row for `R008..R015`:

```bash
python scripts/check_n9_base_apex_d3_p20_residue_obstruction.py \
  --check \
  --assert-expected \
  --json
```

A passed check reports:

```text
rows_closed: 8
combined_p19_p20_closed_rows: 16
remaining_packet_rows_after_p19_p20: 72
```

## What remains

Together with the existing P19 degree obstruction, this closes `16` of the
`88` D=3 profile-capacity packet rows and leaves `72` rows from `P21..P29` as
finite targets.

This is not an incidence-completeness result, not a geometric realizability
test, and not a proof of `n=9`. A useful next checker would try analogous
residue-support, parity, cut, or exact profile-capacity constraints on the
remaining profile multisets before resorting to a full exact CSP.
