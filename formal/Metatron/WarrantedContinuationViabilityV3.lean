import Metatron.WarrantedContinuationViabilityV2
import Metatron.WarrantGraph

namespace Metatron.WarrantedContinuationViabilityV3
open Metatron.WarrantedContinuationViabilityV1

inductive State where
  | metaAdaptive | repairOnly | noCapBoth | primaryOnlyNoCap | backupOnlyNoCap
  deriving DecidableEq, Repr

inductive Encounter where
  | revokePrimary | revokeBackup | revokeRepair | revokeMeta
  deriving DecidableEq, Repr

def depthOne : List Encounter := [.revokePrimary,.revokeBackup,.revokeRepair]
def withMetaLoss : List Encounter := [.revokePrimary,.revokeBackup,.revokeRepair,.revokeMeta]

def step : State → Encounter → Option State
  | .metaAdaptive, .revokeMeta => some .repairOnly
  | .metaAdaptive, _ => some .metaAdaptive
  | .repairOnly, .revokeRepair => some .noCapBoth
  | .repairOnly, _ => some .repairOnly
  | .noCapBoth, .revokePrimary => some .backupOnlyNoCap
  | .noCapBoth, .revokeBackup => some .primaryOnlyNoCap
  | .noCapBoth, _ => some .noCapBoth
  | .primaryOnlyNoCap, .revokePrimary => none
  | .primaryOnlyNoCap, _ => some .primaryOnlyNoCap
  | .backupOnlyNoCap, .revokeBackup => none
  | .backupOnlyNoCap, _ => some .backupOnlyNoCap

def DepthOneKernel (s : State) : Prop := s = .metaAdaptive

theorem depth_one_kernel_postfixed :
    PostFixed step depthOne DepthOneKernel := by
  intro s hs
  subst s
  intro e he
  simp [depthOne] at he
  rcases he with rfl | rfl | rfl <;> exact ⟨.metaAdaptive, rfl, rfl⟩

theorem depth_one_kernel_greatest
    (S : State → Prop) (hS : PostFixed step depthOne S) :
    ∀ s, S s → DepthOneKernel s := by
  intro s hs
  cases s with
  | metaAdaptive => rfl
  | repairOnly =>
      have h1 := hS .repairOnly hs .revokeRepair (by simp [depthOne])
      rcases h1 with ⟨s1, he1, hs1⟩
      have : s1 = .noCapBoth := by simpa [step] using he1.symm
      subst s1
      have h2 := hS .noCapBoth hs1 .revokePrimary (by simp [depthOne])
      rcases h2 with ⟨s2, he2, hs2⟩
      have : s2 = .backupOnlyNoCap := by simpa [step] using he2.symm
      subst s2
      have h3 := hS .backupOnlyNoCap hs2 .revokeBackup (by simp [depthOne])
      rcases h3 with ⟨s3, he3, _⟩
      simp [step] at he3
  | noCapBoth =>
      have h2 := hS .noCapBoth hs .revokePrimary (by simp [depthOne])
      rcases h2 with ⟨s2, he2, hs2⟩
      have : s2 = .backupOnlyNoCap := by simpa [step] using he2.symm
      subst s2
      have h3 := hS .backupOnlyNoCap hs2 .revokeBackup (by simp [depthOne])
      rcases h3 with ⟨s3, he3, _⟩
      simp [step] at he3
  | primaryOnlyNoCap =>
      have h := hS .primaryOnlyNoCap hs .revokePrimary (by simp [depthOne])
      rcases h with ⟨s1, he, _⟩
      simp [step] at he
  | backupOnlyNoCap =>
      have h := hS .backupOnlyNoCap hs .revokeBackup (by simp [depthOne])
      rcases h with ⟨s1, he, _⟩
      simp [step] at he

theorem meta_repair_restores_nonempty_kernel :
    DepthOneKernel .metaAdaptive ∧ PostFixed step depthOne DepthOneKernel :=
  ⟨rfl, depth_one_kernel_postfixed⟩

