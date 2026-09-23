import Metatron.WarrantedContinuationViabilityV7

namespace Metatron.WarrantedContinuationViabilityV8

open Metatron.WarrantedContinuationViability
open Metatron.WarrantedContinuationViabilityV1
open Metatron.WarrantedContinuationViabilityV7

/--
Finite capacity-2 state. The constructor records both whether the inherited
certified repair warrant is live and the exact remaining resource level.
-/
inductive CapacityState where
  | auth0 | auth1 | auth2
  | unauth0 | unauth1 | unauth2
  deriving DecidableEq, Repr

def authorized : CapacityState → Bool
  | .auth0 | .auth1 | .auth2 => true
  | .unauth0 | .unauth1 | .unauth2 => false

def resource : CapacityState → Nat
  | .auth0 | .unauth0 => 0
  | .auth1 | .unauth1 => 1
  | .auth2 | .unauth2 => 2

def liveWarrants : CapacityState → List Nat
  | .auth0 | .auth1 | .auth2 => [0]
  | .unauth0 | .unauth1 | .unauth2 => []

def admittedFailures : List Nat := [0, 1]

def capacity : Nat := 2
def replenishment : Nat := 1

def balancedCost : Nat → Nat
  | 0 => 1
  | 1 => 1
  | _ => 0

def skewedCost : Nat → Nat
  | 0 => 0
  | 1 => 2
  | _ => 0

abbrev ScalarSummary := Nat × Nat × Nat

/--
The scalar deliberately forgets cost geometry: total declared repair demand
over the two admitted failure classes, replenishment per successful repair,
and total resource capacity.
-/
def scalarSummary (cost : Nat → Nat) : ScalarSummary :=
  (cost 0 + cost 1, replenishment, capacity)

theorem balanced_and_skewed_same_scalar_summary :
    scalarSummary balancedCost = scalarSummary skewedCost := by
  rfl

/--
Balanced geometry: either admitted repair costs one unit and the one-unit
replenishment restores that unit immediately. Authorized positive-resource
states are self-loops.
-/
def balancedStep : CapacityState → Nat → Option CapacityState
  | .auth1, 0 | .auth1, 1 => some .auth1
  | .auth2, 0 | .auth2, 1 => some .auth2
  | _, _ => none

/--
Skewed geometry with the same scalar total demand:
failure 0 costs 0 and then receives one replenishment unit;
failure 1 costs 2 and then receives one replenishment unit.
Capacity is capped at 2.
-/
def skewedStep : CapacityState → Nat → Option CapacityState
  | .auth0, 0 => some .auth1
  | .auth1, 0 => some .auth2
  | .auth2, 0 => some .auth2
  | .auth2, 1 => some .auth1
  | _, _ => none

def BalancedKernel (s : CapacityState) : Prop :=
  s = .auth1 ∨ s = .auth2

def EmptyKernel (_ : CapacityState) : Prop := False

theorem balanced_kernel_postfixed :
    PostFixed balancedStep admittedFailures BalancedKernel := by
  intro s hs
  rcases hs with rfl | rfl
  · intro failure hfailure
    have hcases : failure = 0 ∨ failure = 1 := by
      simpa [admittedFailures] using hfailure
    rcases hcases with rfl | rfl
    · exact ⟨.auth1, rfl, Or.inl rfl⟩
    · exact ⟨.auth1, rfl, Or.inl rfl⟩
  · intro failure hfailure
    have hcases : failure = 0 ∨ failure = 1 := by
      simpa [admittedFailures] using hfailure
    rcases hcases with rfl | rfl
    · exact ⟨.auth2, rfl, Or.inr rfl⟩
    · exact ⟨.auth2, rfl, Or.inr rfl⟩

