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

end Erdos97
