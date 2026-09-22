import Metatron.FutureObservations

namespace Metatron.ResidualBasis

universe u v

abbrev Relation (State : Type u) := State → State → Prop

/-- A pair still identified by the current view but distinguished by the target future. -/
def ResidualPair
    {State : Type u}
    (current target : Relation State)
    (x y : State) : Prop :=
  current x y ∧ ¬ target x y

/-- The current relation after adding every separator in a candidate basis. -/
def RefinedBy
    {State : Type u} {Candidate : Type v}
    (current : Relation State)
    (separates : Candidate → State → State → Prop)
    (basis : List Candidate) : Relation State :=
  fun x y =>
    current x y ∧
      ∀ g, g ∈ basis → ¬ separates g x y

/-- Every future-demanded residual pair is hit by at least one basis generator. -/
def CoversResidual
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop)
    (basis : List Candidate) : Prop :=
  ∀ x y,
    ResidualPair current target x y →
      ∃ g, g ∈ basis ∧ separates g x y

/-- The refined present never identifies a pair that the target future distinguishes. -/
def TargetSufficient
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop)
    (basis : List Candidate) : Prop :=
  ∀ x y, RefinedBy current separates basis x y → target x y

/--
The exact bridge between consequential-residual cover and target sufficiency.

This is the finite/declarative core used by the separating-hypergraph policy:
covering every pair that is currently identified but target-distinguishable is
equivalent to the refined observational quotient being sufficient for the
frozen target relation.
-/
theorem certifiedResidualBasis_closes
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop)
    (basis : List Candidate) :
    CoversResidual current target separates basis ↔
      TargetSufficient current target separates basis := by
  classical
  constructor
  · intro hcover x y hrefined
    by_contra htarget
    have hres : ResidualPair current target x y :=
      ⟨hrefined.1, htarget⟩
    rcases hcover x y hres with ⟨g, hg, hsep⟩
    exact (hrefined.2 g hg) hsep
  · intro hsufficient x y hres
    by_contra hnone
    have hall : ∀ g, g ∈ basis → ¬ separates g x y := by
      intro g hg hsep
      apply hnone
      exact ⟨g, hg, hsep⟩
    have hrefined : RefinedBy current separates basis x y :=
      ⟨hres.1, hall⟩
    exact hres.2 (hsufficient x y hrefined)

/-- Exact minimum-cover assumptions transfer directly to minimum target sufficiency. -/
def MinimumCoverByLength
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop)
    (basis : List Candidate) : Prop :=
  CoversResidual current target separates basis ∧
    ∀ other : List Candidate,
      other.length < basis.length →
        ¬ CoversResidual current target separates other

theorem minimumResidualBasis_minimalSufficient
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop)
    (basis : List Candidate)
    (hmin : MinimumCoverByLength current target separates basis) :
    TargetSufficient current target separates basis ∧
      ∀ other : List Candidate,
        other.length < basis.length →
          ¬ TargetSufficient current target separates other := by
  constructor
  · exact
      (certifiedResidualBasis_closes current target separates basis).1
        hmin.1
  · intro other hlt hsufficient
    exact hmin.2 other hlt
      ((certifiedResidualBasis_closes current target separates other).2
        hsufficient)

/-! A minimal positive/negative fixture: one missing Boolean distinction. -/

def boolCurrent : Relation Bool := fun _ _ => True

def boolTarget : Relation Bool := fun x y => x = y

def boolSeparates (_ : Unit) (x y : Bool) : Prop := x ≠ y

theorem bool_singleton_basis_covers :
    CoversResidual boolCurrent boolTarget boolSeparates [()] := by
  intro x y hres
  exact ⟨(), by simp, hres.2⟩

theorem bool_singleton_basis_sufficient :
    TargetSufficient boolCurrent boolTarget boolSeparates [()] :=
  (certifiedResidualBasis_closes
    boolCurrent boolTarget boolSeparates [()]).1
    bool_singleton_basis_covers

theorem bool_empty_basis_fails :
    ¬ TargetSufficient boolCurrent boolTarget boolSeparates [] := by
  intro h
  have hrefined : RefinedBy boolCurrent boolSeparates [] false true := by
    constructor
    · trivial
    · intro g hg
      cases hg
  have hbad : false = true := h false true hrefined
  cases hbad

end Metatron.ResidualBasis
