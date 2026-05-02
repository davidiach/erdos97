# Repository roadmap

## Phase 1: reliable public baseline

- Publish the exact target and claim policy.
- Include the current search engine and verifier.
- Include the current failed B12 near-miss.
- Include survived lemmas and failed ideas.
- Add issue templates for future work.

## Phase 2: stronger finite search

- Enumerate `n=7` Fano labelings up to dihedral cyclic order.
- Encode forced perpendicularities.
- Add exact/interval infeasibility checks for small fixed patterns.
- Maintain the checked `n=8` incidence-completeness and exact-obstruction
  artifacts.
- Use the `n=8` pipeline as the model for the first `n=9` frontier attempt,
  starting from the corrected profile-excess / capacity-deficit ledger in
  `docs/n9-base-apex-frontier.md`.

## Phase 3: numerical exploration

- Run margin sweeps for B12 and B20.
- Add cluster-avoidance diagnostics.
- Add continuation from known 3-neighbor examples.

## Phase 4: exactification

Only attempt exactification for robust candidates with tiny residual and nondegenerate convexity margins.

For finite obstruction work, exactification may also start from a complete
incidence survivor list, as in the checked `n=8` pipeline.

## Near-term review push

- Treat `docs/n8-geometric-proof.md` as the main human-readable small-case proof
  target, pending independent review.
- Build a minimal independent checker for the checked `n=8` incidence and exact
  obstruction data.
- Isolate the class `14` PB+ED and strict-interior certificate into a small
  standalone verifier.
- Extend the minimum-radius short-chord idea only if it grows into
  radius-inequality propagation or cyclic-order search; by itself it does not
  kill `C19_skew`.
- Keep `n >= 9` exploration separate from the repo-local `n <= 8` artifact.
