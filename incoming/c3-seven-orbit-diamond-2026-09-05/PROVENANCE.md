# Provenance and review dependencies

This packet continues the user-owned research repository `davidiach/erdos97`.
The read-verified PR #931 head was
`12ccc553a41fa08fc3100f3da84003343b73032a`. PR #934 independently records the
six-orbit own-side exclusion and was read to avoid presenting that result as
new. This session did not merge or rewrite either PR. A final read confirmed that
#931 was merged on 2026-09-05 at 21:10:52 UTC as
`e955c4513b44989c34bef22e5ae1cdd85b949c3b`. Its final source change
`f52996c56a661007c08e2c5b1a46723db4ca13ce` only renames the ambiguous
variable `l` to `ll` in the background model; that exact lint fix is included
in this packet's `core.py`. All model rows and certificates are unchanged.

## Copied background

Except for the explicitly retained final lint fix to `core.py`, the following bytes come from the preceding user-provided/downloaded
`erdos97_common_suppliers_2026_09_05.zip`, corresponding to
`incoming/c3-common-suppliers-2026-09-05/` in PR #931:

| Current file | Original file | Use here |
|---|---|---|
| `core.py` | `core.py` | Exact folded angle/ordinary-length models and integer certificate checks |
| `common_supplier_background.py` | `check_common_suppliers.py` | Primary radial brancher, interlacing predicate and exact positive controls |
| `common_supplier_certificates.json` | `certificates.json` | Complete 486-case background theorem, replayed rather than assumed |
| `common-supplier-background.md` | `README.md` | Written common-supplier geometric reduction; its relative file names refer to the original packet |
| `audit_expanded_model.py` | `audit_expanded_model.py` | Separate explicit-chord model representation, also instantiated at m=3 and m=7 |

The renamed background checker is imported as a library. Its original
standalone command-line paths are not the new packet entrypoint; use
`verify.py`, which supplies the renamed certificate path explicitly. The
background note's six-orbit claim remains background, not the new result.

## New work

New material comprises the elementary transitive gain/radius reductions;
18 transitive-radius certificates; 162 independently obtained diamond
certificates; the complete seven-orbit radial and phase coverage; 230 exact
seven-orbit angle certificates; the elementary binary proof stream;
separate C++ graph and phase checkers; the exact quadratic-field transitive
positive control; the current written proof, orchestration, tests and reports.

The elementary phase filters were adapted from the mathematical conventions
read in #934's `certificate.py`; the new C++ phase search and its explicit
equality-graph certificate replay were implemented in this session.

Numerical linear programming was used ONLY to discover candidate sparse
multipliers for the small linear contradiction systems. Before saving, every
candidate was rationalized and replayed by exact integer arithmetic. Static
and full proof verification require neither SciPy nor any solver. No
infeasibility status or approximate geometric sample is accepted as a proof.

No statement of novelty relative to published mathematics is made. The repo's
code licensing applies to copied code; research prose and data retain their
repository provenance. The new packet is supplied for review and integration,
not as an accepted source-of-truth status change.
