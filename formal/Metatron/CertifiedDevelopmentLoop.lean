import Metatron.ResidualBasis

namespace Metatron.CertifiedDevelopmentLoop

open Metatron.ResidualBasis

universe u v

structure QualifiedRepair
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop) where
  basis : List Candidate
  covers : CoversResidual current target separates basis

def promote
    {State : Type u} {Candidate : Type v}
    {current target : Relation State}
    {separates : Candidate → State → State → Prop}
    (q : QualifiedRepair current target separates) :
    Relation State :=
  RefinedBy current separates q.basis

theorem promote_refines_current
    {State : Type u} {Candidate : Type v}
    {current target : Relation State}
    {separates : Candidate → State → State → Prop}
    (q : QualifiedRepair current target separates)
    {x y : State}
    (h : promote q x y) :
    current x y := by
  exact h.1

theorem promote_target_sufficient
    {State : Type u} {Candidate : Type v}
    {current target : Relation State}
    {separates : Candidate → State → State → Prop}
    (q : QualifiedRepair current target separates) :
    ∀ x y, promote q x y → target x y := by
  exact
    (certifiedResidualBasis_closes
      current target separates q.basis).1 q.covers

theorem promote_closes_residual
    {State : Type u} {Candidate : Type v}
    {current target : Relation State}
    {separates : Candidate → State → State → Prop}
    (q : QualifiedRepair current target separates) :
    ¬ ∃ x y, ResidualPair (promote q) target x y := by
  rintro ⟨x, y, hres⟩
  exact hres.2 (promote_target_sufficient q x y hres.1)

structure CertifiedLoopResult
    {State : Type u} {Candidate : Type v}
    (current target : Relation State)
    (separates : Candidate → State → State → Prop) where
  promoted : Relation State
  refinesCurrent : ∀ x y, promoted x y → current x y
  targetSufficient : ∀ x y, promoted x y → target x y
  residualClosed : ¬ ∃ x y, ResidualPair promoted target x y

def run
    {State : Type u} {Candidate : Type v}
    {current target : Relation State}
    {separates : Candidate → State → State → Prop}
    (q : QualifiedRepair current target separates) :
    CertifiedLoopResult current target separates where
  promoted := promote q
  refinesCurrent := by
    intro x y h
    exact promote_refines_current q h
  targetSufficient := by
    intro x y h
    exact promote_target_sufficient q x y h
  residualClosed := promote_closes_residual q

/-!
Finite exact fixture: one missing Boolean distinction.

The current relation merges every pair, the target relation is equality, and the
single Unit observation is the minimum useful separator already qualified by
ResidualBasis. This fixture exercises the whole finite loop:
residual → certified repair → promotion → zero remaining target residual.
-/

def boolRepair :
    QualifiedRepair boolCurrent boolTarget boolSeparates where
  basis := [()]
  covers := bool_singleton_basis_covers

theorem bool_has_initial_residual :
    ResidualPair boolCurrent boolTarget false true := by
  exact ⟨by trivial, by decide⟩

theorem bool_promoted_eq_target :
    promote boolRepair = boolTarget := by
  funext x y
  apply propext
  simp [promote, boolRepair, RefinedBy, boolCurrent, boolTarget, boolSeparates]

theorem bool_loop_closes :
    ¬ ∃ x y, ResidualPair (promote boolRepair) boolTarget x y :=
  promote_closes_residual boolRepair

theorem bool_empty_repair_not_qualified :
    ¬ CoversResidual boolCurrent boolTarget boolSeparates [] := by
  intro h
  have hs :
      TargetSufficient boolCurrent boolTarget boolSeparates [] :=
    (certifiedResidualBasis_closes
      boolCurrent boolTarget boolSeparates []).1 h
  exact bool_empty_basis_fails hs

theorem bool_certified_loop_exact :
    let result := run boolRepair
    result.promoted = boolTarget ∧
      (¬ ∃ x y, ResidualPair result.promoted boolTarget x y) := by
  dsimp [run]
  exact ⟨bool_promoted_eq_target, bool_loop_closes⟩

end Metatron.CertifiedDevelopmentLoop
