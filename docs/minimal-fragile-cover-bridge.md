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

### Endpoint-control fragile-cover negative control

The endpoint-control route cannot be proved from fragile-cover incidence,
two-circle cap, crossing, and full-row extendability alone. A compressed
endpoint-failure model on labels `0,...,10` has fragile rows

```text
0 -> {1,3,5,6}
1 -> {0,2,7,9}
6 -> {0,4,8,10}
```

Here `0` is the base center and `1,6` are the angular endpoints in the base
row. Both endpoint rows contain `0` and three outside labels, so they model
endpoint-control failure at `m=4` while also giving critical coverage of the
base center.

The generic fragile-cover checker verifies that this abstract system covers
all `11` labels, satisfies self-exclusion and four-uniformity, has no
pairwise intersection larger than two, has no crossing violation, and has an
essential row-use matching. The full-row extension search also succeeds,
visiting `26` nodes. One extension is:

```text
0  -> {1,3,5,6}
1  -> {0,2,7,9}
2  -> {0,1,3,4}
3  -> {2,4,7,8}
4  -> {1,5,7,10}
5  -> {0,2,3,6}
6  -> {0,4,8,10}
7  -> {1,2,4,9}
8  -> {3,7,9,10}
9  -> {2,5,8,10}
10 -> {0,6,8,9}
```

This is only an abstract incidence/order negative control, not a Euclidean
realization certificate. Its role is to show that a proof of endpoint control
must use a stronger metric or minimality ingredient than the currently
isolated fragile-cover axioms plus full-row incidence extendability.

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

### Endpoint-control row-Ptolemy audit

The displayed full-row extension in the endpoint-control negative control
above is rejected by the row-Ptolemy product-cancellation gate: the exact
replay finds `4` certificates. The first one is centered at row `2`, whose
cyclic witness order is `[3,4,0,1]`; selected-distance quotienting forces
`d02=d23` and `d13=d01`, so Ptolemy forces the positive product `d03*d12` to
vanish.

This does not close the endpoint-control bridge. A bounded deterministic
all-extension search over the same fixed fragile rows finds, after `44`
nodes, a full selected-row extension with no row-Ptolemy
product-cancellation certificate:

```text
0  -> {1,3,5,6}
1  -> {0,2,7,9}
2  -> {1,3,4,10}
3  -> {2,4,5,7}
4  -> {1,6,7,8}
5  -> {0,2,3,6}
6  -> {0,4,8,10}
7  -> {1,2,4,9}
8  -> {3,7,9,10}
9  -> {2,5,8,10}
10 -> {0,1,8,9}
```

Thus row-Ptolemy product-cancellation is useful for rejecting fixed full
extensions, but it is not an all-extension obstruction for this
endpoint-control benchmark. This survivor is not a Euclidean realization
certificate; it only shows that a proof using this row-circle gate needs a
stronger metric layer or an all-extension certificate.

The same endpoint-control survivor also passes the quotient-level
row-Ptolemy feasibility test:

```bash
python scripts/check_endpoint_control_survivor_ptolemy_feasibility.py --assert-expected --json
```

The checker quotients ordinary pair distances by the selected-distance
equalities of the survivor, obtains `25` distance classes, and verifies an
explicit positive rational assignment satisfying all `11` row-Ptolemy
identities. For example, class values include

```text
x0=1, x2=1/2, x4=3, x6=2, x14=19/4, x15=11/4.
```

This rules out a stronger but still quotient-level subclaim: selected-distance
quotienting plus the row-circle Ptolemy equalities alone do not force a
positivity contradiction for the endpoint-control survivor. The certificate
is only algebraic feasibility for the quotient equations. It does not impose
triangle inequalities, Kalmanson inequalities, global metric consistency,
Euclidean realizability, or critical-radius ordering.

A stronger fixed-order Kalmanson quotient-cone layer does reject the same
endpoint-control survivor in the natural cyclic order:

```bash
python scripts/check_endpoint_control_survivor_kalmanson_certificate.py --assert-expected --json
```

The certificate is a positive integer combination of `22` strict Kalmanson
inequalities, with weight sum `89`, whose coefficient vector reduces to zero
across the same `25` selected-distance quotient classes. Summing those strict
inequalities gives `0 > 0`, so this fixed survivor/order is impossible. This
does not contradict the quotient-Ptolemy feasibility result above: Ptolemy
equalities alone are feasible, while Kalmanson order inequalities are not.
The obstruction is still local and fixed-order only. It does not show that
every full-row extension of the endpoint-control fragile rows has such a
certificate, and it does not prove endpoint control.

The same fixed survivor has a small crossing-only cyclic-order frontier:

```bash
python scripts/check_endpoint_control_survivor_spine_pocket_orders.py --assert-expected --json
```

The checker recomputes the `17` two-overlap crossing constraints for this
survivor and enumerates all cyclic orders satisfying them, modulo rotation and
reversal. It visits `38` search nodes and finds exactly five normalized
orders, all with spine form

```text
0,1,2,3, [4,5,6,7 pocket], 8,9,10.
```

This is not an obstruction by itself. It only says that any realization of
this fixed full-row survivor must lie in one of those five crossing-compatible
cyclic orders before any Kalmanson or metric-order certificate is applied.

The five crossing-compatible orders are all rejected by an exact Kalmanson
quotient-cone replay:

