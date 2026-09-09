# Provenance and scope

Research date: 8 September 2026.

The connected GitHub branch read resolved `main` to
`047d05149382e48b602b292df4b8fc9e2da560bb`, the merge of PR #942.
The work was conducted against that frontier. Read sources included the
repository's AGENTS/CONTRIBUTING instructions and current-state material
already retrieved in this conversation, and these pinned research notes:

- `incoming/unbounded-six-exception-family-2026-09-06/README.md`
- `incoming/six-arc-product-obstructions-2026-09-08/frontier.md`
- `incoming/bridge-continuation-2026-09-06/snapshots/rank-one-bridge-2026-09-06/README.md`
- `incoming/bridge-continuation-2026-09-06/snapshots/rank-two-layer-escape-2026-09-06/proofs.md`
- `incoming/bridge-continuation-2026-09-06/snapshots/bridge-closure-audit-2026-09-06/proofs.md`

The nine-point seed is the `m=2` member of the existing six-exception family.
It is not a new construction. The nine-point middle-cycle control adapts the
idea of the prior three-witness control by using two satellite parameters;
the precise four-witness configuration and certificate are generated here.
The off-carrier cap and the exhaustive seed-specific cap certificates were
constructed in this session. Novelty relative to published literature is not
asserted.

Methodological motivation was the OpenAI announcement supplied by the user:
https://openai.com/index/navier-stokes-solution/ . The page was re-read in this
session. No Navier–Stokes theorem is used as a premise of any result here,
and no claim is made that the resources of that project were replicated.

All exact data were generated locally from the delivered formulas. The
primary checker and the separate oracle were written in this research
session. They are different implementations, not external review or
independently commissioned mathematics.

Direct `git ls-remote https://github.com/davidiach/erdos97.git HEAD` failed
with `Could not resolve host: github.com`. Connected GitHub reads worked.
No repository branch, status, file, or PR was changed. Only the scoped local
commands recorded in `validation.json` were run; no repository-wide CI or
Lean verification is claimed.

The final bounded numerical search and its full output are in `exploratory/`.
Other optimizer-debug attempts and intermediate numerical circle scans are
not mathematical evidence and are not incorporated into the exact claims.
The final search's import paths and output destination were adjusted for
this self-contained delivery; its deterministic fixture and mathematical
search logic are unchanged. The adjusted script was rerun with OPENBLAS_NUM_THREADS=1; its complete
JSON output reproduced the retained final numerical report byte-for-byte.
