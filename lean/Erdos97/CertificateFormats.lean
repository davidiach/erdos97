/-!
# Tiny Certificate Shapes

These structures are lightweight Lean-side mirrors of the certificate kernels
that the Python tooling should eventually emit. They are intentionally
syntactic: they do not yet check Euclidean geometry or quotient arithmetic.
-/

namespace Erdos97

universe u v

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

/-- A one-or-more-step reachability relation for strict quotient edges. -/
inductive StrictReach {α : Type u} (gt : α -> α -> Prop) : α -> α -> Prop where
  | single {a b : α} : gt a b -> StrictReach gt a b
  | step {a b c : α} : gt a b -> StrictReach gt b c -> StrictReach gt a c

namespace StrictReach

/-- Collapse a nonempty strict path using transitivity. -/
theorem collapse {α : Type u} {gt : α -> α -> Prop}
    (htrans : forall {a b c : α}, gt a b -> gt b c -> gt a c) :
    forall {a b : α}, StrictReach gt a b -> gt a b := by
  intro a b h
  induction h with
  | single hstep => exact hstep
  | step hstep _ ih => exact htrans hstep ih

/-- A transitive, irreflexive strict relation has no nonempty cycle. -/
theorem not_cycle {α : Type u} {gt : α -> α -> Prop}
    (hirrefl : forall a : α, Not (gt a a))
    (htrans : forall {a b c : α}, gt a b -> gt b c -> gt a c)
    {a : α} :
    Not (StrictReach gt a a) := by
  intro h
  exact hirrefl a (collapse htrans h)

/-- Push a strict path through a map that preserves strict edges. -/
theorem map {α : Type u} {β : Type v} {r : α -> α -> Prop}
    {s : β -> β -> Prop} (f : α -> β)
    (hmap : forall {a b : α}, r a b -> s (f a) (f b)) :
    forall {a b : α}, StrictReach r a b -> StrictReach s (f a) (f b) := by
  intro a b h
  induction h with
  | single hstep => exact StrictReach.single (hmap hstep)
  | step hstep _ ih => exact StrictReach.step (hmap hstep) ih

/--
If every abstract edge strictly decreases a value in an irreflexive transitive
relation, then the abstract graph has no nonempty directed cycle.
-/
theorem no_mapped_cycle {α : Type u} {β : Type v} {r : α -> α -> Prop}
    {gt : β -> β -> Prop} {value : α -> β}
    (hmap : forall {a b : α}, r a b -> gt (value a) (value b))
    (hirrefl : forall a : β, Not (gt a a))
    (htrans : forall {a b c : β}, gt a b -> gt b c -> gt a c)
    {a : α} :
    Not (StrictReach r a a) := by
  intro h
  have hvalue : StrictReach gt (value a) (value a) := map value hmap h
  exact not_cycle hirrefl htrans hvalue

end StrictReach

namespace StrictEdge

/-- A strict edge is sound when it really decreases the assigned value. -/
def Sound {α : Type u} (value : QuotientClass -> α)
    (gt : α -> α -> Prop) (e : StrictEdge) : Prop :=
  gt (value e.source) (value e.target)

/-- A sound strict edge cannot connect classes with equal assigned values. -/
theorem no_between_equal_values {α : Type u} {value : QuotientClass -> α}
    {gt : α -> α -> Prop}
    (hirrefl : forall a : α, Not (gt a a)) {e : StrictEdge}
    (hsound : Sound value gt e)
    (heq : value e.source = value e.target) : False := by
  rw [heq] at hsound
  exact hirrefl (value e.target) hsound

/-- A sound strict edge cannot be a loop. -/
theorem no_self {α : Type u} {value : QuotientClass -> α}
    {gt : α -> α -> Prop}
    (hirrefl : forall a : α, Not (gt a a)) {e : StrictEdge}
    (hsound : Sound value gt e) (hloop : e.source = e.target) : False := by
  have heq : value e.source = value e.target := congrArg value hloop
  exact no_between_equal_values hirrefl hsound heq

end StrictEdge

/-- The quotient graph relation generated by an allowed set of strict edges. -/
def StrictQuotientEdge (edgeAllowed : StrictEdge -> Prop)
    (source target : QuotientClass) : Prop :=
  Exists fun e : StrictEdge =>
    And (edgeAllowed e) (And (e.source = source) (e.target = target))

namespace StrictQuotientEdge

/-- Sound concrete strict edges induce sound quotient-graph edges. -/
theorem sound {α : Type u} {value : QuotientClass -> α}
    {gt : α -> α -> Prop} {edgeAllowed : StrictEdge -> Prop}
    (hsound : forall e : StrictEdge, edgeAllowed e -> StrictEdge.Sound value gt e) :
    forall {source target : QuotientClass},
      StrictQuotientEdge edgeAllowed source target ->
        gt (value source) (value target) := by
  intro source target h
  cases h with
  | intro e hrest =>
      cases hrest with
      | intro hedge hends =>
          cases hends with
          | intro hsource htarget =>
              have hs : gt (value e.source) (value e.target) := hsound e hedge
              rw [← hsource, ← htarget]
              exact hs

/-- A sound strict quotient graph cannot contain a loop. -/
theorem no_loop {α : Type u} {value : QuotientClass -> α}
    {gt : α -> α -> Prop} {edgeAllowed : StrictEdge -> Prop}
    (hsound : forall e : StrictEdge, edgeAllowed e -> StrictEdge.Sound value gt e)
    (hirrefl : forall a : α, Not (gt a a)) {c : QuotientClass}
    (hloop : StrictQuotientEdge edgeAllowed c c) : False := by
  have hstrict : gt (value c) (value c) := sound hsound hloop
  exact hirrefl (value c) hstrict

/-- A sound strict quotient graph cannot contain a directed cycle. -/
theorem no_cycle {α : Type u} {value : QuotientClass -> α}
    {gt : α -> α -> Prop} {edgeAllowed : StrictEdge -> Prop}
    (hsound : forall e : StrictEdge, edgeAllowed e -> StrictEdge.Sound value gt e)
    (hirrefl : forall a : α, Not (gt a a))
    (htrans : forall {a b c : α}, gt a b -> gt b c -> gt a c)
    {c : QuotientClass} :
    Not (StrictReach (StrictQuotientEdge edgeAllowed) c c) := by
  exact StrictReach.no_mapped_cycle (StrictQuotientEdge.sound hsound)
    hirrefl htrans

end StrictQuotientEdge

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
