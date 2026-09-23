import Metatron.WarrantedContinuationViabilityV6

namespace Metatron.WarrantedContinuationViabilityV7

open Metatron.WarrantedContinuationViability
open Metatron.WarrantedContinuationViabilityV1
open Metatron.WarrantedContinuationViabilityV6

/--
Finite quotient of the full repair state. The constructors encode both the
live-warrant projection relevant to the certified route and the one-shot
resource state from V6.
-/
inductive StatefulRepairState where
  | ready
  | depleted
  | unauthorizedReady
  | unauthorizedDepleted
  deriving DecidableEq, Repr

def liveWarrants : StatefulRepairState → List Nat
  | .ready | .depleted => [0]
  | .unauthorizedReady | .unauthorizedDepleted => []

def fuel : StatefulRepairState → Bool
  | .ready | .unauthorizedReady => true
  | .depleted | .unauthorizedDepleted => false

def admittedFailures : List Nat := [0, 1]

/--
Execution without replenishment. Both admitted failures use the same V6
live-authorized, causally certified AB route and consume the sole resource.
-/
def statefulContentionStep : StatefulRepairState → Nat → Option StatefulRepairState
  | .ready, 0 => some .depleted
  | .ready, 1 => some .depleted
  | _, _ => none

/--
Execution with the smallest replenishment policy: after a successful certified
repair the one-shot resource is restored before the next encounter.
-/
def replenishingStep : StatefulRepairState → Nat → Option StatefulRepairState
  | .ready, 0 => some .ready
  | .ready, 1 => some .ready
  | _, _ => none

def EmptyKernel (_ : StatefulRepairState) : Prop := False

def ReplenishedKernel (s : StatefulRepairState) : Prop :=
  s = .ready

theorem ready_live_causal_cover :
    CompleteLiveCausalCover
      (liveWarrants .ready)
      repeatedRoutes repeatedValidB admittedFailures := by
  decide

theorem unauthorized_has_no_live_causal_cover :
    ¬ CompleteLiveCausalCover
      (liveWarrants .unauthorizedReady)
      repeatedRoutes repeatedValidB admittedFailures := by
  decide

theorem ready_execution_matches_v6_failure0 :
    contentionStep repeatedRoutes repeatedValidB
      ⟨liveWarrants .ready, fuel .ready⟩ 0 =
      some ⟨liveWarrants .depleted, fuel .depleted⟩ := by
  decide

theorem ready_execution_matches_v6_failure1 :
    contentionStep repeatedRoutes repeatedValidB
      ⟨liveWarrants .ready, fuel .ready⟩ 1 =
      some ⟨liveWarrants .depleted, fuel .depleted⟩ := by
  decide

/-- No state can belong to any post-fixed set under the one-shot contention
    dynamics. Hence the greatest viability kernel is empty. -/
theorem contention_no_postfixed_state
    (S : StatefulRepairState → Prop)
    (hS : PostFixed statefulContentionStep admittedFailures S) :
    ∀ s, S s → False := by
  intro s hs
  cases s with
  | ready =>
      have h0 := hS .ready hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, hs'⟩
      have hs'Eq : s' = .depleted := by
        simpa [statefulContentionStep] using hstep.symm.symm
      subst s'
      have h1 := hS .depleted hs' 0 (by simp [admittedFailures])
      rcases h1 with ⟨s'', hstep', _⟩
      simp [statefulContentionStep] at hstep'
  | depleted =>
      have h0 := hS .depleted hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, _⟩
      simp [statefulContentionStep] at hstep
  | unauthorizedReady =>
      have h0 := hS .unauthorizedReady hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, _⟩
      simp [statefulContentionStep] at hstep
  | unauthorizedDepleted =>
      have h0 := hS .unauthorizedDepleted hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, _⟩
      simp [statefulContentionStep] at hstep

theorem contention_empty_kernel_postfixed :
    PostFixed statefulContentionStep admittedFailures EmptyKernel := by
  intro s hs
  exact False.elim hs

theorem contention_empty_kernel_greatest
    (S : StatefulRepairState → Prop)
    (hS : PostFixed statefulContentionStep admittedFailures S) :
    ∀ s, S s → EmptyKernel s := by
  intro s hs
  exact contention_no_postfixed_state S hS s hs

theorem replenished_kernel_postfixed :
    PostFixed replenishingStep admittedFailures ReplenishedKernel := by
  intro s hs
  subst s
  intro failure hfailure
  have hcases : failure = 0 ∨ failure = 1 := by
    simpa [admittedFailures] using hfailure
  rcases hcases with rfl | rfl
  · exact ⟨.ready, rfl, rfl⟩
  · exact ⟨.ready, rfl, rfl⟩

theorem replenished_kernel_greatest
    (S : StatefulRepairState → Prop)
    (hS : PostFixed replenishingStep admittedFailures S) :
    ∀ s, S s → ReplenishedKernel s := by
  intro s hs
  cases s with
  | ready =>
      rfl
  | depleted =>
      have h0 := hS .depleted hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, _⟩
      simp [replenishingStep] at hstep
  | unauthorizedReady =>
      have h0 := hS .unauthorizedReady hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, _⟩
      simp [replenishingStep] at hstep
  | unauthorizedDepleted =>
      have h0 := hS .unauthorizedDepleted hs 0 (by simp [admittedFailures])
      rcases h0 with ⟨s', hstep, _⟩
      simp [replenishingStep] at hstep

theorem replenished_kernel_exact :
    ReplenishedKernel .ready ∧
    ¬ ReplenishedKernel .depleted ∧
    ¬ ReplenishedKernel .unauthorizedReady ∧
    ¬ ReplenishedKernel .unauthorizedDepleted := by
  simp [ReplenishedKernel]

theorem scheduling_alone_does_not_restore :
    runViable statefulContentionStep .ready [0, 1] = none ∧
    runViable statefulContentionStep .ready [1, 0] = none := by
  decide

theorem replenishment_restores_both_orders :
    runViable replenishingStep .ready [0, 1] = some .ready ∧
    runViable replenishingStep .ready [1, 0] = some .ready := by
  decide

theorem replenishment_changes_empty_to_nonempty_kernel :
    (∀ S,
      PostFixed statefulContentionStep admittedFailures S →
      ∀ s, S s → False) ∧
    PostFixed replenishingStep admittedFailures ReplenishedKernel ∧
    ReplenishedKernel .ready := by
  exact ⟨contention_no_postfixed_state,
    replenished_kernel_postfixed, rfl⟩

/-! Exact WarrantGraph encoding of the authorization coordinate. -/

def resourceAuthorityBase : List WarrantEntry := [
  ⟨[], none⟩
]

def resourceAuthorityRevoked : List WarrantEntry :=
  resourceAuthorityBase ++ [⟨[], some 0⟩]

theorem resource_authority_base_live :
    warrantLive resourceAuthorityBase = [0] := by
  decide

theorem resource_authority_revoked_live :
    warrantLive resourceAuthorityRevoked = [] := by
  decide

theorem finite_state_authority_projection_matches_warrant_graph :
    liveWarrants .ready = warrantLive resourceAuthorityBase ∧
    liveWarrants .depleted = warrantLive resourceAuthorityBase ∧
    liveWarrants .unauthorizedReady = warrantLive resourceAuthorityRevoked ∧
    liveWarrants .unauthorizedDepleted = warrantLive resourceAuthorityRevoked := by
  decide

end Metatron.WarrantedContinuationViabilityV7
