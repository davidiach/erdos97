# Fragile-cycle halo-lift frontier

Status: exact bounded abstract diagnostic and proof-mining aid. This note does
not claim a fragile-cycle forcing lemma, a Euclidean realization, a proof of
`n=9`, a general proof, or a counterexample.

## Question

The fragile-cycle quotient hierarchy leaves two proper seven-role forms of the
stored scalable four-row Kalmanson circuit. Before treating either form as a
local bridge target, we should ask whether its retained certificate rows can
occur inside the abstract fragile-cover incidence rules after the halo roles
forgotten by the quotient are restored.

The first quotient, `18=23`, identifies two of the four retained strict-row
centers. It therefore cannot lift to four distinct retained fragile rows and is
discarded for this particular purpose. The second quotient, `23=27`, preserves
the four centers. In its canonical seven-role cyclic order the retained data
are

```text
centers: 1, 3, 4, 6
required witness pairs:
  1 -> {0,4}
  3 -> {4,5}
  4 -> {0,2}
  6 -> {2,5}
```

Each retained center chooses two additional witnesses to complete a
self-excluding four-witness row.

## Exact bounded scan

Added halo roles are inserted into the seven cyclic gaps. They are otherwise
interchangeable, so nondecreasing gap multisets give one canonical placement
per halo-label permutation. The checker applies, in order:

- row-intersection size at most two;
- the proper crossing rule for every two-overlap;
- witness-pair multiplicity at most two;
- coverage of every displayed role by the four retained rows; and
- a matching of the four retained rows to distinct covered roles.

For a full extension it then requires one self-excluding four-witness selected
row at every center, the same intersection/crossing and witness-pair rules, and
selected indegree at most `floor(2(n-1)/3)`.

| Added halos | Cyclic placements | Raw retained-row combinations | Essential four-row covers | Covers with a full-extension witness |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 1,296 | 0 | 0 |
| 1 | 7 | 70,000 | 38 | 0 |
| 2 | 28 | 1,417,500 | 7,708 | 6 |

Thus one halo is necessary and sufficient for a four-row fragile cover in this
model, but none of the 38 one-halo covers extends to a full eight-center
selected system. Every one already has a remaining center with zero admissible
row options. Two halos are the first full-extension boundary. The six
extendable covers occur in six placements and yield five dihedral incidence
classes. The checker retains one deterministic full-extension witness per
extendable cover; it does not count every possible full completion of a cover.

## Join to the `n=9` certificate frontier

After relabelling each two-halo cyclic order as `0,1,...,8`, all six full
extensions occur verbatim in the stored review-pending `n=9` frontier:

| Halo gaps after core roles | Assignment | Family | Template | Obstruction |
| --- | --- | --- | --- | --- |
| `0,6` | `A138` | `F04` | `T02` | self-edge |
| `1,5` | `A008` | `F07` | `T11` | strict cycle |
| `2,6` | `A079` | `F05` | `T03` | self-edge |
| `3,4` | `A121` | `F01` | `T02` | self-edge |
| `3,5` | `A179` | `F11` | `T06` | self-edge |
| `5,6` | `A069` | `F11` | `T06` | self-edge |

The artifact maps the stored unit-positive dual for each family back to the
labels of the full extension and verifies that its ordinary pair-distance
coefficient vector is zero. Five witnesses use one strict self-edge term and
one uses a strict directed cycle.

For example, the `A138` witness has the exact selected-row equality chain

```text
d(1,8) = d(0,1) = d(0,8) = d(7,8),
```

supported by rows `1`, `0`, and `8`. Row `0`, whose witnesses are
`{1,5,7,8}`, supplies the strict cyclic-chord comparison

```text
d(1,8) > d(7,8).
```

The strict term plus the three oriented equality differences has identically
zero coefficient balance, so this is an exact positive-circuit contradiction,
not a numerical near-miss.

All six full systems also pass the finite good-deletion check for every one of
the `2^9-2 = 510` nonempty proper deletion seeds. This remains abstract
incidence evidence: passing good deletion is not Euclidean realizability.

## What changed in the bridge target

The seven-role quotient is not itself a realizable four-row fragile cover; at
least one forgotten halo role is structurally active. One halo repairs the
fragile cover but cannot support all selected rows. At the first complete
boundary, two halos, the survivors are already recognized by four existing
`n=9` local certificate templates.

This gives a sharper local target than “force the seven-role quotient”:

```text
force the 23=27 core plus enough controlled halo incidence
    -> either no full selected extension,
       or one of the exact local positive circuits.
```

The implication has only been checked for zero, one, and two formal halo roles.
It does not cover larger halo systems, prove that minimal-counterexample
geometry supplies this core, or defeat the scalable and `Z/16` negative
controls. A useful general Contract F lemma still has to extract genuine
ordinary-distance convex information from a fragile matching cycle and its
halos.

The separate three-halo continuation in
`docs/fragile-cycle-three-halo-vertex-circle.md` exhausts all 84 canonical
placements and finds no full vertex-circle-clean extension. It closes that
fixed abstract slice but still does not control arbitrary halo systems.

## Replay

```bash
python scripts/check_fragile_cycle_halo_lift_frontier.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_three_halo_vertex_circle.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_quotient_hierarchy.py \
  --check --assert-expected --summary-json

python scripts/check_n9_vertex_circle_template_duals.py \
  --check --assert-expected --summary-json
```

The generated artifact is
`data/certificates/fragile_cycle_halo_lift_frontier.json`; do not edit it
directly.