theorem meta_loss_no_postfixed_state
    (S : State → Prop) (hS : PostFixed step withMetaLoss S) :
    ∀ s, ¬ S s := by
  intro s hs
  cases s with
  | metaAdaptive =>
      have h0 := hS .metaAdaptive hs .revokeMeta (by simp [withMetaLoss])
      rcases h0 with ⟨s0, he0, hs0⟩
      have : s0 = .repairOnly := by simpa [step] using he0.symm
      subst s0
      have h1 := hS .repairOnly hs0 .revokeRepair (by simp [withMetaLoss])
      rcases h1 with ⟨s1, he1, hs1⟩
      have : s1 = .noCapBoth := by simpa [step] using he1.symm
      subst s1
      have h2 := hS .noCapBoth hs1 .revokePrimary (by simp [withMetaLoss])
      rcases h2 with ⟨s2, he2, hs2⟩
      have : s2 = .backupOnlyNoCap := by simpa [step] using he2.symm
      subst s2
      have h3 := hS .backupOnlyNoCap hs2 .revokeBackup (by simp [withMetaLoss])
      rcases h3 with ⟨s3, he3, _⟩
      simp [step] at he3
  | repairOnly =>
      have h1 := hS .repairOnly hs .revokeRepair (by simp [withMetaLoss])
      rcases h1 with ⟨s1, he1, hs1⟩
      have : s1 = .noCapBoth := by simpa [step] using he1.symm
      subst s1
      have h2 := hS .noCapBoth hs1 .revokePrimary (by simp [withMetaLoss])
      rcases h2 with ⟨s2, he2, hs2⟩
      have : s2 = .backupOnlyNoCap := by simpa [step] using he2.symm
      subst s2
      have h3 := hS .backupOnlyNoCap hs2 .revokeBackup (by simp [withMetaLoss])
      rcases h3 with ⟨s3, he3, _⟩
      simp [step] at he3
  | noCapBoth =>
      have h2 := hS .noCapBoth hs .revokePrimary (by simp [withMetaLoss])
      rcases h2 with ⟨s2, he2, hs2⟩
      have : s2 = .backupOnlyNoCap := by simpa [step] using he2.symm
      subst s2
      have h3 := hS .backupOnlyNoCap hs2 .revokeBackup (by simp [withMetaLoss])
      rcases h3 with ⟨s3, he3, _⟩
      simp [step] at he3
  | primaryOnlyNoCap =>
      have h := hS .primaryOnlyNoCap hs .revokePrimary (by simp [withMetaLoss])
      rcases h with ⟨s1, he, _⟩
      simp [step] at he
  | backupOnlyNoCap =>
      have h := hS .backupOnlyNoCap hs .revokeBackup (by simp [withMetaLoss])
      rcases h with ⟨s1, he, _⟩
      simp [step] at he

theorem one_more_repair_layer_moves_the_boundary :
    PostFixed step depthOne DepthOneKernel ∧
    (∀ S : State → Prop, PostFixed step withMetaLoss S → ∀ s, ¬ S s) :=
  ⟨depth_one_kernel_postfixed, meta_loss_no_postfixed_state⟩

def recursiveBase : List WarrantEntry := [
  ⟨[],none⟩, ⟨[0],none⟩, ⟨[],none⟩, ⟨[2],none⟩, ⟨[],none⟩, ⟨[],none⟩
]
def repairCapabilityRevoked := recursiveBase ++ [⟨[],some 4⟩]
def repairCapabilityRestored := repairCapabilityRevoked ++ [⟨[5],none⟩]
def restoredRepairThenPrimaryRevoked := repairCapabilityRestored ++ [⟨[],some 0⟩]
def supportRepairedByRestoredCapability :=
  restoredRepairThenPrimaryRevoked ++ [⟨[7],none⟩, ⟨[9],none⟩]
def restoredRepairThenMetaRevoked := repairCapabilityRestored ++ [⟨[],some 5⟩]
def metaRevoked := recursiveBase ++ [⟨[],some 5⟩]
def metaThenRepairRevoked := metaRevoked ++ [⟨[],some 4⟩]
def metaRepairAttempt := metaThenRepairRevoked ++ [⟨[5],none⟩]

theorem recursive_base_live :
    warrantLive recursiveBase = [0,1,2,3,4,5] := by decide
theorem meta_restores_repair_capability :
    warrantLive repairCapabilityRestored = [0,1,2,3,5,7] := by decide
theorem restored_capability_repairs_support :
    warrantLive supportRepairedByRestoredCapability = [2,3,5,7,9,10] := by decide
theorem meta_revocation_cuts_restored_repair :
    warrantLive restoredRepairThenMetaRevoked = [0,1,2,3] := by decide
theorem no_meta_repair_after_meta_loss :
    warrantLive metaRepairAttempt = [0,1,2,3] := by decide

theorem recursive_authority_separator :
    warrantLive repairCapabilityRestored = [0,1,2,3,5,7] ∧
    warrantLive restoredRepairThenMetaRevoked = [0,1,2,3] :=
  ⟨meta_restores_repair_capability, meta_revocation_cuts_restored_repair⟩

end Metatron.WarrantedContinuationViabilityV3
