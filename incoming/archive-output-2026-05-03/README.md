# Archive Output 2026-05-03

Status: raw incoming archive bundle; not source-of-truth project status.

These files came from `C:\Users\User\Desktop\code\erd archive\outputs\data\1\2`.
They are retained so the n=9 review package has local provenance. The repo-native
entrypoint is now `scripts/check_n9_vertex_circle_exhaustive.py`; use that
script rather than editing or relying on these raw files.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.
The official/global status remains falsifiable/open. The current source-of-truth
metadata still records the reviewed local strongest result as the repo-local
machine-checked selected-witness `n <= 8` artifact.

## Archive files reviewed

| File | SHA256 | Initial disposition |
| --- | --- | --- |
| `erdos97_n9_certificates.json` | `6cee9ed564aa290c56a6739ad260bd7489043eb9ae44e2c745fbb49233df7f0a` | Raw n=9 Kalmanson/Farkas certificate bundle; preserved for review. |
| `erdos97_n9_result (1).md` | `2bd32358212e36017cad5b7b9163f619470241447c1c0b5be69b622fa45f7d5a` | Raw n=9 report variant; not imported as a tracked artifact because it uses theorem-style language before independent review. |
| `erdos97_n9_result.md` | `acef027ba26f63a650dfe47155b322b3ebd72bd8d552ca76a8aad6a400989652` | Raw n=9 report variant; not imported as a tracked artifact because it uses theorem-style language before independent review. |
| `erdos97_result (1).md` | `e30673ff9ac2e2037a3adff4fdd47404625b0cbcf22e53ddbc8a313e1e014f` | Raw mixed attempt report; not imported as a tracked artifact because the C13 material is already covered by existing Kalmanson notes. |
| `erdos97_result.md` | `ee9c38ed2b0dd24fe5f7cd4a952d3f99a97b8ad07f4f4832253053053c28b171` | Raw mixed attempt report; not imported as a tracked artifact because the C13 material is already covered by existing Kalmanson notes. |
| `erdos97_result (2).md` | `c9962bbc1f05939d46889fc0249894cf6562d687430156b2003b8f9af3a30ebe` | Raw alternating two-radius / concave decagon report; distilled into `docs/two-orbit-radius-propagation.md` and checker tests rather than imported verbatim. |
| `n9_vertex_circle_crosscheck_output.txt` | `51333a65d8b80a3f7c2c99ccbdc39d3eb9818f4b0d58927a004884b013785c20` | Reproduced by the repo-native n=9 vertex-circle checker. |
| `n9_vertex_circle_exhaustive.py` | `49c98e01cab3d0292ebb0fdb37b9d4ea46dccd0cd595ce7fb25a799a674bfb61` | Raw standalone n=9 exhaustive script; refactored into `src/erdos97/n9_vertex_circle_exhaustive.py`. |
| `n9_vertex_circle_exhaustive_output.txt` | `7043c238fac825bd5706c53351705f45dcd133309cc56c777e01380ea837430a` | Reproduced by the repo-native n=9 vertex-circle checker. |
| `verify_erdos97_n9 (1).py` | `b2c40c030f96611dc6a6ae8262cfb2f78db4e2515c42115d5b526cc4b3771ee5` | Raw 102-certificate verifier variant; preserved for review. |
| `verify_erdos97_n9.py` | `1aa05135de87771adc64c26e1b2e89239388e7583dfa2da50950fddeb8ca677e` | Raw 184-pattern/16-orbit verifier variant; preserved for review. |
| `verify_erdos97_n9_output.txt` | `b57e51c297c2fd6bda0f101100fab6f21458576a71c4164c86242f0ce73cf137` | Reproduced by the raw verifier variant; not the canonical repo check. |

## Review notes

The n=9 material has three related but distinct computational stories:

- a vertex-circle exhaustive search whose cross-check leaves 184 full
  assignments before the vertex-circle filter and kills all 184;
- a 184-labelled-pattern / 16-dihedral-class Kalmanson-gap verifier;
- a 102-row0-reflection-representative Kalmanson/Farkas certificate verifier.

The repo-native integration currently promotes only the first item as a
review-pending executable artifact. The other two are kept here because their
count conventions need a separate audit before they should influence canonical
results text.
