# Provenance and claim scope

The current GitHub default branch was read through the connected GitHub tool.
It remained at `047d05149382e48b602b292df4b8fc9e2da560bb`, the merge of PR #942.
No repository files were written, no accepted status was changed, and no new
pull request was opened.

Relevant source reads at that baseline included:

- `docs/two-parabola-lens-closure.md` (Git blob
  `94022da5115f9005262c62c3977e244a12808e71`): the pre-existing opposite-chain
  scaffold, its square-sum identity, and bounded-grid scope. The new finite
  maximum argument closes precisely that scaffold; the mixed-row case remains
  outside the theorem. `parabola/proof.md` independently derives the moment
  identity and generalizes the carrier-cycle argument.

- `docs/turn-inequality-lemma.md` (Git blob
  `fbbe5daf8f7f8ea492d81cf62a689cdece9fefc2`): the scalar interval-turn
  inequalities checked in the new abstract metric controls.
- `docs/reciprocal-radial-budget.md` (Git blob
  `09537c5328e48e6dcd3a6353eb682a71a5cf6792`): local geometric budgets and the
  still-missing global obligation. No new proof of that obligation is claimed.
- `incoming/six-arc-product-obstructions-2026-09-08/README.md` and its
  `snapshot/proof_attempts/product_component.md`: the fixed product obstruction
  and its mixed-half-plane diamond argument. The new sampled cycle probe does
  not extend those results to all longer cycles.
- `src/erdos97/danzer18_doubling.py` and the preceding exact research archive:
  fixed Danzer source pools and historical numerical base information.

The original three delivered archives were extracted into a separate replay
workspace and were not modified. Their exact dependency chain is preserved by
`inputs/internal_support.zip`, copied byte-for-byte from the last delivered ZIP:

    SHA256 dfd032636763cf67c45338c22f24334eb9e5b17367a0de57b00eb074cdfea0e1

`previous.py` checks that hash and extracts temporary copies only. The archived
internal-support packet in turn contains the cap-closure input archive, which
contains the co-design mathematical input. Their original verifiers, manifests,
proofs, reports, and review qualifications remain in those archives.

New claim-bearing code and data are generated within this packet. The exact
metric matrices, reports, and proofs describe abstract metrics separately from
actual Euclidean configurations. Local coordinates in `circle_star_metric.json`
are reused in separate star charts, not assembled into one claimed polygon.
The explicit Gram and Cayley--Menger certificates show why that assembly fails.

A bounded external literature check did not establish novelty. In particular,
OpenAI's manuscript *Planar Point Sets with Many Unit Distances* was inspected
for its statement and construction outline; the portions inspected concern
unrestricted planar point sets, not strictly convex ones. No assertion or lemma
from that manuscript is used in the new proofs. The result here does not depend
on accepting that external manuscript or the earlier Navier--Stokes announcement.

All mathematical arguments remain review-pending. The final validation and
manifest bind the delivered code/data; passing tests does not independently
verify every geometric reduction or establish an unrestricted result.
