/-!
# Tiny Certificate Shapes

These structures are lightweight Lean-side mirrors of the certificate kernels
that the Python tooling should eventually emit. They are intentionally
syntactic: they do not yet check Euclidean geometry or quotient arithmetic.
-/

namespace Erdos97

/-- A named quotient class of pair-distance expressions. -/
structure QuotientClass where
  name : String
deriving Repr, BEq

/-- A replayable equality path between two quotient classes. -/
structure EqualityPath where
  start : QuotientClass
  finish : QuotientClass
  reasons : List String
deriving Repr

/-- A same-endpoint equality path has equal endpoints by construction. -/
lemma EqualityPath.same_endpoint_mk (q : QuotientClass) (reasons : List String) :
    (EqualityPath.mk q q reasons).start =
      (EqualityPath.mk q q reasons).finish := by
  rfl

/-- A certificate shape for a strict self-edge contradiction. -/
structure SelfEdgeCertificate where
  className : QuotientClass
  equalityPath : EqualityPath
  strictReason : String
deriving Repr

/-- A directed strict edge between quotient classes. -/
structure StrictEdge where
  source : QuotientClass
  target : QuotientClass
  reason : String
deriving Repr

/-- A certificate shape for a strict directed cycle. -/
structure StrictCycleCertificate where
  edges : List StrictEdge
  cycleReason : String
deriving Repr

def StrictCycleCertificate.hasEdges (c : StrictCycleCertificate) : Prop :=
  Not (c.edges = [])

/-- `hasEdges` is exactly non-emptiness of the stored edge list. -/
lemma StrictCycleCertificate.hasEdges_iff (c : StrictCycleCertificate) :
    c.hasEdges ↔ Not (c.edges = []) := by
  rfl

/-- Package a nonempty edge-list proof as `hasEdges`. -/
lemma StrictCycleCertificate.hasEdges_of_ne_nil {c : StrictCycleCertificate}
    (h : Not (c.edges = [])) : c.hasEdges := by
  exact h

/-- Unpackage `hasEdges` as a nonempty edge-list proof. -/
lemma StrictCycleCertificate.ne_nil_of_hasEdges {c : StrictCycleCertificate}
    (h : c.hasEdges) : Not (c.edges = []) := by
  exact h

/-- A certificate whose edge list is headed by one edge has edges. -/
lemma StrictCycleCertificate.hasEdges_cons (edge : StrictEdge)
    (edges : List StrictEdge) (cycleReason : String) :
    (StrictCycleCertificate.mk (edge :: edges) cycleReason).hasEdges := by
  intro h
  cases h

/-- The empty strict-cycle certificate shape does not have edges. -/
lemma StrictCycleCertificate.not_hasEdges_nil (cycleReason : String) :
    Not ((StrictCycleCertificate.mk [] cycleReason).hasEdges) := by
  intro h
  exact h rfl

end Erdos97