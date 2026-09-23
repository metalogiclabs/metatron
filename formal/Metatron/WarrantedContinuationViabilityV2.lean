import Metatron.WarrantedContinuationViabilityV1
import Metatron.WarrantGraph

namespace Metatron.WarrantedContinuationViabilityV2

open Metatron.WarrantedContinuationViabilityV1

inductive State where
  | adaptive
  | noCapBoth
  | primaryOnlyNoCap
  | backupOnlyNoCap
  deriving DecidableEq, Repr

inductive Encounter where
  | revokePrimary
  | revokeBackup
  | revokeCapability
  deriving DecidableEq, Repr

def supportOnly : List Encounter :=
  [.revokePrimary, .revokeBackup]

def withCapabilityLoss : List Encounter :=
  [.revokePrimary, .revokeBackup, .revokeCapability]

/-- The finite semantic quotient after each encounter plus declared
    repair/reclosure policy. A support revocation from adaptive is restored;
    capability revocation removes that ability. -/
def step : State → Encounter → Option State
  | .adaptive, .revokePrimary => some .adaptive
  | .adaptive, .revokeBackup => some .adaptive
  | .adaptive, .revokeCapability => some .noCapBoth
  | .noCapBoth, .revokePrimary => some .backupOnlyNoCap
  | .noCapBoth, .revokeBackup => some .primaryOnlyNoCap
  | .noCapBoth, .revokeCapability => some .noCapBoth
  | .primaryOnlyNoCap, .revokePrimary => none
  | .primaryOnlyNoCap, .revokeBackup => some .primaryOnlyNoCap
  | .primaryOnlyNoCap, .revokeCapability => some .primaryOnlyNoCap
  | .backupOnlyNoCap, .revokePrimary => some .backupOnlyNoCap
  | .backupOnlyNoCap, .revokeBackup => none
  | .backupOnlyNoCap, .revokeCapability => some .backupOnlyNoCap

def SupportKernel (s : State) : Prop :=
  s = .adaptive

theorem support_kernel_postfixed :
    PostFixed step supportOnly SupportKernel := by
  intro s hs
  subst s
  intro e he
  simp [supportOnly] at he
  rcases he with rfl | rfl
  · exact ⟨.adaptive, rfl, rfl⟩
  · exact ⟨.adaptive, rfl, rfl⟩

theorem support_kernel_greatest
    (S : State → Prop)
    (hS : PostFixed step supportOnly S) :
    ∀ s, S s → SupportKernel s := by
  intro s hs
  cases s with
  | adaptive =>
      rfl
  | noCapBoth =>
      have hp := hS .noCapBoth hs .revokePrimary (by simp [supportOnly])
      rcases hp with ⟨_, _, hbackup⟩
      have hb := hS .backupOnlyNoCap hbackup .revokeBackup (by simp [supportOnly])
      rcases hb with ⟨s', hstep, _⟩
      simp [step] at hstep
  | primaryOnlyNoCap =>
      have hp := hS .primaryOnlyNoCap hs .revokePrimary (by simp [supportOnly])
      rcases hp with ⟨s', hstep, _⟩
      simp [step] at hstep
  | backupOnlyNoCap =>
      have hb := hS .backupOnlyNoCap hs .revokeBackup (by simp [supportOnly])
      rcases hb with ⟨s', hstep, _⟩
      simp [step] at hstep

/-- Once capability revocation is admitted, no nonempty post-fixed set
    survives: any adaptive state can lose capability, then lose supports. -/
theorem capability_loss_no_postfixed_state
    (S : State → Prop)
    (hS : PostFixed step withCapabilityLoss S) :
    ∀ s, ¬ S s := by
  intro s hs
  cases s with
  | adaptive =>
      have hc := hS .adaptive hs .revokeCapability (by simp [withCapabilityLoss])
      rcases hc with ⟨_, _, hnoCap⟩
      have hp := hS .noCapBoth hnoCap .revokePrimary (by simp [withCapabilityLoss])
      rcases hp with ⟨_, _, hbackup⟩
      have hb := hS .backupOnlyNoCap hbackup .revokeBackup (by simp [withCapabilityLoss])
      rcases hb with ⟨s', hstep, _⟩
      simp [step] at hstep
  | noCapBoth =>
      have hp := hS .noCapBoth hs .revokePrimary (by simp [withCapabilityLoss])
      rcases hp with ⟨_, _, hbackup⟩
      have hb := hS .backupOnlyNoCap hbackup .revokeBackup (by simp [withCapabilityLoss])
      rcases hb with ⟨s', hstep, _⟩
      simp [step] at hstep
  | primaryOnlyNoCap =>
      have hp := hS .primaryOnlyNoCap hs .revokePrimary (by simp [withCapabilityLoss])
      rcases hp with ⟨s', hstep, _⟩
      simp [step] at hstep
  | backupOnlyNoCap =>
      have hb := hS .backupOnlyNoCap hs .revokeBackup (by simp [withCapabilityLoss])
      rcases hb with ⟨s', hstep, _⟩
      simp [step] at hstep

