# Second-pass audit of corrected synthesis

Date: 2026-04-29

## Scope

This audit checks `corrected_synthesis.md` for overclaiming and for reuse of
the known false claims from the ten prompt outputs.

## Findings

No complete proof or counterexample is claimed. The artifact correctly treats
the full problem as open.

The n <= 6 proof uses the common-witness cap and exception-map argument, not
the unsupported middle-witness uniqueness claim. This is the reliable route
from Outputs 8 and 9.

Output 10 is explicitly rejected. The tangent-support lemma is not reused.

The alpha/3 exterior-angle descent is explicitly rejected. The retained local
angle statement is the weaker alpha/2-style bound and the obtuse-middle lemma.

The false chord claim from Output 2 is explicitly corrected.

The parabola case is marked as a model-case theorem, not as evidence for the
general theorem. The convex-position caveat is included.

The minimal-counterexample lemma is stated as a dependency/fragile-cover
structure, not as a contradiction.

The diameter and octagon examples are marked as corrected/rejected search
notes, not as proof ingredients.

## Residual risks

The tangent-support counterexample is included as an explicit coordinate
example, but the artifact does not independently certify its convexity by exact
symbolic determinant inequalities. It is used only to reject a lemma already
known false, not as a positive theorem.

The parabola model-case proof should receive a standalone formal write-up if it
is promoted into `docs/claims.md` or `RESULTS.md`.

The fragile-cover lemma is summarized from the earlier local repair. If this
artifact is moved into canonical docs, it should link to or include that proof
in full.

## Audit verdict

The synthesis is safe as a reviewed research artifact. It should not be
presented as a proof of the full problem.
