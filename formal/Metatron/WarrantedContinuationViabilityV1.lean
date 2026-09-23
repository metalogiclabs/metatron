import Metatron.WarrantedContinuationViability
import Metatron.WarrantGraph
import Metatron.ProofRelevantOplax

namespace Metatron.WarrantedContinuationViabilityV1

open Metatron.WarrantedContinuationViability

universe u v

/-- One-step viability predecessor over a declared encounter family. -/
def ViablePre
    {State : Type u} {Encounter : Type v}
    (step : State → Encounter → Option State)
    (admitted : List Encounter)
    (S : State → Prop)
    (s : State) : Prop :=
  ∀ e, e ∈ admitted → ∃ s', step s e = some s' ∧ S s'

/-- A set is post-fixed when every admitted encounter has a successor
    remaining inside the set. -/
def PostFixed
    {State : Type u} {Encounter : Type v}
    (step : State → Encounter → Option State)
    (admitted : List Encounter)
    (S : State → Prop) : Prop :=
  ∀ s, S s → ViablePre step admitted S s

inductive KernelState where
  | adaptive
  | primaryOnly
  | backupOnly
  | none
  deriving DecidableEq, Repr

inductive Encounter where
  | revokePrimary
  | revokeBackup
  deriving DecidableEq, Repr

def admitted : List Encounter :=
  [.revokePrimary, .revokeBackup]

/-- Abstract finite quotient of the developmental state after revocation
    and verified reclosure.

    adaptive retains a verified repair capability that restores whichever
    support was revoked before the next admitted encounter.

    primaryOnly and backupOnly have no repair for loss of their last support.
-/
def step : KernelState → Encounter → Option KernelState
  | .adaptive, _ => some .adaptive
  | .primaryOnly, .revokePrimary => none
  | .primaryOnly, .revokeBackup => some .primaryOnly
  | .backupOnly, .revokePrimary => some .backupOnly
  | .backupOnly, .revokeBackup => none
  | .none, _ => none

def Kernel (s : KernelState) : Prop :=
  s = .adaptive

theorem kernel_postfixed :
    PostFixed step admitted Kernel := by
  intro s hs
  subst s
  intro e he
  exact ⟨.adaptive, by cases e <;> rfl, rfl⟩

/-- Greatest-postfixed-set characterization: every set closed under all
    admitted encounters is contained in Kernel. This is the finite
    greatest-fixed-point viability theorem for the declared system. -/
theorem kernel_greatest
    (S : KernelState → Prop)
    (hS : PostFixed step admitted S) :
    ∀ s, S s → Kernel s := by
  intro s hs
  cases s with
  | adaptive =>
      rfl
  | primaryOnly =>
      have h := hS .primaryOnly hs .revokePrimary (by simp [admitted])
      rcases h with ⟨s', hstep, _⟩
      simp [step] at hstep
  | backupOnly =>
      have h := hS .backupOnly hs .revokeBackup (by simp [admitted])
      rcases h with ⟨s', hstep, _⟩
      simp [step] at hstep
  | none =>
      have h := hS .none hs .revokePrimary (by simp [admitted])
      rcases h with ⟨s', hstep, _⟩
      simp [step] at hstep

theorem kernel_exact :
    Kernel .adaptive ∧
    ¬ Kernel .primaryOnly ∧
    ¬ Kernel .backupOnly ∧
    ¬ Kernel .none := by
  simp [Kernel]

/-!
Concrete warrant-log reclosure fixtures.

The base log has two independent two-node support chains:
  0 -> 1
  2 -> 3

A revocation entry removes one root and its dependent consequence.
A fresh verified root plus dependent consequence is then appended.
warrantLive recomputes the live view from the append-only history.
-/

def dualSupportBase : List WarrantEntry := [
  ⟨[], none⟩,
  ⟨[0], none⟩,
  ⟨[], none⟩,
  ⟨[2], none⟩
]

def primaryRevoked : List WarrantEntry :=
  dualSupportBase ++ [⟨[], some 0⟩]

def primaryRepaired : List WarrantEntry :=
  primaryRevoked ++ [
    ⟨[], none⟩,
    ⟨[5], none⟩
  ]

def backupRevoked : List WarrantEntry :=
  dualSupportBase ++ [⟨[], some 2⟩]

def backupRepaired : List WarrantEntry :=
  backupRevoked ++ [
    ⟨[], none⟩,
    ⟨[5], none⟩
  ]

theorem dual_support_base_live :
    warrantLive dualSupportBase = [0, 1, 2, 3] := by
  decide

theorem primary_revocation_cuts_cone :
    warrantLive primaryRevoked = [2, 3] := by
  decide

theorem primary_verified_repair_recloses :
    warrantLive primaryRepaired = [2, 3, 5, 6] := by
  decide

theorem backup_revocation_cuts_cone :
    warrantLive backupRevoked = [0, 1] := by
  decide

theorem backup_verified_repair_recloses :
    warrantLive backupRepaired = [0, 1, 5, 6] := by
  decide

theorem repair_history_is_append_only :
    primaryRepaired.length = dualSupportBase.length + 3 ∧
    backupRepaired.length = dualSupportBase.length + 3 := by
  decide

/-!
Proof-lifted Flash-style support already present in Metatron:
revoking certificate 11 kills one closure trace while an alternative
certified trace survives. V1 consumes that existing theorem rather than
reimplementing proof-lifted closure.
-/

open Metatron.ProofRelevantOplax

theorem proof_lifted_revocation_preserves_alternative :
    (¬ TraceLive 11 (closureTrace flashCert flashPath₁)) ∧
    TraceLive 11 (closureTrace flashCert flashPath₂) := by
  exact ⟨
    flash_revocation_removes_one_support,
    flash_alternative_support_survives
  ⟩

/-- Concrete reclosure evidence and the abstract greatest viability kernel
    meet at the intended boundary: adaptive is the only state whose declared
    repair policy has a successor for every admitted revocation. -/
theorem adaptive_handles_every_admitted_revocation :
    ViablePre step admitted Kernel .adaptive := by
  exact kernel_postfixed .adaptive rfl

end Metatron.WarrantedContinuationViabilityV1
