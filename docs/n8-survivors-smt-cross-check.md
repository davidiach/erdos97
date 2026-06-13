# n=8 survivor classes: independent SMT cross-check

Trust label: `EXACT_OBSTRUCTION` (SMT certificate), repo-local cross-check
pending external review. No general proof of Erdos Problem #97 and no
counterexample are claimed.

This note records an independent, uniform second source for the `n = 8`
exact-survivor obstruction. The repo-local `n <= 8` result enumerates all
necessary selected-witness incidence survivors into 15 canonical classes
(`docs/n8-incidence-enumeration.md`) and kills each class with exact arithmetic
(`docs/n8-exact-survivors.md`): one class by a cyclic-order noncrossing
argument, the other fourteen by perpendicular-bisector / equal-distance
(PB+ED) algebra, four of those (classes 3, 4, 5, 14) via Groebner bases. The
SymPy-free recheck (`docs/n8-independent-obstruction.md`) deliberately leaves
the four Groebner-dependent classes uncovered.

`scripts/check_n8_survivors_smt.py` covers **all 15 classes uniformly** with a
**different decision procedure**: z3 nonlinear real arithmetic (NRA). For each
class it builds

- the **equal-distance** constraints (each center `p_i` is equidistant from
  its four selected witnesses), and
- the derived **perpendicular-bisector** constraints (for each shared-witness
  pair `(i, j)` with common witnesses `(a, b)`, both centers lie on the
  perpendicular bisector of `p_a p_b`),

and asks z3 whether any **strictly convex** octagon (vertices in cyclic label
order, all per-period turn determinants `> 0`) satisfies them. Every class is
**UNSAT** (each in well under a second), so no survivor class has a strictly
convex realization.

## Result

```text
classes 0..14 : UNSAT (15/15)
```

This independently confirms both the cyclic-order conclusion (the single class
killed combinatorially) and the PB+ED / Groebner conclusions (the other
fourteen, including the four Groebner-dependent classes 3, 4, 5, 14), using
neither Groebner bases nor the cyclic-order combinatorics -- only z3's NRA
decision procedure.

## Why this is sound

Any realization of a survivor class is a strictly convex octagon
`p_0, ..., p_7` in label order with every center equidistant from its
witnesses. Such a realization satisfies the equal-distance constraints (and
hence their perpendicular-bisector consequences) together with the strict
convexity inequalities, so z3 UNSAT for that conjunction means **no realization
exists**. The perpendicular-bisector equations are genuine consequences of the
equal-distance constraints (shared witnesses `a, b` of both `i` and `j` force
both centers onto the bisector of `p_a p_b`), so they add no spurious
constraint; the equal-distance constraints plus convexity already suffice.

The gauge `p_0 = (0,0)`, `p_1 = (1,0)` is without loss of generality: the
constraints are similarity-covariant (translation, rotation, scaling), and the
opposite (clockwise) orientation is the `y -> -y` reflection, which preserves
both the constraints and the gauge -- so checking the counter-clockwise
orientation alone is conclusive.

## Independence and scope

- **Independent decision procedure.** The cross-check uses z3 NRA; the existing
  artifacts use SymPy Groebner bases and an exact cyclic-order argument. A bug
  in one decision procedure would not be shared by the other.
- **Shared problem statement.** The incidence-to-equation translation (which
  vertices each center selects, and the resulting equal-distance /
  perpendicular-bisector equations) is the standard one and is *not* the
  independent part -- it is the problem statement. The checker re-implements it
  self-contained (it does not import the existing checkers), and the verdicts
  and per-class equation counts match the existing class-14 audit's
  equation builder.
- This strengthens, but does not replace, the existing `n = 8` artifacts. It
  remains a repo-local exact-obstruction cross-check pending external review;
  it does not regenerate the incidence enumeration and does not turn the
  `n <= 8` result into a public theorem-style claim.

## Reproduce

```bash
python scripts/check_n8_survivors_smt.py --assert-clear \
  --write-artifact data/certificates/n8_survivors_smt.json
```
