# Chord-angle certificates close the eight-orbit own-side C3 case

Date: 2026-09-05. Repository baseline inspected: `b86a5737ed447613b140d0e5b85cb0dd3339f36c`.
Continuation of draft PR #935 at `70fa9b41c74ffc76d9b61ab6d6b803e086fc7a04`.

**Status: REVIEW_PENDING_RESTRICTED_COMPUTER_ASSISTED_OBSTRUCTION.**
The geometric reductions, angle-lift convention, complete enumerators, and
certificate checkers require independent mathematical and code review.
No external review, formalization, or novelty relative to the literature is claimed.
No unrestricted proof or counterexample to Erdős Problem #97 is claimed.

## 1. Result and exact scope

Put

    omega=(-1+i*sqrt(3))/2,
    T_i={z_i,omega*z_i,omega^2*z_i},
    r_i=|z_i|, rho_i=sqrt(3)*r_i.

Representatives are nonzero and describe distinct orbits. The union is in
strictly convex position. An **own-side arrow** `i -> j` of gain `g` means

    |z_i-omega^g*z_j|=rho_i.

**Restricted result, review pending.** With at most eight orbits, it is
impossible that every point has four witnesses at its own-side radius.
An all-own-side construction therefore needs at least nine orbits / 27 points.

This is NOT a 27-vertex lower bound for arbitrary counterexamples. It excludes
neither arbitrary 24-gons nor other-radius four-ties in C3-symmetric sets.
Nine or more orbits, the 22-orbit / 66-point partial construction, and the
unrestricted long-radius problem remain outside the result.
The repository's accepted finite bound and status metadata are not changed.

The proof is a finite reduction followed by exact rejection of every terminal
case. The new angular-first search leaves **632** eight-orbit systems.
All 632 have independently checked integer chord-angle certificates; **369**
also have a simpler obtuse-base certificate. There is no final survivor.
No floating residual or floating infeasibility status is accepted as a proof.

## 2. New reusable geometric rule: a right angle cannot fit inside an acute base

**Lemma (right-angle containment).** Let `i,p,b` be distinct vertices of a
strictly convex polygon, with `|i-p|=|i-b|`. If a forced right angle at `p`
has its endpoint rays inside the interval between the rays `p->i` and
`p->b` in the interior fan at `p`, the configuration is impossible.
Endpoints of the contained interval may equal the outer endpoints.

**Proof.** The triangle `i,p,b` is nondegenerate and isosceles with apex `i`.
Its two base angles are equal and strictly less than `pi/2`. At a strict hull
vertex, the rays to all other vertices are distinct, follow boundary order,
and occupy an angular interval shorter than `pi`. Containment in this fan
therefore implies `angle i p b >= pi/2`, a contradiction. QED.

The right angle itself comes from an own-side arrow. For arbitrary complex
`a,b`, let `c=omega*b`, `d=omega^2*b`. Expansion gives

    2(c-a) dot (d-a)=3|a|^2-|a-b|^2.

Thus an own-side arrow from `a` to `b` forces `angle c a d=pi/2`.
Combining these two elementary facts yields the new obstruction. It applies
at any number of orbits and uses no rational-angle or incident-side cap.
It is stronger than requiring two right-angle intervals at one source to
interlace: it couples a right angle at one vertex to a rich circle at another.

A stored containment certificate is `[i,p,b,u,v]`. The verifier checks the
selected equal legs, the exact own-side arrow forcing `angle u p v=pi/2`,
and cyclic interval containment. No measured angles are involved.

### A quantitative four-orbit corollary

Let `A,B,C,D` be orbit representatives in that order within one fundamental
120-degree sector. If `C -> A` has gain zero, then

    |B-omega*D|^2 > |B-omega*C|^2 + |C-D|^2.                 (1)

To see this, rotate the right angle forced by `C -> A` by `omega`. At
`p=omega*C` it is the angle with endpoints `omega^2*A` and `A`. The fan from
`p` to `omega*D` and `B` strictly contains that right-angle interval: the
relevant cyclic order after `p` is

    omega*D, omega^2*A, ..., A, B.

Thus `angle B (omega*C) (omega*D)>pi/2`. The cosine law gives (1).
In particular, the three arrows

    B -> omega*C,  B -> omega*D,  C -> A

cannot coexist in this sector order. This is an ordered local obstruction,
not a statement that the corresponding abstract directed graph is impossible
in every phase/gain arrangement.

