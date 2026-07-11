# Review record: docs/n8-geometric-proof.md (2026-07-10)

Status: written review record from an AI research session (Claude Code
multi-agent session, 2026-07-10). This is review input for the maintainer's
decision intake, not an external human review, and it does not by itself
change any claim status. No general proof and no counterexample are claimed
for Erdos Problem #97; the official/global status remains falsifiable/open.

Scope: the human-readable small-case proof note `docs/n8-geometric-proof.md`
only (Priority 1 in `docs/review-priorities.md`). The machine pipeline
(`docs/n8-incidence-enumeration.md`, `docs/n8-exact-survivors.md`) is out of
scope here and is not affected.

Supersession note (added while merging onto post-#872 main): this review
was performed against the pre-promotion draft of the note. The 2026-07-09
repository audit independently rederived the note twice and promoted it to
`REPO_LOCAL_THEOREM` (merged in #872), and the promoted text already
contains the repair required below as R1 (no apex on the base line: the
bisector meets line `ab` only at the midpoint). The two efforts were
independent and reached the same verdict and the same required repair; this
record is kept as dated convergent review input. R2-R5 below refer to the
pre-promotion text and should be read against the current note.

Method: two independent passes inside one session, reconciled afterwards:

- Pass 1 (root reviewer): line-by-line re-derivation of every step from
  scratch, done before reading the other pass.
- Pass 2 (dedicated referee agent): independent line-by-line referee run
  against the owner's six checklist items, with exact SymPy machine checks
  of the load-bearing computations (base-apex convex combination, partition
  enumeration, chord/turn trigonometry, vertex-cover minimum), an audit
  against the known failure modes (circumcenter-in-hull assumptions,
  incidence symmetry, common radius, cyclic off-by-one, folklore angle
  bounds), and a k=3/Danzer sanity check on every lemma not using the
  number 4.

Both passes reached the same verdicts on all steps, and independently
identified the same single required repair (R1/M1 below). Process note from
pass 2, kept for provenance: an early version of its tie-detection harness
(sympy.simplify on distance differences) under-detected exact ties in the
regular 9-gon control; it was replaced by an exact cyclotomic-reduction
criterion before the final checks, and the archived scripts use the exact
criterion.

## Reconciled verdict table

Item numbering follows the note top to bottom; "owner item" maps to the six
checklist items in `docs/review-priorities.md`, Priority 1.

| #  | Note step | Owner item | Verdict |
| -- | --------- | ---------- | ------- |
| 1  | Base-apex lemma: at most one apex on each open side of line `ab` | 1 | ACCEPTED |
| 2  | Capacity corollary: side base <= 1 apex, diagonal base <= 2, opposite sides | 1 | ACCEPTED (repair R1) |
| 3  | Lower bound `T(A) >= 6n` for a 4-bad polygon | 2 | ACCEPTED |
| 4  | Upper bound `T(A) <= n + 2(binom(n,2)-n) = n(n-2)` | 2 | ACCEPTED |
| 5  | `6n <= n(n-2)` forces `n >= 8`; no 4-bad polygon with `n <= 7` | 2 | ACCEPTED |
| 6  | Octagon equality `48 <= T <= 48`; each vertex contributes exactly 6 | 3 | ACCEPTED |
| 7  | Unique distance-class profile `(4,1,1,1)` at every vertex | 3 | ACCEPTED |
| 8  | Saturation: every side exactly 1 apex, every diagonal exactly 2 (one per side) | 3 | ACCEPTED |
| 9  | Length-2 diagonal step: `v_{i+1}` forced apex; all side lengths equal | 4 | ACCEPTED (repair R2) |
| 10 | Turn setup and `\|v_{j-1} v_{j+1}\| = 2 s cos(tau_j/2)`; equals `s` iff `tau_j = 2pi/3` | 5 | ACCEPTED (cosmetic R4) |
| 11 | Length-3 diagonal step: for every `i`, `tau_{i+1} = 2pi/3` or `tau_{i+2} = 2pi/3` | 5 | ACCEPTED |
| 12 | `M = {j : tau_j = 2pi/3}` covers all adjacent index pairs; `\|M\| >= 4` | 6 | ACCEPTED |
| 13 | `sum tau_j >= 8pi/3 > 2pi`; contradiction; `n <= 8` closed | 6 | ACCEPTED |
| 14 | Scope and non-overclaiming statements | - | CONSISTENT |

No GAP verdicts from either pass.

## Overall verdict

The note survives review as a correct human-readable proof that no 4-bad
strictly convex polygon exists for `n <= 8`, subject to the minor repairs
below (one required, rest cosmetic). Per the owner's acceptance standard,
this review supports keeping the note as the main human-readable small-case
proof route, with the machine pipeline as an audit appendix, once R1 is
applied. This review does not by itself promote the note to a public
theorem-style claim.

## Key re-derivations (reviewer's own words)

1. Base-apex. Apices of base `{a,b}` lie on the perpendicular bisector.
   If `p = (0,s)` and `q = (0,t)` with `0 < s < t` are apices on the same
   open side (normalized `a = (-1,0)`, `b = (1,0)`), then
   `p = (s/t) q + ((1-s/t)/2) a + ((1-s/t)/2) b` is a strictly positive
   convex combination, so `p` is not an extreme point of the vertex set,
   contradicting convex position. Verified coordinate-wise and by exact
   SymPy check. Only convex position plus no-three-collinear is used.
2. Partition analysis. With `sum m_k = 7`, a part `>= 4`, the per-vertex
   isosceles pair count `sum C(m_k, 2)` takes values: `(7) -> 21`,
   `(6,1) -> 15`, `(5,2) -> 11`, `(5,1,1) -> 10`, `(4,3) -> 9`,
   `(4,2,1) -> 7`, `(4,1,1,1) -> 6`. The value 6 is attained only by
   `(4,1,1,1)` and is the minimum, so `T = 48` forces that profile at every
   vertex. Enumerated exhaustively in both passes.
3. Chord/turn. In the equilateral case the triangle `v_{j-1} v_j v_{j+1}`
   has two sides `s` and included angle `pi - tau_j`, giving third side
   `2 s sin((pi - tau_j)/2) = 2 s cos(tau_j / 2)`; on `tau_j in (0, pi)`
   the map `tau_j -> cos(tau_j/2)` is strictly decreasing, so the value `s`
   pins `tau_j = 2 pi / 3`.
4. Cover and turn budget. The length-3 step yields, for every `i`, that
   `M` meets `{i+1, i+2}`; hence `M` is a vertex cover of the cyclic
   adjacent-pair graph `C_8`, so `|M| >= 4` and
   `sum tau_j >= 4 * 2pi/3 = 8pi/3 > 2pi`, contradicting the exact total
   exterior turn `2 pi` of a strictly convex polygon.

## Required and cosmetic repairs

- R1 (required; found independently by both passes): in the base-apex
  capacity corollary, add one sentence excluding an apex ON the line `ab`:
  the unique point of line `ab` equidistant from `a` and `b` is the midpoint
  of segment `ab`, which cannot be a vertex of a strictly convex polygon
  (it is a convex combination of `a` and `b`; equivalently three collinear
  vertices are excluded). As written, "on each side" silently uses this.
- R2 (wording): state that "strictly convex" is used in the repo sense
  (convex position and no three vertices collinear); the length-2 step uses
  no-three-collinear when placing exactly `v_{i+1}` strictly on the short
  side of the chord `v_i v_{i+2}`.
- R3 (optional clarity): list the partition values (as above) in the
  octagon saturation paragraph so exhaustiveness is visible.
- R4 (cosmetic): note `tau_j in (0, pi)` follows from strict convexity,
  and include the one-line derivation of `2 s cos(tau_j / 2)`.
- R5 (cosmetic): make the normalization/reflection WLOG in the base-apex
  proof explicit (the displayed convex combination is in the frame with
  `a + b = 0`).

## k=3 sanity check

Replacing 4 by 3 weakens the lower bound to `3n` and the counting step to
`3n <= n(n-2)`, i.e. only `n >= 5`, with no saturation cascade at any `n`;
the argument therefore does not exclude Danzer's convex 9-gon with three
equidistant vertices per vertex. The proof uses `k = 4` essentially through
the exact saturation `6n = n(n-2)` at `n = 8`. PASS in both passes.
