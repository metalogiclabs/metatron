namespace Metatron

structure WarrantEntry where
  premises : List Nat
  revokes : Option Nat := none
  deriving DecidableEq, Repr

def warrantRevoked (log : List WarrantEntry) (i : Nat) : Bool :=
  log.any (fun entry => entry.revokes == some i)

def warrantStep
    (log : List WarrantEntry)
    (live : List Nat)
    (i : Nat) : List Nat :=
  match log.get? i with
  | none => live
  | some entry =>
      if entry.revokes.isSome then
        live
      else if warrantRevoked log i then
        live
      else if entry.premises.all (fun premise => live.contains premise) then
        live ++ [i]
      else
        live

def warrantLive (log : List WarrantEntry) : List Nat :=
  (List.range log.length).foldl (warrantStep log) []

def warrantBaseline : List WarrantEntry := [
  ⟨[]⟩,
  ⟨[0]⟩,
  ⟨[1]⟩,
  ⟨[]⟩
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
