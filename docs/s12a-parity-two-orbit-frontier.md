# S12A: a live n=12 parity two-orbit frontier pattern (2026-07-10)

Status: INCIDENCE_PATTERN frontier lead recorded from an AI research
session (Claude Code multi-agent session, 2026-07-10). NOT a
counterexample to Erdos Problem #97 and not a realizability claim; the
official/global status remains falsifiable/open. Artifact:
`data/certificates/s12a_parity_two_orbit_frontier.json`.

## The pattern

`n = 12`, natural cyclic order `0..11`. Selected witness rows are
circulant with parity:

```text
even centers c: S_c = c + {1, 2, 10, 11}   (offsets +-{1, 2})
odd centers  c: S_c = c + {2, 5, 7, 10}    (offsets +-{2, 5})
```

Interpretation: the even labels and odd labels play the roles of two
interleaved 6-point orbits. Each even center selects its two same-orbit
neighbors at offset +-2 and the two cross-orbit points at offset +-1; each
odd center selects its two same-orbit neighbors at offset +-2 and the two
cross-orbit points at offset +-5. This is exactly the selected-witness
shadow of a two-orbit configuration in the sense of
`docs/two-orbit-circulant-obstruction.md` (same-orbit pair plus cross-orbit
pair at every center).

## Why it is interesting

Root-session verification on the unmodified tree (commit `ecf9ea3` plus
this session's additions) confirms that the pair (pattern, natural order)
passes every currently implemented necessary abstract filter:

- two-circle row-pair cap (max intersection 2) and witness-pair capacity
  including the hull-edge refinement: no violations;
- two-overlap radical-axis crossing: no violations;
- vertex-circle selected-distance quotient filter
  (`erdos97.vertex_circle_order_filter.vertex_circle_order_obstruction`):
  not obstructed (108 strict edges, no self-edge, no strict cycle);
- full Kalmanson quotient cone at the natural order: 32 distance classes,
  770 distinct nonzero strict rows, no zero rows, and BOTH normalized LP
  screens (zero-sum and nonpositive) infeasible under HiGHS - i.e. no
  Kalmanson/Farkas certificate exists over this row family at this order
  (solver diagnostic; no exact dual certificate is claimed);
- the new squared-distance value rows
  (`docs/squared-distance-value-rows-2026-07-10.md`): satisfiable at every
  layer (N, N+S, N+OD, N+ODS).

For comparison: every previously registered sparse lead (C13, C19, C25,
C29 fixed orders, P18/P24 parity patterns) is killed by at least one of
these filters; the 16 block-6 escapes die to Kalmanson and to the
short-chord value row. S12A is, as of this session, the only recorded
(pattern, order) pair known to pass all of them.

The in-session order enumeration (agent-reported, terminated early by an
account spend limit, and NOT yet independently replayed) found exactly 4
label-0-rotation-canonical cyclic orders passing caps/crossing plus
vertex-circle for this pattern, all in the single dihedral class of the
natural order, all also passing the two-inequality Kalmanson search. Treat
that enumeration as unverified session evidence until re-run.

## Why it is NOT a counterexample candidate yet

- Passing necessary abstract filters says nothing about Euclidean
  realizability (the C29 precedent: a fixed order survived several filters
  and was later killed by a 165-row Kalmanson/Farkas certificate; stronger
  row families may yet kill S12A).
- The symmetric realization is already excluded: if the twelve points are
  actually two concentric regular hexagons (any radii, any rotation), the
  review-pending two-orbit circulant lemma
  (`docs/two-orbit-circulant-obstruction.md`, Steps 1-5, machine-certified
  window step, reviewed this session in
  `docs/two-orbit-circulant-obstruction-review-2026-07-10.md`) proves the
  configuration is not 4-bad. So any hypothetical realization of S12A must
  be asymmetric - which also explains why symmetric numerical sweeps
  (`docs/dynamic-witness-free-pattern-search.md`) would not have found it.
- The dimension-count heuristic is strongly against realizability
  (36 equations against 20 effective degrees of freedom at n=12), as for
  every fixed pattern; that is heuristic, not proof.

## Next steps (recorded for the backlog)

1. Independently re-enumerate all cyclic orders passing the abstract
   filters for this pattern (the session enumeration is unreplayed).
2. Search stronger exact row families at the natural order (Altman gap
   rows, order-resolved value rows, quantitative obtuse rows with the
   `sin(theta/2)` term, kite rows across the 30 two-overlap center pairs)
   for an exact certificate; store any find as a managed artifact.
3. Run the dynamic-witness numerical searcher restricted to this fixed
   pattern (asymmetric parameterization, anti-cluster floors) and record
   the outcome either way per repo standards.
4. If numerics produce a robust near-miss, attempt exactification per the
   verification contract; a failure to exactify within the pattern's
   dimension count is a negative result to record.

## Replay instructions

The full diagnostic suite (structure, caps/capacity/crossing,
vertex-circle, Kalmanson LP screens, value-row layers) is replayed by the
managed checker:

```bash
python scripts/check_s12a_frontier_pattern.py --check --assert-expected --json
```

The stored artifact embeds its provenance and expected summary; the same
command is registered in the artifact audit registry
(`scripts/run_artifact_audit.py`).
