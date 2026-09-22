import Metatron.FutureObservations

namespace Metatron.FixedPointReflection

open Metatron.FutureObservations

universe u v w z

structure FutureObservation (Step : Type v) (Test : Type w) where
  steps : List Step
  query : Test

def futureObservationEval
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (o : FutureObservation Step Test)
    (x : State) : Val :=
  test o.query (run act o.steps x)

/--
The least observation family generated from protected tests by lawful
one-step prependObsing. This is the concrete μL used in this theorem package.
-/
inductive MuObs
    {Step : Type v} {Test : Type w}
    (Protected : Test → Prop) :
    FutureObservation Step Test → Prop
  | base (q : Test) (hq : Protected q) :
      MuObs Protected ⟨[], q⟩
  | step (s : Step) (o : FutureObservation Step Test)
      (ho : MuObs Protected o) :
      MuObs Protected ⟨s :: o.steps, o.query⟩

def prependObs
    {Step : Type v} {Test : Type w}
    (s : Step) (o : FutureObservation Step Test) :
    FutureObservation Step Test :=
  ⟨s :: o.steps, o.query⟩

/-- One application of the future-observation generator L. -/
def LOp
    {Step : Type v} {Test : Type w}
    (Protected : Test → Prop)
    (S : FutureObservation Step Test → Prop)
    (o : FutureObservation Step Test) : Prop :=
  (o.steps = [] ∧ Protected o.query) ∨
    ∃ s prior, S prior ∧ o = prependObs s prior

theorem muObs_all
    {Step : Type v} {Test : Type w}
    (Protected : Test → Prop)
    (steps : List Step) (q : Test)
    (hq : Protected q) :
    MuObs Protected ⟨steps, q⟩ := by
  induction steps with
  | nil =>
      exact MuObs.base q hq
  | cons s ss ih =>
      exact MuObs.step s ⟨ss, q⟩ ih

theorem muObs_protected
    {Step : Type v} {Test : Type w}
    {Protected : Test → Prop}
    {o : FutureObservation Step Test}
    (ho : MuObs Protected o) :
    Protected o.query := by
  induction ho with
  | base q hq =>
      exact hq
  | step s o ho ih =>
      exact ih

/-- μL is a fixed point of the one-step observation generator. -/
theorem muObs_fixed
    {Step : Type v} {Test : Type w}
    (Protected : Test → Prop)
    (o : FutureObservation Step Test) :
    LOp Protected (MuObs Protected) o ↔ MuObs Protected o := by
  constructor
  · intro h
    cases h with
    | inl hbase =>
        rcases hbase with ⟨hsteps, hq⟩
        cases o with
        | mk steps query =>
            simp only at hsteps
            subst steps
            exact MuObs.base query hq
    | inr hstep =>
        rcases hstep with ⟨s, prior, hprior, rfl⟩
        exact MuObs.step s prior hprior
  · intro h
    induction h with
    | base q hq =>
        exact Or.inl ⟨rfl, hq⟩
    | step s o ho ih =>
        exact Or.inr ⟨s, o, ho, rfl⟩

/--
μL is the least pre-fixed observation family: every family closed under L
contains every generated future observation.
-/
theorem muObs_least
    {Step : Type v} {Test : Type w}
    (Protected : Test → Prop)
    (S : FutureObservation Step Test → Prop)
    (hclosed : ∀ o, LOp Protected S o → S o) :
    ∀ o, MuObs Protected o → S o := by
  intro o ho
  induction ho with
  | base q hq =>
      exact hclosed ⟨[], q⟩ (Or.inl ⟨rfl, hq⟩)
  | step s o ho ih =>
      exact hclosed (prependObs s o) (Or.inr ⟨s, o, ih, rfl⟩)

/--
Indistinguishability by μL is exactly finite-path continuation-safe identity.
-/
theorem alpha_mu_iff_futureEq
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (x y : State) :
    Indistinguishable
      (futureObservationEval act test)
      (MuObs Protected) x y ↔
    FutureEq act test Protected x y := by
  constructor
  · intro h steps q hq
    exact h ⟨steps, q⟩ (muObs_all Protected steps q hq)
  · intro h o ho
    exact h o.steps o.query (muObs_protected ho)

def BOp
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (R : Relation State) : Relation State :=
  fun x y =>
    ImmediateAgreement test Protected x y ∧
      ∀ s, R (act s x) (act s y)

def Postfixed
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (R : Relation State) : Prop :=
  ∀ x y, R x y → BOp act test Protected R x y

/-- Greatest post-fixed relation νB, defined extensionally as the union of all post-fixed relations. -/
def NuB
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) : Relation State :=
  fun x y =>
    ∃ R : Relation State,
      Postfixed act test Protected R ∧ R x y

theorem postfixed_admissible
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (R : Relation State)
    (hR : Postfixed act test Protected R) :
    Admissible act test Protected R := by
  constructor
  · intro x y hxy
    exact (hR x y hxy).1
  · intro x y hxy s
    exact (hR x y hxy).2 s

