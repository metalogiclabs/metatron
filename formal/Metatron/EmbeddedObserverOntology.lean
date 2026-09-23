import Metatron.FutureObservations

namespace Metatron.EmbeddedObserverOntology

open Metatron.FutureObservations

universe u v w z q

structure AbsoluteDynamics
    (World : Type u) (Observer : Type v) (Step : Type w) where
  worldAct : Step → World → World
  observerAct : Step → Observer → Observer

structure ObserverInterface
    (World : Type u) (Observer : Type v) (Step : Type w)
    (Test : Type z) (Val : Type q) where
  accessible : Observer → Step → Prop
  test : Observer → Test → World → Val
  available : Observer → Test → Prop

structure EmbeddedModel
    (World : Type u) (Observer : Type v) (Step : Type w)
    (Test : Type z) (Val : Type q) where
  dynamics : AbsoluteDynamics World Observer Step
  interface : ObserverInterface World Observer Step Test Val

abbrev JointState
    (World : Type u) (Observer : Type v) :=
  World × Observer

def jointAct
    {World : Type u} {Observer : Type v} {Step : Type w}
    (d : AbsoluteDynamics World Observer Step)
    (s : Step)
    (x : JointState World Observer) :
    JointState World Observer :=
  (d.worldAct s x.1, d.observerAct s x.2)

def LawfulPath
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (m : EmbeddedModel World Observer Step Test Val) :
    Observer → List Step → Prop
  | _, [] => True
  | o, s :: ss =>
      m.interface.accessible o s ∧
      LawfulPath m (m.dynamics.observerAct s o) ss

def EmbeddedFutureEq
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (m : EmbeddedModel World Observer Step Test Val)
    (o : Observer) :
    Relation World :=
  fun x y =>
    ∀ steps,
      LawfulPath m o steps →
      ∀ q,
        m.interface.available
          (run m.dynamics.observerAct steps o) q →
        m.interface.test
          (run m.dynamics.observerAct steps o) q
          (run m.dynamics.worldAct steps x) =
        m.interface.test
          (run m.dynamics.observerAct steps o) q
          (run m.dynamics.worldAct steps y)

theorem embeddedFutureEq_refl
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (m : EmbeddedModel World Observer Step Test Val)
    (o : Observer)
    (x : World) :
    EmbeddedFutureEq m o x x := by
  intro steps hsteps q hq
  rfl

theorem embeddedFutureEq_symm
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (m : EmbeddedModel World Observer Step Test Val)
    (o : Observer)
    {x y : World}
    (h : EmbeddedFutureEq m o x y) :
    EmbeddedFutureEq m o y x := by
  intro steps hsteps q hq
  exact (h steps hsteps q hq).symm

