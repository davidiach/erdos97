# n=8 Residual Certificate Audit

Status: `REPO_LOCAL_EXACT_OBSTRUCTION_AUDIT_PENDING_EXTERNAL_REVIEW`.

This note isolates the remaining `n=8` survivor-class certificates not covered
by the SymPy-free independent recheck or the focused class `14` audit. It covers
classes `3`, `4`, and `5` only. It does not regenerate the `n=8` incidence
enumeration, does not check class `14`, and does not turn the repo-local
`n <= 8` finite-case result into a public theorem-style claim.

## What The Checker Verifies

The verifier in `scripts/check_n8_residual_certificates.py` reads the checked-in
survivor rows from `data/incidence/n8_reconstructed_15_survivors.json` and the
stored certificate notes from `certificates/n8_exact_analysis.json`.

It then rebuilds the required perpendicular-bisector equations for the three
classes and verifies the exact substitution chains. Audit output schema
`n8_residual_certificate_audit_v2` includes a Boolean ideal-membership record
for every substitution used downstream. In all three classes the first-stage
relations give `p_2=(x2,y2)` and `p_3=(x2,-y2)`, so distinct polygon vertices
`p_2 != p_3` justify the nonzero branch `y2 != 0`:

- Class `3`: the first PB stage forces `x3=x2`, `y3=-y2`, and
  `y2*(2*x2-1)=0`. The checker now adjoins an inverse variable with
  `inv_y2*y2-1=0`, rather than cancelling `y2` by hand, and reduces
  `2*x2-1` to zero in that saturated ideal. A second saturated basis built
  from the actual first- and second-stage PB equations derives
  `4*y2^2-3`, `2*x4+1`, and `y4-y2`. Only then are those relations
  substituted into the final stage, which forces `p_7=p_0` and hence
  duplicate vertices.
- Class `4`: the shared first PB stage plus the class-specific PB equations
  force the collinearity determinant for labels `2,3,4`; its first-stage
  substitutions use the same explicit `y2 != 0` saturation certificate.
- Class `5`: `PB(01->23)` mechanically derives `x3=x2` and `y3=-y2`.
  On the `y2 != 0` branch, the actual `PB(23->46)` dot and midpoint equations
  then derive `y4-y6` and `x4+x6-2*x2`, justifying the remaining recorded
  substitutions. The recomputed substituted Groebner basis and the stored
  generating set are still checked to define the same ideal and to contain
  `y2`. Independently, the checker now computes the Groebner basis of all
  reconstructed class-`5` PB equations together with `inv_y2*y2-1` and
  verifies that it is the unit ideal. Thus the contradiction no longer relies
  on accepting the substitution chain as an unverified preprocessing step.

## Reproduction

```bash
python scripts/check_n8_residual_certificates.py --check --json
python -m pytest tests/test_n8_residual_certificates.py -q -m artifact
```

The command is also included in the manual artifact audit command list in
`scripts/run_artifact_audit.py`.

## Scope Boundary

This is a focused replay of stored exact certificates for three survivor
classes. It still uses SymPy Groebner reductions and depends on the checked-in
survivor and certificate artifacts as inputs. The result remains a repo-local
exact-obstruction audit pending external review; no general proof of Erdos
Problem #97 and no counterexample are claimed.
