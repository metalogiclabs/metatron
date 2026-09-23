import Metatron.FinitePosetConnectivity

namespace Metatron.EarnedCommutation

open Metatron.CausalLinearization
open Metatron.CausalTraceQuotient
open Metatron.FinitePosetConnectivity
open Metatron.FutureObservations

universe u v

def EarnedPair
    {E : Type u} {Gen : Type} {State : Type v}
    (R : E → E → Prop)
    (act : Gen → State → State)
    (label : E → Gen)
    (a b : E) : Prop :=
  Incomparable R a b ∧
  Commute act (label a) (label b)

inductive EarnedTrace
    {E : Type u} {Gen : Type} {State : Type v}
    (R : E → E → Prop)
    (act : Gen → State → State)
    (label : E → Gen) :
    List E → List E → Prop
  | refl (xs : List E) :
      EarnedTrace R act label xs xs
  | swap
      (pre post : List E)
      (a b : E)
      (hearned : EarnedPair R act label a b) :
      EarnedTrace R act label
        (pre ++ a :: b :: post)
        (pre ++ b :: a :: post)
  | symm
      {xs ys : List E}
      (h : EarnedTrace R act label xs ys) :
      EarnedTrace R act label ys xs
  | trans
      {xs ys zs : List E}
      (hxy : EarnedTrace R act label xs ys)
      (hyz : EarnedTrace R act label ys zs) :
      EarnedTrace R act label xs zs

theorem earnedTrace_to_posetTrace
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    {xs ys : List E}
    (h : EarnedTrace R act label xs ys) :
    PosetTrace R xs ys := by
  induction h with
  | refl xs =>
      exact PosetTrace.refl _
  | swap pre post a b hearned =>
      exact PosetTrace.swap pre post a b hearned.1
  | symm h ih =>
      exact PosetTrace.symm ih
  | trans hxy hyz ihxy ihyz =>
      exact PosetTrace.trans ihxy ihyz

theorem earnedTrace_to_semanticTrace
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    {xs ys : List E}
    (h : EarnedTrace R act label xs ys) :
    TraceEq act (xs.map label) (ys.map label) := by
  induction h with
  | refl xs =>
      exact TraceEq.refl _
  | swap pre post a b hearned =>
      simpa [List.map_append] using
        TraceEq.swap (act := act)
          (pre.map label) (post.map label)
          (label a) (label b) hearned.2
  | symm h ih =>
      exact TraceEq.symm ih
  | trans hxy hyz ihxy ihyz =>
      exact TraceEq.trans ihxy ihyz

theorem earnedTrace_preserves_run
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    {xs ys : List E}
    (h : EarnedTrace R act label xs ys) :
    ∀ s,
      run act (xs.map label) s =
        run act (ys.map label) s := by
  have hsemantic :
      TraceEq act (xs.map label) (ys.map label) :=
    earnedTrace_to_semanticTrace act label h
  exact traceEq_preserves_run act hsemantic

def SameEarnedComponent
    {E : Type u} {Gen : Type} {State : Type v}
    (R : E → E → Prop)
    (act : Gen → State → State)
    (label : E → Gen)
    (xs ys : List E) : Prop :=
  EarnedTrace R act label xs ys

theorem sameEarnedComponent_semantically_equal
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    {xs ys : List E}
    (h : SameEarnedComponent R act label xs ys) :
    ∀ s,
      run act (xs.map label) s =
        run act (ys.map label) s :=
  earnedTrace_preserves_run act label h

def CoversAllIncomparables
    {E : Type u} {Gen : Type} {State : Type v}
    (R : E → E → Prop)
    (act : Gen → State → State)
    (label : E → Gen) : Prop :=
  ∀ a b,
    Incomparable R a b →
      EarnedPair R act label a b

theorem all_incomparables_earned_traceConnected
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    (hall : CoversAllIncomparables R act label)
    {xs ys : List E}
    (hposet : PosetTrace R xs ys) :
    EarnedTrace R act label xs ys := by
  induction hposet with
  | refl xs =>
      exact EarnedTrace.refl _
  | swap pre post a b hinc =>
      exact EarnedTrace.swap pre post a b (hall a b hinc)
  | symm h ih =>
      exact EarnedTrace.symm ih
  | trans hxy hyz ihxy ihyz =>
      exact EarnedTrace.trans ihxy ihyz

theorem all_topological_sorts_one_earned_component
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    (hall : CoversAllIncomparables R act label)
    {xs ys : List E}
    (hx : Topo R xs)
    (hy : Topo R ys)
    (hp : xs.Perm ys) :
    EarnedTrace R act label xs ys := by
  have hposet :
      PosetTrace R xs ys :=
    all_topological_sorts_traceConnected hx hy hp
  exact all_incomparables_earned_traceConnected
    act label hall hposet

theorem all_topological_sorts_equal_if_all_incomparables_earned
    {E : Type u} {Gen : Type} {State : Type v}
    {R : E → E → Prop}
    (act : Gen → State → State)
    (label : E → Gen)
    (hall : CoversAllIncomparables R act label)
    {xs ys : List E}
    (hx : Topo R xs)
    (hy : Topo R ys)
    (hp : xs.Perm ys) :
    ∀ s,
      run act (xs.map label) s =
        run act (ys.map label) s := by
  have htrace :
      EarnedTrace R act label xs ys :=
    all_topological_sorts_one_earned_component
      act label hall hx hy hp
  exact earnedTrace_preserves_run act label htrace

/--
A pairwise commutation certificate is *warranted* only by exact execution
equality. This predicate is the discovery target for finite anonymous actions.
-/
def ExactWarrantedCommute
    {Gen : Type} {State : Type v}
    (act : Gen → State → State)
    (g h : Gen) : Prop :=
  ∀ s, act h (act g s) = act g (act h s)

theorem exactWarrantedCommute_iff_commute
    {Gen : Type} {State : Type v}
    (act : Gen → State → State)
    (g h : Gen) :
    ExactWarrantedCommute act g h ↔
      Commute act g h := by
  rfl

end Metatron.EarnedCommutation
