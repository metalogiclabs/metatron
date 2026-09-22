import Metatron.FixedPointReflection

namespace Metatron.DevelopmentalRelation

open Metatron.FutureObservations
open Metatron.FixedPointReflection

universe u v w z

/--
A developmental state map need not descend to a function between behavioral
quotients. Its canonical quotient semantics is therefore a relation: a source
class is related to every target class reached by some representative.
-/
def QuotientRelation
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState)
    (qa : BehavioralQuotient actA evalA protA)
    (qb : BehavioralQuotient actB evalB protB) : Prop :=
  ∃ x : AState,
    quotientMap actA evalA protA x = qa ∧
    quotientMap actB evalB protB (mapState x) = qb

def Functional
    {A B : Type}
    (R : A → B → Prop) : Prop :=
  ∀ a b₁ b₂, R a b₁ → R a b₂ → b₁ = b₂

theorem quotientRelation_contains_graph
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState)
    (x : AState) :
    QuotientRelation
      actA evalA protA actB evalB protB mapState
      (quotientMap actA evalA protA x)
      (quotientMap actB evalB protB (mapState x)) := by
  exact ⟨x, rfl, rfl⟩

/-- The quotient relation is total on source behavioral classes. -/
theorem quotientRelation_total
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState) :
    ∀ qa : BehavioralQuotient actA evalA protA,
      ∃ qb : BehavioralQuotient actB evalB protB,
        QuotientRelation
          actA evalA protA actB evalB protB mapState qa qb := by
  intro qa
  refine Quotient.inductionOn qa ?_
  intro x
  exact ⟨
    quotientMap actB evalB protB (mapState x),
    quotientRelation_contains_graph
      actA evalA protA actB evalB protB mapState x
  ⟩

/--
Relational universal property: QuotientRelation is the least relation containing
the representative-level graph after quotienting both endpoints.
-/
theorem quotientRelation_least
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState)
    (S :
      BehavioralQuotient actA evalA protA →
      BehavioralQuotient actB evalB protB → Prop)
    (hgraph :
      ∀ x,
        S
          (quotientMap actA evalA protA x)
          (quotientMap actB evalB protB (mapState x))) :
    ∀ qa qb,
      QuotientRelation
        actA evalA protA actB evalB protB mapState qa qb →
      S qa qb := by
  intro qa qb h
  rcases h with ⟨x, hqa, hqb⟩
  subst qa
  subst qb
  exact hgraph x

theorem quotientRelation_functional_of_preserves
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState)
    (hpres :
      ∀ x y,
        FutureEq actA evalA protA x y →
        FutureEq actB evalB protB (mapState x) (mapState y)) :
    Functional
      (QuotientRelation
        actA evalA protA actB evalB protB mapState) := by
  intro qa qb₁ qb₂ h₁ h₂
  rcases h₁ with ⟨x, hxa, hxb⟩
  rcases h₂ with ⟨y, hya, hyb⟩
  have hsource :
      quotientMap actA evalA protA x =
      quotientMap actA evalA protA y := by
    exact hxa.trans hya.symm
  have hxy : FutureEq actA evalA protA x y :=
    Quotient.exact hsource
  have htarget :
      quotientMap actB evalB protB (mapState x) =
      quotientMap actB evalB protB (mapState y) :=
    Quotient.sound (hpres x y hxy)
  exact hxb.symm.trans (htarget.trans hyb)

theorem quotientRelation_preserves_of_functional
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState)
    (hfun :
      Functional
        (QuotientRelation
          actA evalA protA actB evalB protB mapState)) :
    ∀ x y,
      FutureEq actA evalA protA x y →
      FutureEq actB evalB protB (mapState x) (mapState y) := by
  intro x y hxy
  have hqa :
      quotientMap actA evalA protA x =
      quotientMap actA evalA protA y :=
    Quotient.sound hxy
  have hrx :=
    quotientRelation_contains_graph
      actA evalA protA actB evalB protB mapState x
  have hry0 :=
    quotientRelation_contains_graph
      actA evalA protA actB evalB protB mapState y
  have hry :
      QuotientRelation
        actA evalA protA actB evalB protB mapState
        (quotientMap actA evalA protA x)
        (quotientMap actB evalB protB (mapState y)) := by
    simpa [hqa] using hry0
  have hqb :
      quotientMap actB evalB protB (mapState x) =
      quotientMap actB evalB protB (mapState y) :=
    hfun
      (quotientMap actA evalA protA x)
      (quotientMap actB evalB protB (mapState x))
      (quotientMap actB evalB protB (mapState y))
      hrx hry
  exact Quotient.exact hqb