```bash
python scripts/check_endpoint_control_survivor_spine_pocket_kalmanson.py --assert-expected --json
```

For the five orders above, the checker verifies positive integer combinations
of strict Kalmanson inequalities with strict-row counts
`[23, 12, 16, 10, 12]`, weight sums `[541, 51, 79, 27, 38]`, and maximum
weights `[73, 11, 15, 6, 10]`. In each order, the combined coefficient vector
reduces exactly to zero across the survivor's `25` selected-distance quotient
classes. Therefore this fixed full-row survivor is impossible in every cyclic
order satisfying its necessary two-overlap crossing constraints.

This still has the same fixed-survivor quantifier. It is not an obstruction
for every full-row extension of the endpoint-control fragile rows, not an
endpoint-control proof, not a Euclidean non-realizability theorem for the
abstract fragile rows, and not a proof of Erdos #97.

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

A stronger metric-order layer does reject the same fixed survivor in the
natural cyclic order:

```bash
python scripts/check_block6_survivor_kalmanson_certificate.py --assert-expected --json
```

The certificate is a positive integer combination of `31` strict Kalmanson
inequalities, with weight sum `4294`, whose coefficient vector reduces to
zero across the same `33` selected-distance quotient classes. Summing those
strict inequalities gives `0 > 0`, so this fixed survivor/order is impossible.
This is still a local obstruction only: it does not show that every
full-row extension of the two-block fragile rows has such a certificate, and
it does not rule out minimal counterexamples.

A crossing-order upgrade verifies the same fixed survivor across all cyclic
orders compatible with its two-overlap crossing constraints:

```bash
python scripts/check_block6_survivor_crossing_kalmanson.py --assert-expected --json
```

The checker recomputes the `18` crossing constraints, enumerates exactly `4`
normalized crossing-compatible cyclic orders, and verifies one exact
Kalmanson quotient-cone certificate for each order. The certificate row counts
are `[9, 27, 26, 21]`, with weight sums `[13, 576, 820, 85]`.
Therefore this one full selected-row extension is obstructed in every cyclic
order allowed by its necessary crossing constraints. The quantifier is still
fixed-survivor only: this does not show that every full selected-row extension
of the two-block fragile rows has such a certificate, and it does not rule out
minimal counterexamples.

The same fixed survivor also passes the critical-radius propagation filter:

```bash
python scripts/check_block6_survivor_radius_propagation.py --assert-pass --json
```

There are `531441` formal choices of one short witness gap per row in the
natural cyclic order. The replay uses the standard early-exit search and finds
one acyclic choice after `13` nodes. This is a useful negative result for the
critical-radius route: selected-distance quotienting, row-Ptolemy feasibility,
and fixed-order radius-propagation all remain compatible for this survivor.
The later Kalmanson certificate is genuinely stronger for this fixed order.
This pass is not an exhaustive listing of radius-propagation choices, not a
Euclidean realization certificate, not a counterexample, and not an
obstruction for or against other full-row extensions of the two-block fragile
rows.

A compact crosswalk now keeps these fixed-survivor and all-extension layers in
one checked place:

```bash
python scripts/check_block6_fragile_filter_crosswalk.py --assert-expected --json
```

The crosswalk verifies that the shared fixed survivor is exactly the third
row-Ptolemy full-extension survivor; it has no row-Ptolemy
product-cancellation certificate, has a positive quotient-Ptolemy assignment,
passes fixed-order radius propagation, is killed by a natural-order
vertex-circle self-edge, and is killed across all four crossing-compatible
orders by Kalmanson certificates. The same payload also points to the older
natural-order all-extension vertex-circle audit, where the pruned search closes
with zero clean full extensions.

That natural-order all-extension audit is now stored as a checked artifact:

```bash
python scripts/check_block6_fragile_vertex_circle_extension.py --check --assert-expected --json
```

```text
data/certificates/block6_fragile_vertex_circle_extension_audit.json
```

This is bookkeeping, not a new global obstruction. The remaining block-6 bridge
gap is still all full extensions across all compatible cyclic orders, or a
genuine minimal/rich-class geometric reduction that avoids fixing one selected
row at each center too early.

A bounded crossing-order sample begins to probe that gap without changing the
claim scope:

```bash
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py --check --assert-expected --json
```

```text
data/certificates/block6_terminal_crossing_vertex_circle_sample.json
```

It takes two deterministic windows of `100` terminal full extensions from the
natural-order block-6 audit, enumerates all crossing-compatible cyclic orders
for each, and classifies the resulting `796` orders by the vertex-circle
quotient filter. Every sampled crossing order is killed by a self-edge. This is
still only a deterministic sample and not an all-extension, all-order
obstruction.

A slower full sweep has now replaced that sample as the stronger checked
diagnostic:

```bash
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py --full-sweep --check --assert-expected --json
```

```text
data/certificates/block6_terminal_crossing_vertex_circle_full_sweep.json
```

It exhausts the `105,978` terminal full extensions generated by the
natural-order two-block audit, checks all `385,517` crossing-compatible cyclic
orders they admit, and finds no vertex-circle-clean order. This still does not
cover selected-row systems outside that natural-order terminal generator, so
the remaining bridge gap is either a generator-independent all-order closure or
a genuine minimal/rich-class reduction.

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
