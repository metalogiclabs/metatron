import Metatron.Fixture

namespace Metatron

def renderNatList (xs : List Nat) : String :=
  String.intercalate "," (xs.map toString)

def stepTable : List Nat :=
  allStates.map (fun s => stateCode (step s))

def q0Table : List Nat :=
  allStates.map (fun s => boolCode (evalQuery Query.isZero s))

def q1Table : List Nat :=
  allStates.map (fun s => boolCode (evalQuery Query.isOne s))

def q0ProjectCode : Q0Class → Nat
  | .zero => 0
  | .nonzero => 1

def q0ProjectTable : List Nat :=
  allStates.map (fun s => q0ProjectCode (projectQ0 s))

def q0StepTable : List Nat :=
  [Q0Class.zero, Q0Class.nonzero].map (fun c =>
    q0ProjectCode (stepQ0 c))

def idempotentFlag : Nat :=
  boolCode (allStates.all (fun s => decide (step (step s) = step s)))

def compiledExactFlag : Nat :=
  boolCode (allStates.all (fun s =>
    decide (execInstr Instr.step s = step s)))

def referenceMain : IO Unit := do
  IO.println s!"STEP={renderNatList stepTable}"
  IO.println s!"Q0={renderNatList q0Table}"
  IO.println s!"Q1={renderNatList q1Table}"
  IO.println s!"Q0_PROJECT={renderNatList q0ProjectTable}"
  IO.println s!"Q0_STEP={renderNatList q0StepTable}"
  IO.println s!"IDEMPOTENT={idempotentFlag}"
  IO.println s!"COMPILED_EXACT={compiledExactFlag}"

end Metatron

def main : IO Unit := Metatron.referenceMain
