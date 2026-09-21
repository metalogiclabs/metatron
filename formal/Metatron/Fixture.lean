namespace Metatron

inductive State
  | zero | one | two
  deriving DecidableEq, Repr

inductive Query
  | isZero | isOne
  deriving DecidableEq, Repr

def idCap : State → State := fun s => s

def step : State → State
  | .zero => .one
  | .one => .one
  | .two => .two

def evalQuery : Query → State → Bool
  | .isZero, .zero => true
  | .isZero, _ => false
  | .isOne, .one => true
  | .isOne, _ => false

theorem base_cannot_solve_step : idCap State.zero ≠ step State.zero := by
  intro h
  cases h

theorem step_idempotent (s : State) : step (step s) = step s := by
  cases s <;> rfl

theorem q0_merges_one_two :
    evalQuery Query.isZero State.one = evalQuery Query.isZero State.two := rfl

theorem q1_separates_one_two :
    evalQuery Query.isOne State.one ≠ evalQuery Query.isOne State.two := by
  decide

inductive Q0Class
  | zero | nonzero
  deriving DecidableEq, Repr

def projectQ0 : State → Q0Class
  | .zero => .zero
  | .one => .nonzero
  | .two => .nonzero

def stepQ0 : Q0Class → Q0Class
  | .zero => .nonzero
  | .nonzero => .nonzero

theorem step_commutes_q0 (s : State) :
    projectQ0 (step s) = stepQ0 (projectQ0 s) := by
  cases s <;> rfl

inductive Instr
  | id | step
  deriving DecidableEq, Repr

def execInstr : Instr → State → State
  | .id => idCap
  | .step => step

theorem compiled_step_exact (s : State) :
    execInstr Instr.step s = step s := rfl

structure AuthoritySnapshot where
  stepLive : Bool
  deriving Repr

def executeStep (Ω : AuthoritySnapshot) (s : State) : Option State :=
  if Ω.stepLive then some (step s) else none

theorem revoked_step_denied (s : State) :
    executeStep ⟨false⟩ s = none := rfl

def stateCode : State → Nat
  | .zero => 0
  | .one => 1
  | .two => 2

def boolCode (b : Bool) : Nat := if b then 1 else 0

def allStates : List State := [.zero, .one, .two]

end Metatron
