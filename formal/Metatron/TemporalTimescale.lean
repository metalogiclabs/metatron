import Metatron.TemporalConcentration
import Lean.Elab.Tactic.Omega

namespace Metatron.TemporalTimescale

open Metatron.TemporalConcentration

universe u v w

/-- Number of observed state changes across a fixed list of sampling intervals.
    Comparing this count on the same interval list compares event-rate numerators
    over the same underlying time horizon. -/
def TransitionCount
    {A : Type u} {B : Type v}
    [DecidableEq B]
    (observe : A → B) : List (A × A) → Nat
  | [] => 0
  | p :: ps =>
      (if observe p.1 = observe p.2 then 0 else 1) +
        TransitionCount observe ps

/-- A deterministic downstream readout cannot create a macro transition on an
    interval where the upstream state did not change. -/
theorem downstream_change_requires_upstream_change
    {A : Type u} {B : Type v} {C : Type w}
    (f : A → B) (g : B → C)
    {x y : A}
    (h : g (f x) ≠ g (f y)) :
    f x ≠ f y := by
  intro hxy
  exact h (congrArg g hxy)

/-- On a fixed sampling grid, deterministic postcomposition cannot increase
    the number of observed transition events. -/
theorem transitionCount_postcompose_le
    {A : Type u} {B : Type v} {C : Type w}
    [DecidableEq B] [DecidableEq C]
    (f : A → B) (g : B → C) :
    ∀ intervals : List (A × A),
      TransitionCount (fun a => g (f a)) intervals ≤
        TransitionCount f intervals := by
  intro intervals
  induction intervals with
  | nil =>
      simp [TransitionCount]
  | cons p ps ih =>
      by_cases hf : f p.1 = f p.2
      · have hg : g (f p.1) = g (f p.2) := congrArg g hf
        simp [TransitionCount, hf, hg, ih]
      · by_cases hg : g (f p.1) = g (f p.2)
        · simp [TransitionCount, hf, hg]
          omega
        · simp [TransitionCount, hf, hg]
          omega

/-- Operational same-horizon notion of a slower-or-equal observed timescale:
    no more state-transition events occur on the same underlying intervals. -/
def SlowerOrEqualOn
    {A : Type u} {B : Type v} {C : Type w}
    [DecidableEq B] [DecidableEq C]
    (micro : A → B) (macro : A → C)
    (intervals : List (A × A)) : Prop :=
  TransitionCount macro intervals ≤ TransitionCount micro intervals

theorem deterministic_readout_slower_or_equal
    {A : Type u} {B : Type v} {C : Type w}
    [DecidableEq B] [DecidableEq C]
    (micro : A → B) (readout : B → C)
    (intervals : List (A × A)) :
    SlowerOrEqualOn micro (fun a => readout (micro a)) intervals :=
  transitionCount_postcompose_le micro readout intervals

/-! Reuse the qualified V0 traffic-style fixture on one fixed three-interval
    departure grid. Its observed event counts fall strictly at each gate. -/

def departureIntervals : List (Departure × Departure) :=
  [(.t0, .t1), (.t1, .t2), (.t2, .t3)]

theorem departure_transition_count :
    TransitionCount (fun t : Departure => t) departureIntervals = 3 := by
  decide

theorem gate1_transition_count :
    TransitionCount gate1 departureIntervals = 2 := by
  decide

theorem downstream_transition_count :
    TransitionCount downstream departureIntervals = 1 := by
  decide

theorem gate1_no_faster :
    SlowerOrEqualOn
      (fun t : Departure => t)
      gate1
      departureIntervals := by
  simpa [SlowerOrEqualOn] using
    transitionCount_postcompose_le
      (fun t : Departure => t) gate1 departureIntervals

theorem downstream_no_faster_than_gate1 :
    SlowerOrEqualOn gate1 downstream departureIntervals := by
  simpa [SlowerOrEqualOn, downstream] using
    transitionCount_postcompose_le gate1 gate2 departureIntervals

theorem fixture_strict_event_rate_slowing :
    TransitionCount downstream departureIntervals <
      TransitionCount gate1 departureIntervals ∧
    TransitionCount gate1 departureIntervals <
      TransitionCount (fun t : Departure => t) departureIntervals := by
  decide

/-- V0 kernel concentration and V1 event-rate slowing coincide on the same
    finite fixture: each gate both merges histories and lowers the transition
    count on the fixed sampling grid. -/
theorem concentration_with_strict_slowing :
    StrictConcentrationWitness
        (fun t : Departure => t) gate1 .t0 .t1 ∧
    StrictConcentrationWitness gate1 gate2 .t2 .t3 ∧
    TransitionCount downstream departureIntervals <
      TransitionCount gate1 departureIntervals ∧
    TransitionCount gate1 departureIntervals <
      TransitionCount (fun t : Departure => t) departureIntervals := by
  exact ⟨
    first_gate_strictly_concentrates,
    second_gate_strictly_concentrates,
    fixture_strict_event_rate_slowing
  ⟩

end Metatron.TemporalTimescale
