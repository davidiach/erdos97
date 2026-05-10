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

## Row-circle full-extension gate

The full-row extension condition has an additional geometric gate that is not
captured by the fragile hypergraph checker. In any strictly convex
counterexample, every selected row `S_i={w0,w1,w2,w3}` lies on one circle
centered at `i`. If the witnesses are written in their cyclic order around
`i`, then Ptolemy's theorem gives the exact row-circle identity

```text
d02*d13 = d01*d23 + d03*d12,
```

where `dab = |p_{wa}p_{wb}|`. Therefore a fragile-cover system from a minimal
counterexample must admit at least one full selected-row extension that
satisfies all such row-circle identities in the supplied cyclic order, in
addition to the pair/crossing incidence checks above.

One exact way this gate can reject a proposed full extension is the
row-Ptolemy product-cancellation certificate from
`docs/row-ptolemy-product-filter.md`. If selected-distance quotienting in the
full extension forces, for example,

```text
d02 = d23
d13 = d01,
```

then substituting into Ptolemy forces `d03*d12 = 0`, impossible for distinct
strictly convex vertices.

The quantifier is important. Killing one arbitrary full extension is not
enough to reject a fragile-cover candidate: a minimal counterexample only
requires existence of some full selected-row extension compatible with the
fragile rows and all row-circle constraints. Thus a bridge proof using this
gate must either check all relevant extensions or prove that every extension
falls to a row-circle certificate.

### Bounded block-6 row-Ptolemy audit

The following bounded exact audit tests this gate on the two-block fragile
negative control:

```bash
python scripts/check_block6_row_ptolemy_extensions.py --blocks 2 --max-extensions 3 --assert-survivor --json
```

In the deterministic full-extension order used by the checker, the first two
full selected-row extensions are rejected by row-Ptolemy
product-cancellation. The third extension has no row-Ptolemy
product-cancellation certificate. Its selected rows are:

```text
0  -> {1,2,3,4}
1  -> {3,6,9,11}
2  -> {1,3,5,10}
3  -> {0,2,4,5}
4  -> {0,3,8,11}
5  -> {0,1,6,7}
6  -> {7,8,9,10}
7  -> {1,5,6,8}
8  -> {0,5,7,9}
9  -> {6,8,10,11}
10 -> {2,5,9,11}
11 -> {0,4,6,10}
```

This is a counterexample to the overstrong subclaim that row-Ptolemy
product-cancellation alone kills every full selected-row extension of the
two-block block-6 fragile rows. It is not a counterexample to Erdos #97 and is
not a Euclidean realization certificate. It only says that this particular
row-circle gate must be strengthened, or applied through an all-extension
certificate, before it can close the fragile-cover bridge.

The survivor also passes a weaker quotient-level row-Ptolemy feasibility test:

```bash
python scripts/check_block6_survivor_ptolemy_feasibility.py --assert-expected --json
```

The checker quotients ordinary pair distances by the selected-distance
equalities of the survivor, obtains `33` distance classes, and verifies an
explicit positive rational assignment satisfying all `12` row-Ptolemy
identities. For example, class values include

```text
x0=1, x5=3, x6=1/2, x9=1/2, x27=6, x32=3/2.
```

This rules out the next overstrong subclaim: selected-distance quotienting plus
the row-circle Ptolemy equalities alone do not already force a positivity
contradiction for the survivor. The certificate is only algebraic feasibility
for the quotient equations. It does not impose triangle inequalities,
Kalmanson inequalities, global metric consistency, or Euclidean realizability.

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

There is also an exact geometric sharpness example for one six-vertex fragile
block. The coordinates recorded in `docs/bridge-negative-controls.md` realize
the two fragile rows as unique exact 4-ties in a strictly convex hexagon and
satisfy the crossing/bisection geometry for their two-overlap. This does not
make the block a counterexample: the other four centers are not bad. Its role
is only to show that even exact local fragile-row geometry is not enough by
itself.

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
