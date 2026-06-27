# GPT-5.5 Pro Zip Batch Triage - 2026-06-27

Status: provenance and task-selection guidance only. This note does not change
the repository claims: no general proof and no counterexample are claimed, the
official/global status remains open, and the strongest promoted local finite
result remains the repo-local `n <= 8` selected-witness artifact.

## Batch Summary

Ten zip packets from the 2026-06-27 GPT-5.5 Pro run were reviewed. One packet
contained a non-duplicate, claim-safe artifact worth importing: the `n=9`
Kalmanson three-row core compression from
`erdos97_progress_packet(11).zip`. It was reshaped into repo-native checker,
artifact, docs, metadata, audit registration, tests, and merged in PR #861.

The remaining packets were not imported because they were duplicates of
existing artifacts, superseded by the new Kalmanson compression artifact, or
lower-value bounded/numerical route-pruning evidence.

## Decisions

| zip | Main content | Decision |
| --- | --- | --- |
| `erdos97_progress_2026_06_27.zip` | Row-sliced standalone `n=9` and `n=10` selected-witness vertex-circle replay, matching current counts. | Do not import. Duplicate/corroborating evidence for existing `n=9` and `n=10` selected-witness replay artifacts; packet wording would need status downgrades before any reuse. |
| `erdos97_progress_n9_packet.zip` | Localized support counting plus exact-four `n=9` frontier/core mining; reports 182 three-row and 2 four-row vertex-circle cores. | Do not import. Mostly superseded by existing mixed-rich support reduction/crosswalk and vertex-circle local-core artifacts. The 2 residual IDs `81` and `151` are already active bridge targets in later repo notes. |
| `erdos97_progress_packet(10).zip` | Independent `n=9` Kalmanson local-core catalog; all 184 terminal assignments have three-row Kalmanson cores and 56 labelled families. | Superseded by the stronger packet `(11)` import, which adds first-self-edge comparison, best-core search, stable digests, and repo-native checks. |
| `erdos97_progress_packet(11).zip` | Self-contained `n=9` Kalmanson core compressor; all 184 terminal assignments have optimally chosen three-row Kalmanson self-edge cores. | Imported and merged in PR #861 as `n9_kalmanson_three_row_core_compression`. Review-pending proof-mining evidence only. |
| `erdos97_progress_packet(12).zip` | Standalone `n=9` vertex-circle obstruction certificates and C++ `n=10` replay. | Do not import. Duplicates existing `n=9` obstruction-certificate and `n=10` singleton replay trail without adding a new claim boundary or certificate type. |
| `erdos97_progress_packet(13).zip` | Fresh `n=10` selected-witness second-source replay and an `n=10` four/five rich-support profile bound. | Do not import. The replay is duplicate evidence; the profile bound is already covered or strengthened by the repo's `n=10` mixed-rich capacity, q=2 rich vertex-circle, and q=1 rich vertex-circle artifacts. |
| `erdos97_progress_results_2026-06-27.zip` | Standalone `n=9` parallel-endpoint closure plus direct pruned search; two-ring exact-family scan. | Do not import. The parallel-endpoint closure is already represented by `n9_parallel_endpoint_closure`; the two-ring scan is restricted-family route-pruning evidence and not higher leverage than current bridge tasks. |
| `erdos97_results(1).zip` | Repo overlay for `n=9` parallel-endpoint regeneration and a bounded `n=10` initial-survivor Kalmanson probe. | Do not import. The `n=9` part duplicates the existing parallel-endpoint closure; the `n=10` probe is a bounded sample, not a stronger exhaustive artifact. |
| `erdos97_results.zip` | Standalone `n=9` independent vertex-circle replay and portable C++ `n=10` replay. | Do not import. Duplicate corroboration for existing finite replay artifacts; no new certificate shape. |
| `erdos97_results_2026-06-27.zip` | No-repo-import `n=9` verifier with local obstruction cores plus floating affine-regular sweep through `N <= 50`. | Do not import. The `n=9` verifier overlaps existing independent replays/local cores; the affine-regular sweep is numerical route-pruning evidence and should remain outside exact claim artifacts. |

## Imported Artifact

Merged PR #861 added:

```text
scripts/check_n9_kalmanson_three_row_core_compression.py
data/certificates/n9_kalmanson_three_row_core_compression.json
docs/n9-kalmanson-three-row-core-compression.md
tests/test_n9_kalmanson_three_row_core_compression.py
```

The checker regenerates the fixed-order `n=9` selected-witness frontier without
project imports or stored Kalmanson-certificate input. It then searches all
strict Kalmanson inequalities and all selected-row subsets in increasing
cardinality. The checked result is:

```text
terminal assignments: 184
first Kalmanson split: K1 = 150, K2 = 34
best Kalmanson minimal core size histogram: {"3": 184}
best Kalmanson kind/core split: K1 = 95, K2 = 89
best cyclic-dihedral core signatures: 56
compressed certificate sha256:
  55edb73475517dcc4e8413cdb84082957bc8426d2d67bd25cc28502ef3c124c0
```

The import deliberately keeps the scope at
`MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`: it is local-lemma
mining evidence, not a proof of `n=9`, not a bridge proof, not a proof of Erdos
Problem #97, and not a counterexample.

## Follow-up Guidance

Do not spend another pass importing duplicate `n=9`/`n=10` replay packets from
this batch unless they provide a new exact certificate type, an independent
review of a currently open gate, or a smaller human-auditable local lemma.

The best follow-up from the accepted packet is to classify the 56 three-row
Kalmanson core signatures into reusable local lemmas and look for bridge
hypotheses that force one of those cores without enumerating the full `n=9`
frontier.
