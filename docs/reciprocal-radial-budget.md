# Reciprocal Radial Budget

Status: `RESEARCH_PACKET`.

This note records a local necessary inequality for one selected row of four
equal-distance witnesses in a strictly convex polygon. It is not a proof of
Erdos Problem #97, and it is not a counterexample search result. The missing
ingredient remains a global budget or cycle theorem that prevents all rows of a
hypothetical counterexample from satisfying these local inequalities
simultaneously.

## Scope

This packet sharpens the existing middle-witness angle constraint in
`docs/claims.md`. The older lemma uses only the angles between consecutive
equal-distance witnesses. The reciprocal-radial budget also sees the local edge
directions at a middle witness.

It is not a distance-unimodality or squared-distance Monge claim. The radial
function below may oscillate, and equal-level vertices need not form a
consecutive block on the boundary.

## Setup

Let `P = (p_0, ..., p_{n-1})` be a strictly convex polygon in counterclockwise
cyclic order. Write

```text
e_j = p_{j+1} - p_j
[u,v] = det(u,v)
```

with indices modulo `n`. Fix a center `i`, and list vertices on the visible
chain

```text
p_{i+1}, p_{i+2}, ..., p_{i-1}
```

in that boundary order. Suppose four distinct witnesses `a,b,c,d` occur in this
order and satisfy

```text
|p_i - p_a| = |p_i - p_b| = |p_i - p_c| = |p_i - p_d| = r.
```

Set

```text
x_t = p_t - p_i.
```

The middle witnesses `b` and `c` are non-adjacent to `i`. The determinant
orientation convention is the one induced by the visible chain, so for adjacent
edge vectors at a middle witness,

```text
[x_t,e_{t-1}] > 0,
[x_t,e_t] > 0,
[e_{t-1},e_t] > 0.
```

## Local Budget Lemma

For the middle witness `b`,

```text
r^2 [e_{b-1},e_b]
-------------------------------
[x_b,e_{b-1}] [x_b,e_b]

<=

[x_a,x_b]                 [x_b,x_c]
-------------------   +   -------------------
r^2 + x_a . x_b           r^2 + x_b . x_c
```

and for the middle witness `c`,

```text
r^2 [e_{c-1},e_c]
-------------------------------
[x_c,e_{c-1}] [x_c,e_c]

<=

[x_b,x_c]                 [x_c,x_d]
-------------------   +   -------------------
r^2 + x_b . x_c           r^2 + x_c . x_d.
```

All displayed denominators are positive. The two `r^2 + dot` denominators are
positive because consecutive equal-radius witness rays lie in an angular span
less than `pi`.

Equivalently, define `beta_t^-` and `beta_t^+` as oriented angles from the ray
`p_i -> p_t` counterclockwise to the incoming and outgoing edge directions
`e_{t-1}` and `e_t`. Then

```text
0 < beta_t^- < beta_t^+ < pi
```

and the left side is

```text
cot(beta_t^-) - cot(beta_t^+)
  = sin(tau_t) / (sin(beta_t^-) sin(beta_t^+)),
```

where `tau_t` is the exterior turn at `p_t`.

## Proof

Relabel locally so the center is `p_0`, and consider the opposite chain

```text
p_1, p_2, ..., p_{n-1}.
```

For rays inside the open incident cone at `p_0`, strict convexity gives a
unique intersection with this chain. Let `theta` be polar angle around `p_0`,
let `rho(theta)` be the intersection distance, and set

```text
q(theta) = 1 / rho(theta).
```

On the edge from `p_j` to `p_{j+1}`, write `v_j = p_j - p_0`. A point
`lambda u(theta)`, where `u(theta) = (cos theta, sin theta)`, lies on the
supporting line of that edge exactly when

```text
[lambda u(theta) - v_j, e_j] = 0.
```

Thus

```text
lambda = [v_j,e_j] / [u(theta),e_j],
q(theta) = [u(theta),e_j] / [v_j,e_j].
```

It follows that `q'' + q = 0` on each open edge interval.

At a visible non-adjacent vertex `p_t`, the one-sided derivatives are

```text
q'_-(theta_t) = [R u,e_{t-1}] / [x_t,e_{t-1}],
q'_+(theta_t) = [R u,e_t]     / [x_t,e_t],
```

where `u = x_t / |x_t|` and `R` is counterclockwise rotation by `pi/2`.
Therefore

```text
J_{0,t} = q'_+(theta_t) - q'_-(theta_t)
        = |x_t| [e_{t-1},e_t] / ([x_t,e_{t-1}] [x_t,e_t]) > 0.
```

So, in the distributional sense,

```text
q'' + q = sum_t J_{0,t} delta_{theta_t},
```

with positive atomic mass at the visible non-adjacent vertices.

Now take two equal-level vertices `u < v` in angular order:

```text
q(theta_u) = q(theta_v) = s = 1/r,
delta = theta_v - theta_u in (0,pi).
```

Solving from the left gives

```text
q(theta_v)
  = q(theta_u) cos(delta)
  + q'_+(theta_u) sin(delta)
  + integral_(theta_u,theta_v) sin(theta_v - phi) dmu(phi).
```

Since `mu >= 0`,

```text
q'_+(theta_u) <= s tan(delta/2).
```

Solving backward gives

```text
q'_-(theta_v) >= -s tan(delta/2).
```

Apply the backward bound to the pair `(a,b)` and the forward bound to the pair
`(b,c)`. Then

```text
J_{0,b} <= s (tan(delta_ab/2) + tan(delta_bc/2)).
```

Multiplying by `r` and substituting the jump formula gives the determinant
inequality for `b`. The proof for `c` is identical.

Finally, for equal-length vectors `x` and `y` spanning an angle in `(0,pi)`,

```text
tan(angle(x,y)/2) = [x,y] / (r^2 + x . y).
```

This gives the displayed algebraic form.

## Cleared Polynomial Form

For the middle witness `b`, clearing positive denominators gives:

```text
r^2 [e_{b-1},e_b]
(r^2 + x_a . x_b)
(r^2 + x_b . x_c)

<=

[x_b,e_{b-1}] [x_b,e_b]
(
  [x_a,x_b] (r^2 + x_b . x_c)
  + [x_b,x_c] (r^2 + x_a . x_b)
).
```

The corresponding formula for `c` is obtained by replacing `(a,b,c)` with
`(b,c,d)`.

## Negative Control

The local lemma cannot rule out a single bad vertex. In the pentagon

```text
p_0 = (0,0),
p_1 = (cos 20 deg,  sin 20 deg),
p_2 = (cos 60 deg,  sin 60 deg),
p_3 = (cos 120 deg, sin 120 deg),
p_4 = (cos 160 deg, sin 160 deg),
```

the center `p_0` sees the other four vertices at unit distance, and both middle
budget inequalities are tight. This is consistent with the known local
counterexample to single-vertex obstruction arguments in
`docs/canonical-synthesis.md`.

## Next Use

The useful next test is not whether this packet alone kills an existing finite
frontier. It should first be used as an exact local filter:

1. sort a selected row's four witnesses along the visible chain from the
   center;
2. emit the two middle-witness inequalities;
3. clear the listed positive denominators;
4. test whether these nonlinear inequalities create reusable obstruction
   motifs that are not already vertex-circle, Kalmanson, Altman, or Ptolemy
   certificates.

Any future promotion requires a separate global budget theorem or a checked
finite certificate that combines these inequalities with other exact
constraints.