def EmptyKernel (_ : State) : Prop := False

theorem capability_loss_empty_kernel_postfixed :
    PostFixed step withCapabilityLoss EmptyKernel := by
  intro s hs
  exact False.elim hs

theorem capability_loss_empty_kernel_greatest
    (S : State → Prop)
    (hS : PostFixed step withCapabilityLoss S) :
    ∀ s, S s → EmptyKernel s := by
  intro s hs
  exact capability_loss_no_postfixed_state S hS s hs

theorem admitting_capability_loss_collapses_kernel :
    SupportKernel .adaptive ∧
    (∀ S : State → Prop,
      PostFixed step withCapabilityLoss S →
      ∀ s, ¬ S s) := by
  constructor
  · rfl
  · exact capability_loss_no_postfixed_state

/-!
Concrete proof-carrying authority fixture.

Indices:
  0 primary root
  1 primary consequence
  2 backup root
  3 backup consequence
  4 verified repair capability

Repair entries explicitly depend on capability 4. Therefore revoking capability
4 invalidates any repair cone whose warrant depends on it.
-/

def capabilityBase : List WarrantEntry := [
  ⟨[], none⟩,
  ⟨[0], none⟩,
  ⟨[], none⟩,
  ⟨[2], none⟩,
  ⟨[], none⟩
]

def primaryRevoked : List WarrantEntry :=
  capabilityBase ++ [⟨[], some 0⟩]

def primaryRepaired : List WarrantEntry :=
  primaryRevoked ++ [
    ⟨[4], none⟩,
    ⟨[6], none⟩
  ]

def repairedThenCapabilityRevoked : List WarrantEntry :=
  primaryRepaired ++ [⟨[], some 4⟩]

def capabilityRevoked : List WarrantEntry :=
  capabilityBase ++ [⟨[], some 4⟩]

def capabilityThenPrimaryRevoked : List WarrantEntry :=
  capabilityRevoked ++ [⟨[], some 0⟩]

def repairAttemptAfterCapabilityLoss : List WarrantEntry :=
  capabilityThenPrimaryRevoked ++ [
    ⟨[4], none⟩,
    ⟨[7], none⟩
  ]

theorem capability_base_live :
    warrantLive capabilityBase = [0, 1, 2, 3, 4] := by
  decide

theorem primary_repair_is_capability_backed :
    warrantLive primaryRepaired = [2, 3, 4, 6, 7] := by
  decide

/-- Revoking the repair capability invalidates the repair cone that depended
    on it; only the independent backup chain remains live. -/
theorem capability_revocation_cuts_repair_cone :
    warrantLive repairedThenCapabilityRevoked = [2, 3] := by
  decide

theorem capability_revocation_preserves_history :
    repairedThenCapabilityRevoked.length = capabilityBase.length + 4 := by
  decide

/-- If capability is already revoked, appending a would-be replacement whose
    premise is that capability does not create live authority. -/
theorem no_repair_after_capability_loss :
    warrantLive repairAttemptAfterCapabilityLoss = [2, 3] := by
  decide

/-- Concrete warrant semantics justify the abstract distinction:
    repair succeeds while capability 4 is live, and the same repair pattern
    fails to become live after capability 4 is revoked. -/
theorem concrete_capability_separator :
    warrantLive primaryRepaired = [2, 3, 4, 6, 7] ∧
    warrantLive repairAttemptAfterCapabilityLoss = [2, 3] := by
  exact ⟨primary_repair_is_capability_backed, no_repair_after_capability_loss⟩

end Metatron.WarrantedContinuationViabilityV2
