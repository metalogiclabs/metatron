import Std

namespace Metatron.WarrantedContinuationViability

universe u v

/-- Deterministic objective-viability runner.
    none is the fail-closed UNKNOWN boundary: no lawful continuation
    was available for the current encounter. -/
def runViable
    {State : Type u} {Encounter : Type v}
    (step : State → Encounter → Option State) :
    State → List Encounter → Option State
  | s, [] => some s
  | s, e :: es =>
      match step s e with
      | none => none
      | some s' => runViable step s' es

/-- Successful local continuation preserves a protected invariant. -/
def StepPreserves
    {State : Type u} {Encounter : Type v}
    (guarded : State → Prop)
    (step : State → Encounter → Option State) : Prop :=
  ∀ s e s', guarded s → step s e = some s' → guarded s'

/-- Local protected-continuation preservation composes across every
    successful finite encounter stream. -/
theorem runViable_preserves
    {State : Type u} {Encounter : Type v}
    (guarded : State → Prop)
    (step : State → Encounter → Option State)
    (hstep : StepPreserves guarded step) :
    ∀ s es s',
      guarded s →
      runViable step s es = some s' →
      guarded s' := by
  intro s es
  induction es generalizing s with
  | nil =>
      intro s' hs hrun
      simp [runViable] at hrun
      cases hrun
      exact hs
  | cons e es ih =>
      intro s' hs hrun
      cases hse : step s e with
      | none =>
          simp [runViable, hse] at hrun
      | some s1 =>
          have hs1 : guarded s1 :=
            hstep s e s1 hs hse
          have htail : runViable step s1 es = some s' := by
            simpa [runViable, hse] using hrun
          exact ih s1 s' hs1 htail

/-- Viable continuation is compositional across concatenated encounter streams. -/
theorem runViable_append
    {State : Type u} {Encounter : Type v}
    (step : State → Encounter → Option State) :
    ∀ s xs ys,
      runViable step s (xs ++ ys) =
        (runViable step s xs).bind (fun s' => runViable step s' ys) := by
  intro s xs
  induction xs generalizing s with
  | nil =>
      intro ys
      simp [runViable]
  | cons e es ih =>
      intro ys
      cases hse : step s e with
      | none =>
          simp [runViable, hse]
      | some s1 =>
          simp [runViable, hse, ih]

inductive Residual where
  | alpha
  | beta
  deriving DecidableEq, Repr

inductive Outcome where
  | reused
  | acquired
  | unknown
  deriving DecidableEq, Repr

structure DevState where
  budgetAlpha : Nat
  budgetBeta : Nat
  compiledAlpha : Bool := false
  compiledBeta : Bool := false
  liveAlpha : Bool := false
  liveBeta : Bool := false
  guarded : Bool := true
  deriving DecidableEq, Repr

def typedBudget : DevState → Residual → Nat
  | s, .alpha => s.budgetAlpha
  | s, .beta => s.budgetBeta

def liveRepair : DevState → Residual → Bool
  | s, .alpha => s.liveAlpha
  | s, .beta => s.liveBeta

/-- Minimal finite Flash-style reclosure:
    compiled typed repairs become live reusable authority. -/
def reclose (s : DevState) : DevState :=
  { s with
      liveAlpha := s.compiledAlpha
      liveBeta := s.compiledBeta }

/-- Acquire one typed repair and retain it as compiled lineage. -/
def acquire (s : DevState) : Residual → DevState
  | .alpha =>
      { s with
          budgetAlpha := s.budgetAlpha - 1
          compiledAlpha := true }
  | .beta =>
      { s with
          budgetBeta := s.budgetBeta - 1
          compiledBeta := true }

/-- Objective continuation step:
    reuse if already live; otherwise spend typed acquisition capacity;
    otherwise return UNKNOWN as none. -/
def objectiveStep (s : DevState) (r : Residual) : Option DevState :=
  if liveRepair s r then
    some (reclose s)
  else if 0 < typedBudget s r then
    some (reclose (acquire s r))
  else
    none

/-- Total authority step records UNKNOWN rather than fabricating a repair. -/
def authorityStep (s : DevState) (r : Residual) : DevState × Outcome :=
  if liveRepair s r then
    (reclose s, .reused)
  else if 0 < typedBudget s r then
    (reclose (acquire s r), .acquired)
  else
    (s, .unknown)

def runAuthority :
    DevState → List Residual → DevState × List Outcome
  | s, [] => (s, [])
  | s, r :: rs =>
      let first := authorityStep s r
      let rest := runAuthority first.1 rs
      (rest.1, first.2 :: rest.2)

def objectiveViable (s : DevState) (stream : List Residual) : Bool :=
  (runViable objectiveStep s stream).isSome

/-- Aggregate scalar summary intentionally forgets residual type. -/
def scalarSummary (s : DevState) (stream : List Residual) : Nat × Nat :=
  (s.budgetAlpha + s.budgetBeta, stream.length)

def balanced : DevState :=
  { budgetAlpha := 1, budgetBeta := 1 }

def skewed : DevState :=
  { budgetAlpha := 2, budgetBeta := 0 }

def encounterStream : List Residual :=
  [.alpha, .beta, .alpha, .beta]

theorem same_scalar_summary :
    scalarSummary balanced encounterStream =
      scalarSummary skewed encounterStream := by
  decide

theorem balanced_objective_viable :
    objectiveViable balanced encounterStream = true := by
  decide

theorem skewed_not_objective_viable :
    objectiveViable skewed encounterStream = false := by
  decide

theorem balanced_authority_trace :
    (runAuthority balanced encounterStream).2 =
      [.acquired, .acquired, .reused, .reused] := by
  decide

theorem skewed_authority_trace :
    (runAuthority skewed encounterStream).2 =
      [.acquired, .unknown, .reused, .unknown] := by
  decide

theorem both_preserve_guarded_boundary :
    (runAuthority balanced encounterStream).1.guarded = true ∧
    (runAuthority skewed encounterStream).1.guarded = true := by
  decide

theorem skewed_unknown_does_not_fabricate_beta :
    (runAuthority skewed encounterStream).1.compiledBeta = false ∧
    (runAuthority skewed encounterStream).1.liveBeta = false := by
  decide

/-- Exact scalar-insufficiency falsifier:
    identical aggregate capacity and disturbance count do not determine
    typed protected-objective viability. -/
theorem same_scalar_different_typed_viability :
    scalarSummary balanced encounterStream =
      scalarSummary skewed encounterStream ∧
    objectiveViable balanced encounterStream = true ∧
    objectiveViable skewed encounterStream = false := by
  decide

/-- Compounding witness: after the first typed acquisition of each class,
    the balanced system reuses both repairs on repeated encounters. -/
theorem reclosure_compiles_future_reuse :
    (runAuthority balanced encounterStream).2 =
      [.acquired, .acquired, .reused, .reused] := by
  decide

end Metatron.WarrantedContinuationViability
