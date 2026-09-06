# Incoming research packets

Status: navigation and retention policy only; no general proof or counterexample
is claimed. Presence in `main` means the material is retained, not that a pending
mathematical claim has been accepted. [Current state](../STATE.md).

## Structured review packets

All six packets below remain review-pending under their own stated hypotheses.
Retain their original reports and pinned source files. Run commands from the
packet directory; see its README for prerequisites, full replays, and limitations.
No packet in this table is declared superseded by another here.

| Packet | Purpose and current scope | Check entry point |
|---|---|---|
| [Radius descent / n11](radius-descent-n11-2026-09-05/README.md) | Restricted radius arguments and finite-search evidence | `python validate.py`; `python replay.py --quick --sanitize` |
| [Side-cap extension](side-cap-extension-2026-09-05/README.md) | Restricted radius-window argument and controls | `python check_side_cap_extension.py --check` |
| [Long-radius cubic](long-radius-cubic-2026-09-05/README.md) | Restricted C3 algebraic and geometric controls | `python check_long_radius.py --check` |
| [Six own-side orbits](c3-own-side-six-orbits-2026-09-05/README.md) | Restricted own-side search and certificates | `python all_systems.py --check`; `python certificate.py --check` |
| [Seven own-side orbits](c3-own-side-seven-orbits-2026-09-05/README.md) | Restricted search and independent replay | `python verify.py --check`; `python replay.py --quick --check` |
| [Common suppliers](c3-common-suppliers-2026-09-05/README.md) | Restricted supplier/radius conditions | `python check_common_suppliers.py --check` |

## Historical imports

| Packet | Retention and successor |
|---|---|
| [May 3 archive](archive-output-2026-05-03/README.md) | Historical source/output bytes; use the repo-native n9 checker identified in its README for current replay |
| [ChatGPT matrix runs](chatgpt-runs/audit.md) | Conversation provenance; the audit distinguishes usable statements and cautions |
| [Prompt 0](prompt0-runs/audit.md) | Conversation provenance; retain the audit's scope limits |
| [Prompt 2](prompt2-runs/audit.md) | Conversation provenance; retain the audit's scope limits |
| [Prompt 3](prompt3-runs/audit.md) | Conversation provenance; retain the audit's scope limits |

Conversation directories have no blanket acceptance or universal replay command.
Follow the evidence cited by their audits. No additional successor is assigned
by this inventory.

## Lifecycle

1. Add a README with purpose, provenance, claim scope, prerequisites, and checks.
2. Retain source bytes and existing manifests; link them rather than duplicating
   their fields into a second registry.
3. Record review decisions and scope limits in the packet. Integrate reusable
   code into `src/` only with preserved command compatibility and validation.
4. If superseded, add an explicit forward pointer; do not silently remove the
   original evidence. Update this inventory when packet directories change.
5. A stronger accepted claim follows the [status-transition contract](../docs/status-transitions.md).

Future sessions belong in bounded dated reports; see
[maintenance conventions](../docs/repository-maintenance.md).