An exact 12-point positive control satisfies the hypotheses and has strict
squared-distance margin `108289137/1430637325 > 0`. It checks that the arrow
`C -> A` alone is permitted and forces the comparison, not a contradiction.

## 3. Preliminary reductions, proved here rather than assumed by a prune

### Distinct suppliers and no reciprocity

A different target orbit supplies at most one own-side witness. If `b` and
`omega*b` both witness `a`, their perpendicular bisector gives
`a=t*omega^2*b` for real `t`. The radius equation becomes

    t^2+t+1=3t^2, hence (t-1)(2t+1)=0.

At `t=1` the orbits coincide. At `t=-1/2`, `a` is the midpoint of `b,omega*b`
and is not extreme. Neither is allowed. Four own-side witnesses therefore
permit choosing exactly two distinct supplier orbits at every representative.
Rotate those two choices to the other vertices of the source orbit; a
covariant selected system always exists, even if other choices were possible.

The existing polynomial identity, verified by multiplication, is

    product_g (|a-omega^g*b|^2-3s)
       = |a^3-b^3|^2-9s(s-t)^2,  s=|a|^2, t=|b|^2.

Consequently an arrow `i -> j` gives

    |z_i^3-z_j^3|=3r_i |r_i^2-r_j^2|.                      (2)

An arrow at equal radii would identify the orbits. Opposite arrows likewise
force equal radii, then coincident orbits. The graph is therefore oriented.
For fewer than five orbits, `2m <= m(m-1)/2` is already impossible.

### Increasing-radius paths have no downward shortcut

For a path of at least two selected undirected edges with strictly increasing
radii, set `R` equal to its largest radius. Formula (2) bounds the sum of its
cubed-chord lengths by

    sum(path lengths) < 3R*(last squared radius-first squared radius).

Each edge's source radius is at most `R`, and at least one is strictly less.
A downward arrow from the largest to the smallest endpoint would have exactly
the length on the right, contradicting the triangle inequality. No convexity
of the cubed points, power-quotient theorem, or commensurable angles are used.

### Right-angle interlacing

Two disjoint endpoint pairs subtending right angles at one strict hull vertex
must interlace: two length-`pi/2` subintervals in a fan shorter than `pi` can
neither be disjoint nor contain one another. Therefore the opposite supplier
sides for the source's two arrows properly cross. The previous seven-orbit
packet proved and used this rule; it is included here for self-containment.

## 4. Complete angular-first enumeration

The new search does NOT first enumerate graphs in radius order. It fixes the
actual sector boundary order as labels `0,...,m-1`, repeated in three sectors.
Choose an orbit of maximum norm, rotate one vertex to the positive real ray,
and call it label zero. Other orbit phases lie strictly between zero and
`2pi/3`. Two orbits cannot share a phase: the nearer radial point would be
inside the other orbit triangle. Thus this normalization loses no configuration.
There is no assumption that angular labels sort the radii.

For each source choose two distinct target orbits and all three rotation
gains for each. Remove a choice only for a proved necessary condition.
If `u=r_j/r_i`, an arrow gives

    cos(theta)=u/2-1/u.

This strictly increasing function equals `-1/2` at `u=1`. Thus a witness in
the open angular sector `(2pi/3,4pi/3)` relative to its source is a strictly
smaller-radius target; the other two gains give strictly larger targets.
The angular order tells which sector contains each rotated target, without
choosing numerical angles. Add the weak maximum bounds `r_i <= r_0`.
Ties among unconnected orbits are permitted; every selected edge is strict.

The primary enumerator uses target/gain loops, bitset row compatibility,
bitset radius closure, partial increasing-path checks, and minimum-domain
branching. The second enumerator starts from pairs of physical witness
labels, tests all nine rotated center pairs, uses Boolean-matrix path closure,
a physical-chord DSU, and topological deletion for distance comparisons.
It reverses tie-breaking and uses a different row order.

The following partial-state prunes are sound:

* Two distinct centered circles share at most two witnesses. With two common
  witnesses, their center chord must cross the common-witness chord. Otherwise
  one of two apices on the same perpendicular-bisector half-line is non-extreme.
* A radius-comparison cycle is impossible. The only weak starting edges point
  to maximum label zero, so any directed cycle contains a strict comparison.
* A known increasing-radius path with a downward shortcut contradicts (2).
  A weak maximum comparison on a selected edge is strict because edge endpoints
  cannot have equal radii.
