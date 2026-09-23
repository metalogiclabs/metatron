import Std

namespace Metatron.TemporalConcentration

universe u v w

/-- Equality of histories induced by their current downstream consequence. -/
def KernelOf {A : Type u} {B : Type v} (f : A → B) : A → A → Prop :=
  fun x y => f x = f y

/-- Deterministic postcomposition cannot split histories that have already
    been identified by an upstream map. -/
theorem kernel_postcompose_mono
    {A : Type u} {B : Type v} {C : Type w}
    (f : A → B) (g : B → C)
    {x y : A}
    (h : KernelOf f x y) :
    KernelOf (fun a => g (f a)) x y := by
  exact congrArg g h

/-- A strict concentration witness: two histories are distinct at one stage
    but become equal after the next deterministic gate. -/
def StrictConcentrationWitness
    {A : Type u} {B : Type v} {C : Type w}
    (f : A → B) (g : B → C) (x y : A) : Prop :=
  f x ≠ f y ∧ g (f x) = g (f y)

/-- Any strict witness shows that the postcomposed kernel is strictly coarser
    on at least one pair. -/
theorem strict_witness_adds_identification
    {A : Type u} {B : Type v} {C : Type w}
    {f : A → B} {g : B → C} {x y : A}
    (h : StrictConcentrationWitness f g x y) :
    ¬ KernelOf f x y ∧ KernelOf (fun a => g (f a)) x y := by
  exact ⟨h.1, h.2⟩

/-! A minimal fixed-gate fixture: four departures compress to three
    intermediate event times and then to two downstream event times. -/

inductive Departure where
  | t0 | t1 | t2 | t3
  deriving DecidableEq, Repr

inductive Stage1 where
  | a | b | c
  deriving DecidableEq, Repr

inductive Stage2 where
  | u | v
  deriving DecidableEq, Repr

def gate1 : Departure → Stage1
  | .t0 => .a
  | .t1 => .a
  | .t2 => .b
  | .t3 => .c

def gate2 : Stage1 → Stage2
  | .a => .u
  | .b => .v
  | .c => .v

def downstream : Departure → Stage2 :=
  fun t => gate2 (gate1 t)

theorem first_gate_strictly_concentrates :
    StrictConcentrationWitness
      (fun t : Departure => t) gate1 .t0 .t1 := by
  constructor
  · intro h
    cases h
  · rfl

theorem second_gate_strictly_concentrates :
    StrictConcentrationWitness gate1 gate2 .t2 .t3 := by
  constructor
  · intro h
    cases h
  · rfl

theorem first_merge_survives_second_gate :
    KernelOf gate1 .t0 .t1 →
      KernelOf downstream .t0 .t1 := by
  intro h
  exact kernel_postcompose_mono gate1 gate2 h

theorem second_gate_adds_new_merge :
    ¬ KernelOf gate1 .t2 .t3 ∧
      KernelOf downstream .t2 .t3 := by
  exact strict_witness_adds_identification second_gate_strictly_concentrates

/-- Once two histories are equal at the intermediate event boundary,
    no deterministic continuation can make their downstream event differ. -/
theorem no_reseparation_after_merge
    {C : Type u}
    (continuation : Stage1 → C)
    {x y : Departure}
    (h : KernelOf gate1 x y) :
    KernelOf (fun t => continuation (gate1 t)) x y :=
  kernel_postcompose_mono gate1 continuation h

end Metatron.TemporalConcentration
