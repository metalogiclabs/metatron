import Metatron.ResidualSynergy
import Metatron.PortEventStructure

namespace Metatron.CausalRepairCover

open Metatron.ResidualBasis
open Metatron.ResidualSynergy
open Metatron.PortEventStructure
open Metatron.FutureObservations

universe u v

def OccursBefore (schedule : List Nat) (a b : Nat) : Prop :=
  ∃ pre mid post,
    schedule = pre ++ a :: mid ++ b :: post

structure CausalRepair (Gen : Type u) where
  pes : PES Nat
  schedule : List Nat
  label : Nat → Gen

def CausalRepair.support
    {Gen : Type u}
    (r : CausalRepair Gen) : List Gen :=
  r.schedule.map r.label

def Certified
    {Gen : Type u}
    (r : CausalRepair Gen) : Prop :=
  r.schedule.Nodup ∧
  (∀ e, e ∈ r.pes.events ↔ e ∈ r.schedule) ∧
  ∀ a b,
    a ∈ r.pes.events →
    b ∈ r.pes.events →
    r.pes.beforeB a b = true →
    OccursBefore r.schedule a b

abbrev CertifiedRepair (Gen : Type u) :=
  {r : CausalRepair Gen // Certified r}

def execute
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (r : CausalRepair Gen)
    (s : State) : State :=
  run act r.support s

def repairSeparates
    {Gen : Type u} {State : Type v} {Val : Type}
    (act : Gen → State → State)
    (observe : State → Val)
    (r : CertifiedRepair Gen)
    (s t : State) : Prop :=
  observe (execute act r.1 s) ≠
    observe (execute act r.1 t)

def CausalRepairCovers
    {Gen : Type u} {State : Type v} {Val : Type}
    (current target : Metatron.ResidualBasis.Relation State)
    (act : Gen → State → State)
    (observe : State → Val)
    (repairs : List (CertifiedRepair Gen)) : Prop :=
  CoversResidual current target
    (repairSeparates act observe) repairs

theorem causalRepairCover_iff_targetSufficient
    {Gen : Type u} {State : Type v} {Val : Type}
    (current target : Metatron.ResidualBasis.Relation State)
    (act : Gen → State → State)
    (observe : State → Val)
    (repairs : List (CertifiedRepair Gen)) :
    CausalRepairCovers current target act observe repairs ↔
      TargetSufficient current target
        (repairSeparates act observe) repairs :=
  certifiedResidualBasis_closes
    current target (repairSeparates act observe) repairs

def MinimumCausalRepairCover
    {Gen : Type u} {State : Type v} {Val : Type}
    (current target : Metatron.ResidualBasis.Relation State)
    (act : Gen → State → State)
    (observe : State → Val)
    (repairs : List (CertifiedRepair Gen)) : Prop :=
  MinimumCoverByLength current target
    (repairSeparates act observe) repairs

theorem minimumCausalRepair_minimalSufficient
    {Gen : Type u} {State : Type v} {Val : Type}
    (current target : Metatron.ResidualBasis.Relation State)
    (act : Gen → State → State)
    (observe : State → Val)
    (repairs : List (CertifiedRepair Gen))
    (hmin : MinimumCausalRepairCover
      current target act observe repairs) :
    TargetSufficient current target
      (repairSeparates act observe) repairs ∧
    ∀ other : List (CertifiedRepair Gen),
      other.length < repairs.length →
        ¬ TargetSufficient current target
          (repairSeparates act observe) other :=
  minimumResidualBasis_minimalSufficient
    current target (repairSeparates act observe) repairs hmin

/-! Ordinary generators embed as one-event causal repairs. -/

def atomNatPES (cert inPort outPort : Nat) : PES Nat where
  events := [0]
  beforeB := fun _ _ => false
  inputPort := fun e => if e = 0 then some inPort else none
  outputPort := fun e => if e = 0 then some outPort else none
  cert := fun e => if e = 0 then cert else 0

def singletonRepair
    {Gen : Type u}
    (g : Gen)
    (cert inPort outPort : Nat) : CausalRepair Gen where
  pes := atomNatPES cert inPort outPort
  schedule := [0]
  label := fun _ => g

theorem singletonRepair_certified
    {Gen : Type u}
    (g : Gen)
    (cert inPort outPort : Nat) :
    Certified (singletonRepair g cert inPort outPort) := by
  constructor
  · simp [singletonRepair]
  constructor
  · intro e
    simp [singletonRepair, atomNatPES]
  · intro a b ha hb hbefore
    simp [singletonRepair, atomNatPES] at hbefore

def certifiedSingletonRepair
    {Gen : Type u}
    (g : Gen)
    (cert inPort outPort : Nat) :
    CertifiedRepair Gen :=
  ⟨singletonRepair g cert inPort outPort,
    singletonRepair_certified g cert inPort outPort⟩

theorem singleton_support_is_arity_one
    {Gen : Type u}
    (g : Gen)
    (cert inPort outPort : Nat) :
    (certifiedSingletonRepair g cert inPort outPort).1.support = [g] := by
  simp [certifiedSingletonRepair, singletonRepair, CausalRepair.support]

/-! A two-event port-wired causal repair. -/

def chain2PES (cert0 cert1 : Nat) : PES Nat where
  events := [0, 1]
  beforeB := fun a b => decide (a = 0 ∧ b = 1)
  inputPort := fun e =>
    if e = 0 then some 1
    else if e = 1 then some 2
    else none
  outputPort := fun e =>
    if e = 0 then some 2
    else if e = 1 then some 3
    else none
  cert := fun e =>
    if e = 0 then cert0
    else if e = 1 then cert1
    else 0

def chain2Repair
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) : CausalRepair Gen where
  pes := chain2PES cert0 cert1
  schedule := [0, 1]
  label := fun e => if e = 0 then g0 else g1

