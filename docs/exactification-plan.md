# Exactification plan

Numerical candidates are not accepted as counterexamples until exact or certified verification is available.

## Trigger threshold

Only attempt exactification when a candidate has approximately:

```text
max selected-distance spread < 1e-10
convexity margin            > 1e-3
minimum edge length         > 1e-3
independent verifier passes
```

The current best candidate does not meet this threshold.

## Polynomial equations

For each center `i`, choose a representative `a in S_i`. For each `b in S_i \ {a}`, require

```text
(x_i-x_a)^2 + (y_i-y_a)^2 - (x_i-x_b)^2 - (y_i-y_b)^2 = 0.
```

Strict convexity is checked by orientation determinants

```text
orient(p_i, p_{i+1}, p_{i+2}) > 0
```

for all `i`, using cyclic indices.

## Certificate format

A certificate should contain:

- `n`;
- exact coordinates or exact algebraic parameters;
- selected 4-sets `S_i`;
- exact zero checks for all distance equalities;
- exact positivity checks for all orientation determinants;
- optional Sympy/Sage/Lean verification script.

See `certificates/best_B12_certificate_template.json` for a placeholder format.
