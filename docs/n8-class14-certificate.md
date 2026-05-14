# n=8 Class 14 Certificate Audit

Status: `REPO_LOCAL_EXACT_OBSTRUCTION_AUDIT_PENDING_EXTERNAL_REVIEW`.

This note isolates the most delicate `n=8` survivor-class obstruction from
`docs/n8-exact-survivors.md`. It is a focused audit of class `14` only. It does
not regenerate the `n=8` incidence enumeration, it does not check the other
survivor classes, and it does not turn the repo-local `n <= 8` result into a
public theorem-style claim.

## What The Checker Verifies

The verifier in `scripts/check_n8_class14_certificate.py` reads:

- `data/incidence/n8_reconstructed_15_survivors.json`;
- `certificates/n8_exact_analysis.json`.

It then rebuilds only the class `14` polynomial system in the standard gauge
`p_0=(0,0)`, `p_1=(1,0)`:

- 20 shared-witness `phi` edges;
- 40 perpendicular-bisector equations;
- 24 selected equal-distance equations.

The checker recomputes the lexicographic Groebner basis over `QQ` for those
64 equations and compares it with the 12-polynomial basis recorded in
`certificates/n8_exact_analysis.json`. It also checks that the recorded basis
reduces all rebuilt `PB+ED` equations to zero and is zero-dimensional.

From the triangular basis, the checker derives the four real branches:

```text
x_3 =  sqrt(3)/2, y_5 =  1
x_3 =  sqrt(3)/2, y_5 = -1
x_3 = -sqrt(3)/2, y_5 =  1
x_3 = -sqrt(3)/2, y_5 = -1
```

with the remaining coordinates forced by the linear basis relations. These four
derived branches are compared exactly with the four branches stored in the
certificate artifact.

Finally, each branch is checked by exact orientation signs. In every branch,
four labels form a strictly convex quadrilateral and the remaining four labels
are strict interior points of that quadrilateral. Therefore class `14` has no
strictly convex octagon realization under the checked `PB+ED` system.

## Reproduction

```bash
python scripts/check_n8_class14_certificate.py --check --json
python -m pytest tests/test_n8_class14_certificate.py -q -m artifact
```

The command is also included in the manual artifact audit command list in
`scripts/run_artifact_audit.py`.

## Scope Boundary

This is a small, reviewer-facing replay for one stored survivor class. It is not
SymPy-free, and it still depends on the checked-in survivor and certificate
artifacts as inputs. The result remains a repo-local exact-obstruction audit
pending external review; no general proof of Erdos Problem #97 and no
counterexample are claimed.
