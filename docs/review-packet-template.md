# Reviewer Packet Template

Status: template only; not mathematical evidence.

Use this template when packaging a finite-case artifact, fixed-pattern
certificate, local lemma candidate, or review-pending bridge result for
independent review. A reviewer packet should be printable, linkable, and
replayable, but it does not change claim status by itself.

Recommended target path:

```text
papers/<short-name>-reviewer-packet.md
```

If a PDF is produced later, generate it from the Markdown source and keep the
source as the version-controlled object.

## Packet Skeleton

```markdown
# <Artifact Name> Reviewer Packet

Status: <claim-neutral packet status>
Claim scope: <repo-local finite case | fixed order | fixed pattern | all-order fixed pattern | local lemma candidate | bridge target>
Source of truth: `STATE.md`, `RESULTS.md`, `docs/claims.md`, `metadata/erdos97.yaml`
Last reviewed: <YYYY-MM-DD or unreviewed>

## Non-Claims

- This packet does not prove Erdos Problem #97.
- This packet does not claim a counterexample.
- This packet does not update the official/global status.
- This packet does not promote review-pending artifacts without independent
  review and source-of-truth updates.

## Claim Being Reviewed

State the exact local claim, including all hypotheses and scope limits.

## Files To Inspect

- `<source document>`
- `<checker script>`
- `<certificate or JSON artifact>`
- `<tests, if any>`

## Reproduction Commands

```bash
<command 1>
<command 2>
```

## Expected Outputs

Record stable invariants rather than long terminal transcripts.

- status:
- count:
- exact certificate field:
- expected uncertainty field, if any:

## Mathematical Proof Sketch

Explain why the checker output implies the scoped claim. Keep informal
motivation separate from exact proof dependencies.

## Certificate Schema

Describe the trusted input fields, derived fields, and fields that are only
diagnostic.

## Independent Review Checklist

- Does the checker treat checked-in artifacts as input data?
- Are all cyclic-order, incidence, or algebraic hypotheses explicit?
- Does the proof use only necessary geometric conditions?
- Are symmetry reductions justified?
- Is every solver-backed step replayed or clearly marked as solver-trust risk?
- Are numerical values excluded from exact claim support unless certified?

## Known Weak Points

- <mathematical gap, if any>
- <implementation trust gap, if any>
- <literature or terminology risk, if any>

## Relation To Other Artifacts

Explain which artifacts this packet supersedes, supports, or leaves unchanged.

## Status-Update Rules

State exactly what review result would be required before any update to
`STATE.md`, `RESULTS.md`, `docs/claims.md`, or `metadata/erdos97.yaml`.
```

## Packet Rules

- Keep the first screen scoped: status, claim scope, source-of-truth files, and
  non-claims.
- Prefer short expected-output invariants over copied logs.
- Link every proof-facing statement to a checker, certificate, or existing
  source-of-truth document.
- Mark heuristic, numerical, sampled-window, fixed-order, fixed-pattern, and
  all-order fixed-pattern claims separately.
- Include negative review outcomes. A failed packet is useful if it prevents
  repeated work.

## First Good Targets

The highest-value initial packets are:

- `n=8` selected-witness finite-case artifact;
- `n=8` class `14` standalone obstruction;
- C19 all-order Kalmanson/Z3 certificate, with solver-trust boundary called
  out explicitly;
- n=9 vertex-circle T01/F09 and T10/F12 local lemma candidates;
- n=10 singleton-slice draft, as an audit packet only.
