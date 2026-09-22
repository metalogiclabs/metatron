import Metatron.CausalLinearization

namespace Metatron.CausalTraceQuotient

open Metatron.CausalRepairCover
open Metatron.CausalLinearization
open Metatron.FutureObservations

universe u v

theorem run_append
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (xs ys : List Gen)
    (s : State) :
    run act (xs ++ ys) s =
      run act ys (run act xs s) := by
  induction xs generalizing s with
  | nil =>
      rfl
  | cons x xs ih =>
      simp [run, ih]

inductive TraceEq
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State) :
    List Gen → List Gen → Prop
  | refl (xs : List Gen) :
      TraceEq act xs xs
  | swap
      (pre post : List Gen)
      (g h : Gen)
      (hcomm : Commute act g h) :
      TraceEq act
        (pre ++ g :: h :: post)
        (pre ++ h :: g :: post)
  | symm
      {xs ys : List Gen}
      (h : TraceEq act xs ys) :
      TraceEq act ys xs
  | trans
      {xs ys zs : List Gen}
      (hxy : TraceEq act xs ys)
      (hyz : TraceEq act ys zs) :
      TraceEq act xs zs

theorem adjacent_commuting_swap_preserves_run
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (pre post : List Gen)
    (g h : Gen)
    (hcomm : Commute act g h)
    (s : State) :
    run act (pre ++ g :: h :: post) s =
      run act (pre ++ h :: g :: post) s := by
  rw [run_append act pre (g :: h :: post) s]
  rw [run_append act pre (h :: g :: post) s]
  simp only [run]
  rw [hcomm (run act pre s)]

theorem traceEq_preserves_run
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    {xs ys : List Gen}
    (htrace : TraceEq act xs ys) :
    ∀ s, run act xs s = run act ys s := by
  induction htrace with
  | refl xs =>
      intro s
      rfl
  | swap pre post g h hcomm =>
      intro s
      exact adjacent_commuting_swap_preserves_run
        act pre post g h hcomm s
  | symm h ih =>
      intro s
      exact (ih s).symm
  | trans hxy hyz ihxy ihyz =>
      intro s
      exact Eq.trans (ihxy s) (ihyz s)

theorem traceEq_preserves_observation
    {Gen : Type u} {State : Type v} {Val : Type}
    (act : Gen → State → State)
    (observe : State → Val)
    {xs ys : List Gen}
    (htrace : TraceEq act xs ys)
    (s : State) :
    observe (run act xs s) =
      observe (run act ys s) := by
  rw [traceEq_preserves_run act htrace s]

abbrev TopologicalCertified
    {Gen : Type u}
    (r : CausalRepair Gen) : Prop :=
  Certified r

def SamePresentation
    {Gen : Type u}
    (left right : CausalRepair Gen) : Prop :=
  left.pes = right.pes ∧
  left.label = right.label

theorem repair_traceEq_swapSafe
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (left right : CausalRepair Gen)
    (htrace : TraceEq act left.support right.support) :
    SwapSafe act left right := by
  intro s
  exact traceEq_preserves_run act htrace s

theorem topological_linearizations_equivalent_if_traceConnected
    {Gen : Type u} {State : Type v}
    (act : Gen → State → State)
    (left right : CausalRepair Gen)
    (_hleft : TopologicalCertified left)
    (_hright : TopologicalCertified right)
    (_hsame : SamePresentation left right)
    (htrace : TraceEq act left.support right.support) :
    SwapSafe act left right :=
  repair_traceEq_swapSafe act left right htrace

theorem topological_observations_equivalent_if_traceConnected
    {Gen : Type u} {State : Type v} {Val : Type}
    (act : Gen → State → State)
    (observe : State → Val)
    (left right : CausalRepair Gen)
    (hleft : TopologicalCertified left)
    (hright : TopologicalCertified right)
    (hsame : SamePresentation left right)
    (htrace : TraceEq act left.support right.support)
    (s : State) :
    observe (execute act left s) =
      observe (execute act right s) := by
  rw [topological_linearizations_equivalent_if_traceConnected
    act left right hleft hright hsame htrace s]

inductive TGen where
  | sourceFlip
  | noiseFlip
  | observedFlip
  deriving DecidableEq, Repr

def tAct : TGen → ResidualSynergy.State → ResidualSynergy.State
  | .sourceFlip, s => { s with source := !s.source }
  | .noiseFlip, s => { s with hidden := !s.hidden }
  | .observedFlip, s => { s with observed := !s.observed }

theorem source_noise_commute :
    Commute tAct TGen.sourceFlip TGen.noiseFlip := by
  intro s
  cases s
  rfl

theorem source_observed_commute :
    Commute tAct TGen.sourceFlip TGen.observedFlip := by
  intro s
  cases s
  rfl

def t0 : List TGen :=
  [.sourceFlip, .noiseFlip, .observedFlip]

def t1 : List TGen :=
  [.noiseFlip, .sourceFlip, .observedFlip]

def t2 : List TGen :=
  [.noiseFlip, .observedFlip, .sourceFlip]

theorem t0_trace_t1 :
    TraceEq tAct t0 t1 := by
  simpa [t0, t1] using
    TraceEq.swap tAct [] [TGen.observedFlip]
      TGen.sourceFlip TGen.noiseFlip source_noise_commute

theorem t1_trace_t2 :
    TraceEq tAct t1 t2 := by
  simpa [t1, t2] using
    TraceEq.swap tAct [TGen.noiseFlip] []
      TGen.sourceFlip TGen.observedFlip source_observed_commute

theorem t0_trace_t2 :
    TraceEq tAct t0 t2 :=
  TraceEq.trans t0_trace_t1 t1_trace_t2

theorem three_event_trace_same_state
    (s : ResidualSynergy.State) :
    run tAct t0 s = run tAct t2 s :=
  traceEq_preserves_run tAct t0_trace_t2 s

theorem three_event_trace_same_observation
    (s : ResidualSynergy.State) :
    ResidualSynergy.observe (run tAct t0 s) =
      ResidualSynergy.observe (run tAct t2 s) :=
  traceEq_preserves_observation
    tAct ResidualSynergy.observe t0_trace_t2 s

theorem ab_same_pes_not_trace_quotiented :
    ¬ SwapSafe ResidualSynergy.act
      CausalLinearization.abIndependentLR
      CausalLinearization.abIndependentRL :=
  CausalLinearization.ab_not_swapSafe

end Metatron.CausalTraceQuotient
