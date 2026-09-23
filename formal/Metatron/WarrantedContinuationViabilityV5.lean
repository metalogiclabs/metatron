import Metatron.WarrantedContinuationViabilityV4
import Metatron.WarrantGraph

namespace Metatron.WarrantedContinuationViabilityV5

open Metatron.WarrantedContinuationViabilityV1

structure RepairHyperedge where
  failure : Nat
  requires : List Nat
  deriving DecidableEq, Repr

def edgeLive (live : List Nat) (edge : RepairHyperedge) : Bool :=
  edge.requires.all live.contains

def coversFailureB
    (live : List Nat)
    (edges : List RepairHyperedge)
    (failure : Nat) : Bool :=
  edges.any (fun edge =>
    (edge.failure == failure) && edgeLive live edge)

def CoversFailure
    (live : List Nat)
    (edges : List RepairHyperedge)
    (failure : Nat) : Prop :=
  coversFailureB live edges failure = true

instance coversFailureDecidable
    (live : List Nat)
    (edges : List RepairHyperedge)
    (failure : Nat) :
    Decidable (CoversFailure live edges failure) := by
  unfold CoversFailure
  infer_instance

def completeCoverB
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) : Bool :=
  admitted.all (coversFailureB live edges)

def CompleteCover
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) : Prop :=
  completeCoverB live edges admitted = true

instance completeCoverDecidable
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) :
    Decidable (CompleteCover live edges admitted) := by
  unfold CompleteCover
  infer_instance

def repairStep
    (edges : List RepairHyperedge)
    (live : List Nat)
    (failure : Nat) : Option (List Nat) :=
  if coversFailureB live edges failure then some live else none

def SingletonKernel (live : List Nat) (state : List Nat) : Prop :=
  state = live

theorem all_true_of_mem
    {α : Type}
    (p : α → Bool) :
    ∀ (xs : List α) (x : α), xs.all p = true → x ∈ xs → p x = true := by
  intro xs
  induction xs with
  | nil =>
      intro x h hx
      simp at hx
  | cons a rest ih =>
      intro x h hx
      simp at h hx
      rcases hx with rfl | hx
      · exact h.1
      · exact ih x h.2 hx

theorem all_true_intro
    {α : Type}
    (p : α → Bool) :
    ∀ (xs : List α), (∀ x, x ∈ xs → p x = true) → xs.all p = true := by
  intro xs
  induction xs with
  | nil =>
      intro h
      rfl
  | cons a rest ih =>
      intro h
      simp
      constructor
      · exact h a (by simp)
      · apply ih
        intro x hx
        exact h x (by simp [hx])

/-- Complete live repair coverage is sufficient for one-step invariant
    viability under every admitted failure. -/
theorem complete_cover_implies_postfixed
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat)
    (hcover : CompleteCover live edges admitted) :
    PostFixed (repairStep edges) admitted (SingletonKernel live) := by
  intro state hstate
  subst state
  intro failure hfailure
  have hc : coversFailureB live edges failure = true := by
    exact all_true_of_mem
      (coversFailureB live edges)
      admitted failure hcover hfailure
  exact ⟨live, by simp [repairStep, hc], rfl⟩

/-- If the singleton live state is post-fixed under the repair semantics,
    then every admitted failure has a live warranted repair hyperedge. -/
theorem postfixed_implies_complete_cover
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat)
    (hpost : PostFixed (repairStep edges) admitted (SingletonKernel live)) :
    CompleteCover live edges admitted := by
  apply all_true_intro (coversFailureB live edges) admitted
  intro failure hfailure
  have h := hpost live rfl failure hfailure
  rcases h with ⟨state', hstep, _⟩
  cases hcov : coversFailureB live edges failure with
  | false =>
      simp [repairStep, hcov] at hstep
  | true =>
      rfl

theorem complete_cover_iff_postfixed
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) :
    CompleteCover live edges admitted ↔
      PostFixed (repairStep edges) admitted (SingletonKernel live) := by
  constructor
  · exact complete_cover_implies_postfixed live edges admitted
  · exact postfixed_implies_complete_cover live edges admitted

def afterCut (live cut : List Nat) : List Nat :=
  live.filter (fun c => !cut.contains c)

def RepairCut
    (live cut : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) : Prop :=
  completeCoverB (afterCut live cut) edges admitted = false

instance repairCutDecidable
    (live cut : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) :
    Decidable (RepairCut live cut edges admitted) := by
  unfold RepairCut
  infer_instance

