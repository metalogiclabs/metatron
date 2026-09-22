namespace Metatron.FutureObservations

universe u v w z

abbrev ObservationFamily (Obs : Type v) := Obs → Prop
abbrev Relation (State : Type u) := State → State → Prop

/-- States are indistinguishable by a declared family of observations. -/
def Indistinguishable
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs) : Relation State :=
  fun x y => ∀ o, S o → eval o x = eval o y

/-- An observation respects an equivalence candidate when it is constant on it. -/
def Respects
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (R : Relation State)
    (o : Obs) : Prop :=
  ∀ x y, R x y → eval o x = eval o y

def Compatible
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (R : Relation State)
    (S : ObservationFamily Obs) : Prop :=
  ∀ o, S o → Respects eval R o

/--
The observation/equivalence Galois law.
A relation lies inside the kernel induced by S iff every observation in S
respects that relation.
-/
theorem futureObservations_galois
    {State : Type u} {Obs : Type v} {Val : Type w}
    (eval : Obs → State → Val)
    (S : ObservationFamily Obs)
    (R : Relation State) :
    (∀ x y, R x y → Indistinguishable eval S x y) ↔
      Compatible eval R S := by
  constructor
  · intro h o ho x y hxy
    exact h x y hxy o ho
  · intro h x y hxy o ho
    exact h o ho x y hxy

/-- Execute a finite continuation path left-to-right. -/
def run
    {State : Type u} {Step : Type v}
    (act : Step → State → State) : List Step → State → State
  | [], x => x
  | s :: ss, x => run act ss (act s x)

def ImmediateAgreement
    {State : Type u} {Test : Type v} {Val : Type w}
    (test : Test → State → Val)
    (Protected : Test → Prop) : Relation State :=
  fun x y => ∀ q, Protected q → test q x = test q y

/--
Continuation-safe equivalence: no finite lawful continuation followed by a
protected test can distinguish the two states.
-/
def FutureEq
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) : Relation State :=
  fun x y =>
    ∀ steps q, Protected q →
      test q (run act steps x) = test q (run act steps y)

def StepClosed
    {State : Type u} {Step : Type v}
    (act : Step → State → State)
    (R : Relation State) : Prop :=
  ∀ x y, R x y → ∀ s, R (act s x) (act s y)

def Admissible
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (R : Relation State) : Prop :=
  (∀ x y, R x y → ImmediateAgreement test Protected x y) ∧
    StepClosed act R

theorem futureEq_refl
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (x : State) :
    FutureEq act test Protected x x := by
  intro steps q hq
  rfl

theorem futureEq_symm
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    {x y : State}
    (h : FutureEq act test Protected x y) :
    FutureEq act test Protected y x := by
  intro steps q hq
  exact (h steps q hq).symm

theorem futureEq_trans
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    {x y z' : State}
    (hxy : FutureEq act test Protected x y)
    (hyz : FutureEq act test Protected y z') :
    FutureEq act test Protected x z' := by
  intro steps q hq
  exact (hxy steps q hq).trans (hyz steps q hq)

theorem futureEq_immediate
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :
    ∀ x y, FutureEq act test Protected x y →
      ImmediateAgreement test Protected x y := by
  intro x y hxy q hq
  simpa [run] using hxy [] q hq

theorem futureEq_stepClosed
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :
    StepClosed act (FutureEq act test Protected) := by
  intro x y hxy s steps q hq
  simpa [run] using hxy (s :: steps) q hq

theorem futureEq_admissible
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :
    Admissible act test Protected (FutureEq act test Protected) := by
  constructor
  · exact futureEq_immediate act test Protected
  · exact futureEq_stepClosed act test Protected

/--
Every relation that agrees on protected tests and is preserved by one-step
continuations is contained in FutureEq. Hence FutureEq is the greatest such
relation.
-/
theorem admissible_le_futureEq
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (R : Relation State)
    (hR : Admissible act test Protected R) :
    ∀ x y, R x y → FutureEq act test Protected x y := by
  intro x y hxy steps
  induction steps generalizing x y with
  | nil =>
      intro q hq
      exact hR.1 x y hxy q hq
  | cons s ss ih =>
      intro q hq
      exact ih (x := act s x) (y := act s y) (hR.2 x y hxy s) q hq

def GreatestAdmissible
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (R : Relation State) : Prop :=
  Admissible act test Protected R ∧
    ∀ S, Admissible act test Protected S →
      ∀ x y, S x y → R x y

/-- FutureEq is the greatest fixed-point style continuation-safe relation. -/
theorem continuationSafe_eq_gfp
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :
    GreatestAdmissible act test Protected (FutureEq act test Protected) := by
  constructor
  · exact futureEq_admissible act test Protected
  · intro R hR x y hxy
    exact admissible_le_futureEq act test Protected R hR x y hxy

def futureSetoid
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) : Setoid State where
  r := FutureEq act test Protected
  iseqv := {
    refl := futureEq_refl act test Protected
    symm := futureEq_symm act test Protected
    trans := futureEq_trans act test Protected
  }

abbrev BehavioralQuotient
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :=
  Quotient (futureSetoid act test Protected)

def quotientMap
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (x : State) :
    BehavioralQuotient act test Protected :=
  Quotient.mk (futureSetoid act test Protected) x

def factor
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    {Y : Type}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (f : State → Y)
    (hf : ∀ x y, FutureEq act test Protected x y → f x = f y) :
    BehavioralQuotient act test Protected → Y :=
  Quotient.lift f (by
    intro x y hxy
    exact hf x y hxy)

/--
State-map universal property of the continuation-safe behavioral quotient.
This is deliberately weaker than a full CLC transport reflection: it proves
factorization of maps constant on FutureEq classes, not yet factorization of
backward test transformers, protected lifts, or certificates.
-/
theorem behavioralQuotient_reflection
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    {Y : Type}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (f : State → Y)
    (hf : ∀ x y, FutureEq act test Protected x y → f x = f y) :
    ∃ g : BehavioralQuotient act test Protected → Y,
      (∀ x, g (quotientMap act test Protected x) = f x) ∧
      ∀ h : BehavioralQuotient act test Protected → Y,
        (∀ x, h (quotientMap act test Protected x) = f x) → h = g := by
  refine ⟨factor act test Protected f hf, ?_, ?_⟩
  · intro x
    rfl
  · intro h hh
    funext qx
    exact Quotient.inductionOn qx (fun x => by
      simpa [factor, quotientMap] using hh x)

end Metatron.FutureObservations