* Strict ordinary-distance Kalmanson inequalities hold for `a<b<c<d`:

      d_ac+d_bd > d_ab+d_cd,
      d_ac+d_bd > d_ad+d_bc.

  They follow by splitting the crossing diagonals and adding strict triangle
  inequalities. Cancellations give strict length comparisons. A zero row,
  a strict comparison cycle, or domination by known radius comparisons rejects
  the state. Every comparison cycle includes at least one strict edge.

All rotational chord-length equalities are retained, including at unselected
pairs. This is an exact consequence of C3 symmetry, not an additional prune
on an arbitrary polygon. Unselected non-equivalent chords stay distinct.
The new obtuse-base rule is deliberately deferred until the terminal frontier.

### Completed finite coverage

Both enumerators freshly exclude five, six, and seven orbits. At eight orbits,
label zero has 21 possible target pairs, both selected with downward gains.
All 21 slices of EACH implementation were exhausted without a node limit.

| Size | Primary DFS nodes (unsliced for sizes 5–7) | Terminal abstract systems |
|---:|---:|---:|
| 5 | 148 | 0 |
| 6 | 3,432 | 0 |
| 7 | 134,443 | 0 |
| 8 | 11,415,572 across all 21 slices | 632 |

At size eight the primary rejection totals are:

    radius cycles                 2,459,965
    increasing-path shortcuts     5,698,856
    metric contradictions         2,814,662
    empty compatibility domains           0
    terminal abstract systems           632
    internal nonterminal states     441,457

These numbers partition the visited states, not the far larger unvisited row
product. The separate implementation returns the identical 632 systems.
Its total node count agrees, though its per-slice counts differ under reversed
branch ordering. Complete frontier equality, not just agreement of counts,
was checked. The implementations are separate constructions in this session,
not external independent review.

## 5. Exact chord-angle certificates for all 632 systems

The chord-direction linearization is adapted from the existing common-supplier
packet in draft #931, commit `12ccc553a41fa08fc3100f3da84003343b73032a`,
`incoming/c3-common-suppliers-2026-09-05/README.md`, Sections 6–8.
This packet does not claim that underlying method as a new discovery. Here it
is applied to the complete eight-orbit frontier, augmented by explicit
right-angle equations, and checked by a separately reconstructed verifier.
The previous seven-orbit right-angle interlacing input is credited in Section 3.

For a directed chord from physical vertex `a` to `b`, `a<b`, choose consistent
unwrapped directions `phi_ab`. In a strictly convex counterclockwise polygon,
for every `a<b<c`, the triangle's three angles are

    phi_ac-phi_ab,
    pi+phi_ab-phi_bc,
    phi_bc-phi_ac,                                           (3)

all strictly positive. A consistent lift is obtained by letting both chord
endpoints move forward on the convex boundary and choosing the interior-fan
branch at the initial endpoint. A full revolution increases the lift by
`2pi`. The reverse chord differs by `pi`; no triangle chooses its own
incompatible branch.

Choose the lexicographically first endpoint pair `(u,v)` in each threefold
rotation class. Tracking endpoint rotation and reversal gives

    3phi_ab = q_class + eta_ab*pi,
    eta_ab=(a+b-u-v)/m.                                     (4)

The offset is integral. Rotating both endpoints without a wrap adds `2pi/3`;
one wrapped endpoint reverses the sorted chord and subtracts `pi`; two wrapped
endpoints subtract `2pi`. These are exactly the offset changes in (4).
An own-triangle chord has the same convention. Arbitrary global direction is
left free; it is not constrained to be a rational multiple of pi.

For eight orbits there are `8+3*binom(8,2)=92` chord-direction variables and
one pi variable. Substitute (4) into three times (3). Add:

* strict positivity of every triangle angle and pi;
* equality of opposite angles whenever the selected/rotational chord-length
  classes are equal;
* strict opposite-angle order for proved strict own-radius comparisons;
* the right-angle equations forced by own-side arrows.

Every actual geometric realization supplies a solution of

    A*x > 0,  E*x=0,

with integer matrices. The model is only necessary; feasibility would NOT
certify coordinates. The two geometric positive controls also have exactly
checked rational feasible vectors for this relaxation.

Each rejection certificate is a nonempty positive-integer combination of
strict rows, plus a signed-integer combination of equality rows, whose entire
coefficient vector is zero:

    sum lambda_s*A_s + sum mu_t*E_t = 0,
    lambda_s > 0.

