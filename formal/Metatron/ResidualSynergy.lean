import Metatron.ResidualBasis
import Metatron.FutureObservations

namespace Metatron.ResidualSynergy

open Metatron.FutureObservations
open Metatron.ResidualBasis

inductive Gen where
  | a
  | b
  deriving DecidableEq, Repr

structure State where
  source : Bool
  hidden : Bool
  observed : Bool
  deriving DecidableEq, Repr

def act : Gen → State → State
  | .a, s => { s with hidden := s.source }
  | .b, s => { s with observed := s.hidden }

def observe (s : State) : Bool := s.observed

def x : State := ⟨false, false, false⟩
def y : State := ⟨true, false, false⟩

def Allowed (basis steps : List Gen) : Prop :=
  ∀ g, g ∈ steps → g ∈ basis

def BasisEq (basis : List Gen) : Relation State :=
  fun s t =>
    ∀ steps, Allowed basis steps →
      observe (run act steps s) = observe (run act steps t)

def sameHiddenObserved (s t : State) : Prop :=
  s.hidden = t.hidden ∧ s.observed = t.observed

theorem onlyA_preserves_observed
    (steps : List Gen)
    (s t : State)
    (hallowed : Allowed [.a] steps)
    (hobs : observe s = observe t) :
    observe (run act steps s) = observe (run act steps t) := by
  induction steps generalizing s t with
  | nil =>
      exact hobs
  | cons g gs ih =>
      have hg : g = Gen.a := by
        have hmem := hallowed g (by simp)
        simpa using hmem
      subst g
      have htail : Allowed [.a] gs := by
        intro q hq
        exact hallowed q (by simp [hq])
      have hnext :
          observe (act Gen.a s) = observe (act Gen.a t) := by
        exact hobs
      simpa [run] using
        ih (act Gen.a s) (act Gen.a t) htail hnext

theorem onlyB_preserves_hiddenObserved
    (steps : List Gen)
    (s t : State)
    (hallowed : Allowed [.b] steps)
    (hst : sameHiddenObserved s t) :
    sameHiddenObserved (run act steps s) (run act steps t) := by
  induction steps generalizing s t with
  | nil =>
      exact hst
  | cons g gs ih =>
      have hg : g = Gen.b := by
        have hmem := hallowed g (by simp)
        simpa using hmem
      subst g
      have htail : Allowed [.b] gs := by
        intro q hq
        exact hallowed q (by simp [hq])
      have hnext :
          sameHiddenObserved (act Gen.b s) (act Gen.b t) := by
        constructor
        · exact hst.1
        · exact hst.1
      simpa [run] using
        ih (act Gen.b s) (act Gen.b t) htail hnext

theorem singletonA_indistinguishable :
    BasisEq [.a] x y := by
  intro steps hallowed
  apply onlyA_preserves_observed steps x y hallowed
  rfl

theorem singletonB_indistinguishable :
    BasisEq [.b] x y := by
  intro steps hallowed
  exact
    (onlyB_preserves_hiddenObserved
      steps x y hallowed ⟨rfl, rfl⟩).2

theorem a_then_b_separates :
    observe (run act [.a, .b] x) ≠
      observe (run act [.a, .b] y) := by
  simp [run, act, observe, x, y]

theorem b_then_a_does_not_separate :
    observe (run act [.b, .a] x) =
      observe (run act [.b, .a] y) := by
  rfl

def current : Relation State := fun _ _ => True

def target : Relation State := BasisEq [.a, .b]

theorem target_separates_xy :
    ¬ target x y := by
  intro h
  have hbad := h [.a, .b] (by
    intro g hg
    exact hg)
  exact a_then_b_separates hbad

def singletonSeparates (g : Gen) (s t : State) : Prop :=
  ¬ BasisEq [g] s t

theorem singletonA_has_no_xy_edge :
    ¬ singletonSeparates .a x y :=
  singletonA_indistinguishable

theorem singletonB_has_no_xy_edge :
    ¬ singletonSeparates .b x y :=
  singletonB_indistinguishable

theorem ordinarySingletonCover_fails :
    ¬ CoversResidual current target singletonSeparates [.a, .b] := by
  intro hcover
  have hres : ResidualPair current target x y :=
    ⟨True.intro, target_separates_xy⟩
  rcases hcover x y hres with ⟨g, hg, hsep⟩
  have hcases : g = Gen.a ∨ g = Gen.b := by
    simpa using hg
  cases hcases with
  | inl ha =>
      subst g
      exact hsep singletonA_indistinguishable
  | inr hb =>
      subst g
      exact hsep singletonB_indistinguishable

def CompositionalSufficient (basis : List Gen) : Prop :=
  ∀ s t, BasisEq basis s t → target s t

theorem jointBasis_sufficient :
    CompositionalSufficient [.a, .b] := by
  intro s t h
  exact h

theorem singletonA_insufficient :
    ¬ CompositionalSufficient [.a] := by
  intro h
  exact target_separates_xy (h x y singletonA_indistinguishable)

theorem singletonB_insufficient :
    ¬ CompositionalSufficient [.b] := by
  intro h
  exact target_separates_xy (h x y singletonB_indistinguishable)

def interactionSeparates
    (unit : List Gen)
    (s t : State) : Prop :=
  ¬ BasisEq unit s t

def InteractionCovers (units : List (List Gen)) : Prop :=
  CoversResidual current target interactionSeparates units

theorem pairInteraction_covers :
    InteractionCovers [[.a, .b]] := by
  intro s t hres
  exact ⟨[.a, .b], by simp, hres.2⟩

theorem emptyInteraction_fails :
    ¬ InteractionCovers [] := by
  intro hcover
  have hres : ResidualPair current target x y :=
    ⟨True.intro, target_separates_xy⟩
  rcases hcover x y hres with ⟨unit, hmem, _⟩
  cases hmem

end Metatron.ResidualSynergy
