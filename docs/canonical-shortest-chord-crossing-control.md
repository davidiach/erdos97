# Canonical shortest-chord crossing negative control

Status: `EXACT_CERTIFICATE_DIAGNOSTIC` / `EXACT_LOCAL_NEGATIVE_CONTROL`.

This note records an exact rational strictly convex decagon with exactly two bad
centers whose canonical shortest witness chords cross. It rejects a purely
local noncrossing claim for one deterministic chord-selection rule. It is
exactly not a counterexample to Erdos Problem #97: every other center is good.

## Construction

Use the rational parametrization

```text
u(t) = ((1-t^2)/(1+t^2), 2t/(1+t^2)).
```

Set

```text
p0 = (0,0)
p1 = (1/800,-1/76)
R  = 223/222

p2 = u(11/280)          p3 = p1 + R*u(43/354)
p4 = u(2/13)            p5 = p1 + R*u(96/407)
p6 = u(108/347)         p7 = p1 + R*u(95/239)
p8 = u(219/409)         p9 = p1 + R*u(201/197).
```

The claimed counterclockwise cyclic order is

```text
p0,p1,p2,p3,p4,p5,p6,p7,p8,p9.
```

All coordinates and all checks below are rational.

## Exact replay

Run:

```bash
python scripts/check_canonical_shortest_chord_crossing.py \
  --check --assert-expected --summary-json
```

The checker recomputes the managed artifact
`data/certificates/canonical_shortest_chord_crossing_control.json`. It verifies:

- all `80` directed-edge/other-point determinants are positive, so the stated
  order is strictly convex;
- the minimum determinant is
  `4166275382872427/4803025334488832400`, attained for directed edge `p3p4`
  and point `p5`;
- center `p0` has exactly one distance class of size at least four, namely
  `{p2,p4,p6,p8}` at squared radius `1`;
- center `p1` has exactly one distance class of size at least four, namely
  `{p3,p5,p7,p9}` at squared radius `49729/49284`;
- every other distance class at either bad center is a singleton;
- centers `p2` through `p9` each have nine singleton distance classes, so the
  decagon has exactly two bad centers and is not a counterexample;
- `p2p4` is the unique shortest chord in the first rich class, with squared
  length `695556/13584133`;
- `p3p5` is the unique shortest chord in the second rich class, with squared
  length `13510836652681/273978475879725`;
- the endpoints occur as `p2,p3,p4,p5` in cyclic order, so `p2p4` and `p3p5`
  cross.

Thus the rule

```text
choose the smallest rich radius, then the unique shortest chord in that class
```

does not produce pairwise noncrossing chords from local bad-center hypotheses
alone.

## Claim boundary

The other eight centers are exactly good, so this construction is not a
counterexample. The two canonical chords are distinct, so it does not refute
canonical-chord injectivity. It also does not rule out a different chord
assignment or a theorem that uses extra global all-bad or
minimal-counterexample hypotheses. It proves no finite-case exclusion, gives
no all-bad polygon, and changes neither the repo-local `n <= 8` result nor the
official/global falsifiable/open status.
