# 2026-06-09 research-pass archive triage

Status: provenance and audit triage only. This is not mathematical evidence by
itself, not an `n=9` proof, not a general proof, and not a counterexample.

## Source packet

The incoming archive contained:

- `erdos97_research_pass.zip`;
- `convex_polygon_equidistance_note.tex`;
- `convex_polygon_equidistance_note.pdf`.

The durable additions harvested from the packet are intentionally narrow:

- the direct gear-equation certificate now recorded in
  `docs/symmetric-two-orbit-reduction.md`;
- the `--gear-equation` verifier mode in
  `scripts/check_two_orbit_radius_propagation.py`;
- this provenance note for the independent `n=9` reproduction counts.

The packet is not imported wholesale. In particular, the archive branchers are
not treated as source-of-truth artifacts, and the TeX note's `n <= 6` argument
is not promoted because the repository already records a stronger `n <= 8`
repo-local finite-case result.

## Independent n=9 reproduction

The archive's compact Python brancher reports the same review-pending
vertex-circle counts already recorded by the repository:

```text
n=9, incidence/order filters only:
  row0 choices: 70
  nodes visited: 100817
  full assignments surviving pair/crossing/count filters: 184
  frontier digest:
    b660e35b161f489af902630ec997e8dfed29b54aaa2b810e61f4ec391248cc43
  vertex-circle status on the 184 frontier:
    self-edge:     158
    strict-cycle:   26

n=9, with vertex-circle partial pruning:
  row0 choices: 70
  nodes visited: 16752
  full assignments surviving all filters: 0
  partial self-edge prunes:     11271
  partial strict-cycle prunes:  11011
```

The archive's C brancher independently reproduces the pruned run:

```text
nodes=16752
full=0
partial_self=11271
partial_cycle=11011
```

These counts are useful as independent reproduction/provenance for the
review-pending `n=9` vertex-circle route. They do not replace the repo-native
artifact stack, do not validate the geometric filters by themselves, and do
not promote `n=9` beyond review-pending status.

## Two-orbit gear proof

The archive's strongest proof-facing item was a direct trigonometric proof for
the half-step two-orbit gear equation. That proof has been folded into
`docs/symmetric-two-orbit-reduction.md` and the checker command

```bash
python scripts/check_two_orbit_radius_propagation.py \
  --gear-equation \
  --k 3 \
  --k-max 12 \
  --assert-gear-equation
```

This kills only the stated two-orbit half-step gear class after the separate
phase-locking reduction. It is not a proof of Erdos Problem #97.

## TeX note

The TeX note is readable and mostly aligns with existing repository language:

- the pairwise circle-intersection cap is already a core repo lemma;
- the `n <= 6` proof is superseded by the repo-local `n <= 8` finite-case
  pipeline;
- the two-axis symmetric octagon exclusion looks suitable as a future
  failed-family note, but it is not needed for the current source-of-truth
  claim ledger.

No claim is promoted from the TeX note in this triage pass.
