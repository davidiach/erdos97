# Fragile-cycle active-halo motif forcing

Status: exact bounded active-halo motif forcing. This note does not force the
23=27 quotient core, control arbitrary halo counts, prove Euclidean
realizability, prove Erdos Problem #97, or give a counterexample.

## Result

At the first two bounded halo levels of the stored 23=27 quotient core:

- all 38 one-halo essential fragile covers contain an equilateral hinge or
  one of the generic Kalmanson splice footprints;
- the one-halo covers have no full selected-row extension, as established by
  the source halo-lift frontier;
- among 7,708 two-halo essential covers, the source frontier proves that
  exactly six admit at least one full selected-row extension; and
- an exhaustive hinge-pruned replay proves that none of those six covers has
  any hinge-free full selected-row extension.

Consequently, within this exact bounded contract, every admissible full
selected-row extension at the first complete boundary contains the generic
equilateral-hinge obstruction. This replaces the imported n=9 positive-dual
join for that boundary with one native local endgame.

## One-halo motif split

The 38 essential covers split as follows:

| Classification | Covers |
|---|---:|
| hinge only | 16 |
| splice only | 9 |
| both | 13 |
| motif free | 0 |

Thus 29 covers contain a hinge and 22 contain a splice, with overlap. The
splice scan checks all rotations and reflections of the cyclic order; it uses
only the displayed selected-row pair memberships and the two generic
Kalmanson splice lemmas.

## Two-halo hinge-free exhaustions

The source frontier retains one deterministic full-extension witness for each
of its six extendable covers. Each witness already contains multiple hinge
instances. The stronger replay starts from the fragile cover, runs the same
full-extension incidence, crossing, witness-pair, and selected-indegree rules,
and prunes a branch as soon as a hinge appears. Hinge occurrence is monotone
under adding rows, so each prune is sound.

| Assignment | States | Branches | Dead ends | Hinge prunes | Hinge-free full extension |
|---|---:|---:|---:|---:|---|
| A138 | 13 | 12 | 2 | 7 | none |
| A008 | 7 | 6 | 0 | 3 | none |
| A079 | 3 | 2 | 0 | 1 | none |
| A121 | 3 | 2 | 0 | 1 | none |
| A179 | 4 | 3 | 1 | 1 | none |
| A069 | 6 | 5 | 0 | 4 | none |

The source frontier's exact 6/7,708 extendability classification covers all
other two-halo essential covers: those other covers have no full extension at
all. Combining the two exhaustive layers proves the bounded conclusion.

## Scope and next target

This is genuine motif forcing after the 23=27 core and the one- or two-halo
contract have been fixed. It is not the missing geometric entry lemma. Three
or more formal halo roles are not reduced to this two-halo boundary, and the
core itself is not forced from minimal-counterexample geometry.

The next useful bridge step is therefore structural rather than enumerative:
show that a genuine fragile matching cycle admits a 23=27 reduction with at
most two active halo roles, or prove that a third active halo forces a named
rich-class/deletion alternative.

## Reproduction

    python scripts/check_fragile_cycle_halo_motif_forcing.py \
      --check --assert-expected --summary-json

The generated artifact is
data/certificates/fragile_cycle_halo_motif_forcing.json; do not edit it
directly.
