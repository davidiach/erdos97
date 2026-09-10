# Research log — 9 September 2026

This file records this continuation, not additional independent reviewers or
invented background agents. Search, derivation, and checking were alternated
in one session. No unrestricted solution was obtained.

## Launch and provenance

Fresh connected GitHub read found main at
9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7, merging #943. Earlier #942 restrictions
and the new #943 cap frontier were retained. Targeted official-record and
primary-source checking found no verified new resolution; a forum reduction
still had a challenged removable-vertex implication. Literature did not replace
checking the actual geometric hypotheses.

Only the attached prior files were available locally, not a full repository.
Original available inputs were copied unchanged under inputs/. The C3 angle
model and BFS certificate checker were newly adapted/reimplemented from the
pinned repository methods; they are not falsely labelled byte-identical imports.
The Q(sqrt(3)) arithmetic module is copied byte-for-byte from the attached earlier
control checker and separately retained as an immutable input.

## Round 1: exactify the old nine-orbit failures

Hypothesis: the stored negative LP margins support genuine rational cancellation
certificates. Result: all 160 distinct systems in the two historical files have
such certificates (2,530 terms). A standard-library physical-chord/BFS checker
accepts them, with no optimizer import. Scope: those fixed systems/order only.

Greedy support reduction found a three-arrow, four-orbit obstruction. The
human proof was strengthened to supplier-arc radial lifting at arbitrary size,
under explicit C3/own-side hypotheses. The positive 12-point control checks
non-vacuity and strictness. Adding this rule changes the search assumptions.

## Round 2: stronger bounded enumeration and certificate mining

The three-arrow compatibility search reached 10,000,001 visited states under a
10,000,000-node guard, recording 221 leaves before termination. The supplier-arc
version reached 2,000,001 states under a 2,000,000-node guard, recording 36 leaves.
Both are incomplete enumerations; counters are not promoted to a theorem.
The latter 36 happen to overlap the original stored 160; this is not 36 new
independent systems. The union of all stored rows has 333 distinct systems.

Eight additional survivors were reduced to local exact cores. Six shared a
second three-arrow pattern. The small core certificates do not establish that
every all-rich geometry contains one of these patterns.

## Round 3: the first positive base-angle/metric survivors

A primal LP run stopped at an external command timeout after 164 saved cases;
a direct-dual run later stopped after 314. Neither unresolved run was reported
as an exact rejection. The processes were terminated. Disabling presolve in the
resumed bounded solver allowed progress. This exposed three systems for which
no base-angle contradiction exists: exact positive rational vectors were found.

Full ordinary-distance preflight also has positive rational vectors for these
three, including all Kalmanson and triangle inequalities, maximum-root and
supplier-arc orders. A separate exact checker rederives every premise. The
angle and distance vectors are separate, not mutually consistent coordinates.

Ninety phase-cycle coordinate attempts (30 per system, recorded seeds and
starting phases) approached collisions and nonconvexity. No strict convex
realization was found. Their ~1e-9 residuals are not certificates: minimum
separations shrink to ~1e-10 and some support signs are negative.

The degeneration suggested auditing matched circle intersections, rather than
rerunning the same optimizer. Two aligned diamonds force
z0*z6=z1*z2 and z2*z3=omega^2*z6*z8. Their cancellation contradicts phase order
0<1<3<8. All three systems are exactly excluded, independently of the failed
numerical realization runs. The reusable gain-labelled phase equation and its
strict endpoint argument are written in proof_attempts/diamond_phase.md.

The final corpus has 330 base-angle certificates and three diamond-phase
certificates. Its 10,291 integer terms are checked exactly. No claim of
exhausting all nine-orbit systems is made.

## Construction and hostile-verification lines

The old numerical six-cycle product's factors already have only six hull
vertices each. A new exactly specified quartic-root six-cycle proves same-upper
monodromy closure, but its eighteen points have twelve strict interior points.
All actual distance classes have maximum size three. This is not a counterexample.

A separate C3 maximum-root local search found a 21-point strictly convex
configuration; rational parameters were fixed and exactified in Q(sqrt(3)).
The independent checker confirms nine rich points, twelve good points, all 399
global supporting inequalities, and no actual rich radius exceeding the root's.
This refutes the proposed maximum-root neighborhood shortcut even inside C3.

Unrestricted-witness integer-lattice searches at side lengths 7 and 9 used all
actual distance groups and exact nonconvex-subset/collinearity constraints.
HiGHS returned infeasible, but no exact solver certificates were supplied.
These observations are not promoted to finite-case theorems.

The diamond-free 60-state group graph is an exact INCIDENCE-ONLY negative
control. It refutes forcing a diamond from outdegree two plus nonreciprocity
alone, not from genuine convex geometry.

## Validation and publication

35 defensive full-packet tests pass, including corrupt certificates, bad gains,
wrong convex orders, collisions, wrong roots and exact positive relaxations.
The small publication core has 12 tests, also passing under pytest (the same
12 tests, not another 12 independent tests). Full exact replay runs in a
separate temporary copy and checks immutable input hashes before and after.

The publication core contains the new diamond phase proof and the three
fixed-system certificates, not every file of the broader continuation. The
full continuation is supplied as a separate complete research archive.
Remote publication details are recorded separately once the write succeeds.
Repository-wide fast/artifact gates, Ruff, and compatibility interpreters are
not available in this scoped export; they are not inferred from focused tests.
No accepted mathematical status, root workflow, secret or permission is altered.


## Phase-filter continuation after opening the draft

The new phase rule was incorporated before terminal output as a necessary
integer filter in C++: a single diamond equation or a two-row integer
combination cannot have all coefficients of the strictly positive cyclic phase
gaps weakly one-signed and nonzero. A separate Python construction agrees on all
333 stored systems and produces 200 exact phase certificates (five single and
195 double diamonds). This is overlapping proof evidence, not a new 200-case
universe.

A fresh 2,000,000-node guarded run visited 2,000,001 states, recorded 55,504
phase prunes and 15 terminal systems, and stopped at the node guard. Every
terminal system is already exactly excluded in the corpus. An earlier larger
invocation was externally timed out before a final report; no complete rows
were saved and no completeness or zero-survivor claim follows.

The strict supplier-arc control checker was hardened to bind all named source
premises, certify the sector order, and check |C|<|D|<|A|. Three new tests bring
the full-packet suite to 38, alongside the 12 core tests: 50 distinct tests.
The mathematical corpus and control coordinates did not change.

## Successful publication and initial CI repair

Draft PR #944 was opened at de2ce5a5e6a391103fa011b9697533d002ce8f00, based on
9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7. All five original core blobs match the
locally tested bytes. The draft initially failed hosted lint due to E741 on
`l`, and a maintenance test due to the omitted incoming-index link. Hosted
pytest shard 1 otherwise recorded 1,069 passes; the lint-blocked shard did not
run its tests. Those were publication mistakes, not mathematical contradictions.

Fast-forward repair 832fe620583488b5c4a1169c75b486b2debf4bad renamed the local
variable to `tip` and added the packet link/count to incoming/README.md.
Certificate logic, proof statements, and cases are unchanged. The 12 core tests
passed again locally. No check was weakened. This repair makes the PR diff
five new core files plus one navigation-only change, superseding the initial
five-files-only scope description. Latest observed hosted status is kept in
reports/publication.json; unobserved complete-gate passes are not claimed.