theorem embeddedFutureEq_trans
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (m : EmbeddedModel World Observer Step Test Val)
    (o : Observer)
    {x y z' : World}
    (hxy : EmbeddedFutureEq m o x y)
    (hyz : EmbeddedFutureEq m o y z') :
    EmbeddedFutureEq m o x z' := by
  intro steps hsteps q hq
  exact (hxy steps hsteps q hq).trans
    (hyz steps hsteps q hq)

theorem accessible_transition_already_anticipated
    {World : Type u} {Observer : Type v} {Step : Type w}
    {Test : Type z} {Val : Type q}
    (m : EmbeddedModel World Observer Step Test Val)
    (o : Observer)
    (s : Step)
    (hs : m.interface.accessible o s)
    {x y : World}
    (hxy : EmbeddedFutureEq m o x y) :
    EmbeddedFutureEq m
      (m.dynamics.observerAct s o)
      (m.dynamics.worldAct s x)
      (m.dynamics.worldAct s y) := by
  intro steps hsteps q hq
  have hlegal : LawfulPath m o (s :: steps) :=
    ⟨hs, hsteps⟩
  simpa [run] using hxy (s :: steps) hlegal q hq

/-! Concrete embedded-observer fixture. -/

structure World where
  hidden : Bool
  visible : Bool
  deriving DecidableEq, Repr

inductive Observer where
  | coarse
  | fine
  deriving DecidableEq, Repr

inductive Step where
  | stay
  | learn
  deriving DecidableEq, Repr

inductive Test where
  | visible
  | hidden
  deriving DecidableEq, Repr

def absoluteDynamics :
    AbsoluteDynamics World Observer Step where
  worldAct := fun _ w => w
  observerAct
    | .stay, o => o
    | .learn, _ => .fine

def observerTest : Observer → Test → World → Bool
  | _, .visible, w => w.visible
  | _, .hidden, w => w.hidden

def testAvailable : Observer → Test → Prop
  | _, .visible => True
  | .coarse, .hidden => False
  | .fine, .hidden => True

def closedInterface :
    ObserverInterface World Observer Step Test Bool where
  accessible
    | .coarse, .stay => True
    | .coarse, .learn => False
    | .fine, _ => True
  test := observerTest
  available := testAvailable

def anticipatoryInterface :
    ObserverInterface World Observer Step Test Bool where
  accessible := fun _ _ => True
  test := observerTest
  available := testAvailable

def closedModel :
    EmbeddedModel World Observer Step Test Bool where
  dynamics := absoluteDynamics
  interface := closedInterface

def anticipatoryModel :
    EmbeddedModel World Observer Step Test Bool where
  dynamics := absoluteDynamics
  interface := anticipatoryInterface

theorem same_absolute_dynamics :
    closedModel.dynamics = anticipatoryModel.dynamics := by
  rfl

theorem world_run_identity
    (steps : List Step)
    (w : World) :
    run absoluteDynamics.worldAct steps w = w := by
  induction steps generalizing w with
  | nil =>
      rfl
  | cons s ss ih =>
      simpa [run, absoluteDynamics] using ih w

theorem closed_lawful_keeps_coarse
    (steps : List Step)
    (h : LawfulPath closedModel Observer.coarse steps) :
    run absoluteDynamics.observerAct steps Observer.coarse =
      Observer.coarse := by
  induction steps with
  | nil =>
      rfl
  | cons s ss ih =>
      cases s with
      | stay =>
          simpa [run, closedModel, closedInterface, absoluteDynamics] using
            ih h.2
      | learn =>
          exact False.elim h.1

theorem closed_coarse_iff_visible
    (x y : World) :
    EmbeddedFutureEq closedModel Observer.coarse x y ↔
      x.visible = y.visible := by
  constructor
  · intro h
    simpa [closedModel, closedInterface, observerTest, testAvailable, run] using
      h [] True.intro Test.visible True.intro
  · intro hvis steps hsteps q hq
    have ho := closed_lawful_keeps_coarse steps hsteps
    have hx := world_run_identity steps x
    have hy := world_run_identity steps y
    cases q with
    | visible =>
        simpa [closedModel, closedInterface, observerTest, ho, hx, hy] using hvis
    | hidden =>
        have : False := by
          simpa [closedModel, closedInterface, testAvailable, ho] using hq
        exact False.elim this

def witness0 : World := ⟨false, false⟩
def witness1 : World := ⟨true, false⟩

theorem closed_coarse_identifies_witness :
    EmbeddedFutureEq closedModel Observer.coarse
      witness0 witness1 := by
  apply (closed_coarse_iff_visible witness0 witness1).2
  rfl

theorem fine_separates_witness :
    ¬ EmbeddedFutureEq closedModel Observer.fine
      witness0 witness1 := by
  intro h
  have hhidden :=
    h [] True.intro Test.hidden True.intro
  simp [closedModel, closedInterface, observerTest, testAvailable,
    witness0, witness1, run] at hhidden

theorem observer_state_strictly_refines_identity :
    EmbeddedFutureEq closedModel Observer.coarse
      witness0 witness1 ∧
    ¬ EmbeddedFutureEq closedModel Observer.fine
      witness0 witness1 := by
  exact ⟨closed_coarse_identifies_witness, fine_separates_witness⟩

theorem closed_learning_not_accessible :
    ¬ closedModel.interface.accessible Observer.coarse Step.learn := by
  simp [closedModel, closedInterface]

theorem anticipatory_learning_accessible :
    anticipatoryModel.interface.accessible Observer.coarse Step.learn := by
  simp [anticipatoryModel, anticipatoryInterface]

theorem anticipatory_coarse_sees_future_hidden :
    ¬ EmbeddedFutureEq anticipatoryModel Observer.coarse
      witness0 witness1 := by
  intro h
  have hlegal :
      LawfulPath anticipatoryModel Observer.coarse [Step.learn] := by
    simp [LawfulPath, anticipatoryModel, anticipatoryInterface,
      absoluteDynamics]
  have hhidden :=
    h [Step.learn] hlegal Test.hidden True.intro
  simp [anticipatoryModel, anticipatoryInterface, absoluteDynamics,
    observerTest, testAvailable, witness0, witness1, run] at hhidden

theorem same_world_dynamics_different_relational_identity :
    closedModel.dynamics = anticipatoryModel.dynamics ∧
    EmbeddedFutureEq closedModel Observer.coarse witness0 witness1 ∧
    ¬ EmbeddedFutureEq anticipatoryModel Observer.coarse
      witness0 witness1 := by
  exact ⟨same_absolute_dynamics,
    closed_coarse_identifies_witness,
    anticipatory_coarse_sees_future_hidden⟩

/--
Absolute dynamics remain fixed while the observer-relative identity relation is
lawfully determined by the observer's accessible future interface.
-/
theorem absolute_dynamics_relational_identity :
    closedModel.dynamics = anticipatoryModel.dynamics ∧
    (EmbeddedFutureEq closedModel Observer.coarse witness0 witness1) ∧
    (¬ EmbeddedFutureEq anticipatoryModel Observer.coarse
      witness0 witness1) :=
  same_world_dynamics_different_relational_identity

end Metatron.EmbeddedObserverOntology
