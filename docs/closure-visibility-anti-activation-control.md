# Closure-visibility anti-activation control

Status: `EXACT_NEGATIVE_CONTROL` / `PROVENANCE`. No general proof of Erdos
Problem #97 is claimed. No counterexample is claimed.

This note isolates the sparse closure-visibility control that is also
summarized in `docs/closure-activation-negative-controls.md`. It blocks a
different overstrong bridge move from the full-row anti-activation control:

```text
center c in cl(A) and target triple T subset cl(A)
    => c has a selected or rich row containing T.
```

The checked artifact is:

```text
data/certificates/closure_visibility_anti_activation_control.json
```

Run the checker with:

```bash
python scripts/check_closure_visibility_anti_activation_control.py --check --assert-expected --json
```

Regenerate the artifact after an intentional source change with:

```bash
python scripts/check_closure_visibility_anti_activation_control.py --write
```

## Control

The control uses cyclic order `0,1,2,3,4,5,6,7,8` and two sparse rich rows:

```text
3 -> {0,1,4,6}
7 -> {0,3,4,8}
```

The target is a `151:7`-style closure-exposed row with center `7`, target
witnesses `{0,1,4}`, private witness `6`, and target row `{0,1,4,6}`.

Starting from seed `{0,1,4}`, closure proceeds as:

```text
{0,1,4}
  -> add 3 via {0,1,4}
  -> {0,1,3,4}
  -> add 7 via {0,3,4}
  -> {0,1,3,4,7}
```

At the end, the closure contains center `7` and all target witnesses
`{0,1,4}`. However, center `7` entered through the different triple
`{0,3,4}`, and its row contains neither the target triple nor the target row.

## Checked Conditions

The checker verifies:

- four-uniformity and self-exclusion for the sparse rich rows;
- row-pair intersections of size at most two;
- the witness-pair cap;
- the two-overlap crossing of source chord `{3,7}` with witness chord `{0,4}`;
- the displayed closure steps;
- absence of the target row at center `7`;
- absence of target-triple activation for center `7`.

Current compact summary:

| Quantity | Value |
|---|---:|
| final closure | `{0,1,3,4,7}` |
| target center in closure | `true` |
| target witnesses in closure | `{0,1,4}` |
| target row present at center `7` | `false` |
| target center activated by target triple | `false` |

## Bridge Lesson

This control separates visibility from activation provenance. Seeing the target
center and the target triple somewhere in the same deletion closure is weaker
than knowing the target center was activated by that triple, and weaker still
than knowing the specified fourth witness lies in the same rich class.

## Nonclaims

This is not a polygon, not a Euclidean realizability certificate, not a
counterexample, and not a refutation of activation lemmas that require
provenance, critical-row uniqueness, or all-fourth obstruction hypotheses.