At any alleged solution the left side must be strictly positive, while the
right side is zero. This is the exact contradiction. There are 24,343 terms
across the 632 stored certificates.

SciPy/HiGHS helped discover multipliers. Each multiplier was reconstructed as
an exact rational number, cleared to integers, and checked in exact arithmetic.
A floating solver's `infeasible` return is never the acceptance rule.

`c3_eight_check.py` independently reconstructs certificate premises using
physical-chord BFS components and explicit rotation orbits. It checks each
selected equality, right angle, side order, rotation offset, sign, and final
integer sum. It does not import the generator's matrix model or any LP library.
Every certificate is verified. The simpler containment certificate additionally
rejects 369 cases; the remaining 263 have the chord-angle route.

## 6. Exact controls and defensive tests

`c3_eight_controls.py` works with coordinates `(x,sqrt(3)*y)` over rationals.
It independently checks all supporting-edge determinants and all squared
pair distances for the following controls:

* the exact nine-point irrational-angle own-side directed cycle, where every
  vertex has maximum multiplicity three;
* the nine-point fixture with two extra own-side witnesses at one source
  orbit, with multiplicity distribution `{2:6,4:3}`;
* the 12-point strict Pythagorean order fixture in Section 2.

The first two pass the right-angle containment rule and have exact rational
feasible angle-model vectors. Those vectors are controls for the linear
relaxation, not claimed to equal the actual geometric angles.

The 25 focused tests passed under both unittest and pytest; these are the same
25 tests, not two independent suites. They cover all stored certificates, altered multipliers,
wrong premises, malformed labels, duplicate cases, exact positive controls,
independent angle-row reconstruction, early exits, malformed CLI numbers,
first-survivor reporting, and compiled small-case searches.

## 7. Reproduction and evidence boundaries

No third-party Python package is needed for certificate and control checks:

```sh
python c3_eight_check.py --check
python c3_eight_controls.py
python build_report.py --check
python -m unittest -v test_c3_eight.py
```

Fresh complete enumeration and certificate replay, with a GNU-compatible
C++17 compiler:

```sh
python replay.py --full --jobs 4 --check --output fresh-full.json
```

A smaller replay checks sizes five through seven and eight-orbit slice zero
of both implementations. It is NOT complete eight-orbit coverage:

```sh
python replay.py --quick --check
python replay.py --quick --sanitize --check
```

Optional new certificate discovery needs NumPy and SciPy. It reuses the stored
frontier and does not regenerate graph coverage. Different solver versions may
produce different certificates, which must still pass exact verification:

```sh
python generate_certificates.py --index 0 --output regenerated-case-zero.json
```

`runs.json` records actual completed full runs bound to the two source hashes.
`report.json` summarizes the checked evidence; `build_report.py --write`
regenerates it and the byte-integrity manifest. `validation.json` records the
completed local test commands and their precise coverage. Rechecking those saved reports
alone is not fresh exhaustive enumeration. CLI node limits and first-survivor
stops never report exhaustion. A search survivor is only an abstract system.

Repository-wide `make verify-fast`, `make verify-artifacts`, Ruff, and hosted CI
were not run for this new packet. Ruff is not installed in this environment. Local GitHub git access failed DNS resolution,
and the available GitHub connector exposed read operations but no branch,
commit, or PR creation action. No new GitHub PR was opened in this session.
A ready-to-apply repository patch and draft PR body accompany the package. A quick UBSan replay
passed both implementations at sizes five through seven and at eight-orbit
slice zero only; no full eight-orbit sanitizer sweep is claimed.

## 8. What remains

The all-size obstruction has NOT been obtained. The new right-angle containment
and distance-comparison rules apply at arbitrary size, but their unavoidable
occurrence has only been established here in the bounded search through eight
orbits, supplemented by the chord-angle certificates.

A larger all-own-side counterexample could have no nonempty witness-closed
subsystem of at most eight orbits: retaining that subsystem would contradict
the bounded theorem. In particular, each sink strongly connected component
of a selected two-out system would contain at least nine orbits. This is a
necessary condition, not a finite bound on arbitrary counterexamples.

There is still no reduction from a general hypothetical counterexample to
C3 symmetry, nor from arbitrary rich radii to own-triangle-side radii. The
66-point partial construction is not completed or excluded by this result.
