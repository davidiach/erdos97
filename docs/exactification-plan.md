# Exactification plan

Numerical candidates are not accepted as counterexamples until exact or
certified verification is available.

## Trigger threshold

Only attempt exactification when a candidate has approximately:

```text
max selected-distance spread < 1e-10
convexity margin            > 1e-3
minimum edge length         > 1e-3
minimum pair distance       > 1e-3
independent verifier passes
```

The current saved near-misses do not meet this threshold.[^repo]

## Polynomial equations

For each center `i`, choose a representative `a in S_i`. For each
`b in S_i \ {a}`, require

```text
(x_i-x_a)^2 + (y_i-y_a)^2 - (x_i-x_b)^2 - (y_i-y_b)^2 = 0.
```

The same equation is affine-linear in `(x_i,y_i)` and quadratic overall, which
is useful for elimination and circumcenter checks.[^alg]

## Convexity encoding

Consecutive orientation margins are useful diagnostics. For an exact
semialgebraic certificate in free coordinates, prefer inequalities against
each oriented edge line:

```text
orient(p_i, p_{i+1}, p_j) > 0
```

for every edge `(i,i+1)` and every non-edge vertex `j`, with cyclic indices.
This avoids relying only on consecutive left turns when the cyclic order itself
has not already been certified.[^alg]

## Paraboloid and circumcenter views

The paraboloid lift converts a centered equal-distance condition into a
coplanarity condition in `R^3`: lifted witnesses lie in a plane parallel to the
tangent plane at the lifted center.[^syn]

Equivalently, if three witnesses are noncollinear, the center is the
circumcenter of that triangle and the fourth witness must lie on the same
circle.[^alg]

## Rank frontier

For selected squared-distance constraints, translations and rotation are always
Jacobian kernel directions. At an exact solution, homogeneity gives the scaling
kernel as well, so `rank R_W(p) <= 2n-4` for a nondegenerate solution.[^rank]

Generic rank `2n-3` at random non-solutions is therefore only a diagnostic. The
current exactification frontier is to understand special rank-drop loci for
fixed patterns, especially whether an ear-orderable pattern can be ruled out
by combining a repaired rank theorem with the scaling-kernel lemma.[^rank]

## Certificate format

A certificate should contain:

- `n`;
- exact coordinates or exact algebraic parameters;
- selected 4-sets `S_i`;
- exact zero checks for all distance equalities;
- exact positivity checks for convexity;
- minimum pair-distance separation;
- a reproducible Sympy/Sage/Lean-style verification script.[^repo]

See `certificates/best_B12_certificate_template.json` for a placeholder format.

[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^alg]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/04_algebraic_and_semicircle_corrections.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
[^rank]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/03_RANK_AND_BRIDGE_STATUS.md`.
