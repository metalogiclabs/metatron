import Metatron.EmbeddedObserverOntology

namespace Metatron.NovelCapabilityGenesis

open Metatron.FutureObservations
open Metatron.EmbeddedObserverOntology

universe u v w z q

structure InterfaceExtension
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (oldI newI : ObserverInterface World Observer Step Test Val) : Prop where
  accessible_mono :
    ∀ o s, oldI.accessible o s → newI.accessible o s
  available_mono :
    ∀ o t, oldI.available o t → newI.available o t
  test_same :
    ∀ o t x, newI.test o t x = oldI.test o t x

def modelWith
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (d : AbsoluteDynamics World Observer Step)
    (i : ObserverInterface World Observer Step Test Val) :
    EmbeddedModel World Observer Step Test Val where
  dynamics := d
  interface := i

theorem lawfulPath_mono
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (d : AbsoluteDynamics World Observer Step)
    (oldI newI : ObserverInterface World Observer Step Test Val)
    (hext : InterfaceExtension oldI newI)
    (o : Observer)
    (steps : List Step)
    (h : LawfulPath (modelWith d oldI) o steps) :
    LawfulPath (modelWith d newI) o steps := by
  induction steps generalizing o with
  | nil =>
      trivial
  | cons s ss ih =>
      exact ⟨hext.accessible_mono o s h.1,
        ih (d.observerAct s o) h.2⟩

theorem interfaceExtension_refines
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (d : AbsoluteDynamics World Observer Step)
    (oldI newI : ObserverInterface World Observer Step Test Val)
    (hext : InterfaceExtension oldI newI)
    (o : Observer)
    {x y : World}
    (hnew : EmbeddedFutureEq (modelWith d newI) o x y) :
    EmbeddedFutureEq (modelWith d oldI) o x y := by
  intro steps hold q hq
  have hnewPath :=
    lawfulPath_mono d oldI newI hext o steps hold
  have hnewAvail :
      newI.available (run d.observerAct steps o) q :=
    hext.available_mono _ _ hq
  have hEq := hnew steps hnewPath q hnewAvail
  simpa [modelWith, hext.test_same] using hEq

def StrictInterfaceRefinement
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (d : AbsoluteDynamics World Observer Step)
    (oldI newI : ObserverInterface World Observer Step Test Val)
    (o : Observer) : Prop :=
  (∀ x y,
    EmbeddedFutureEq (modelWith d newI) o x y →
      EmbeddedFutureEq (modelWith d oldI) o x y) ∧
  ∃ x y,
    EmbeddedFutureEq (modelWith d oldI) o x y ∧
    ¬ EmbeddedFutureEq (modelWith d newI) o x y

theorem extension_with_new_distinction_is_strict
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (d : AbsoluteDynamics World Observer Step)
    (oldI newI : ObserverInterface World Observer Step Test Val)
    (hext : InterfaceExtension oldI newI)
    (o : Observer)
    (x y : World)
    (hold : EmbeddedFutureEq (modelWith d oldI) o x y)
    (hnew : ¬ EmbeddedFutureEq (modelWith d newI) o x y) :
    StrictInterfaceRefinement d oldI newI o := by
  constructor
  · intro a b hab
    exact interfaceExtension_refines d oldI newI hext o hab
  · exact ⟨x, y, hold, hnew⟩

def HasNovelAccess
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (oldI newI : ObserverInterface World Observer Step Test Val) : Prop :=
  (∃ o s, newI.accessible o s ∧ ¬ oldI.accessible o s) ∨
  (∃ o t, newI.available o t ∧ ¬ oldI.available o t)

theorem strict_extension_requires_novel_interface_witness
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (d : AbsoluteDynamics World Observer Step)
    (oldI newI : ObserverInterface World Observer Step Test Val)
    (hext : InterfaceExtension oldI newI)
    (o : Observer)
    (hstrict : StrictInterfaceRefinement d oldI newI o)
    (hnoNovel :
      ∀ o s, newI.accessible o s ↔ oldI.accessible o s)
    (hnoTestNovel :
      ∀ o t, newI.available o t ↔ oldI.available o t) :
    False := by
  rcases hstrict.2 with ⟨x, y, hold, hnotnew⟩
  apply hnotnew
  intro steps hsteps q hq
  have holdPath : LawfulPath (modelWith d oldI) o steps := by
    induction steps generalizing o with
    | nil =>
        trivial
    | cons s ss ih =>
        exact ⟨(hnoNovel o s).1 hsteps.1,
          ih (d.observerAct s o) hsteps.2⟩
  have holdAvail :
      oldI.available (run d.observerAct steps o) q :=
    (hnoTestNovel _ _).1 hq
  have hEq := hold steps holdPath q holdAvail
  rw [hext.test_same, hext.test_same]
  exact hEq

/-! Concrete strict novel-test acquisition fixture. -/

def gainedHiddenInterface :
    ObserverInterface World Observer Step Test Bool where
  accessible := closedInterface.accessible
  test := observerTest
  available
    | _, .visible => True
    | _, .hidden => True

theorem closed_to_gained_extension :
    InterfaceExtension closedInterface gainedHiddenInterface := by
  constructor
  · intro o s h
    exact h
  · intro o t h
    cases o <;> cases t <;> simp [closedInterface, gainedHiddenInterface,
      testAvailable] at h ⊢
  · intro o t x
    rfl

theorem gained_hidden_separates_witness :
    ¬ EmbeddedFutureEq
      (modelWith absoluteDynamics gainedHiddenInterface)
      Observer.coarse witness0 witness1 := by
  intro h
  have hh := h [] True.intro Test.hidden True.intro
  simp [modelWith, gainedHiddenInterface, observerTest, witness0, witness1, run] at hh

theorem hidden_test_acquisition_is_strict :
    StrictInterfaceRefinement
      absoluteDynamics
      closedInterface
      gainedHiddenInterface
      Observer.coarse := by
  apply extension_with_new_distinction_is_strict
    absoluteDynamics closedInterface gainedHiddenInterface
    closed_to_gained_extension Observer.coarse witness0 witness1
  · exact closed_coarse_identifies_witness
  · exact gained_hidden_separates_witness

theorem hidden_test_is_genuinely_novel :
    HasNovelAccess closedInterface gainedHiddenInterface := by
  right
  refine ⟨Observer.coarse, Test.hidden, True.intro, ?_⟩
  simp [closedInterface, testAvailable]

end Metatron.NovelCapabilityGenesis
