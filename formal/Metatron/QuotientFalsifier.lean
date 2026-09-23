import Metatron.ResidualBasis

namespace Metatron.QuotientFalsifier

open Metatron.ResidualBasis

universe u v w

/-- Equality induced by a representation. -/
def KernelOf {X : Type u} {Q : Type v} (q : X → Q) : Relation X :=
  fun x y => q x = q y

/-- A protected target is recoverable from q alone when it factors through q. -/
def FactorsThrough {X : Type u} {Q : Type v} {Y : Type w}
    (q : X → Q) (target : X → Y) : Prop :=
  ∃ lift : Q → Y, ∀ x, lift (q x) = target x

/-- A same-quotient / different-target pair is the minimal decisive falsifier. -/
def SeparatingWitness {X : Type u} {Q : Type v} {Y : Type w}
    (q : X → Q) (target : X → Y) : Prop :=
  ∃ x y, q x = q y ∧ target x ≠ target y

theorem witness_refutes_factorization
    {X : Type u} {Q : Type v} {Y : Type w}
    {q : X → Q} {target : X → Y}
    (h : SeparatingWitness q target) :
    ¬ FactorsThrough q target := by
  intro hfactor
  rcases hfactor with ⟨lift, hlift⟩
  rcases h with ⟨x, y, hq, htarget⟩
  apply htarget
  calc
    target x = lift (q x) := (hlift x).symm
    _ = lift (q y) := congrArg lift hq
    _ = target y := hlift y

/-- Existing Metatron residual language is exactly enough to produce a
    representation-level factorization falsifier. -/
theorem residualPair_refutes_factorization
    {X : Type u} {Q : Type v} {Y : Type w}
    {q : X → Q} {target : X → Y}
    {x y : X}
    (h : ResidualPair (KernelOf q) (KernelOf target) x y) :
    ¬ FactorsThrough q target := by
  apply witness_refutes_factorization
  exact ⟨x, y, h.1, h.2⟩

/-! Minimal fixture: a constant representation loses a protected Boolean bit. -/

def boolQuotient (_ : Bool) : Unit := ()
def boolTarget (x : Bool) : Bool := x

theorem bool_pair_is_kernel_residual :
    ResidualPair
      (KernelOf boolQuotient)
      (KernelOf boolTarget)
      false true := by
  constructor
  · rfl
  · decide

theorem bool_quotient_not_target_sufficient :
    ¬ FactorsThrough boolQuotient boolTarget :=
  residualPair_refutes_factorization bool_pair_is_kernel_residual

end Metatron.QuotientFalsifier
