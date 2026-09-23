import Metatron.WarrantedContinuationViabilityV5
import Metatron.CausalRepairCover
import Metatron.WarrantGraph

namespace Metatron.WarrantedContinuationViabilityV6

open Metatron.WarrantedContinuationViabilityV1
open Metatron.WarrantedContinuationViability
open Metatron.WarrantedContinuationViabilityV5
open Metatron.CausalRepairCover
open Metatron.ResidualSynergy

structure CausalRoute where
  failure : Nat
  requires : List Nat
  repairId : Nat
  deriving DecidableEq, Repr

def routeAuthorizedB (live : List Nat) (route : CausalRoute) : Bool :=
  route.requires.all live.contains

def coversLiveCausalFailureB
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (failure : Nat) : Bool :=
  routes.any (fun route =>
    (route.failure == failure) &&
    routeAuthorizedB live route &&
    validB route.repairId failure)

def completeLiveCausalCoverB
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (admitted : List Nat) : Bool :=
  admitted.all (coversLiveCausalFailureB live routes validB)

def CompleteLiveCausalCover
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (admitted : List Nat) : Prop :=
  completeLiveCausalCoverB live routes validB admitted = true

instance completeLiveCausalCoverDecidable
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (admitted : List Nat) :
    Decidable (CompleteLiveCausalCover live routes validB admitted) := by
  unfold CompleteLiveCausalCover
  infer_instance

def staticCausalStep
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (live : List Nat)
    (failure : Nat) : Option (List Nat) :=
  if coversLiveCausalFailureB live routes validB failure then
    some live
  else
    none

def StaticKernel (live state : List Nat) : Prop :=
  state = live

theorem complete_live_causal_cover_implies_postfixed
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (admitted : List Nat)
    (hcover : CompleteLiveCausalCover live routes validB admitted) :
    PostFixed
      (staticCausalStep routes validB)
      admitted
      (StaticKernel live) := by
  intro state hstate
  subst state
  intro failure hfailure
  have hc :
      coversLiveCausalFailureB live routes validB failure = true := by
    exact all_true_of_mem
      (coversLiveCausalFailureB live routes validB)
      admitted failure hcover hfailure
  exact ⟨live, by simp [staticCausalStep, hc], rfl⟩

theorem postfixed_implies_complete_live_causal_cover
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (admitted : List Nat)
    (hpost :
      PostFixed
        (staticCausalStep routes validB)
        admitted
        (StaticKernel live)) :
    CompleteLiveCausalCover live routes validB admitted := by
  apply all_true_intro
    (coversLiveCausalFailureB live routes validB)
    admitted
  intro failure hfailure
  have h := hpost live rfl failure hfailure
  rcases h with ⟨state', hstep, _⟩
  cases hc : coversLiveCausalFailureB live routes validB failure with
  | false =>
      simp [staticCausalStep, hc] at hstep
  | true =>
      rfl

theorem complete_live_causal_cover_iff_postfixed
    (live : List Nat)
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (admitted : List Nat) :
    CompleteLiveCausalCover live routes validB admitted ↔
      PostFixed
        (staticCausalStep routes validB)
        admitted
        (StaticKernel live) := by
  constructor
  · exact complete_live_causal_cover_implies_postfixed
      live routes validB admitted
  · exact postfixed_implies_complete_live_causal_cover
      live routes validB admitted

/-! Authority + causal-oracle composition fixture. -/

def oracleValidB : Nat → Nat → Bool
  | 0, 0 => true
  | _, _ => false

def oracleRoutes : List CausalRoute := [
  ⟨0, [0], 0⟩,
  ⟨0, [1], 1⟩
]

def oracleAdmitted : List Nat := [0]

def authorityOnlyCoversB
    (live : List Nat)
    (routes : List CausalRoute)
    (failure : Nat) : Bool :=
  routes.any (fun route =>
    (route.failure == failure) &&
    routeAuthorizedB live route)

theorem oracle_route0_matches_actual_causal_repair :
    oracleValidB 0 0 = true ∧
    repairSeparates act observe abRepair x y := by
  exact ⟨rfl, ab_repair_separates_xy⟩