theorem chain2Repair_certified
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) :
    Certified (chain2Repair g0 g1 cert0 cert1) := by
  constructor
  · simp [chain2Repair]
  constructor
  · intro e
    simp [chain2Repair, chain2PES]
  · intro a b ha hb hbefore
    have hab : a = 0 ∧ b = 1 := by
      simpa [chain2Repair, chain2PES] using hbefore
    rcases hab with ⟨rfl, rfl⟩
    exact ⟨[], [], [], rfl⟩

def abRepair : CertifiedRepair Gen :=
  ⟨chain2Repair Gen.a Gen.b 101 102,
    chain2Repair_certified Gen.a Gen.b 101 102⟩

def baRepair : CertifiedRepair Gen :=
  ⟨chain2Repair Gen.b Gen.a 102 101,
    chain2Repair_certified Gen.b Gen.a 102 101⟩

theorem ab_port_order :
    certBefore abRepair.1.pes 101 102 = true := by
  decide

theorem ba_port_order :
    certBefore baRepair.1.pes 102 101 = true := by
  decide

theorem ab_support :
    abRepair.1.support = [Gen.a, Gen.b] := by
  simp [abRepair, chain2Repair, CausalRepair.support]

theorem ba_support :
    baRepair.1.support = [Gen.b, Gen.a] := by
  simp [baRepair, chain2Repair, CausalRepair.support]

theorem ab_repair_separates_xy :
    repairSeparates act observe abRepair x y := by
  simpa [repairSeparates, execute, ab_support] using
    a_then_b_separates

theorem ba_repair_does_not_separate_xy :
    ¬ repairSeparates act observe baRepair x y := by
  intro h
  exact h (by
    simpa [execute, ba_support] using
      b_then_a_does_not_separate)

/--
The target relation for a certified repair is exactly the observation boundary
created by executing that causal repair.
-/
def abTarget : Metatron.ResidualBasis.Relation State :=
  fun s t =>
    observe (execute act abRepair.1 s) =
      observe (execute act abRepair.1 t)

def allCurrent : Metatron.ResidualBasis.Relation State :=
  fun _ _ => True

theorem xy_is_ab_residual :
    ResidualPair allCurrent abTarget x y := by
  constructor
  · trivial
  · exact ab_repair_separates_xy

theorem ordinary_singletons_still_fail :
    ¬ CoversResidual allCurrent abTarget singletonSeparates [.a, .b] := by
  intro hcover
  rcases hcover x y xy_is_ab_residual with ⟨g, hg, hsep⟩
  have hcases : g = Gen.a ∨ g = Gen.b := by
    simpa using hg
  cases hcases with
  | inl ha =>
      subst g
      exact hsep singletonA_indistinguishable
  | inr hb =>
      subst g
      exact hsep singletonB_indistinguishable

theorem ab_causal_repair_covers :
    CausalRepairCovers allCurrent abTarget act observe [abRepair] := by
  intro s t hres
  exact ⟨abRepair, by simp, hres.2⟩

theorem ab_causal_repair_sufficient :
    TargetSufficient allCurrent abTarget
      (repairSeparates act observe) [abRepair] :=
  (causalRepairCover_iff_targetSufficient
    allCurrent abTarget act observe [abRepair]).1
    ab_causal_repair_covers

theorem ba_causal_repair_fails_cover :
    ¬ CausalRepairCovers allCurrent abTarget act observe [baRepair] := by
  intro hcover
  rcases hcover x y xy_is_ab_residual with ⟨r, hr, hsep⟩
  have hre : r = baRepair := by
    simpa using hr
  subst r
  exact ba_repair_does_not_separate_xy hsep

theorem empty_causal_repair_fails :
    ¬ CausalRepairCovers allCurrent abTarget act observe [] := by
  intro hcover
  rcases hcover x y xy_is_ab_residual with ⟨r, hr, _⟩
  cases hr

theorem ab_is_minimum_one_repair :
    MinimumCausalRepairCover
      allCurrent abTarget act observe [abRepair] := by
  constructor
  · exact ab_causal_repair_covers
  · intro other hlt
    have hzero : other = [] := by
      cases other with
      | nil => rfl
      | cons head tail =>
          simp at hlt
    subst other
    exact empty_causal_repair_fails

end Metatron.CausalRepairCover
