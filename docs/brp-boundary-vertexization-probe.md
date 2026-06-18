# Barany--Roldan-Pensado boundary vertexization probe

Status: `NUMERICAL_GEOMETRIC_DIAGNOSTIC`.

This note records a first contrarian probe of the convex-body boundary
construction lane. It does not prove Erdos Problem #97, does not give a
counterexample, and does not model the full Barany--Roldan-Pensado 15-gon.

## Question

Barany--Roldan-Pensado construct convex bodies whose boundary has high
centered-circle intersection multiplicity. The obstruction for Erdos #97 is
that those extra circle intersections may lie in edge interiors rather than at
vertices.

The first finite-vertex question is deliberately smaller:

```text
For the recorded 3-fold seed points, do centered circles already convert
boundary richness into vertex richness?
```

## Modeled seed

The checker uses the four quoted source points

```text
A1 = (1000, 0)
A2 = (906, 114)
A3 = (645, 359)
A4 = (-498, 871)
```

and their rotations by `2*pi/3` and `4*pi/3`, giving the 12 modeled vertices

```text
A1,A2,A3,A4,B1,B2,B3,B4,C1,C2,C3,C4.
```

The seed order is strictly convex in the float64 check. The source paper then
uses Lemma 3.1 to prove the existence of a point `A5` in a neighborhood of the
broken line `A4B1B2B3`, but it does not give coordinates for `A5`. The checker
therefore keeps the explicit 12-point seed separate from any synthetic `A5`
stress test.

## Checker

Run:

```bash
python3 scripts/check_brp_boundary_probe.py --assert-expected
```

The checked artifact is
`data/certificates/brp_boundary_vertexization_probe.json`, managed by
`metadata/generated_artifacts.yaml`. Replay the artifact check with:

```bash
python3 scripts/check_brp_boundary_probe.py --check --assert-expected --json
```

The checker:

- represents vertex-to-vertex squared distances exactly in `Q(sqrt(3))` for
  the 120-degree rotated seed;
- enumerates every distinct circle centered at a seed vertex and passing
  through another seed vertex;
- intersects each such circle numerically with the 12 seed boundary edges;
- separates hits at modeled vertices from hits in edge interiors;
- runs a small signed synthetic `A5` edge-pocket scan with
  `A5(t,h)=A4+t*(B1-A4)+h*unit_left_normal(A4B1)`, rotating the result to
  `B5` and `C5`. This is only a stress test, not the source paper's `A5`.
- records the actual Lemma 3.1 role preflight
  `A=A3, B=A4, C=B1, D=B2`, including the acute-angle check and a reproducible
  `Bprime = B + tau*(A-B)` neighbourhood budget.
- runs a bounded `N=1` Lemma 3.1 A5 constraint scan near `A4`, using the
  parameterization
  `A5(t,h)=A4+t*(B1-A4)+h*unit_left_normal(A4B1)`.
- checks a tiny outward-rounded float64 interval box around the sampled
  witness:
  `t in [239999/10000000, 240001/10000000]` and
  `h in [-50001/10000000, -49999/10000000]`.
- records the centered-circle boundary support profiles for the sampled
  synthetic 15-gon from `t=3/125, h=-1/200`, including the best boundary-rich
  circles. These radii and edge parameters are float64 diagnostics, not exact
  algebraic certificates. The sampled support scan uses a `1e-7` edge-root
  boundary margin to avoid platform-dependent near-endpoint root counts.

## Current result

The stable checked summary is:

```text
seed vertices: 12
distinct centered vertex radii: 120
max seed-vertex hits on one centered circle: 2
max seed-boundary hits on one centered circle: 5
circles with at least four boundary hits: 45
circles with at least four seed vertices: 0
synthetic A5 edge-pocket candidates: 36
strictly convex synthetic A5 candidates: 0
synthetic candidates with at least four vertices on a centered circle: 0
Lemma 3.1 role angle ABC: 87.7725247 degrees
Lemma 3.1 default Bprime tau: 1/100
Lemma 3.1 A5 constraint samples: 2000
sampled Lemma 3.1 A5 witnesses: 1
first sampled witness: t=3/125, h=-1/200
rotated 15-gon convex for sampled witness: yes
sampled-witness centered circles with four vertices: 0
float64 A5 interval box checks pass: yes
interval max local turn upper bound: -0.026805405
interval rotated 15-gon min turn lower bound: 0.026803636
sampled 15-gon centered-circle profiles: 195
sampled 15-gon max boundary hits: 6
sampled 15-gon circles with at least four boundary hits: 87
sampled 15-gon circles with at least four vertices: 0
```