theorem futureEq_postfixed
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :
    Postfixed act test Protected (FutureEq act test Protected) := by
  intro x y hxy
  exact ⟨
    futureEq_immediate act test Protected x y hxy,
    fun s => futureEq_stepClosed act test Protected x y hxy s
  ⟩

theorem nuB_iff_futureEq
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (x y : State) :
    NuB act test Protected x y ↔
      FutureEq act test Protected x y := by
  constructor
  · intro h
    rcases h with ⟨R, hpost, hxy⟩
    exact admissible_le_futureEq act test Protected R
      (postfixed_admissible act test Protected R hpost) x y hxy
  · intro hxy
    exact ⟨FutureEq act test Protected,
      futureEq_postfixed act test Protected, hxy⟩

/-- νB is a fixed point of B. -/
theorem nuB_fixed
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (x y : State) :
    BOp act test Protected (NuB act test Protected) x y ↔
      NuB act test Protected x y := by
  constructor
  · intro h
    apply (nuB_iff_futureEq act test Protected x y).2
    intro steps
    induction steps generalizing x y with
    | nil =>
        intro q hq
        exact h.1 q hq
    | cons s ss ih =>
        intro q hq
        have hnext : FutureEq act test Protected (act s x) (act s y) :=
          (nuB_iff_futureEq act test Protected (act s x) (act s y)).1 (h.2 s)
        exact hnext ss q hq
  · intro h
    have hf : FutureEq act test Protected x y :=
      (nuB_iff_futureEq act test Protected x y).1 h
    constructor
    · exact futureEq_immediate act test Protected x y hf
    · intro s
      exact (nuB_iff_futureEq act test Protected (act s x) (act s y)).2
        (futureEq_stepClosed act test Protected x y hf s)

/--
The literal conjugate fixed-point theorem for this deterministic same-form
kernel: α(μL) = νB.
-/
theorem alpha_mu_eq_nu_b
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :
    Indistinguishable
      (futureObservationEval act test)
      (MuObs Protected) =
    NuB act test Protected := by
  funext x y
  apply propext
  exact (alpha_mu_iff_futureEq act test Protected x y).trans
    (nuB_iff_futureEq act test Protected x y).symm

/-!
Full-form reflection test.

CLC V1 only requires FutureEq to preserve protected tests. Therefore arbitrary
unprotected tests need not descend to the behavioral quotient. The following
fixture proves that a quotient carrying the entire original evaluator cannot
exist in general.
-/

def tinyAct (_ : Unit) (x : Bool) : Bool := x

def tinyEval (q x : Bool) : Bool :=
  if q then x else false

def tinyProtected (q : Bool) : Prop :=
  q = false

theorem tinyRun (steps : List Unit) (x : Bool) :
    run tinyAct steps x = x := by
  induction steps with
  | nil =>
      rfl
  | cons s ss ih =>
      simpa [run, tinyAct] using ih

theorem tinyFutureEq :
    FutureEq tinyAct tinyEval tinyProtected false true := by
  intro steps q hq
  subst q
  simp [tinyEval, tinyRun]

/--
No evaluator on the behavioral quotient can preserve every original test in
this fixture: the protected language identifies false and true, while the
unprotected test q=true distinguishes them.
-/
theorem fullEvaluatorDescent_impossible :
    ¬ ∃ qeval :
        BehavioralQuotient tinyAct tinyEval tinyProtected → Bool → Bool,
      ∀ x q,
        qeval (quotientMap tinyAct tinyEval tinyProtected x) q =
          tinyEval q x := by
  intro h
  rcases h with ⟨qeval, hfactor⟩
  have hquot :
      quotientMap tinyAct tinyEval tinyProtected false =
      quotientMap tinyAct tinyEval tinyProtected true :=
    Quotient.sound tinyFutureEq
  have hsame := congrArg (fun qx => qeval qx true) hquot
  have hfalse := hfactor false true
  have htrue := hfactor true true
  have hcontra : false = true := by
    calc
      false = qeval (quotientMap tinyAct tinyEval tinyProtected false) true :=
        hfalse.symm
      _ = qeval (quotientMap tinyAct tinyEval tinyProtected true) true :=
        hsame
      _ = true := htrue
  cases hcontra

/--
The correct quotient test language consists of observations compatible with the
continuation-safe boundary.
-/
def CompatibleTest
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop) :=
  {q : Test //
    ∀ x y, FutureEq act test Protected x y → test q x = test q y}

def compatibleQuotientEval
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (qx : BehavioralQuotient act test Protected)
    (q : CompatibleTest act test Protected) : Val :=
  Quotient.lift
    (fun x => test q.1 x)
    (by
      intro x y hxy
      exact q.2 x y hxy)
    qx

def protectedCompatible
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (q : Test)
    (hq : Protected q) :
    CompatibleTest act test Protected :=
  ⟨q, by
    intro x y hxy
    exact futureEq_immediate act test Protected x y hxy q hq⟩

theorem compatibleQuotientEval_mk
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (test : Test → State → Val)
    (Protected : Test → Prop)
    (x : State)
    (q : CompatibleTest act test Protected) :
    compatibleQuotientEval act test Protected
      (quotientMap act test Protected x) q =
      test q.1 x := by
  rfl

end Metatron.FixedPointReflection
