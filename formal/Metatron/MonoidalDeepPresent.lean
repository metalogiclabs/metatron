import Metatron.ProofRelevantOplax

namespace Metatron.MonoidalDeepPresent

open Metatron.FutureObservations
open Metatron.FixedPointReflection
open Metatron.DevelopmentalRelation
open Metatron.ProofRelevantOplax

universe u v w z

/-!
1. Parallel history.

A naive tensor on the existing flat certificate trace concatenates the left and
right traces. This preserves both histories, but it forgets that they were
independent/concurrent.
-/

def tensorCertified
    {A : Type u} {B : Type v} {C : Type w} {D : Type z}
    (f : CertifiedMap A B)
    (g : CertifiedMap C D) :
    CertifiedMap (A × C) (B × D) :=
  ⟨fun x => (f.map x.1, g.map x.2), f.trace ++ g.trace⟩

theorem parallelHistory_tensor
    {A : Type u} {B : Type v} {C : Type w} {D : Type z}
    (f : CertifiedMap A B)
    (g : CertifiedMap C D) :
    (tensorCertified f g).trace = f.trace ++ g.trace := by
  rfl

def flatF₁ : CertifiedMap Bool Bool := ⟨fun x => x, [1]⟩
def flatF₂ : CertifiedMap Bool Bool := ⟨fun x => x, [2]⟩
def flatG₁ : CertifiedMap Bool Bool := ⟨fun x => x, [3]⟩
def flatG₂ : CertifiedMap Bool Bool := ⟨fun x => x, [4]⟩

/--
Flat ordered traces do not satisfy monoidal interchange: the two serial/parallel
parenthesizations have the same state map but different certificate order.
-/
theorem flatTrace_interchange_fails :
    ccomp
      (tensorCertified flatF₁ flatF₂)
      (tensorCertified flatG₁ flatG₂) ≠
    tensorCertified
      (ccomp flatF₁ flatG₁)
      (ccomp flatF₂ flatG₂) := by
  intro h
  have ht := congrArg CertifiedMap.trace h
  change [1, 2, 3, 4] = [1, 3, 2, 4] at ht
  simp at ht

/-!
Concurrency-aware repair.

A layered trace records a list of causal stages; each stage contains events
that are concurrent for this experiment. Sequential composition appends stages.
Parallel composition aligns stages and unions the events inside each stage.
-/

structure LayeredMap (A : Type u) (B : Type v) where
  map : A → B
  stages : List (List Nat)

def latom
    {A : Type u} {B : Type v}
    (f : A → B)
    (cert : Nat) :
    LayeredMap A B :=
  ⟨f, [[cert]]⟩

def lcomp
    {A : Type u} {B : Type v} {C : Type w}
    (f : LayeredMap A B)
    (g : LayeredMap B C) :
    LayeredMap A C :=
  ⟨fun x => g.map (f.map x), f.stages ++ g.stages⟩

def parStages : List (List Nat) → List (List Nat) → List (List Nat)
  | [], ys => ys
  | xs, [] => xs
  | x :: xs, y :: ys => (x ++ y) :: parStages xs ys

def ltensor
    {A : Type u} {B : Type v} {C : Type w} {D : Type z}
    (f : LayeredMap A B)
    (g : LayeredMap C D) :
    LayeredMap (A × C) (B × D) :=
  ⟨fun x => (f.map x.1, g.map x.2), parStages f.stages g.stages⟩

/--
For synchronized one-step components, serial and parallel composition satisfy
the interchange law exactly once evidence records concurrency by layers.
-/
theorem serialParallel_interchange
    {A : Type u} {B : Type v} {C : Type w}
    {D : Type z} {E : Type} {F : Type}
    (f₁ : A → B) (g₁ : B → C)
    (f₂ : D → E) (g₂ : E → F)
    (a b c d : Nat) :
    lcomp
      (ltensor (latom f₁ a) (latom f₂ b))
      (ltensor (latom g₁ c) (latom g₂ d)) =
    ltensor
      (lcomp (latom f₁ a) (latom g₁ c))
      (lcomp (latom f₂ b) (latom g₂ d)) := by
  rfl

def asyncF₁ : LayeredMap Bool Bool :=
  ⟨fun x => x, [[1], [2]]⟩

def asyncF₂ : LayeredMap Bool Bool :=
  ⟨fun x => x, [[3]]⟩

def asyncG₁ : LayeredMap Bool Bool :=
  ⟨fun x => x, [[4]]⟩

def asyncG₂ : LayeredMap Bool Bool :=
  ⟨fun x => x, [[5], [6]]⟩

/--
Layered traces repair synchronized interchange, but not arbitrary asynchronous
composition. A total ordering into global stages is still too rigid when the
two sides have different causal depths.
-/
theorem layered_async_interchange_fails :
    lcomp
      (ltensor asyncF₁ asyncF₂)
      (ltensor asyncG₁ asyncG₂) ≠
    ltensor
      (lcomp asyncF₁ asyncG₁)
      (lcomp asyncF₂ asyncG₂) := by
  intro h
  have ht := congrArg LayeredMap.stages h
  change
    [[1, 3], [2], [4, 5], [6]] =
    [[1, 3], [2, 5], [4, 6]] at ht
  simp at ht

/-!
2. Feedback / causal re-entry.

At the proof-relevant relation level, a feedback wire is an existentially
hidden loop state together with the evidence that the same loop state returns.
-/

