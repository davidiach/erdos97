# Transverse Edge-Event And Cap-Cut Constraints

Status: `RESEARCH_PACKET`.

This note records two local necessary-condition packets for selected-witness
systems. They do not solve Erdos Problem #97, do not promote any finite-case
claim, and do not change the repository source of truth. Their purpose is to
turn arbitrary selected 4-ties into exact constraints that can be checked,
mined, or later combined with stronger bridge arguments.

The two packets are deliberately complementary:

- the edge-event packet works with actual polygon coordinates and edge-vector
  identities;
- the cap-cut packet works in squared-distance variables for a fixed selected
  witness system and cyclic order.

## Edge-Event / Gram Packet

Let `P=(p_0,...,p_{n-1})` be a strictly convex polygon in cyclic order and put

```text
e_k = p_{k+1} - p_k
```

with indices modulo `n`. Define

```text
D_{i,k} = |p_i - p_{k+1}|^2 - |p_i - p_k|^2.
```

Then the exact first-difference identity is

```text
D_{i,k} = (|p_{k+1}|^2 - |p_k|^2) - 2 p_i . e_k.
```

Thus the matrix `D` has rank at most `3`. Adjacent row differences recover the
edge Gram matrix:

```text
D_{i+1,k} - D_{i,k} = -2 e_i . e_k.
```

So, for `G_{i,k}=e_i.e_k`,

```text
G is positive semidefinite,   rank(G) <= 2,   G 1 = 0.
```

If a selected row centered at `i` has four equal-distance witnesses
`a_1,a_2,a_3,a_4` in boundary order around `p_i`, each consecutive gap
`I_s=[a_s,a_{s+1})` satisfies the zero interval identity

```text
sum_{k in I_s} D_{i,k} = 0.
```

The stronger transverse signs are

```text
sum_{k in I_s} G_{i,k} < 0,
sum_{k in I_s} G_{i-1,k} < 0.
```

Equivalently,

```text
sum_{k in I_s} D_{i+1,k} > 0,
sum_{k in I_s} D_{i-1,k} < 0.
```

This is stronger than raw row sign-change counting. The open bridge problem is
to prove that no closed positive-turn edge system can support the `3n`
selected zero intervals with these transverse signs and the Gram constraints,
or to find the extra condition needed to make that statement true.

The coordinate extractor is:

```bash
python scripts/check_edge_event_packet.py input.json --assert-verified
```

The input JSON uses `coordinates` or `vertices`, and may include
`selected_rows` as either a dictionary or a list of row records.

## Cap-Cut / Squared-Chord Packet

Write

```text
D_uv = |p_u - p_v|^2.
```

If `D_ia = D_ib` and `x` lies on the open boundary arc from `a` to `b` that
does not contain `i`, strict convexity gives the centered cap-cut inequality

```text
2D_ix - D_ax - D_bx + D_ab - D_ia - D_ib > 0.
```

If `x` is also tied at the same radius from `i`, this reduces to squared-chord
superadditivity:

```text
D_ab > D_ax + D_xb.
```

For four selected witnesses `w_1,w_2,w_3,w_4` in boundary order around `i`,
one useful row consequence is

```text
D_{w_1 w_4} > D_{w_1 w_2} + D_{w_2 w_3} + D_{w_3 w_4}.
```

Summing that chain inequality over all selected rows gives an immediate
outer-dominance necessary condition. Let `O(e)` count selected rows where the
unordered pair `e` is the outer pair `{w_1,w_4}`, and let `A(e)` count selected
rows where `e` is one of the adjacent pairs
`{w_1,w_2}`, `{w_2,w_3}`, `{w_3,w_4}`. Then any geometric counterexample with
these selected rows must have some pair with

```text
O(e) > A(e).
```

The corrected pair-cap consequence is important. A fixed unordered pair can
occur together in selected witness sets for at most two centers. Since a pair
cannot be both outer and adjacent in the same selected row, the only
pair-cap-compatible outer-dominant types are

```text
(O,A) = (1,0) or (2,0).
```

The previously suggested `(2,1)` type is not pair-cap-compatible.

The selected-pattern checker is:

```bash
python scripts/check_cap_cut_constraints.py --pattern C13_sidon_1_2_4_10 --json
```

It emits selected triple superadditivity counts, chain inequality diagnostics,
general cap-cut inequality counts, corrected pair-role counts, and a unit
chain-superadditivity obstruction when the summed chain row is already
coordinatewise nonpositive after selected-distance quotienting.

## Trust Boundary

These packets are exact local necessary conditions. They are useful only if
later work either:

- mines exact certificates for fixed selected systems;
- finds reusable local templates from those certificates;
- proves a global packing or infeasibility theorem for the combined edge-event
  and cap-cut constraints.

No such global theorem is claimed here.
