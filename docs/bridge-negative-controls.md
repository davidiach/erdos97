# Bridge negative controls

Status: `EXACT_NEGATIVE_CONTROL` / `PROVENANCE`. No general proof of Erdos
Problem #97 is claimed. No counterexample is claimed.

This note records small exact guardrails extracted from the 2026-05-10
bridge-output triage. Their purpose is to prevent overstrong bridge claims.
They are not evidence for a real counterexample.

Run the replay checker with:

```bash
python scripts/check_bridge_negative_controls.py --assert-expected
```

## C13 linear selected system

Let `V = Z/13Z` and

```text
S_i = i + {1,2,4,10}.
```

The set `{1,2,4,10}` is a Sidon difference set modulo `13`, so every two rows
meet in exactly one witness. Consequently:

- the row-pair cap holds in the sparse form `|S_i cap S_j| <= 1`;
- the witness-pair cap holds;
- the `phi` map has no edges;
- two-overlap filters, odd perpendicularity cycles, mutual-rhombus equations,
  and phi-4 rectangle traps have no input;
- the fixed selected system has no forward ear order from a three-vertex seed.

All rows may also be declared fragile at the abstract incidence level: the map
`x -> x - 1` assigns each vertex to a row that covers it.

This is an abstract incidence negative control only. The fixed C13 Sidon
selected pattern is already killed across all cyclic orders by the repo's
exact Kalmanson/Farkas search.

More generally, any full selected-witness system with `n > 4`, `|S_i| = 4`,
`i notin S_i`, and

```text
|S_i cap S_j| <= 1 for all i != j
```

is not forward-ear-orderable. From a three-vertex seed, either no row contains
the seed, or a unique row contains it and only that row's center can be added.
After that addition, linearity prevents every remaining row from seeing three
vertices in the closure. Thus every three-seed closure has size at most four.
This is an abstract selected-row lemma, not a geometric realization claim.

## Exact block-6 fragile atom

The following six points, in cyclic order `0,1,2,3,4,5`, realize the block-6
fragile rows exactly over `Q(sqrt(3))`:

```text
p0 = (0, 0)
p1 = (-5/13, 12/13)
p2 = (1/2, sqrt(3)/2)
p3 = (1, 0)
p4 = (1/2, -sqrt(3)/2)
p5 = (2/5, -4/5)
```

The fragile rows are:

```text
F_0 = {1,2,3,4}
F_3 = {0,2,4,5}
```

The checker verifies:

- strict convexity in the displayed order by exact edge-side determinants;
- the equalities `|p0 pj|^2 = 1` for `j in F_0`;
- the equalities `|p3 pj|^2 = 1` for `j in F_3`;
- uniqueness of these size-4 distance classes at centers `0` and `3`;
- the fragile-cover axioms for the two retained rows;
- crossing of source chord `{0,3}` and witness chord `{2,4}`.

This realizes only the fragile critical rows. Centers `1,2,4,5` are not shown
to be bad, so the atom is not a counterexample and not a full selected-witness
realization. Its value is sharper: fragile-cover geometry alone is not enough
to prove the theorem.

## Two-block no-forward-ear incidence control

One abstract 12-row full selected extension from the triage bundle passes the
row-pair cap, witness-pair cap, and crossing checks in its supplied cyclic
order, but has no forward ear order. It is retained as an incidence-only
negative control.

The checker also records the correction to the similar 12-row table from
Outputs 8 and 10: that table is in fact forward-ear-orderable, with seed
`[0,7,10]`. It must not be used as a no-ear obstruction.

## What these controls rule out

They rule out proof schemas that try to derive ear-orderability or an immediate
two-overlap obstruction from only:

```text
self-exclusion
four-uniformity
row-pair cap
witness-pair cap
fragile cover
row-use matching
full selected-row extension
two-overlap crossing checks
```

They do not rule out Erdos Problem #97, and they do not rule out the existence
of a stronger bridge using metric/order information.
