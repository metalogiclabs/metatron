import Metatron.CausalRepairCover

namespace Metatron.CausalLinearization

open Metatron.CausalRepairCover
open Metatron.ResidualSynergy
open Metatron.PortEventStructure
open Metatron.FutureObservations

universe u v

def Commute
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (g h : Gen) : Prop :=
  ∀ s, act h (act g s) = act g (act h s)

def independent2PES (cert0 cert1 : Nat) : PES Nat where
  events := [0, 1]
  beforeB := fun _ _ => false
  inputPort := fun _ => none
  outputPort := fun _ => none
  cert := fun e => if e = 0 then cert0 else cert1

def independent2LR
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) : CausalRepair Gen where
  pes := independent2PES cert0 cert1
  schedule := [0, 1]
  label := fun e => if e = 0 then g0 else g1

def independent2RL
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) : CausalRepair Gen where
  pes := independent2PES cert0 cert1
  schedule := [1, 0]
  label := fun e => if e = 0 then g0 else g1

theorem independent2LR_certified
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) :
    Certified (independent2LR g0 g1 cert0 cert1) := by
  constructor
  · simp [independent2LR]
  constructor
  · intro e
    simp [independent2LR, independent2PES]
  · intro a b ha hb hbefore
    simp [independent2LR, independent2PES] at hbefore

theorem independent2RL_certified
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) :
    Certified (independent2RL g0 g1 cert0 cert1) := by
  constructor
  · simp [independent2RL]
  constructor
  · intro e
    simp [independent2RL, independent2PES]
  · intro a b ha hb hbefore
    simp [independent2RL, independent2PES] at hbefore

theorem independent_support_same
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) :
    (independent2LR g0 g1 cert0 cert1).pes.events =
      (independent2RL g0 g1 cert0 cert1).pes.events := by
  rfl

theorem independent_causal_signature_same
    {Gen : Type u}
    (g0 g1 : Gen)
    (cert0 cert1 : Nat) :
    causalSignature
      (independent2LR g0 g1 cert0 cert1).pes [cert0, cert1] =
    causalSignature
      (independent2RL g0 g1 cert0 cert1).pes [cert0, cert1] := by
  rfl

theorem independentSwap_invariant_of_commute
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (g0 g1 : Gen)
    (cert0 cert1 : Nat)
    (hcomm : Commute act g0 g1)
    (s : State) :
    execute act (independent2LR g0 g1 cert0 cert1) s =
      execute act (independent2RL g0 g1 cert0 cert1) s := by
  simpa [execute, CausalRepair.support, independent2LR, independent2RL, run]
    using hcomm s

theorem independentObservation_invariant_of_commute
    {Gen : Type u} {State : Type v} {Val : Type}
    (act : Gen → State → State)
    (observe : State → Val)
    (g0 g1 : Gen)
    (cert0 cert1 : Nat)
    (hcomm : Commute act g0 g1)
    (s : State) :
    observe (execute act (independent2LR g0 g1 cert0 cert1) s) =
      observe (execute act (independent2RL g0 g1 cert0 cert1) s) := by
  rw [independentSwap_invariant_of_commute
    act g0 g1 cert0 cert1 hcomm s]

/-! Positive fixture: two independent updates really commute. -/

inductive CGen where
  | sourceFlip
  | noiseFlip
  deriving DecidableEq, Repr

def cAct : CGen → State → State
  | .sourceFlip, s => { s with source := !s.source }
  | .noiseFlip, s => { s with hidden := !s.hidden }

theorem commuting_fixture :
    Commute cAct CGen.sourceFlip CGen.noiseFlip := by
  intro s
  cases s
  rfl

theorem commuting_linearizations_same_state
    (s : State) :
    execute cAct
      (independent2LR CGen.sourceFlip CGen.noiseFlip 201 202) s =
    execute cAct
      (independent2RL CGen.sourceFlip CGen.noiseFlip 201 202) s :=
  independentSwap_invariant_of_commute
    cAct CGen.sourceFlip CGen.noiseFlip 201 202 commuting_fixture s

theorem commuting_linearizations_same_observation
    (s : State) :
    observe (execute cAct
      (independent2LR CGen.sourceFlip CGen.noiseFlip 201 202) s) =
    observe (execute cAct
      (independent2RL CGen.sourceFlip CGen.noiseFlip 201 202) s) :=
  independentObservation_invariant_of_commute
    cAct observe CGen.sourceFlip CGen.noiseFlip 201 202 commuting_fixture s

/-!
Negative fixture: the same empty causal order does not justify swapping
semantically interfering actions.
-/

def abIndependentLR : CausalRepair Gen :=
  independent2LR Gen.a Gen.b 301 302

def abIndependentRL : CausalRepair Gen :=
  independent2RL Gen.a Gen.b 301 302

theorem ab_independent_same_causal_signature :
    causalSignature abIndependentLR.pes [301, 302] =
      causalSignature abIndependentRL.pes [301, 302] := by
  rfl

theorem ab_independent_lr_separates :
    observe (execute act abIndependentLR x) ≠
      observe (execute act abIndependentLR y) := by
  simpa [abIndependentLR, independent2LR, execute, CausalRepair.support]
    using a_then_b_separates

theorem ab_independent_rl_does_not_separate :
    observe (execute act abIndependentRL x) =
      observe (execute act abIndependentRL y) := by
  simpa [abIndependentRL, independent2RL, execute, CausalRepair.support]
    using b_then_a_does_not_separate

theorem ab_actions_do_not_commute :
    ¬ Commute act Gen.a Gen.b := by
  intro hcomm
  have h := hcomm y
  have hob :=
    congrArg State.observed h
  decide at hob

theorem causalStructureAlone_not_enough :
    (causalSignature abIndependentLR.pes [301, 302] =
       causalSignature abIndependentRL.pes [301, 302]) ∧
    (observe (execute act abIndependentLR y) ≠
       observe (execute act abIndependentRL y)) := by
  constructor
  · exact ab_independent_same_causal_signature
  · decide

/--
Two certified linearizations may be identified only when every adjacent swap
used to pass between them is backed by semantic commutation. This two-event
theorem is the minimal quotient law.
-/
def SwapSafe
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (left right : CausalRepair Gen) : Prop :=
  ∀ s, execute act left s = execute act right s

theorem independent_swapSafe_of_commute
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (g0 g1 : Gen)
    (cert0 cert1 : Nat)
    (hcomm : Commute act g0 g1) :
    SwapSafe act
      (independent2LR g0 g1 cert0 cert1)
      (independent2RL g0 g1 cert0 cert1) := by
  intro s
  exact independentSwap_invariant_of_commute
    act g0 g1 cert0 cert1 hcomm s

theorem ab_not_swapSafe :
    ¬ SwapSafe act abIndependentLR abIndependentRL := by
  intro hsafe
  have h := hsafe y
  have hob := congrArg State.observed h
  decide at hob

end Metatron.CausalLinearization
