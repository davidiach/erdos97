# Two overlapping diamonds force an impossible phase identity

9 September 2026. **Restricted paper proof and exact fixed-system certificates;
independent mathematical review pending.** No unrestricted proof or counterexample
to Erdos #97, exhaustive nine-orbit exclusion, accepted status promotion, or
external review is claimed.

This draft publishes the mathematical core of a broader research continuation:
a general gain-labelled phase equation and its application to three specified
nine-orbit systems. It does not import the continuation's other searches,
333-case collection, numerical realization attempts, or geometric controls.

## Statement and conventions

Let omega=exp(2*pi*i/3), T(z)={z,omega*z,omega^2*z}, and assume finitely many
pairwise distinct nonzero orbits have a strictly convex union. Choose their
representatives in one sector of width L=2*pi/3, with strictly increasing
phases theta_0<...<theta_(m-1)<theta_0+L.

An arrow i -(g)-> j means

    |z_i-omega^g*z_j|^2 = 3|z_i|^2.

The radius is the SOURCE triangle's side length. Neither arbitrary witness
radii nor an arbitrary nonsymmetric polygon satisfy these extra hypotheses.
No equally spaced phases or rational angles are assumed.

For four distinct orbit labels i,j,k,l, suppose the arrows are

    i -(a)-> j,  i -(b)-> k,  j -(c)-> l,  k -(d)-> l,
    a+c = b+d (mod 3).

Then, writing g=b-c (mod 3) and sigma(0)=0, sigma(1)=1, sigma(2)=-1,

    z_i*z_l = omega^g*z_j*z_k,                              (1)
    theta_i+theta_l-theta_j-theta_k = sigma(g)*L.             (2)

This is a local rule at any number of orbits, not only a rectangular product.
Gain alignment and strict convexity are essential.

## Proof of the local rule

The circle-completion identity is already in PR #942,
`incoming/six-arc-product-obstructions-2026-09-08/snapshot/proof_attempts/product_component.md`,
Section 3 (Git blob `2ccb3e6eb195eaad77f780d2fc56c4dd744636d0`). The new use here is
its gain-labelled phase translation and cancellation between overlapping diamonds.
No novelty relative to the external literature is claimed.

Suppose |A-x|^2=|B-x|^2=3|x|^2 and C has distance sqrt(3)|A| from A and
sqrt(3)|B| from B. Normalize x=1 by a similarity. Both AB and -2 lie on the
last two circles: |AB-A|^2=|A|^2|B-1|^2=3|A|^2, and the first equation also
gives |A+2|^2=3|A|^2; likewise for B. Distinct centers give at most two
intersection points. Therefore C=AB or C=-2. Tangency or coincident displayed
roots create no additional branch.

The second branch is impossible in a strictly convex orbit union, because
x=(omega*C+omega^2*C)/2 when C=-2x. Thus C=AB/x.

Apply this with x=z_i, A=omega^a*z_j, B=omega^b*z_k and
C=omega^(a+c)*z_l. The gain-alignment equation makes C the same physical
point in both circles. The product formula becomes (1).

The phase difference in (2) lies strictly in (-2L,2L), since all four
representatives lie in one sector of width L. By (1) it equals gL modulo
2*pi=3L. Only 0, L, -L, respectively, lie in that open interval.
The alternative endpoints +/-2L are excluded by strictness. This proves (2).

The sector normalization itself is legitimate: distinct orbits cannot share
a ray, since the smaller point would lie in the other orbit triangle. The
origin lies inside each triangle T(z_i).

## The seven-arrow obstruction

Each of the three systems in `cases.json` contains these seven arrows:

    0 -(1)-> 1,  0 -(1)-> 2,
    1 -(1)-> 6,  2 -(1)-> 6,
    2 -(1)-> 8,
    6 -(2)-> 3,  8 -(2)-> 3.

The two diamonds are (0,1,2,6) and (2,6,8,3). They imply

    z_0*z_6 = z_1*z_2,
    z_2*z_3 = omega^2*z_6*z_8.

All factors are nonzero, so cancellation gives

    z_0*z_3 = omega^2*z_1*z_8.                             (3)

But the prescribed sector order has 0<1<3<8. The quotient z_3/z_1 has phase
in (0,L), whereas omega^2*z_8/z_0 has its corresponding phase in (-L,0).
They cannot agree. Equivalently, the two equations (2) sum to

    (theta_3-theta_1)+(L-theta_8+theta_0)=0,

with both summands strictly positive. This is the exact contradiction.
The locations of the two intermediate labels 2 and 6 are immaterial to this
last step. Other phase orders and other gains are not excluded by this claim.

## Exact certificate contract and replay

`verify.py` reconstructs every arrow/gain premise and the two integer phase
equations. The certificate has two positive strict-order terms and the
negatives of the two diamond equalities. It requires exact cancellation,
not a floating residual or a solver status.

From this directory, using Python 3.10+ and only the standard library:

```sh
python -S verify.py
python -S -m unittest -v test_diamond_phase_obstruction_20260909.py
```

Do not disable assertions. Tests reject missing arrows, mismatched gains,
wrong phase orders, corrupt multipliers, repeated orbit labels, duplicate
cases and missing strictness. A rational positive phase vector for a single
consistent diamond is retained as a non-vacuity control for the phase model;
it is not labelled a geometric realization.

The elementary geometric proof remains an expert-review obligation. Arithmetic
replay and two implementations prepared in one session are not external review.

## Remaining problem and publication limits

No argument forces arbitrary globally four-rich convex polygons to have these
orbits or these diamonds. Even within C3, the full nine-orbit search was not
exhausted. These three fixed systems are excluded, not every 27-point polygon.

This core was prepared against main
`9b8b8f807ae8b21f10780a7d11f6c5cec65f26e7`, which includes merged PR #943.
No accepted claims, existing certificates, root configuration or workflow are
changed. Repository-wide `make verify-fast`, `make verify-artifacts`, and
compatibility gates were not run locally: this session has a scoped file export,
not a complete checkout. No Lean source changed. Scoped checks are reported in
`validation.json`; normal PR CI and independent mathematical review remain
separate outstanding gates. Keep the PR draft; no merge is requested.