/-- In the declared repair semantics, a cut destroys viability exactly when
    it destroys complete live repair coverage. -/
theorem cut_breaks_viability_iff
    (live cut : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) :
    RepairCut live cut edges admitted ↔
      ¬ PostFixed
        (repairStep edges)
        admitted
        (SingletonKernel (afterCut live cut)) := by
  rw [← complete_cover_iff_postfixed (afterCut live cut) edges admitted]
  unfold RepairCut CompleteCover
  cases h : completeCoverB (afterCut live cut) edges admitted <;> simp [h]

/-! Redundant + conjunctive finite fixture. -/

def fixtureEdges : List RepairHyperedge := [
  ⟨0, [0]⟩,
  ⟨0, [1]⟩,
  ⟨1, [1, 2]⟩,
  ⟨1, [3]⟩
]

def fixtureLive : List Nat := [0, 1, 2, 3]
def fixtureAdmitted : List Nat := [0, 1]

theorem fixture_complete_cover :
    CompleteCover fixtureLive fixtureEdges fixtureAdmitted := by
  decide

theorem every_singleton_cut_preserves_cover :
    CompleteCover (afterCut fixtureLive [0]) fixtureEdges fixtureAdmitted ∧
    CompleteCover (afterCut fixtureLive [1]) fixtureEdges fixtureAdmitted ∧
    CompleteCover (afterCut fixtureLive [2]) fixtureEdges fixtureAdmitted ∧
    CompleteCover (afterCut fixtureLive [3]) fixtureEdges fixtureAdmitted := by
  decide

theorem three_pair_cuts_break_cover :
    RepairCut fixtureLive [0, 1] fixtureEdges fixtureAdmitted ∧
    RepairCut fixtureLive [1, 3] fixtureEdges fixtureAdmitted ∧
    RepairCut fixtureLive [2, 3] fixtureEdges fixtureAdmitted := by
  decide

theorem conjunctive_path_is_not_singleton_equivalent :
    CoversFailure fixtureLive fixtureEdges 1 ∧
    edgeLive fixtureLive ⟨1, [1, 2]⟩ = true ∧
    edgeLive (afterCut fixtureLive [1]) ⟨1, [1, 2]⟩ = false := by
  decide

/-! Exact authority cut using WarrantGraph liveness. -/

def coverageBaseLog : List WarrantEntry := [
  ⟨[], none⟩,
  ⟨[], none⟩,
  ⟨[], none⟩,
  ⟨[], none⟩
]

def coverageCut13Log : List WarrantEntry :=
  coverageBaseLog ++ [
    ⟨[], some 1⟩,
    ⟨[], some 3⟩
  ]

theorem coverage_base_live :
    warrantLive coverageBaseLog = [0, 1, 2, 3] := by
  decide

theorem coverage_cut13_live :
    warrantLive coverageCut13Log = [0, 2] := by
  decide

theorem cut13_preserves_failure0_but_breaks_failure1 :
    CoversFailure (warrantLive coverageCut13Log) fixtureEdges 0 ∧
    ¬ CoversFailure (warrantLive coverageCut13Log) fixtureEdges 1 := by
  decide

theorem warrant_cut_breaks_complete_cover :
    RepairCut fixtureLive [1, 3] fixtureEdges fixtureAdmitted ∧
    ¬ CompleteCover (warrantLive coverageCut13Log) fixtureEdges fixtureAdmitted := by
  decide

/-- Exact finite synthesis:
    viable continuation is equivalent to complete live repair coverage, and
    the WarrantGraph cut {1,3} is consequential because it uncovers admitted
    failure class 1 while leaving class 0 covered. -/
theorem repair_cover_cut_characterization_fixture :
    PostFixed
      (repairStep fixtureEdges)
      fixtureAdmitted
      (SingletonKernel fixtureLive) ∧
    ¬ PostFixed
      (repairStep fixtureEdges)
      fixtureAdmitted
      (SingletonKernel (warrantLive coverageCut13Log)) := by
  constructor
  · exact
      (complete_cover_iff_postfixed
        fixtureLive fixtureEdges fixtureAdmitted).1
        fixture_complete_cover
  · intro hpost
    have hc :=
      postfixed_implies_complete_cover
        (warrantLive coverageCut13Log)
        fixtureEdges fixtureAdmitted hpost
    exact warrant_cut_breaks_complete_cover.2 hc

end Metatron.WarrantedContinuationViabilityV5
