namespace Metatron

structure WarrantEntry where
  premises : List Nat
  revokes : Option Nat
  deriving DecidableEq, Repr

def warrantRevoked (log : List WarrantEntry) (i : Nat) : Bool :=
  log.any (fun entry => entry.revokes == some i)

def warrantStep
    (log : List WarrantEntry)
    (state : Nat × List Nat)
    (entry : WarrantEntry) : Nat × List Nat :=
  let i := state.1
  let live := state.2
  let nextLive :=
    if entry.revokes.isSome then
      live
    else if warrantRevoked log i then
      live
    else if entry.premises.all (fun premise => live.contains premise) then
      live ++ [i]
    else
      live
  (i + 1, nextLive)

def warrantLive (log : List WarrantEntry) : List Nat :=
  (log.foldl (warrantStep log) (0, [])).2

def warrantBaseline : List WarrantEntry := [
  ⟨[], none⟩,
  ⟨[0], none⟩,
  ⟨[1], none⟩,
  ⟨[], none⟩
]

def warrantRevokedFixture : List WarrantEntry :=
  warrantBaseline ++ [⟨[], some 1⟩]

theorem warrant_baseline_all_live :
    warrantLive warrantBaseline = [0, 1, 2, 3] := by
  decide

theorem warrant_revocation_cuts_dependency_cone :
    warrantLive warrantRevokedFixture = [0, 3] := by
  decide

theorem warrant_history_is_not_deleted :
    warrantRevokedFixture.length = warrantBaseline.length + 1 := by
  rfl

end Metatron
