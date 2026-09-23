import Metatron.FutureObservations

namespace Metatron.DeathSpiral

open Metatron.FutureObservations

universe u v

/-- Every step in a trace belongs to the currently available action family. -/
def Allowed {Action : Type u}
    (allowed : List Action) (steps : List Action) : Prop :=
  ∀ a, a ∈ steps → a ∈ allowed

/-- A region is closed under the available action family when no available
    action can leave it once entered. -/
def ClosedUnder
    {State : Type u} {Action : Type v}
    (act : Action → State → State)
    (allowed : List Action)
    (region : State → Prop) : Prop :=
  ∀ a, a ∈ allowed → ∀ s, region s → region (act a s)

/-- Once a trajectory enters a region closed under the available actions,
    every allowed finite continuation remains in that region. -/
theorem closedUnder_run
    {State : Type u} {Action : Type v}
    (act : Action → State → State)
    (allowed : List Action)
    (region : State → Prop)
    (hclosed : ClosedUnder act allowed region) :
    ∀ steps s,
      Allowed allowed steps →
      region s →
      region (run act steps s) := by
  intro steps
  induction steps with
  | nil =>
      intro s hallowed hs
      simpa [run] using hs
  | cons a rest ih =>
      intro s hallowed hs
      have ha : a ∈ allowed := hallowed a (by simp)
      have hrest : Allowed allowed rest := by
        intro q hq
        exact hallowed q (by simp [hq])
      have hnext : region (act a s) :=
        hclosed a ha s hs
      simpa [run] using ih (act a s) hrest hnext

/-- A restriction creates a trap relative to the full action family when the
    region is closed under restricted actions but some full action can leave it. -/
def RestrictionCreatesTrap
    {State : Type u} {Action : Type v}
    (act : Action → State → State)
    (full restricted : List Action)
    (region : State → Prop) : Prop :=
  ClosedUnder act restricted region ∧
    ∃ a, a ∈ full ∧ a ∉ restricted ∧
      ∃ s, region s ∧ ¬ region (act a s)

/-! Minimal four-state witness. -/

inductive State where
  | start
  | left
  | right
  | out
  deriving DecidableEq, Repr

inductive Action where
  | follow
  | escape
  deriving DecidableEq, Repr

def act : Action → State → State
  | .follow, .start => .left
  | .follow, .left => .right
  | .follow, .right => .left
  | .follow, .out => .out
  | .escape, _ => .out

def full : List Action := [.follow, .escape]
def restricted : List Action := [.follow]

def trap : State → Prop
  | .left => True
  | .right => True
  | _ => False

theorem restricted_trap_closed :
    ClosedUnder act restricted trap := by
  intro a ha s hs
  have hfollow : a = Action.follow := by
    simpa [restricted] using ha
  subst a
  cases s <;> simp [trap, act] at hs ⊢

theorem escape_leaves_trap :
    trap State.left ∧ ¬ trap (act Action.escape State.left) := by
  simp [trap, act]

theorem restriction_creates_trap :
    RestrictionCreatesTrap act full restricted trap := by
  constructor
  · exact restricted_trap_closed
  · refine ⟨Action.escape, ?_, ?_, State.left, ?_⟩
    · simp [full]
    · simp [restricted]
    · exact escape_leaves_trap

theorem restricted_start_enters_trap :
    trap (run act [Action.follow] State.start) := by
  simp [run, act, trap]

theorem restricted_two_cycle :
    act Action.follow State.left = State.right ∧
    act Action.follow State.right = State.left := by
  exact ⟨rfl, rfl⟩

theorem full_left_has_escape :
    act Action.escape State.left = State.out := by
  rfl

theorem full_right_has_escape :
    act Action.escape State.right = State.out := by
  rfl

/-- Any restricted continuation starting after entry remains trapped. -/
theorem restricted_no_escape_after_entry
    (steps : List Action)
    (hallowed : Allowed restricted steps) :
    trap (run act steps State.left) := by
  apply closedUnder_run act restricted trap restricted_trap_closed
  · exact hallowed
  · simp [trap]

/-- The exact finite pattern behind the "death spiral" analogy:
    restriction removes the escape action, the unique remaining action funnels
    start into a closed two-cycle, while the full action family had an escape. -/
theorem finite_constraint_collapse_witness :
    RestrictionCreatesTrap act full restricted trap ∧
    trap (run act [Action.follow] State.start) ∧
    act Action.follow State.left = State.right ∧
    act Action.follow State.right = State.left ∧
    act Action.escape State.left = State.out := by
  exact ⟨
    restriction_creates_trap,
    restricted_start_enters_trap,
    rfl,
    rfl,
    rfl
  ⟩

end Metatron.DeathSpiral
