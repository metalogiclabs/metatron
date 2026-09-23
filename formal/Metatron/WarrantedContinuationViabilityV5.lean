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

def CoversFailure
    (live : List Nat)
    (edges : List RepairHyperedge)
    (failure : Nat) : Prop :=
  ∃ edge, edge ∈ edges ∧ edge.failure = failure ∧ edgeLive live edge = true

def CompleteCover
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) : Prop :=
  ∀ failure, failure ∈ admitted → CoversFailure live edges failure

def repairStep
    (live : List Nat)
    (edges : List RepairHyperedge)
    (failure : Nat) : Option (List Nat) :=
  if CoversFailure live edges failure then some live else none

def SingletonKernel (live : List Nat) (state : List Nat) : Prop :=
  state = live

/-- The declared live repair cover is sufficient for one-step invariant
    viability under every admitted failure. -/
theorem complete_cover_implies_postfixed
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat)
    (hcover : CompleteCover live edges admitted) :
    PostFixed (repairStep live edges) admitted (SingletonKernel live) := by
  intro state hstate
  subst state
  intro failure hfailure
  have hc : CoversFailure live edges failure := hcover failure hfailure
  exact ⟨live, by simp [repairStep, hc], rfl⟩

/-- If the singleton live state is post-fixed under the repair semantics,
    then every admitted failure has a live warranted repair hyperedge. -/
theorem postfixed_implies_complete_cover
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat)
    (hpost : PostFixed (repairStep live edges) admitted (SingletonKernel live)) :
    CompleteCover live edges admitted := by
  intro failure hfailure
  have h := hpost live rfl failure hfailure
  rcases h with ⟨state', hstep, _⟩
  by_contra hcov
  simp [repairStep, hcov] at hstep

theorem complete_cover_iff_postfixed
    (live : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) :
    CompleteCover live edges admitted ↔
      PostFixed (repairStep live edges) admitted (SingletonKernel live) := by
  constructor
  · exact complete_cover_implies_postfixed live edges admitted
  · exact postfixed_implies_complete_cover live edges admitted

def afterCut (live cut : List Nat) : List Nat :=
  live.filter (fun c => !cut.contains c)

def RepairCut
    (live cut : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) : Prop :=
  ¬ CompleteCover (afterCut live cut) edges admitted

/-- In the declared repair semantics, a cut destroys viability exactly when
    it destroys complete live repair coverage. -/
theorem cut_breaks_viability_iff
    (live cut : List Nat)
    (edges : List RepairHyperedge)
    (admitted : List Nat) :
    RepairCut live cut edges admitted ↔
      ¬ PostFixed
        (repairStep (afterCut live cut) edges)
        admitted
        (SingletonKernel (afterCut live cut)) := by
  unfold RepairCut
  exact not_congr (complete_cover_iff_postfixed (afterCut live cut) edges admitted)

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
    the WarrantGraph cut {1,3} is a consequential cut because it uncovers
    admitted failure class 1 while leaving class 0 covered. -/
theorem repair_cover_cut_characterization_fixture :
    PostFixed
      (repairStep fixtureLive fixtureEdges)
      fixtureAdmitted
      (SingletonKernel fixtureLive) ∧
    ¬ PostFixed
      (repairStep (warrantLive coverageCut13Log) fixtureEdges)
      fixtureAdmitted
      (SingletonKernel (warrantLive coverageCut13Log)) := by
  constructor
  · exact (complete_cover_iff_postfixed fixtureLive fixtureEdges fixtureAdmitted).1
      fixture_complete_cover
  · intro hpost
    have hc :=
      (postfixed_implies_complete_cover
        (warrantLive coverageCut13Log) fixtureEdges fixtureAdmitted hpost)
    exact warrant_cut_breaks_complete_cover.2 hc

end Metatron.WarrantedContinuationViabilityV5
