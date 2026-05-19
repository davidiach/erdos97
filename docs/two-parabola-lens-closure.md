# Two-Parabola Lens Closure Scaffold

Status: `SEARCH_SCAFFOLD` / `PROVENANCE`.

This note records a structured counterexample-search ansatz suggested by the
parabola model-case obstruction. It is not a proof of Erdos Problem #97, not a
counterexample, and not evidence that the ansatz is feasible.

## Pattern

Fix a real height `H` and consider two opposite parabolic chains

```text
L_a = (a, a^2),
U_b = (b, H - b^2).
```

For finite parameter sets `A,B`, the sampled set is

```text
P(A,B,H) = { L_a : a in A } union { U_b : b in B }.
```

The intended geometry is a strictly convex lens, with the lower samples on the
lower boundary and the upper samples on the upper boundary. This is an extra
geometric constraint: the algebra below does not by itself prove that all
sampled points are vertices of the convex hull.

## Opposite-Chain Witness Ansatz

The narrow selected-witness ansatz is:

- each lower center `L_a` uses four upper witnesses from `U_B`;
- each upper center `U_b` uses four lower witnesses from `L_A`.

This does not cover mixed witness classes and does not classify all possible
counterexamples inside a two-parabola point set.

## Lower-to-Upper Row Equations

For a lower center `L_a`, the squared distance to an upper point `U_b` is

```text
D_a(b) = (b-a)^2 + (H - b^2 - a^2)^2.
```

Expanding in the upper parameter `b` gives

```text
D_a(b) = b^4 + (1 - 2H + 2a^2)b^2 - 2ab + C_a,
```

where the constant term is irrelevant for equal-distance roots. Write

```text
c = 1 - 2H.
```

Four distinct upper parameters `q1,q2,q3,q4` are equidistant from `L_a` if and
only if, for some radius, they are the four roots of

```text
b^4 + (c + 2a^2)b^2 - 2ab + C = 0.
```

Equivalently, by Vieta, the chosen 4-subset `Q_a` of `B` satisfies

```text
sum(q for q in Q_a) = 0,
sum(q*r for {q,r} in binom(Q_a,2)) = c + 2a^2,
sum(q*r*s for {q,r,s} in binom(Q_a,3)) = 2a.
```

The conditions are sufficient for that chosen upper 4-subset to lie on one
circle centered at `L_a`: the common squared radius is determined by the
constant term.

They also imply the square-sum identity

```text
sum(q^2 for q in Q_a) = -2c - 4a^2.
```

Thus the one-parabola minimum-parameter descent no longer applies when
`c < 0`; the right side can remain nonnegative for bounded `a`.

## Upper-to-Lower Row Equations

By symmetry, for an upper center `U_b` and four lower witnesses `Q_b` in `A`,
the analogous closure equations are

```text
sum(q for q in Q_b) = 0,
sum(q*r for {q,r} in binom(Q_b,2)) = c + 2b^2,
sum(q*r*s for {q,r,s} in binom(Q_b,3)) = 2b.
```

Again,

```text
sum(q^2 for q in Q_b) = -2c - 4b^2.
```

## Finite Closure Problem

The resulting exact search problem is:

Find finite sets `A,B`, a parameter `c`, and selected 4-subsets

```text
Q_a subset B  for each a in A,
Q_b subset A  for each b in B,
```

such that all lower-to-upper and upper-to-lower moment equations above hold,
all selected witness parameters are distinct, and the resulting point set
`P(A,B,H)` with `H=(1-c)/2` is in strict convex position.

Necessary immediate bounds are

```text
c < 0,
a^2 <= -c/2 for every selected lower center a,
b^2 <= -c/2 for every selected upper center b,
```

because the selected square sums must be nonnegative.

If such data are found with exact parameters and a strict-convexity
certificate, they would give a counterexample within this restricted
opposite-chain ansatz. Conversely, any counterexample following this exact
opposite-chain selected-witness ansatz must satisfy these closure equations.

## Caveats

This scaffold is deliberately narrower than Erdos Problem #97:

- it assumes two specific parabolic arcs;
- it assumes all selected witnesses come from the opposite chain;
- it does not encode the strict-convex lens inequalities;
- it does not rule out or construct mixed same-chain/opposite-chain witness
  systems;
- it provides no exact solution, certificate, or numerical candidate.

Its value is search discipline: it turns one plausible non-ledger route into a
finite algebraic closure problem instead of another unstructured selected-row
enumeration.
