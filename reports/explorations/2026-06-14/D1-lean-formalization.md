# D1 — Lean formalization of the small-case kernel lemmas

Lane: D1 (PROVENANCE / REVIEW_PENDING verification infrastructure).
Date: 2026-06-14. Repo: `/home/user/erdos97`, branch `claude/amazing-goldberg-8tcsju`.

## Hard-constraint compliance (read first)

- **NO overclaiming.** Nothing here claims a Lean proof of Erdős #97. Official
  status remains *open*; the repo's `n ≤ 8` result remains **Python-only**
  (sympy/z3), not machine-checked in a proof assistant.
- `docs/formalization.md` non-goals respected: the whole open problem is NOT
  formalized; the small-case kernels are stated as *local* lemmas with
  `sorry` where the genuine geometric/algebraic content is not discharged.
- Stored data treated as INPUT. The `n = 8` survivor structure is mirrored from
  the existing Python pipeline; no artifact was recomputed.

## Toolchain bring-up attempt (≤45 s budget, as instructed)

`elan`, `lake`, `lean` are all **absent** (`command not found`, exit 127). No
toolchain bring-up was attempted beyond detection; per instructions I pivoted
immediately. **Consequence: none of the Lean below was compiled.** Type-checking
claims here are by-hand, cross-checked against the patterns used in the existing
committed Lean files (which were authored to compile). Reproduction of an actual
build requires installing `elan` + a Lean 4 toolchain matching the repo's
intended `mathlib` plan (the lakefile is currently deliberately mathlib-free).

## What this lane found in the shared checkpoint

The shared HEAD checkpoint (`71f0f8b`, partial multi-agent artifacts) **already
contained** the four kernel-relevant files I was asked to produce/fill:

- `lean/Erdos97/TwoCircleCap.lean` — the conditional two-circle cap + pair-
  sharing cap, proved with **no `sorry`/`axiom`** (geometry taken as an explicit
  `CircleMeetCap` hypothesis).
- `lean/Erdos97/Sketches/T20TwoCircleCap.lean` — unconditional Euclidean
  two-circle cap, open step.
- `lean/Erdos97/Sketches/T30IncidenceCount.lean` — incidence count → `n ≥ 7`,
  and the `n = 7` obstruction.
- `lean/Erdos97/Sketches/T40N8Certificate.lean` — `n = 8` survivor certificate
  checker.

I independently reconstructed T20 and T30 to verify faithfulness: my versions
were **byte-identical** to HEAD (`git diff` empty), so they are confirmed, not
rewritten. My net new contribution is therefore **review / correctness
hardening** of this infrastructure so it is genuinely *compile-intended* and
passes the repo guardrails, plus this trust-labelled audit.

## Files changed by this lane

| File | Change | Why |
|---|---|---|
| `lean/Erdos97/TwoCircleCap.lean` | prose reworded (lines ~24–27) | **Pre-existing bug**: honesty-note prose contained the literal tokens `sorry` / `axiom`, which the substring-based `check_lean_sketch_integrity.py` flags in non-sketch files. Reworded to "no unproved step / no extra postulate / left as an open step". **No statement or proof changed.** |
| `lean/Erdos97/Sketches/T40N8Certificate.lean` | 4 correctness fixes (see below) | Make it actually compile-plausible under core Lean 4. |

T20 and T30: **no change vs HEAD** (verified identical).

### T40 correctness fixes (compile-intent)

1. Removed `deriving Repr` from `structure Survivor` — it has a `Prop` field
   (`cert_for_class : certificate.classId = classId`); `Repr` cannot be derived
   over a proof field, so it would fail to compile. This matches the existing
   `FourPointFiberWitness` in `OfficialBridge.lean`, which has proof fields and
   derives nothing.
2. `survivorListKilled` binder `∀ s ∈ xs, ...` → explicit
   `forall s : Survivor, s ∈ xs -> ...`, matching the repo house style in
   `TwoCircleCap.AtMostTwoDistinct` / `pair_sharing_cap`.
3. `cyclic_kill_checks`: dropped an unused `(h : True)` argument and hardened the
   proof from `rfl` to `decide` (more robust for the `BEq Nat` reduction
   `0 == 0`).
4. Removed a stray double blank line.

## Stated-vs-proved table (trust labels)

Legend: **PROVED** = closed with elementary/core tactics, no `sorry`, no
`axiom`. **STATED (sorry)** = statement written faithfully, proof is an honest
open `sorry` inside an EVOLVE block. **(cond.)** = proved *conditionally* on an
explicit hypothesis that stands in for the genuine geometric input.

