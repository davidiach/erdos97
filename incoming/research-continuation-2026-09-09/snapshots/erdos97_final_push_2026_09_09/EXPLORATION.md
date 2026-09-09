# Exploration record and limits

Research date: 9 September 2026; some computations began before midnight on
8 September. Dates in historical input packets are preserved.

## Exact metric constructions

The alternating linear-program searches were run at n=18,24,30,39,48 with
seeds 1,2,3,4,5 respectively. The first used 50 iterations; the others used
120. Their best objective errors were 15, approximately 14, 19, 14, and 27.
These are numerical searches in a distance relaxation, not coordinate
realizations or infeasibility certificates. Their failure cannot exclude an
all-rich metric; the subsequent explicit construction provides one.

The raw seven-by-seven grid record is not a four-rich control: some grid
points have only three retained incidences. A retained four-core exploration
is not used in the final theorems or finite matrix certificates. The final
explicit metric controls both use the audited eight-by-eight grid: 64 points,
74 retained lines, minimum incidence four.

The first exact metric retains strict Ptolemy everywhere. The later, stronger
construction replaces each internal block metric by a rational circle metric,
and perturbs nonincidence cross entries to remove unintended ties. It preserves
actual planar realizability of every complete rich star, but not their global
compatibility. The two constructions have different scopes and are retained
separately. A strict Ptolemy inequality cannot replace the Ptolemy equality
forced by four concyclic witnesses.

## Scalar turn discovery

A numerical linear program supplied a candidate vector of normalized turns.
Its floating reported optimum is not used as a proof of optimality. Rational
reconstruction produced exact values with denominator 83. `turn_values.json`
is the authoritative feasible vector; `turn_control.py` reads the integer
metric matrices and checks every applicable equal-distance pair inequality
with rational arithmetic. `turn_discovery_full.json` retains the intermediate
numerical value, rational vector, fibers, and supports.

There are 2,465 repeated fibers and 8,686 pair inequalities in the first metric.
The stronger star metric has only its 138 unit fibers repeated, giving 4,032
pair inequalities. The same exact vector passes both. This does not certify
angles compatible with the distances; an exact inequality in the proof note
shows that these supplied turns cannot be the actual turns at consecutive
vertices of the circle block.

## Tripled-Danzer assignments

The fixed nine source pools and cyclic order come from the preceding packet.
Each physical center has 81 choices of a 2+1+1 witness row. For each source
triple, exact enumeration of 81^3 choices leaves 13,122 pair/cover-saturated
choices and 4,374 choices passing the source median rule.

An initial bounded eight-round search used source medians but not the full
cross-block target-owner median constraints. Its saved target-median failures
are diagnostic records, not candidates.

The stronger mixed-integer search used 40,878 binary configuration variables
and 531 initial constraints. It enforced both source and target medians and
same-side pair capacities. Five complete assignments were obtained; their
exact Kalmanson certificates number 7,16,4,7,20, totaling 54. All are replayed
both by the inherited equality-quotient checker and by a separate chord-graph
representation. The next attempt timed out at its configured 30-second limit
without a candidate. No full-family infeasibility claim follows. None of the
exactly obstructed assignments was sent to new coordinate optimization.

## Fixed-seed and own-side numerical scouts

The incoming-repair/old-supplier C3 probe examined 26 real numerical circle
branches, of which four passed the sampled single-orbit hull test. It found
no cross-supplier equality between those four under its tolerance. This is a
narrow numerical diagnostic, not a continuous-domain exclusion and not an
exhaustion of caps with two internally supported vertices.

The same-half-plane cycle probe used 10,000 random trials at each orbit count
from three through ten. It solved the last two multiplier equations by circle
intersection and retained the stated upper-half-plane and norm restrictions.
No full convex cycle was found. This is not an all-size nonexistence proof;
its configurations would not automatically be four-rich even if convex.

## Verification history

The initial replay passed the preceding packet and its two inherited packets:
40 plus 61 tests. The first new validation passed 36 new tests and the first
complete metric audit; its source hashes are retained in
`validation_before_turn_extension.json`.

The later star/turn extension adds 18 tests. One initial test compared a Python
dictionary with integer histogram keys to its JSON-decoded version with string
keys and failed that serialization comparison. The test was corrected to
compare canonical JSON structures; the geometric data were not changed to
make it pass. The initial failure log is retained as historical evidence.
`validation_full_before_parabola.json` records the fresh 54-test run, both
exact metric audits, and the requested inherited replay at that stage. The
later consolidated report adds the standalone parabola checks as described
below; it does not relabel the earlier execution as a later one.

Independent implementations in one session are not external mathematical
review. No Lean proof, published novelty, or full repository-wide CI is claimed.

## Final all-size parabola argument

A final review of the stored two-parabola scaffold identified an extremal
consequence of its existing square-sum identity. This gives an arbitrary-real,
arbitrary-size contradiction, not another finite-grid exclusion. The signed
height-drift formula from a circle/parabola quartic extends the proof to
finite deterministic cycles of parallel parabolas. The mixed-witness case is
not covered. The standalone parabola verifier adds 12 tests and 96 exact row
controls, including a strictly convex positive control with only one rich
vertex. These are separate from the 54 core/star tests.

The final consolidated validation preserves the full core/inherited replay
as it was actually run, verifies that all its mathematical Python/C++ sources
and pinned input archive are unchanged, and adds a fresh complete Python run
including the parabola checks. The replay wrapper alone changes to include
the new standalone verifier. The complete C++ metric scans are not falsely
attributed to an additional run in this last consolidation step.
