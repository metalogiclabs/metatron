import CLC.Support
import Metatron.WarrantGraph

namespace CLCMetatronAdapter

open CLC
open Metatron

def revokedTargets (L : List WarrantEntry) : List Nat :=
  L.filterMap (fun entry => entry.revokes)

theorem mem_revokedTargets_warrantRevoked_true
    {L : List WarrantEntry} {i : Nat}
    (h : i ∈ revokedTargets L) :
    warrantRevoked L i = true := by
  simpa [revokedTargets, warrantRevoked] using h

theorem warrantStep_preserves_not_revoked
    (L : List WarrantEntry)
    (state : Nat × List Nat)
    (entry : WarrantEntry)
    (h : ∀ j ∈ state.2, warrantRevoked L j = false) :
    ∀ j ∈ (warrantStep L state entry).2, warrantRevoked L j = false := by
  intro j hj
  cases hentry : entry.revokes with
  | some target =>
      have hj' : j ∈ state.2 := by
        simpa [warrantStep, hentry] using hj
      exact h j hj'
  | none =>
      cases hcur : warrantRevoked L state.1 with
      | true =>
          have hj' : j ∈ state.2 := by
            simpa [warrantStep, hentry, hcur] using hj
          exact h j hj'
      | false =>
          by_cases hprem :
              ∀ premise ∈ entry.premises, premise ∈ state.2
          · have hj' : j ∈ state.2 ∨ j = state.1 := by
              simpa [warrantStep, hentry, hcur, hprem] using hj
            rcases hj' with hjOld | rfl
            · exact h j hjOld
            · exact hcur
          · have hj' : j ∈ state.2 := by
              simpa [warrantStep, hentry, hcur, hprem] using hj
            exact h j hj'

theorem fold_preserves_not_revoked
    (L xs : List WarrantEntry)
    (state : Nat × List Nat)
    (h : ∀ j ∈ state.2, warrantRevoked L j = false) :
    ∀ j ∈ (xs.foldl (warrantStep L) state).2,
      warrantRevoked L j = false := by
  induction xs generalizing state with
  | nil =>
      intro j hj
      exact h j hj
  | cons entry rest ih =>
      simp only [List.foldl_cons]
      exact ih (warrantStep L state entry)
        (warrantStep_preserves_not_revoked L state entry h)

theorem warrant_live_not_revoked (L : List WarrantEntry) :
    ∀ j ∈ warrantLive L, warrantRevoked L j = false := by
  intro j hj
  unfold warrantLive at hj
  exact fold_preserves_not_revoked L L (0, []) (by simp) j hj

theorem live_revoked_disjoint (L : List WarrantEntry) :
    Disjoint (warrantLive L).toFinset (revokedTargets L).toFinset := by
  rw [Finset.disjoint_left]
  intro i hiLive hiRevoked
  have hiLive' : i ∈ warrantLive L := by
    simpa using hiLive
  have hiRevoked' : i ∈ revokedTargets L := by
    simpa using hiRevoked
  have hFalse := warrant_live_not_revoked L i hiLive'
  have hTrue := mem_revokedTargets_warrantRevoked_true hiRevoked'
  rw [hTrue] at hFalse
  simp at hFalse

def snapshotOf (L : List WarrantEntry) : CLC.TokenSnapshot Nat where
  live := (warrantLive L).toFinset
  revoked := (revokedTargets L).toFinset
  disjoint := live_revoked_disjoint L

theorem warrant_support_iff
    (L : List WarrantEntry)
    (F : CLC.SupportFamily Nat) :
    (CLC.liveView (snapshotOf L) F).Nonempty ↔
      ∃ s ∈ F, ∀ i ∈ s, i ∈ Metatron.warrantLive L := by
  constructor
  · intro h
    rcases CLC.normalize_live_nonempty_iff.mp h with ⟨s, hsF, hsLive⟩
    refine ⟨s, hsF, ?_⟩
    change s ⊆ (snapshotOf L).live at hsLive
    intro i hi
    have hiFin : i ∈ (snapshotOf L).live := hsLive hi
    simpa [snapshotOf] using hiFin
  · rintro ⟨s, hsF, hs⟩
    apply CLC.normalize_live_nonempty_iff.mpr
    refine ⟨s, hsF, ?_⟩
    change s ⊆ (snapshotOf L).live
    intro i hi
    have hiLive : i ∈ warrantLive L := hs i hi
    simpa [snapshotOf] using hiLive

end CLCMetatronAdapter
