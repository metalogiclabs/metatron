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
    {A : Type u} {B : Type v}
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
Concrete boundary-growth witness: the old quotient merges false/true, while
protecting all tests makes the target quotient distinguish them. The induced
developmental quotient relation is therefore genuinely one-to-many.
-/
def allTinyProtected (_ : Bool) : Prop := True

theorem tinyAll_not_futureEq :
    ¬ FutureEq tinyAct tinyEval allTinyProtected false true := by
  intro h
  have hnow := h [] true trivial
  change false = true at hnow
  cases hnow

theorem protectedGrowth_relation_not_functional :
    ¬ Functional
      (QuotientRelation
        tinyAct tinyEval tinyProtected
        tinyAct tinyEval allTinyProtected
        (fun x => x)) := by
  exact quotientRelation_not_functional_of_split
    tinyAct tinyEval tinyProtected
    tinyAct tinyEval allTinyProtected
    (fun x => x)
    false true tinyFutureEq tinyAll_not_futureEq


/-!
Composition law.

Developmental quotient semantics is not strictly functorial in general. The
direct quotient relation of a composite is always contained in relational
composition. The reverse inclusion is recovered when the second state map
preserves the intermediate continuation-safe equivalence.
-/

def RelComp
    {A : Type u} {B : Type v} {C : Type w}
    (R : A → B → Prop)
    (S : B → C → Prop) :
    A → C → Prop :=
  fun a c => ∃ b, R a b ∧ S b c

theorem quotientRelation_id_iff_eq
    {State : Type u} {Step Test Val : Type}
    (act : Step → State → State)
    (eval : Test → State → Val)
    (prot : Test → Prop)
    (qa qb : BehavioralQuotient act eval prot) :
    QuotientRelation
      act eval prot act eval prot (fun x => x) qa qb ↔
    qa = qb := by
  constructor
  · intro h
    rcases h with ⟨x, hqa, hqb⟩
    exact hqa.symm.trans hqb
  · intro h
    subst qb
    refine Quotient.inductionOn qa ?_
    intro x
    exact ⟨x, rfl, rfl⟩

theorem quotientRelation_comp_oplax
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (actC : CStep → CState → CState)
    (evalC : CTest → CState → Val)
    (protC : CTest → Prop)
    (f : AState → BState)
    (g : BState → CState)
    (qa : BehavioralQuotient actA evalA protA)
    (qc : BehavioralQuotient actC evalC protC) :
    QuotientRelation
      actA evalA protA actC evalC protC (fun x => g (f x)) qa qc →
    RelComp
      (QuotientRelation
        actA evalA protA actB evalB protB f)
      (QuotientRelation
        actB evalB protB actC evalC protC g)
      qa qc := by
  intro h
  rcases h with ⟨x, hqa, hqc⟩
  refine ⟨quotientMap actB evalB protB (f x), ?_, ?_⟩
  · exact ⟨x, hqa, rfl⟩
  · exact ⟨f x, rfl, hqc⟩

theorem quotientRelation_comp_reverse_of_preserves
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (actC : CStep → CState → CState)
    (evalC : CTest → CState → Val)
    (protC : CTest → Prop)
    (f : AState → BState)
    (g : BState → CState)
    (hg :
      ∀ x y,
        FutureEq actB evalB protB x y →
        FutureEq actC evalC protC (g x) (g y))
    (qa : BehavioralQuotient actA evalA protA)
    (qc : BehavioralQuotient actC evalC protC) :
    RelComp
      (QuotientRelation
        actA evalA protA actB evalB protB f)
      (QuotientRelation
        actB evalB protB actC evalC protC g)
      qa qc →
    QuotientRelation
      actA evalA protA actC evalC protC (fun x => g (f x)) qa qc := by
  intro h
  rcases h with ⟨qb, hfrel, hgrel⟩
  rcases hfrel with ⟨x, hqa, hfb⟩
  rcases hgrel with ⟨y, hyb, hyc⟩
  have hmid :
      quotientMap actB evalB protB (f x) =
      quotientMap actB evalB protB y := by
    exact hfb.trans hyb.symm
  have hB : FutureEq actB evalB protB (f x) y :=
    Quotient.exact hmid
  have hC :
      quotientMap actC evalC protC (g (f x)) =
      quotientMap actC evalC protC (g y) :=
    Quotient.sound (hg (f x) y hB)
  exact ⟨x, hqa, hC.trans hyc⟩

/--
If the second leg is strict with respect to continuation-safe identity, quotient
relation semantics composes exactly.
-/
theorem quotientRelation_comp_eq_of_preserves
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (actC : CStep → CState → CState)
    (evalC : CTest → CState → Val)
    (protC : CTest → Prop)
    (f : AState → BState)
    (g : BState → CState)
    (hg :
      ∀ x y,
        FutureEq actB evalB protB x y →
        FutureEq actC evalC protC (g x) (g y)) :
    QuotientRelation
      actA evalA protA actC evalC protC (fun x => g (f x)) =
    RelComp
      (QuotientRelation
        actA evalA protA actB evalB protB f)
      (QuotientRelation
        actB evalB protB actC evalC protC g) := by
  funext qa qc
  apply propext
  constructor
  · exact quotientRelation_comp_oplax
      actA evalA protA actB evalB protB
      actC evalC protC f g qa qc
  · exact quotientRelation_comp_reverse_of_preserves
      actA evalA protA actB evalB protB
      actC evalC protC f g hg qa qc

end Metatron.DevelopmentalRelation