def FeedbackEvidence
    {A : Type u} {B : Type v} {S : Type w}
    (E : (A × S) → (B × S) → Type z)
    (a : A) (b : B) : Type (max w z) :=
  Σ s : S, E (a, s) (b, s)

def FeedbackSupport
    {A : Type u} {B : Type v} {S : Type w}
    (E : (A × S) → (B × S) → Type z)
    (a : A) (b : B) : Prop :=
  Nonempty (FeedbackEvidence E a b)

inductive LoopEvidence : (Bool × Bool) → (Bool × Bool) → Type
  | reenter : LoopEvidence (false, true) (true, true)

theorem causalReentry_feedback :
    FeedbackSupport LoopEvidence false true := by
  exact ⟨⟨true, LoopEvidence.reenter⟩⟩

theorem causalReentry_feedback_requires_live_loop :
    ∀ e : FeedbackEvidence LoopEvidence false true, e.1 = true := by
  intro e
  rcases e with ⟨s, h⟩
  cases h
  rfl

/-!
3. Deep present as a compatible cone over refinement views.
-/

structure DeepCone3
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (P0 P1 P2 : Test → Prop)
    (h01 : ∀ q, P0 q → P1 q)
    (h12 : ∀ q, P1 q → P2 q) where
  q2 : BehavioralQuotient act eval P2
  q1 : BehavioralQuotient act eval P1
  q0 : BehavioralQuotient act eval P0
  compat21 :
    forgetRefinement act eval P1 P2 h12 q2 = q1
  compat10 :
    forgetRefinement act eval P0 P1 h01 q1 = q0

def coneFromTop
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (P0 P1 P2 : Test → Prop)
    (h01 : ∀ q, P0 q → P1 q)
    (h12 : ∀ q, P1 q → P2 q)
    (q2 : BehavioralQuotient act eval P2) :
    DeepCone3 act eval P0 P1 P2 h01 h12 :=
  {
    q2 := q2
    q1 := forgetRefinement act eval P1 P2 h12 q2
    q0 := forgetRefinement act eval P0 P1 h01
      (forgetRefinement act eval P1 P2 h12 q2)
    compat21 := rfl
    compat10 := rfl
  }

theorem deepPresent_compatibleCone
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (P0 P1 P2 : Test → Prop)
    (h01 : ∀ q, P0 q → P1 q)
    (h12 : ∀ q, P1 q → P2 q)
    (q2 : BehavioralQuotient act eval P2) :
    ∃ cone : DeepCone3 act eval P0 P1 P2 h01 h12,
      cone.q2 = q2 := by
  exact ⟨coneFromTop act eval P0 P1 P2 h01 h12 q2, rfl⟩

theorem deepPresent_direct_projection
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (P0 P1 P2 : Test → Prop)
    (h01 : ∀ q, P0 q → P1 q)
    (h12 : ∀ q, P1 q → P2 q)
    (h02 : ∀ q, P0 q → P2 q)
    (q2 : BehavioralQuotient act eval P2) :
    forgetRefinement act eval P0 P2 h02 q2 =
      (coneFromTop act eval P0 P1 P2 h01 h12 q2).q0 := by
  exact congrFun
    (forgetRefinement_comp
      act eval P0 P1 P2 h01 h12 h02) q2

/-!
4. Ostiary admission as Galois closure.

Given an accessible observation family S, gamma(alpha(S)) is the maximal
observation family compatible with exactly the same indistinguishability
boundary. This is a genuine closure operator.
-/

def ObsClosure
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs) :
    ObservationFamily Obs :=
  fun o => Respects eval (Indistinguishable eval S) o

theorem obsClosure_extensive
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs) :
    ∀ o, S o → ObsClosure eval S o := by
  intro o ho x y hxy
  exact hxy o ho

theorem obsClosure_monotone
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S T : ObservationFamily Obs)
    (hST : ∀ o, S o → T o) :
    ∀ o, ObsClosure eval S o → ObsClosure eval T o := by
  intro o ho x y hxy
  apply ho x y
  intro s hs
  exact hxy s (hST s hs)

theorem obsClosure_idempotent
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs) :
    ObsClosure eval (ObsClosure eval S) = ObsClosure eval S := by
  funext o
  apply propext
  constructor
  · intro h x y hxy
    apply h x y
    intro p hp
    exact hp x y hxy
  · intro h
    exact obsClosure_extensive eval (ObsClosure eval S) o h

theorem obsClosure_preserves_boundary
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs) :
    Indistinguishable eval (ObsClosure eval S) =
      Indistinguishable eval S := by
  funext x y
  apply propext
  constructor
  · intro h o ho
    exact h o (obsClosure_extensive eval S o ho)
  · intro h o ho
    exact ho x y h

/--
The ostiary operator is extensive, monotone, idempotent, and boundary
preserving: it admits every observation compatible with the current boundary
without silently refining that boundary.
-/
theorem ostium_admission_closure
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs) :
    (∀ o, S o → ObsClosure eval S o) ∧
    ObsClosure eval (ObsClosure eval S) = ObsClosure eval S ∧
    Indistinguishable eval (ObsClosure eval S) =
      Indistinguishable eval S := by
  exact ⟨
    obsClosure_extensive eval S,
    obsClosure_idempotent eval S,
    obsClosure_preserves_boundary eval S
  ⟩

end Metatron.MonoidalDeepPresent