Thus the modeled 12-point seed shows the expected continuous/discrete gap:
many centered circles hit the polygonal boundary four or five times, but none
hits four modeled seed vertices.

The synthetic `A5` pocket scan is also a useful failed route: the sampled
signed normal-offset stand-ins do not remain strictly convex. This only
rejects those 36 sampled edge-pocket candidates; it does not rule out other
naive edge-pocket placements or the source construction's existential `A5`.
It is still not evidence against the full contrarian lane: the source
construction's Lemma 3.1 choice is existential, and the relevant
edge-parameter closure remains unmodeled.

The Lemma 3.1 role preflight pins the source-paper mapping for the local
insertion step. With `A=A3`, `B=A4`, `C=B1`, and `D=B2`, the four role points
are strictly convex in counter-clockwise order, the angle `ABC` is acute, and
the default point `Bprime=A4+(A3-A4)/100` has `B1` outside the circle centered
at `Bprime` through `A4`.

The follow-up A5 constraint scan samples 100 rational positions close to `A4`
along `A4->B1` and 20 signed normal offsets. Exactly one sampled point,
`t=3/125, h=-1/200`, satisfies the `N=1` Lemma 3.1 local bullets in float64:
`B2,B1,A5,A4,A3` is extreme and clockwise, `A5` is outside the circle centered
at `A3` through `A4`, the angle `A3 A4 A5` is acute, and the segment `B1A5`
intersects the default `S_Bprime` twice. Rotating this sampled point gives a
strictly convex synthetic 15-gon, but its centered vertex circles still have
maximum vertex multiplicity `2`; no centered circle hits four modeled vertices.

This is a useful next-step witness for the source construction lane, not an
exact certificate. The sampled `A5` remains a float64 point in a bounded search
family, the final BRP boundary-intersection proof is not replayed, and the
boundary-hit/finite-vertex gap remains open.

The interval-box follow-up makes the sampled point less brittle inside the
checker's own numeric model. With outward-rounded float64 interval arithmetic,
the whole box above keeps `B2,B1,A5,A4,A3` clockwise, keeps `A5` outside the
circle centered at `A3` through `A4`, keeps the angle `A3 A4 A5` acute, keeps
the default `S_Bprime` intersection roots inside `(0,1)`, and keeps the
rotated synthetic 15-gon strictly convex. This is still not an exact algebraic
certificate for the source `Q(sqrt(3))` coordinates and it does not certify
the BRP boundary-intersection count throughout the box.

The sampled boundary-support scan makes the final-polygon diagnostic more
concrete. For the same sampled synthetic 15-gon, the checker enumerates 195
centered circles through modeled vertices, finds three circles with six
boundary hits, and records the best profiles centered at `A3`, `B3`, and `C3`.
Each of those circles hits two modeled vertices and four edge-interior points.
Across the sampled 15-gon, 87 centered circles have at least four boundary
hits, while no centered circle has four modeled vertices. This sharpens the
boundary-to-vertex gap for the sampled stand-in only; it does not replay the
source paper's continuum argument, does not certify the boundary hits exactly,
and does not produce a finite counterexample.

## Next steps

Useful follow-up work should avoid more visual inspection and instead make the
edge-interior hits algebraic:

1. Replace the float64 interval box with an exact algebraic or directed-decimal
   certificate over the source coordinates.
2. Certify the sampled final-15-gon boundary hits with exact algebraic or
   interval checks.
3. Promote each interior circle-edge hit to a candidate vertex parameter.
4. Iterate the closure condition: promoted vertices become centers that must
   themselves acquire four vertex hits.
5. Replace float64 edge intersections with exact algebraic or interval
   certificates.
6. If every closure attempt explodes into new edge interiors, extract the
   failure as a boundary-to-vertex obstruction lemma.

## Guardrails

Do not cite this probe as:

- a proof of Erdos Problem #97;
- a counterexample or counterexample candidate;
- a finite extraction from the Barany--Roldan-Pensado body;
- an exact check of the source paper's final 15-gon;
- an exact construction of the actual existential `A5` from Lemma 3.1;
- an exact certificate for boundary intersections.
