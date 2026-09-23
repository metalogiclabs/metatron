import Metatron.WarrantedContinuationViabilityV3
import Metatron.WarrantGraph
import Lean.Elab.Tactic.Omega

namespace Metatron.WarrantedContinuationViabilityV4

open Metatron.WarrantedContinuationViabilityV1

/-- Strict serial repair tower.

Depth 0 is failed.
At depth 1, failure class 0 is unrepairable.
At depth d+2, failure class d+1 removes the current outermost repair layer,
while every other failure class is either lower and repaired by the tower or
outside the currently live tower. -/
def towerStep : Nat → Nat → Option Nat
  | 0, _ => none
  | 1, 0 => none
  | 1, _ => some 1
  | d + 2, f =>
      if f = d + 1 then some (d + 1) else some (d + 2)

/-- A failure class strictly below the current outer boundary is absorbed. -/
theorem lower_failure_absorbed
    (d f : Nat)
    (h : f < d + 1) :
    towerStep (d + 2) f = some (d + 2) := by
  simp [towerStep]
  omega

/-- The current outermost failure class removes exactly one repair layer. -/
theorem outer_failure_removes_one_layer (d : Nat) :
    towerStep (d + 2) (d + 1) = some (d + 1) := by
  simp [towerStep]

/-- Adding one fresh outer repair layer turns the former outer failure
    into an absorbed lower failure. -/
theorem one_more_layer_moves_boundary (d : Nat) :
    towerStep (d + 2) d = some (d + 2) := by
  apply lower_failure_absorbed
  omega

theorem base_support_failure_unrepairable :
    towerStep 1 0 = none := by
  rfl

def cascade : Nat → List Nat
  | 0 => []
  | n + 1 => n :: cascade n

def runTower : Nat → List Nat → Option Nat
  | s, [] => some s
  | s, f :: fs =>
      match towerStep s f with
      | none => none
      | some s' => runTower s' fs

/-- A depth-n strict tower fails under the descending sequence of all its
    outer boundaries. This is the generic finite depth boundary law. -/
theorem descending_boundary_cascade_fails :
    ∀ n, runTower (n + 1) (cascade (n + 1)) = none := by
  intro n
  induction n with
  | zero =>
      rfl
  | succ n ih =>
      change runTower (n + 2) ((n + 1) :: cascade (n + 1)) = none
      rw [runTower, outer_failure_removes_one_layer]
      exact ih

def lowerAdmitted (depth : Nat) : List Nat :=
  List.range (depth - 1)

def TopKernel (depth s : Nat) : Prop :=
  s = depth

/-- For every positive depth, the full-depth state is post-fixed under all
    failure classes strictly below its outermost repair layer. -/
theorem top_depth_postfixed_under_lower_failures
    (depth : Nat)
    (hdepth : 0 < depth) :
    PostFixed towerStep (lowerAdmitted depth) (TopKernel depth) := by
  intro s hs
  subst s
  intro e he
  cases depth with
  | zero =>
      omega
  | succ d =>
      cases d with
      | zero =>
          simp [lowerAdmitted] at he
      | succ k =>
          have helow : e < k + 1 := by
            simpa [lowerAdmitted] using (List.mem_range.mp he)
          refine ⟨k + 2, ?_, rfl⟩
          apply lower_failure_absorbed
          omega

/-!
Cross-layer repair falsifier.

This fixture shows that the strict serial tower is sufficient for the generic
depth theorem above but is not a necessary authority geometry.

Indices:
0 support root
1 protected consequence
2 ordinary repair capability
3 shared cross-layer repair capability

After revoking ordinary repair 2 and support 0, shared capability 3 directly
warrants a fresh support root and consequence. Ordinary repair 2 remains
revoked. Thus support viability can be restored without first restoring the
missing intermediate repair layer.
-/

def crossLayerBase : List WarrantEntry := [
  ⟨[], none⟩,
  ⟨[0], none⟩,
  ⟨[], none⟩,
  ⟨[], none⟩
]

def ordinaryRepairRevoked : List WarrantEntry :=
  crossLayerBase ++ [⟨[], some 2⟩]

def ordinaryAndSupportRevoked : List WarrantEntry :=
  ordinaryRepairRevoked ++ [⟨[], some 0⟩]

def crossLayerSupportRepaired : List WarrantEntry :=
  ordinaryAndSupportRevoked ++ [
    ⟨[3], none⟩,
    ⟨[6], none⟩
  ]

theorem cross_layer_base_live :
    warrantLive crossLayerBase = [0, 1, 2, 3] := by
  decide

theorem cross_layer_both_revoked :
    warrantLive ordinaryAndSupportRevoked = [3] := by
  decide

theorem shared_capability_repairs_across_missing_layer :
    warrantLive crossLayerSupportRepaired = [3, 6, 7] := by
  decide

theorem ordinary_repair_remains_revoked :
    (warrantLive crossLayerSupportRepaired).contains 2 = false := by
  decide

/-- Exact falsifier of a universal strict-tower necessity claim:
    protected support can be restored while the intermediate ordinary repair
    capability remains revoked. -/
theorem strict_serial_tower_not_necessary :
    warrantLive crossLayerSupportRepaired = [3, 6, 7] ∧
    (warrantLive crossLayerSupportRepaired).contains 2 = false := by
  exact ⟨
    shared_capability_repairs_across_missing_layer,
    ordinary_repair_remains_revoked
  ⟩

end Metatron.WarrantedContinuationViabilityV4
