import Erdos97.CertificateFormats

/-!
# T40 `n = 8` Certificate-Checker Sketch (docs target (6))

This is a marked proof-sketch shell for the `n = 8` survivor obstruction
certificate checker. It mirrors the Python pipeline
(`scripts/analyze_n8_exact_survivors.py`,
`scripts/check_n8_class14_certificate.py`) at the Lean level: the `n = 8`
incidence enumeration leaves a `15`-class survivor list (up to relabeling), and
each survivor is *killed* by exactly one of two certificate kinds:

* `cyclicNoncrossing` — no compatible strict-convex cyclic order exists (the
  same-color chord classes are forced to cross); equivalently the compatible
  cyclic-order count is `0`;
* `spanY2Zero` — the perpendicular-bisector + equal-distance polynomial system
  forces every `y`-coordinate (so the polygon area) into the rational span of
  the degeneracy generators, i.e. `y² = 0`, contradicting strict convexity.

It is NOT a proof of Erdos Problem #97 and claims no Lean proof of it.

## Honest status

* The certificate *format* and the *checker* (`Survivor.killed`,
  `survivorListKilled`) are defined and the structural lemmas about them are
  proved WITHOUT `sorry` (pure `Bool`/`List` combinatorics).
* The **soundness bridge** — that a `killed` certificate really implies the
  survivor has no strictly-convex Euclidean realization — is the genuine
  geometric/algebraic content and is STATED but left `sorry`
  (`killed_implies_no_realization`). It needs the squared-distance ideal
  membership / cyclic-order crossing facts that live in the Python checker and
  would need mathlib to formalise.
* The top-level `n8_all_survivors_killed_open` is STATED over an abstract
  survivor list and left `sorry`: feeding the actual 15 certificates is data the
  Python tooling owns, not reproved here.
-/

namespace Erdos97.Sketches.T40N8Certificate

open Erdos97

universe u

-- EVOLVE-BLOCK-START

/-- The two certificate kinds that kill an `n = 8` survivor class. -/
inductive KillKind where
  | cyclicNoncrossing
  | spanY2Zero
deriving Repr, BEq, DecidableEq

/--
A kill certificate for one survivor class.

* `classId` is the survivor's reconstructed class id (`0 … 14`).
* `kind` is which obstruction killed it.
* `compatibleOrderCount` mirrors the Python `compatible_cyclic_orders_count`;
  for a `cyclicNoncrossing` kill this must be `0`.
* `spanContainsY2` mirrors the `pb_linear_span_y2_zero` ideal-membership flag;
  for a `spanY2Zero` kill this must be `true`.
-/
structure KillCertificate where
  classId : Nat
  kind : KillKind
  compatibleOrderCount : Nat
  spanContainsY2 : Bool
deriving Repr

/--
Purely syntactic well-formedness of a kill certificate: the recorded data is
consistent with the claimed `kind`. This is a decidable `Bool` check and is the
finite part the Python artifact also enforces.
-/
def KillCertificate.checks (c : KillCertificate) : Bool :=
  match c.kind with
  | KillKind.cyclicNoncrossing => c.compatibleOrderCount == 0
  | KillKind.spanY2Zero => c.spanContainsY2

/-- A survivor class together with its claimed kill certificate. -/
structure Survivor where
  classId : Nat
  certificate : KillCertificate
  /-- The certificate must be for this class. -/
  cert_for_class : certificate.classId = classId
deriving Repr

/-- A survivor is *killed* when its certificate passes the syntactic checker. -/
def Survivor.killed (s : Survivor) : Prop :=
  s.certificate.checks = true

/-- `killed` is decidable (it is a `Bool` equality). -/
instance (s : Survivor) : Decidable s.killed := by
  unfold Survivor.killed
  infer_instance

/-- A whole survivor list is killed when every member is killed. -/
def survivorListKilled (xs : List Survivor) : Prop :=
  ∀ s ∈ xs, s.killed

/--
A `cyclicNoncrossing` certificate with the recorded zero count passes the
checker. (Pure `Bool`, no `sorry`.)
-/
theorem cyclic_kill_checks (classId : Nat) (h : True) :
    (KillCertificate.mk classId KillKind.cyclicNoncrossing 0 false).checks = true := by
  rfl

/--
A `spanY2Zero` certificate with the ideal-membership flag set passes the
checker. (Pure `Bool`, no `sorry`.)
-/
theorem span_kill_checks (classId : Nat) (count : Nat) :
    (KillCertificate.mk classId KillKind.spanY2Zero count true).checks = true := by
  rfl

/-- An empty survivor list is vacuously killed. -/
theorem survivorListKilled_nil : survivorListKilled [] := by
  intro s hs
  cases hs

/-- Cons of a killed head onto a killed tail stays killed. -/
theorem survivorListKilled_cons {s : Survivor} {xs : List Survivor}
    (hs : s.killed) (hxs : survivorListKilled xs) :
    survivorListKilled (s :: xs) := by
  intro t ht
  cases ht with
  | head => exact hs
  | tail _ ht' => exact hxs t ht'

/--
**Soundness bridge (genuinely open).**

If a survivor passes the certificate checker, then it has no strictly-convex
Euclidean realization. The conclusion is phrased against an abstract
`HasRealization : Survivor → Prop` standing for "there is a strictly convex
`8`-gon whose `i`-th equidistant `4`-set incidence row matches this class". The
honest geometric/algebraic content (cyclic-order crossing forces no order;
ideal membership forces `y² = 0`, i.e. collinearity, contradicting strict
convexity) is exactly what the Python checker computes over `QQ` and is NOT
reproved here.

Honest status: STATED, NOT PROVED (`sorry`).
-/
theorem killed_implies_no_realization
    (HasRealization : Survivor → Prop)
    (s : Survivor) (hkill : s.killed) :
    Not (HasRealization s) := by
  -- Requires the squared-distance ideal-membership / cyclic crossing facts.
  -- Not available without mathlib in this dependency-free pilot.
  sorry

/--
**Top-level `n = 8` survivor obstruction (target (6)), stated and left open.**

If the full survivor list is the `n = 8` reconstructed list and every class is
killed, then no class is realizable. This is the formal record of "the `n = 8`
case is closed by certificate checking"; the realizability bridge it rests on is
the open `killed_implies_no_realization`, so the whole statement is left `sorry`.

Honest status: STATED, NOT PROVED (`sorry`). This must NOT be read as a Lean
proof of the `n ≤ 8` result, which remains Python-only.
-/
theorem n8_all_survivors_killed_open
    (HasRealization : Survivor → Prop)
    (survivors : List Survivor)
    (hkilled : survivorListKilled survivors) :
    ∀ s ∈ survivors, Not (HasRealization s) := by
  -- Would follow from `killed_implies_no_realization` once that is closed.
  sorry

-- EVOLVE-BLOCK-END

end Erdos97.Sketches.T40N8Certificate
