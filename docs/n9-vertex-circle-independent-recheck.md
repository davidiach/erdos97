# Independent recheck of the n=9 vertex-circle finite-case result

Status: independent finite-case recheck. No general proof of Erdos Problem #97
is claimed, and no counterexample is claimed. The official/global status
remains falsifiable/open. This note does not by itself promote the n=9 checker;
it records an independent audit pass directed at Priority 5 in
`docs/review-priorities.md`.

## What was audited

The target is the review-pending artifact
`data/certificates/n9_vertex_circle_exhaustive.json` and its generator
`src/erdos97/n9_vertex_circle_exhaustive.py`, which claim:

- 184 complete n=9 selected-witness systems survive the necessary incidence
  filters (two-circle cap, two-overlap crossing, witness-pair cap, indegree
  cap) with the cyclic order fixed to the identity `0,1,...,8`; and
- every one of those 184 is killed by an exact vertex-circle quotient
  obstruction, split `158` self-edge and `26` strict-cycle, leaving `0`
  surviving systems.

## Independent reproduction

`scripts/independent_n9_vertex_circle_recheck.py` re-derives and rechecks the
whole pipeline without importing the existing checker. The independence is
deliberate:

- the search uses a **fixed** center order `0,1,...,8` with plain recursion,
  not the dynamic minimum-remaining-options brancher;
- selected rows and unordered pairs are `frozenset` objects, with no integer
  bitmasks;
- the cyclic crossing test, the union-find over distance classes, and the
  strict-cycle detector (Kahn sink-peeling rather than DFS coloring) are all
  reimplemented.

Result: the independent search reproduces **exactly 184** incidence survivors,
with vertex-circle status split **158 self-edge / 26 strict-cycle** and **0**
survivors after vertex-circle pruning. Compared against
`data/certificates/n9_vertex_circle_frontier_motif_classification.json`, the
184 systems match **as a set** (not merely in count), and the per-system
self-edge/strict-cycle labels agree on every system.

This directly addresses two of the Priority 5 review items:

- *"minimum-remaining-options branching changes only search order."* The
  independent search uses a fixed center order `0,1,...,8`, while the stored
  artifact uses dynamic minimum-remaining-options branching. These two search
  strategies agree on the same 184-system frontier. This is branch-order
  agreement evidence, not a separate reversed-order audit.
- *"the absence of a hidden symmetry quotient in the 70 row-0 choices."* The
  independent search enumerates all assignments with no quotienting of row 0;
  it still terminates at the same 184.

The pruning used in the independent search only ever rejects a partial
assignment when an already-placed pair of rows violates a necessary condition,
or a running pair/indegree count exceeds its cap. All of these are monotone
necessary conditions, so the pruning cannot discard a survivor, and every
complete assignment is additionally re-validated against all conditions before
being accepted.

## Geometric consistency guard for the vertex-circle filter

The vertex-circle filter asserts strict inequalities between ordinary distances
purely from the cyclic order. The recheck adds an implementation-level
consistency stress test: it samples random **strictly convex** 9-gons and
checks the two facts the nesting lemma depends on.

- **S1.** From every vertex `c`, the angular order of the other vertices equals
  the cyclic boundary order `c+1, c+2, ..., c+8 (mod 9)`, and those vertices
  span an angular wedge strictly less than `pi` (so every witness-witness chord
  central angle lies in `(0, pi)`).
- **S2.** On a common circle, a strictly larger central angle in `(0, pi)`
  yields a strictly longer chord.

Over the sampled polygons there were **0** angular-order failures, **0**
wedge-width failures, and **0** chord-monotonicity failures (hundreds of
thousands of chord comparisons in the default run). This is a useful regression
guard for the implementation and conventions. It is not a replacement for the
exact geometric proof of the nesting lemma.

Run:

```bash
python scripts/independent_n9_vertex_circle_recheck.py --json
```

## Minimal obstruction cores

`scripts/n9_vertex_circle_minimal_cores.py` refines the existing motif-family /
compact-core view. For each of the 184 systems it finds every **minimal**
sub-configuration of selected rows whose vertex-circle quotient already forces
a contradiction (minimal by row-set inclusion), then canonicalizes the cores
under the dihedral group `D_9` of the cyclic order.

Findings, recorded in `data/certificates/n9_vertex_circle_minimal_cores.json`:

- **219** distinct minimal obstruction cores up to `D_9` symmetry;
- by size: `105` use three rows, `106` use four, `7` use five, `1` uses six;
- by status: `36` self-edge cores and `183` strict-cycle cores;
- **complete cover**: every one of the 184 systems contains at least one
  catalogued minimal core; and
- each catalogued core was re-verified in isolation as an exact obstruction
  from only the rows it names (`0` mismatches).

The structural content is that every incidence-surviving nonagon system dies
from a **local** obstruction of at most six selected rows, and usually from
just three. These minimal cores are `n`-independent in the precise sense that
they involve a fixed bounded number of rows and cyclic positions; they are the
natural candidate ingredients for a general bridge lemma, and a sharper handle
than a single representative per motif family.

Run:

```bash
python scripts/n9_vertex_circle_minimal_cores.py --check --assert-expected --json
```

## Conclusion of this audit pass

The independent recheck found **no mathematical or implementation gap**. It
reproduces the 184-system frontier and the `158 + 26` kill split by independent
implementation choices, matches the stored frontier set and labels exactly,
passes the geometric consistency stress test, and shows the whole frontier is
covered by small minimal obstruction cores. This supports the Priority 5 review
case, but does not by itself promote the n=9 vertex-circle artifact to the
same repo-local machine-checked finite-case status as `n <= 8`. This audit was
produced by a single automated agent and does not substitute for the external
human review required by the repo's trust policy before any public
theorem-style claim.