/--
A developmental quotient relation is functional exactly when the state map
preserves continuation-safe identity. Strict transports are exactly the
functional special case.
-/
theorem quotientRelation_functional_iff_preserves
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState) :
    Functional
      (QuotientRelation
        actA evalA protA actB evalB protB mapState) ↔
    (∀ x y,
      FutureEq actA evalA protA x y →
      FutureEq actB evalB protB (mapState x) (mapState y)) := by
  constructor
  · exact quotientRelation_preserves_of_functional
      actA evalA protA actB evalB protB mapState
  · exact quotientRelation_functional_of_preserves
      actA evalA protA actB evalB protB mapState

theorem quotientRelation_not_functional_of_split
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (mapState : AState → BState)
    (x y : AState)
    (hA : FutureEq actA evalA protA x y)
    (hB :
      ¬ FutureEq actB evalB protB (mapState x) (mapState y)) :
    ¬ Functional
      (QuotientRelation
        actA evalA protA actB evalB protB mapState) := by
  intro hfun
  exact hB
    (quotientRelation_preserves_of_functional
      actA evalA protA actB evalB protB mapState hfun x y hA)

/-!
Same-carrier refinement has an additional contravariant structure: if the new
protected language extends the old one, the finer quotient canonically forgets
back to the coarser quotient.
-/

def forgetRefinement
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (Pold Pnew : Test → Prop)
    (hprotect : ∀ q, Pold q → Pnew q) :
    BehavioralQuotient act eval Pnew →
      BehavioralQuotient act eval Pold :=
  Quotient.lift
    (fun x => quotientMap act eval Pold x)
    (by
      intro x y hnew
      exact Quotient.sound
        (futureEq_antitone_protected
          act eval Pold Pnew hprotect x y hnew))

theorem forgetRefinement_mk
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (Pold Pnew : Test → Prop)
    (hprotect : ∀ q, Pold q → Pnew q)
    (x : State) :
    forgetRefinement act eval Pold Pnew hprotect
      (quotientMap act eval Pnew x) =
    quotientMap act eval Pold x := by
  rfl

theorem forgetRefinement_surjective
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (Pold Pnew : Test → Prop)
    (hprotect : ∀ q, Pold q → Pnew q) :
    Function.Surjective
      (forgetRefinement act eval Pold Pnew hprotect) := by
  intro qold
  refine Quotient.inductionOn qold ?_
  intro x
  exact ⟨quotientMap act eval Pnew x, rfl⟩

/--
A genuine residual-driven split makes the forgetful map non-injective: two new
states of distinction collapse back to one old operational identity.
-/
theorem forgetRefinement_not_injective_of_strict
    {State : Type u} {Step : Type v} {Test : Type w} {Val : Type z}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (Pold Pnew : Test → Prop)
    (hprotect : ∀ q, Pold q → Pnew q)
    (x y : State)
    (hOld : FutureEq act eval Pold x y)
    (hNew : ¬ FutureEq act eval Pnew x y) :
    ¬ Function.Injective
      (forgetRefinement act eval Pold Pnew hprotect) := by
  intro hinj
  have holdq :
      quotientMap act eval Pold x =
      quotientMap act eval Pold y :=
    Quotient.sound hOld
  have hforget :
      forgetRefinement act eval Pold Pnew hprotect
        (quotientMap act eval Pnew x) =
      forgetRefinement act eval Pold Pnew hprotect
        (quotientMap act eval Pnew y) := by
    simpa [forgetRefinement_mk] using holdq
  have hnewq :
      quotientMap act eval Pnew x =
      quotientMap act eval Pnew y :=
    hinj hforget
  exact hNew (Quotient.exact hnewq)

/--
The earlier lax-refinement fixture is genuinely relational: its source
behavioral class branches into distinct target behavioral classes.
-/
theorem laxFixture_relation_not_functional :
    ¬ Functional
      (QuotientRelation
        laxAAct laxAEval laxAProtected
        laxBAct laxBEval laxBProtected
        laxMapState) := by
  apply quotientRelation_not_functional_of_split
    laxAAct laxAEval laxAProtected
    laxBAct laxBEval laxBProtected
    laxMapState false true laxAFutureEq
  intro h
  have hnow := futureEq_immediate
    laxBAct laxBEval laxBProtected () () h () trivial
  exact Bool.noConfusion hnow

end Metatron.DevelopmentalRelation
