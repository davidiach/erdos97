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

namespace EqualityPath

/-- If both endpoints of an equality path are a common class, the path is a loop. -/
theorem endpoints_eq_of_common_class {path : EqualityPath} {q : QuotientClass}
    (hstart : path.start = q) (hfinish : path.finish = q) :
    path.start = path.finish := by
  rw [hstart, hfinish]

end EqualityPath

/-- A certificate shape for a strict self-edge contradiction. -/
structure SelfEdgeCertificate where
  className : QuotientClass
  equalityPath : EqualityPath
  strictReason : String
deriving Repr

namespace SelfEdgeCertificate

/-- A self-edge certificate whose equality path returns to its class has equal endpoints. -/
theorem equalityPath_endpoints_eq {c : SelfEdgeCertificate}
    (hstart : c.equalityPath.start = c.className)
    (hfinish : c.equalityPath.finish = c.className) :
    c.equalityPath.start = c.equalityPath.finish := by
  exact EqualityPath.endpoints_eq_of_common_class hstart hfinish

end SelfEdgeCertificate

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

namespace StrictCycleCertificate

/-- The `hasEdges` predicate is exactly nonemptiness of the edge list. -/
theorem edges_ne_nil (c : StrictCycleCertificate) (h : c.hasEdges) :
    Not (c.edges = []) :=
  h

/-- A certificate whose edge list is known to be a cons list has edges. -/
theorem hasEdges_of_edges_eq_cons {c : StrictCycleCertificate}
    {e : StrictEdge} {rest : List StrictEdge} (h : c.edges = e :: rest) :
    c.hasEdges := by
  intro hempty
  rw [h] at hempty
  cases hempty

/-- A cons edge list is a nonempty strict-cycle certificate. -/
theorem hasEdges_cons (e : StrictEdge) (rest : List StrictEdge)
    (cycleReason : String) :
    ({ edges := e :: rest, cycleReason := cycleReason } : StrictCycleCertificate).hasEdges := by
  exact hasEdges_of_edges_eq_cons rfl

/-- An empty edge list does not satisfy `hasEdges`. -/
theorem not_hasEdges_empty (cycleReason : String) :
    Not (({ edges := [], cycleReason := cycleReason } : StrictCycleCertificate).hasEdges) := by
  intro h
  exact h rfl

/-- `hasEdges` is equivalent to decomposing the edge list as a head and tail. -/
theorem hasEdges_iff_exists_cons (c : StrictCycleCertificate) :
    c.hasEdges <->
      Exists fun e : StrictEdge => Exists fun rest : List StrictEdge => c.edges = e :: rest := by
  constructor
  · intro h
    cases c with
    | mk edges cycleReason =>
      cases edges with
      | nil =>
        exact False.elim (h rfl)
      | cons e rest =>
        exact Exists.intro e (Exists.intro rest rfl)
  · intro h
    cases h with
    | intro e hrest =>
      cases hrest with
      | intro rest heq =>
        exact hasEdges_of_edges_eq_cons heq

end StrictCycleCertificate

end Erdos97
