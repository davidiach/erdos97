# n=9 Base-apex D=3 P19 Degree Obstruction

Status: `EXACT_FINITE_PROFILE_CAPACITY_OBSTRUCTION` for the P19 rows of the
D=3 profile-capacity packet only.

This note closes the first eight representative rows `R000..R007` of
`data/certificates/n9_base_apex_d3_incidence_capacity_packet.json`. It does not
prove `n=9`, does not claim a counterexample, does not test Euclidean
realizability, and does not update the official/global status of Erdos Problem
#97.

## Packet slice

The D=3 packet has `88` representative profile/escape rows, arranged as the
`11` profile multisets `P19..P29` crossed with the `8` escape classes
`X00..X07`. The P19 multiset is

```text
[0,0,0,0,0,0,0,0,6].
```

In distance-profile terms, this means eight centers have profile
`[4,1,1,1,1]`, and one center has profile `[4,4]`.

## Incident-degree congruence

For one apex/center, count the generated base pairs incident to a fixed vertex
`v`.

A `[4,1,1,1,1]` profile contributes either `3` to `v` if `v` lies in the
4-class, or `0` otherwise. A `[4,4]` profile contributes `3` to every non-center
vertex, and `0` to the center itself. Therefore every P19 profile-capacity
assignment has incident base-pair count divisible by `3` at every vertex.

In a nonagon, the full base-apex incident capacity at a fixed vertex is

```text
2 side capacities + 6 diagonal capacities = 2*1 + 6*2 = 14.
```

A D=3 escape row subtracts one unit from each endpoint of its three deficient
length-2 or length-3 base chords. If `delta_v` is the number of deficient chords
incident to `v`, the target incident count at `v` is

```text
14 - delta_v.
```

For this to be divisible by `3`, every `delta_v` would have to be `2 mod 3`.
But the three deficient chords have total endpoint degree

```text
sum_v delta_v = 6.
```

It is impossible for all nine vertices to have deficient degree `2 mod 3` with
total degree `6`. Thus no P19 row can satisfy the exact profile-capacity target,
independent of which center carries the `[4,4]` profile and independent of the
chosen distance classes.

## Checker

The checker treats the checked-in D=3 packet as input data and verifies this
obstruction row-by-row for `R000..R007`:

```bash
python scripts/check_n9_base_apex_d3_p19_degree_obstruction.py \
  --check \
  --assert-expected \
  --json
```

A passed check reports:

```text
rows_closed: 8
remaining_packet_rows: 80
```

## What remains

This closes only the P19 profile-capacity slice. The companion P20 residue
obstruction closes the next slice in
`docs/n9-base-apex-d3-p20-residue-obstruction.md`. The remaining D=3 profile
ledgers `P21..P29` remain finite targets for the profile-capacity feasibility
program. A useful next checker would try analogous degree, parity, or cut
constraints on those nine remaining profile multisets before resorting to a
full exact CSP.