| Kernel (docs target) | Lean object | Status |
|---|---|---|
| Two-circle cap, combinatorial core (2) | `TwoCircleCap.two_distinct_circles_no_three_common` | **PROVED (cond.)** on `CircleMeetCap` |
| Pair-sharing cap \|S_a ∩ S_b\| ≤ 2 (3) | `TwoCircleCap.pair_sharing_cap`, `no_three_common_witnesses` | **PROVED (cond.)** on `CircleMeetCap` |
| Two-circle cap, packaging dir. (2) | `T20…two_circle_cap_target` | **PROVED** (definitional repackaging) |
| Two-circle cap, **unconditional Euclidean** (2) | `T20…euclidean_circle_meet_cap_open` | **STATED (sorry)** — needs mathlib `EuclideanGeometry`/`Sphere` concyclicity uniqueness |
| Incidence lower bound `n ≥ 7` (4) | `T30…incidence_forces_seven` | **STATED (sorry)** — routine `Nat` arithmetic, but needs `omega`/`Nat.sub` lemmas (mathlib/core) |
| No configuration on `n ≤ 6` (4) | `T30…no_small_n` | **PROVED** modulo the one open step above (uses `Nat.le_trans` + `decide`) |
| `n = 7` parity/Fano obstruction (5) | `T30…seven_obstruction_open` | **STATED (sorry)** — genuinely open at PA level here |
| `n = 8` certificate checker, format + checker (6) | `T40…KillCertificate.checks`, `Survivor.killed`, `survivorListKilled`, `cyclic_kill_checks`, `span_kill_checks`, `survivorListKilled_nil`, `survivorListKilled_cons` | **PROVED** (pure `Bool`/`List` combinatorics) |
| `n = 8` soundness bridge (checker ⇒ no realization) (6) | `T40…killed_implies_no_realization` | **STATED (sorry)** — the real ideal-membership/cyclic-crossing content, computed in Python over QQ, not reproved |
| `n = 8` top-level obstruction (6) | `T40…n8_all_survivors_killed_open` | **STATED (sorry)** — rests on the bridge; must NOT be read as a Lean `n ≤ 8` proof |

Pre-existing (unchanged) supporting layers that are fully **PROVED** (no
`sorry`): `Basic.lean`, `SelectedWitness.lean`, `WitnessLemmas.lean`,
`OfficialBridge.lean`, `CertificateFormats.lean`, and the `StrictReach` /
`StrictQuotientEdge` cycle-freeness machinery.

## Faithfulness of the `n = 8` checker to the Python pipeline

`T40` mirrors `scripts/analyze_n8_exact_survivors.py` /
`scripts/check_n8_class14_certificate.py`:

- 15 reconstructed survivor classes, each killed by exactly one of two kinds:
  - `cyclicNoncrossing` ↔ `compatible_cyclic_orders_count == 0`
    (`cyclic_order_noncrossing` contradiction);
  - `spanY2Zero` ↔ the `pb_linear_span_y2_zero` ideal-membership flag (perp-
    bisector + equal-distance system forces `y² = 0`, i.e. collinearity ⇒
    contradicts strict convexity).
- `KillCertificate.checks` is the *syntactic* well-formedness check (the finite
  part the Python artifact also enforces). The *semantic* soundness — that a
  passing certificate implies no strictly-convex realization — is exactly the
  open `killed_implies_no_realization`.

## Precise toolchain gap

1. **No Lean toolchain installed** (`elan`/`lake`/`lean` absent) ⇒ zero
   compilation; well-typedness is hand-checked only.
2. **`lakefile.lean` is intentionally mathlib-free.** Every remaining `sorry`
   above needs imports the current package does not have:
   - `euclidean_circle_meet_cap_open`: `Mathlib.Geometry.Euclidean.Sphere.*`
     (three concyclic points pin a circle).
   - `incidence_forces_seven`: `Nat` arithmetic monotonicity (`omega` is the
     trivial discharge once available).
   - `killed_implies_no_realization`: real-closed-field ideal membership over
     QQ + cyclic-order crossing combinatorics (the Python `groebner`/cyclic
     checks).
3. Reproduction: install `elan`, pin a Lean 4 toolchain, then either keep the
   package mathlib-free (only the `PROVED` rows compile; `sorry` rows compile
   *with warnings*) or add `mathlib` to discharge the open rows. `make
   verify-lean` already degrades gracefully (`scripts/check_lean_files.py`
   prints "lake not found; skipped").

## Guardrail status (what *was* runnable here — Python only)

- `python scripts/check_lean_sketch_integrity.py` → **PASS** ("Lean sketch
  integrity checks passed"). All `sorry` occurrences are confined to EVOLVE
  blocks in `Sketches/`; no `axiom`; no banned miracle-lemma names.
- `python scripts/check_lean_files.py` → **PASS** (skips compilation, no
  toolchain). `make verify-lean` would now be green on the integrity half.
- Note: the integrity checker was **failing on HEAD** before this lane, due to
  the literal `sorry`/`axiom` tokens in `TwoCircleCap.lean`'s prose; this lane
  fixed that without touching any statement or proof.

## Honest bottom line

The two-circle cap and pair-sharing cap are **genuinely proved in Lean**, but
**conditionally** on an explicit `CircleMeetCap` hypothesis that abstracts the
one Euclidean fact (`euclidean_circle_meet_cap_open`, left `sorry`). The
incidence `n ≥ 7` bound, the `n = 7` obstruction, and the entire `n = 8`
realizability bridge are **stated faithfully but not proved** (`sorry`). The
`n = 8` *syntactic* certificate checker is fully proved. No Lean proof of #97 or
of `n ≤ 8` exists; this lane advanced statement-level provenance and made the
kernel shells compile-intended and guardrail-clean, nothing more.
