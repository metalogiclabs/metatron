import Metatron.EarnedCommutation

namespace Metatron.BehavioralCommutation

open Metatron.FutureObservations
open Metatron.CausalTraceQuotient
open Metatron.CausalLinearization

universe u v w z

def RelCommute
    {State : Type u} {Step : Type v}
    (R : Relation State)
    (act : Step → State → State)
    (g h : Step) : Prop :=
  ∀ s, R (act h (act g s)) (act g (act h s))

theorem stepClosed_run
    {State : Type u} {Step : Type v}
    (act : Step → State → State)
    (R : Relation State)
    (hclosed : StepClosed act R)
    {x y : State}
    (hxy : R x y)
    (steps : List Step) :
    R (run act steps x) (run act steps y) := by
  induction steps generalizing x y with
  | nil =>
      exact hxy
  | cons s ss ih =>
      exact ih (hclosed x y hxy s)

theorem behavioral_adjacent_swap_preserves
    {State : Type u} {Step : Type v}
    (act : Step → State → State)
    (R : Relation State)
    (hclosed : StepClosed act R)
    (pre post : List Step)
    (g h : Step)
    (hcomm : RelCommute R act g h)
    (s : State) :
    R
      (run act (pre ++ g :: h :: post) s)
      (run act (pre ++ h :: g :: post) s) := by
  rw [run_append act pre (g :: h :: post) s]
  rw [run_append act pre (h :: g :: post) s]
  simp only [run]
  exact stepClosed_run act R hclosed
    (hcomm (run act pre s)) post

inductive BehavioralTrace
    {State : Type u} {Step : Type v}
    (R : Relation State)
    (act : Step → State → State) :
    List Step → List Step → Prop
  | refl (xs : List Step) :
      BehavioralTrace R act xs xs
  | swap
      (pre post : List Step)
      (g h : Step)
      (hcomm : RelCommute R act g h) :
      BehavioralTrace R act
        (pre ++ g :: h :: post)
        (pre ++ h :: g :: post)
  | symm
      {xs ys : List Step}
      (h : BehavioralTrace R act xs ys) :
      BehavioralTrace R act ys xs
  | trans
      {xs ys zs : List Step}
      (hxy : BehavioralTrace R act xs ys)
      (hyz : BehavioralTrace R act ys zs) :
      BehavioralTrace R act xs zs

theorem behavioralTrace_preserves
    {State : Type u} {Step : Type v}
    (act : Step → State → State)
    (R : Relation State)
    (hrefl : ∀ x, R x x)
    (hsymm : ∀ {x y}, R x y → R y x)
    (htrans : ∀ {x y z'}, R x y → R y z' → R x z')
    (hclosed : StepClosed act R)
    {xs ys : List Step}
    (htrace : BehavioralTrace R act xs ys) :
    ∀ s, R (run act xs s) (run act ys s) := by
  induction htrace with
  | refl xs =>
      intro s
      exact hrefl _
  | swap pre post g h hcomm =>
      intro s
      exact behavioral_adjacent_swap_preserves
        act R hclosed pre post g h hcomm s
  | symm h ih =>
      intro s
      exact hsymm (ih s)
  | trans hxy hyz ihxy ihyz =>
      intro s
      exact htrans (ihxy s) (ihyz s)

def FutureCommute
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (g h : Step) : Prop :=
  RelCommute (FutureEq act test Protected) act g h

theorem futureBehavioralTrace_preserves
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    {xs ys : List Step}
    (htrace :
      BehavioralTrace
        (FutureEq act test Protected) act xs ys) :
    ∀ s,
      FutureEq act test Protected
        (run act xs s)
        (run act ys s) := by
  exact behavioralTrace_preserves
    act (FutureEq act test Protected)
    (futureEq_refl act test Protected)
    (fun h => futureEq_symm act test Protected h)
    (fun hxy hyz => futureEq_trans act test Protected hxy hyz)
    (futureEq_stepClosed act test Protected)
    htrace

theorem futureBehavioralTrace_preserves_protected_observation
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    {xs ys : List Step}
    (htrace :
      BehavioralTrace
        (FutureEq act test Protected) act xs ys)
    (s : State)
    (q : Test)
    (hq : Protected q) :
    test q (run act xs s) =
      test q (run act ys s) := by
  have hfuture :=
    futureBehavioralTrace_preserves
      act test Protected htrace s
  exact futureEq_immediate act test Protected
    _ _ hfuture q hq

/-! Strict quotient gain fixture. -/

structure QState where
  hidden : Bool
  observed : Bool
  deriving DecidableEq, Repr

inductive QStep where
  | hiddenSetFalse
  | hiddenToggle
  | observedSetFalse
  | observedToggle
  deriving DecidableEq, Repr

def qAct : QStep → QState → QState
  | .hiddenSetFalse, s => { s with hidden := false }
  | .hiddenToggle, s => { s with hidden := !s.hidden }
  | .observedSetFalse, s => { s with observed := false }
  | .observedToggle, s => { s with observed := !s.observed }

inductive QTest where
  | observed
  deriving DecidableEq, Repr

def qTest : QTest → QState → Bool
  | .observed, s => s.observed

def qProtected : QTest → Prop
  | .observed => True

theorem qRun_preserves_observed_equality
    {x y : QState}
    (hxy : x.observed = y.observed)
    (steps : List QStep) :
    (run qAct steps x).observed =
      (run qAct steps y).observed := by
  induction steps generalizing x y with
  | nil =>
      exact hxy
  | cons s ss ih =>
      apply ih
      cases s <;> simp [qAct, hxy]

theorem qFutureEq_iff_observed_eq
    (x y : QState) :
    FutureEq qAct qTest qProtected x y ↔
      x.observed = y.observed := by
  constructor
  · intro h
    simpa [qTest, qProtected, run] using
      h [] QTest.observed True.intro
  · intro h steps q hq
    cases q
    exact qRun_preserves_observed_equality h steps

theorem hidden_pair_not_exact_commute :
    ¬ Commute qAct
      QStep.hiddenSetFalse
      QStep.hiddenToggle := by
  intro h
  have heq := h ⟨false, false⟩
  have hhidden := congrArg QState.hidden heq
  simp [qAct] at hhidden

theorem hidden_pair_futureCommute :
    FutureCommute qAct qTest qProtected
      QStep.hiddenSetFalse
      QStep.hiddenToggle := by
  intro s
  apply (qFutureEq_iff_observed_eq _ _).2
  cases s
  rfl

theorem observed_pair_not_futureCommute :
    ¬ FutureCommute qAct qTest qProtected
      QStep.observedSetFalse
      QStep.observedToggle := by
  intro h
  have hq := h ⟨false, false⟩
  have hobs := (qFutureEq_iff_observed_eq _ _).1 hq
  simp [qAct] at hobs

theorem behavioral_commutation_strictly_extends_exact :
    (¬ Commute qAct
      QStep.hiddenSetFalse
      QStep.hiddenToggle) ∧
    FutureCommute qAct qTest qProtected
      QStep.hiddenSetFalse
      QStep.hiddenToggle := by
  exact ⟨hidden_pair_not_exact_commute, hidden_pair_futureCommute⟩

end Metatron.BehavioralCommutation
