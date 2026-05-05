# Minimal Fragile-Cover Bridge

Status: `LEMMA` / partial bridge theorem. No general proof of Erdos Problem #97
is claimed. No counterexample is claimed.

This note records a modest bridge theorem that is actually proved, in contrast
to the open ear-orderable bridge. It converts minimality of a hypothetical
counterexample into a covering family of exact critical 4-ties.

## Definitions

Let `P` be a strictly convex counterexample with the minimum possible number of
vertices, if any counterexample exists.

For a center `y`, call a distance class `C_y(r)` **critical** if

```text
|C_y(r)| = 4.
```

It is critical for a vertex `x in C_y(r)` when deleting `x` makes `y` good,
meaning that no distance class of size at least `4` remains at `y`.

A **fragile-cover witness system** is a partial selected-witness system
consisting of some centers `y` and exact 4-sets `F_y`, with:

- `y notin F_y`;
- `|F_y| = 4`;
- the sets `F_y` cover every vertex of `P`;
- there is a witness map `pi: V -> {fragile centers}` with `x in F_{pi(x)}`.
- every retained fragile center is used by at least one vertex under `pi`.

## Lemma

Every minimal counterexample admits a fragile-cover witness system.

## Proof

Fix a vertex `x` of a minimal counterexample `P`, and delete it. By minimality,
the remaining polygon is not a counterexample, so some remaining vertex `y`
has `E(y) <= 3` after deletion.

In the original polygon, every distance class at `y` of size at least `4` must
contain `x`; otherwise that class would still have size at least `4` after
deleting `x`. Since `x` lies at one distance from `y`, there is at most one
such class. Its size is exactly `4`, because if it had size at least `5`, then
after deleting `x` it would still have size at least `4`. Thus `x` belongs to
a unique exact 4-tie at `y`.

Do this for every vertex `x`. If several vertices choose the same center and
the same exact 4-tie, keep one copy. Every retained row has at least one
generating vertex, so the retained rows can be matched to distinct covered
vertices. The retained exact 4-ties cover all vertices by construction, giving
the desired partial witness system and witness map.

There is one more incidence-level consequence. Since every vertex of the
original polygon is bad, choose one selected 4-neighbor row at every
non-fragile center. At a retained fragile center, use its critical row: because
that row is used by some deleted vertex, the critical-tie proof shows it is the
unique distance class of size at least `4` at that center. Thus every minimal
counterexample also gives a full selected-witness incidence system extending
the fragile rows.

## Immediate Geometric Constraints

Any fragile-cover witness system coming from a minimal counterexample also
satisfies the usual exact selected-witness constraints:

- Two fragile rows intersect in at most two vertices, by the two-circle cap.
- If two fragile rows `F_a` and `F_b` intersect in exactly `{u,v}`, then the
  source chord `{a,b}` crosses the witness chord `{u,v}` in the cyclic order,
  by the radical-axis crossing/bisection lemma.

These are exactly the checks implemented by
`src/erdos97/fragile_hypergraph.py` and exposed through
`scripts/check_fragile_hypergraph.py`. The checker also reports the row-use
matching condition above as `essential_cover_ok`.

The same script can optionally test the full-row extension condition:

```bash
python scripts/check_fragile_hypergraph.py --blocks 1 --check-full-extension --json
```

This searches for a full selected-witness incidence system extending the
fragile rows, subject to self-exclusion, four-uniformity, the two-circle cap,
and the two-overlap crossing rule. Passing this extension check is still not a
Euclidean realization certificate.

## What This Does Not Prove

The bridge is necessary, not sufficient. The checked block-6 family passes the
abstract fragile-cover constraints:

```bash
python scripts/check_fragile_hypergraph.py --blocks 2 --assert-ok --json
```

For each six-vertex block with local labels `b,...,b+5`, the rows are:

```text
b   -> {b+1,b+2,b+3,b+4}
b+3 -> {b,b+2,b+4,b+5}
```

The two fragile rows in a block cover the six vertices, intersect in
`{b+2,b+4}`, and satisfy the cyclic crossing rule. Disjoint copies preserve
the same abstract checks. Therefore pure fragile-cover hypergraph constraints
cannot prove Erdos #97.

The full-extension diagnostic rejects the single six-vertex block: it cannot be
extended to full selected rows satisfying the pair and crossing constraints.
However, two disjoint blocks still pass the full-extension diagnostic. Thus
full-row extendability is a real strengthening, but it is still far from a
proof.

## Research Use

This bridge is still useful because it gives a necessary finite object for any
minimal counterexample:

1. Search pipelines can require at least one cover by exact critical 4-tie
   rows, rather than arbitrary selected rows alone.
2. Stuck-set and ear-orderability failures should be analyzed together with
   a witness map `pi`, not only as full fixed-row patterns.
3. The next bridge target is to add a genuinely geometric constraint to the
   fragile cover: for example, dependency-cycle restrictions, critical-radius
   ordering, or row-circle exact constraints on the fragile rows.

This is a foothold toward a bridge theorem, not the central ear-orderable
bridge itself.
