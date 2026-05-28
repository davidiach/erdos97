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

/-- Equal quotient classes have equal names. -/
lemma QuotientClass.name_eq_of_eq {q r : QuotientClass} (h : q = r) :
    q.name = r.name := by
  cases h
  rfl

/-- Quotient classes are equal when their names agree. -/
lemma QuotientClass.eq_of_name_eq {q r : QuotientClass} (h : q.name = r.name) :
    q = r := by
  cases q
  cases r
  cases h
  rfl

/-- A replayable equality path between two quotient classes. -/
structure EqualityPath where
  start : QuotientClass
  finish : QuotientClass
  reasons : List String
deriving Repr

/-- Equal equality paths have equal starts. -/
lemma EqualityPath.start_eq_of_eq {path other : EqualityPath}
    (h : path = other) : path.start = other.start := by
  cases h
  rfl

/-- Equal equality paths have equal finishes. -/
lemma EqualityPath.finish_eq_of_eq {path other : EqualityPath}
    (h : path = other) : path.finish = other.finish := by
  cases h
  rfl

/-- Equal equality paths have equal replay-reason lists. -/
lemma EqualityPath.reasons_eq_of_eq {path other : EqualityPath}
    (h : path = other) : path.reasons = other.reasons := by
  cases h
  rfl

/-- A same-endpoint equality path has equal endpoints by construction. -/
lemma EqualityPath.same_endpoint_mk (q : QuotientClass) (reasons : List String) :
    (EqualityPath.mk q q reasons).start =
      (EqualityPath.mk q q reasons).finish := by
  rfl

/-- Reverse an equality-path endpoint equality. -/
lemma EqualityPath.finish_eq_start_of_start_eq_finish (path : EqualityPath)
    (h : path.start = path.finish) : path.finish = path.start := by
  exact h.symm

/-- A certificate shape for a strict self-edge contradiction. -/
structure SelfEdgeCertificate where
  className : QuotientClass
  equalityPath : EqualityPath
  strictReason : String
deriving Repr

/-- If both equality-path endpoints are the certificate class, the path is closed. -/
lemma SelfEdgeCertificate.path_start_eq_finish_of_endpoints
    (c : SelfEdgeCertificate)
    (hstart : c.equalityPath.start = c.className)
    (hfinish : c.equalityPath.finish = c.className) :
    c.equalityPath.start = c.equalityPath.finish := by
  exact hstart.trans hfinish.symm

/-- The reverse form of `path_start_eq_finish_of_endpoints`. -/
lemma SelfEdgeCertificate.path_finish_eq_start_of_endpoints
    (c : SelfEdgeCertificate)
    (hstart : c.equalityPath.start = c.className)
    (hfinish : c.equalityPath.finish = c.className) :
    c.equalityPath.finish = c.equalityPath.start := by
  exact (SelfEdgeCertificate.path_start_eq_finish_of_endpoints c hstart hfinish).symm

/-- A directed strict edge between quotient classes. -/
structure StrictEdge where
  source : QuotientClass
  target : QuotientClass
  reason : String
deriving Repr

/-- Equal strict edges have equal sources. -/
lemma StrictEdge.source_eq_of_eq {e f : StrictEdge} (h : e = f) :
    e.source = f.source := by
  cases h
  rfl

/-- Equal strict edges have equal targets. -/
lemma StrictEdge.target_eq_of_eq {e f : StrictEdge} (h : e = f) :
    e.target = f.target := by
  cases h
  rfl

/-- Equal strict edges have equal reasons. -/
lemma StrictEdge.reason_eq_of_eq {e f : StrictEdge} (h : e = f) :
    e.reason = f.reason := by
  cases h
  rfl

/-- If a strict edge source and target are the same class, it is a self-edge. -/
lemma StrictEdge.source_eq_target_of_eq_class (e : StrictEdge)
    {q : QuotientClass} (hsource : e.source = q) (htarget : e.target = q) :
    e.source = e.target := by
  exact hsource.trans htarget.symm

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

/-- A certificate with an explicitly empty edge list does not have edges. -/
lemma StrictCycleCertificate.not_hasEdges_of_edges_eq_nil
    {c : StrictCycleCertificate} (h : c.edges = []) : Not c.hasEdges := by
  intro hc
  exact hc h

/-- A certificate whose edge list is known to be a cons list satisfies `hasEdges`. -/
lemma StrictCycleCertificate.hasEdges_of_edges_eq_cons
    {c : StrictCycleCertificate} {edge : StrictEdge} {edges : List StrictEdge}
    (h : c.edges = edge :: edges) : c.hasEdges := by
  intro hnil
  have hcons_nil : edge :: edges = [] := h.symm.trans hnil
  cases hcons_nil

/-- A singleton strict-cycle edge list is nonempty. -/
lemma StrictCycleCertificate.hasEdges_singleton (edge : StrictEdge)
    (cycleReason : String) :
    (StrictCycleCertificate.mk [edge] cycleReason).hasEdges := by
  exact StrictCycleCertificate.hasEdges_cons edge [] cycleReason

end Erdos97