theorem oracle_route1_rejected_by_actual_causal_repair :
    oracleValidB 1 0 = false ∧
    ¬ repairSeparates act observe baRepair x y := by
  exact ⟨rfl, ba_repair_does_not_separate_xy⟩

theorem oracle_base_complete_live_causal_cover :
    CompleteLiveCausalCover [0, 1] oracleRoutes oracleValidB oracleAdmitted := by
  decide

def oracleAuthorityBase : List WarrantEntry := [
  ⟨[], none⟩,
  ⟨[], none⟩
]

def oracleAuthorityCut0 : List WarrantEntry :=
  oracleAuthorityBase ++ [⟨[], some 0⟩]

theorem oracle_authority_cut_live :
    warrantLive oracleAuthorityCut0 = [1] := by
  decide

/-- A live-authority-only route survives the cut, but it is the causally wrong
    BA repair. Once causal validity is composed in, cover is lost. -/
theorem authority_alone_is_not_causal_cover :
    authorityOnlyCoversB
      (warrantLive oracleAuthorityCut0) oracleRoutes 0 = true ∧
    completeLiveCausalCoverB
      (warrantLive oracleAuthorityCut0)
      oracleRoutes oracleValidB oracleAdmitted = false := by
  decide

/-! Shared-resource contention fixture.

Failures 0 and 1 are two admitted occurrences of the same protected residual
class. Both are statically covered by the same live, causally certified AB
repair route. Execution consumes a one-shot resource token.
-/

def repeatedValidB : Nat → Nat → Bool
  | 0, 0 => true
  | 0, 1 => true
  | _, _ => false

def repeatedRoutes : List CausalRoute := [
  ⟨0, [0], 0⟩,
  ⟨1, [0], 0⟩
]

def repeatedAdmitted : List Nat := [0, 1]

theorem repeated_route_uses_actual_certified_causal_repair :
    repairSeparates act observe abRepair x y :=
  ab_repair_separates_xy

structure ResourceState where
  live : List Nat
  fuel : Bool
  deriving DecidableEq, Repr

def contentionStep
    (routes : List CausalRoute)
    (validB : Nat → Nat → Bool)
    (state : ResourceState)
    (failure : Nat) : Option ResourceState :=
  if state.fuel then
    if coversLiveCausalFailureB state.live routes validB failure then
      some { state with fuel := false }
    else
      none
  else
    none

def contentionInitial : ResourceState :=
  ⟨[0], true⟩

def contentionDepleted : ResourceState :=
  ⟨[0], false⟩

theorem repeated_static_complete_cover :
    CompleteLiveCausalCover
      contentionInitial.live
      repeatedRoutes repeatedValidB repeatedAdmitted := by
  decide

theorem each_failure_individually_repairable :
    contentionStep repeatedRoutes repeatedValidB contentionInitial 0 =
      some contentionDepleted ∧
    contentionStep repeatedRoutes repeatedValidB contentionInitial 1 =
      some contentionDepleted := by
  decide

theorem shared_resource_breaks_sequence_01 :
    runViable
      (contentionStep repeatedRoutes repeatedValidB)
      contentionInitial [0, 1] = none := by
  decide

theorem shared_resource_breaks_sequence_10 :
    runViable
      (contentionStep repeatedRoutes repeatedValidB)
      contentionInitial [1, 0] = none := by
  decide

/-- Exact higher-order separator:
    static live-authorized causal cover of every admitted failure does not
    imply multi-step viability when executing one repair changes shared
    resource state needed by another repair. -/
theorem static_live_causal_cover_not_sequentially_sufficient :
    CompleteLiveCausalCover
      contentionInitial.live
      repeatedRoutes repeatedValidB repeatedAdmitted ∧
    runViable
      (contentionStep repeatedRoutes repeatedValidB)
      contentionInitial [0, 1] = none := by
  exact ⟨repeated_static_complete_cover, shared_resource_breaks_sequence_01⟩

end Metatron.WarrantedContinuationViabilityV6