theorem balanced_kernel_greatest
    (S : CapacityState → Prop)
    (hS : PostFixed balancedStep admittedFailures S) :
    ∀ s, S s → BalancedKernel s := by
  intro s hs
  cases s with
  | auth0 =>
      have h := hS .auth0 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [balancedStep] at hstep
  | auth1 =>
      exact Or.inl rfl
  | auth2 =>
      exact Or.inr rfl
  | unauth0 =>
      have h := hS .unauth0 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [balancedStep] at hstep
  | unauth1 =>
      have h := hS .unauth1 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [balancedStep] at hstep
  | unauth2 =>
      have h := hS .unauth2 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [balancedStep] at hstep

theorem balanced_kernel_exact :
    BalancedKernel .auth1 ∧
    BalancedKernel .auth2 ∧
    ¬ BalancedKernel .auth0 ∧
    ¬ BalancedKernel .unauth0 ∧
    ¬ BalancedKernel .unauth1 ∧
    ¬ BalancedKernel .unauth2 := by
  simp [BalancedKernel]

theorem skewed_no_postfixed_state
    (S : CapacityState → Prop)
    (hS : PostFixed skewedStep admittedFailures S) :
    ∀ s, S s → False := by
  intro s hs
  cases s with
  | auth0 =>
      have h := hS .auth0 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [skewedStep] at hstep
  | auth1 =>
      have h := hS .auth1 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [skewedStep] at hstep
  | auth2 =>
      have h := hS .auth2 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, hs'⟩
      have hs'Eq : .auth1 = s' := by
        simpa [skewedStep] using hstep
      subst s'
      have h' := hS .auth1 hs' 1 (by simp [admittedFailures])
      rcases h' with ⟨s'', hstep', _⟩
      simp [skewedStep] at hstep'
  | unauth0 =>
      have h := hS .unauth0 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [skewedStep] at hstep
  | unauth1 =>
      have h := hS .unauth1 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [skewedStep] at hstep
  | unauth2 =>
      have h := hS .unauth2 hs 1 (by simp [admittedFailures])
      rcases h with ⟨s', hstep, _⟩
      simp [skewedStep] at hstep

theorem skewed_empty_kernel_postfixed :
    PostFixed skewedStep admittedFailures EmptyKernel := by
  intro s hs
  exact False.elim hs

theorem skewed_empty_kernel_greatest
    (S : CapacityState → Prop)
    (hS : PostFixed skewedStep admittedFailures S) :
    ∀ s, S s → EmptyKernel s := by
  intro s hs
  exact skewed_no_postfixed_state S hS s hs

theorem balanced_repeated_heavy_survives :
    runViable balancedStep .auth2 [1, 1] = some .auth2 := by
  decide

theorem skewed_repeated_heavy_fails :
    runViable skewedStep .auth2 [1, 1] = none := by
  decide

/--
Exact scalar falsifier: equal total declared repair demand, equal replenishment
and equal capacity do not determine viability once repair-cost geometry is
retained in the stateful transition system.
-/
theorem scalar_average_summary_not_viability_sufficient :
    scalarSummary balancedCost = scalarSummary skewedCost ∧
    PostFixed balancedStep admittedFailures BalancedKernel ∧
    (∀ S,
      PostFixed skewedStep admittedFailures S →
      ∀ s, S s → False) := by
  exact ⟨balanced_and_skewed_same_scalar_summary,
    balanced_kernel_postfixed,
    skewed_no_postfixed_state⟩

theorem authorized_projection_inherits_v7_warrant :
    liveWarrants .auth0 = WarrantedContinuationViabilityV7.liveWarrants
      WarrantedContinuationViabilityV7.StatefulRepairState.ready ∧
    liveWarrants .auth1 = WarrantedContinuationViabilityV7.liveWarrants
      WarrantedContinuationViabilityV7.StatefulRepairState.ready ∧
    liveWarrants .auth2 = WarrantedContinuationViabilityV7.liveWarrants
      WarrantedContinuationViabilityV7.StatefulRepairState.ready := by
  decide

end Metatron.WarrantedContinuationViabilityV8
