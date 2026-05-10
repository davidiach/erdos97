# GPT Pro output triage, 2026-05-10

Status: provenance and task-selection guidance only; not mathematical evidence.

This note reviews three GPT Pro reconstructions supplied in chat. It does not
promote any claim, alter the source-of-truth status, or replace the checked
finite-case and exact-obstruction artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Decision

Only the first output is worth preserving as a possible benchmark/provenance
thread. The second and third outputs should not be added as standalone
research notes.

## Output 1: Desargues plus matching attack

Triage: salvageable as `NUMERICAL_EVIDENCE` / `FAILED_APPROACH` provenance.

What to keep:

- The Fishburn--Reeds-style 20-point seed, its 30 selected equal-distance
  edges, and the observation that the 3-regular graph is the Desargues graph.
- The perfect-matching upgrade formulation: add ten non-edges and ask whether
  the resulting 4-regular graph can be realized at one common distance.
- The verified numerical diagnostics from the pasted coordinates:
  - seed selected squared-distance agreement with
    `D = 3.8757564588765137` is within about `6.4e-12`;
  - seed minimum consecutive turn determinant is about `1.52e-7`;
  - the bottleneck squared distance `d(15,2)^2` is about
    `3.7936489633873993`, roughly `2.12%` short in squared-distance terms;
  - the later matching-upgrade coordinates have selected squared-length range
    `[3.8507069914391727, 3.89934239029103]`;
  - the minimax midpoint is `3.8750246908651014`, with worst relative
    squared-length error about `0.00627549535`.

How to add if this branch is revived:

- Add a compact machine-readable artifact under `data/runs/`, for example
  `data/runs/desargues_k3_matching_upgrade.json`, containing the seed points,
  selected triples, the tested matchings, optimized points, and the diagnostic
  values above.
- Add a short companion doc, for example
  `docs/desargues-matching-upgrade.md`, labelled as a strict global-radius
  attack and not a candidate counterexample.
- Keep the claim scope explicit: this branch is stronger than Erdos #97 because
  it requires one global distance for all 40 selected edges. A plateau or
  obstruction here does not prove the variable-radius problem, and a numerical
  near-miss is not a counterexample.

Recommended current action: do not spend a main research PR on this unless the
goal is benchmark hygiene or negative-control documentation. The current bridge
and finite-case review tasks have higher value.

## Output 2: Danzer quantifier move

Triage: logically correct but not original enough to add.

The reduction is simply:

```text
Danzer arbitrary-k statement => Danzer k=4 => a counterexample to Erdos #97.
```

This is already covered by the literature-risk material. The official page
records the all-`k` Danzer report as unverified and presumably mistaken, so
this should remain `LITERATURE_RISK`, not a proof program.

Recommended current action: no new file. Keep `docs/literature-risk.md` and
`metadata/erdos97.yaml` as the source of truth for this point.

## Output 3: selected-witness synthesis

Triage: not salvageable as written.

The selected-witness reduction itself is valid, but the output mixes valid
repo-local facts with speculative or vague lemmas. In particular:

- it describes `docs/n8-geometric-proof.md` as though it were the incidence
  enumeration certificate, but that file is a separate proof-note draft using
  a base-apex/isoceles-triangle count;
- its alternation, cap, and extraction claims are not stated at the precision
  required by `docs/claims.md`;
- the proposed large-to-8 extraction lemma is open and should not be presented
  as the only remaining routine step.

Recommended current action: ignore as a source document. When mining
selected-witness ideas, use the current ledgers instead:

- `docs/claims.md`
- `docs/n8-incidence-enumeration.md`
- `docs/n8-exact-survivors.md`
- `docs/review-priorities.md`
- `docs/codex-backlog.md`

## Prompt-experiment note

Running this prompt more times is unlikely to produce a new proof ingredient
unless the prompt is changed to request machine-checkable artifacts, exact
failure modes, or concrete local lemma packets.

The only non-obvious reusable item in this batch is the Desargues-plus-matching
numerical benchmark. If prompting is repeated, the highest-yield version would
ask for:

1. a JSON artifact with coordinates, selected rows, and exact diagnostic code;
2. a list of claims sorted by repo trust label;
3. an explicit diff against `STATE.md`, `RESULTS.md`, and `docs/claims.md`;
4. no theorem-style prose unless backed by a verifier command.
