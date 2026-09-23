import Metatron.ResidualBasis

namespace Metatron.ResidualGeneratedCapability

open Metatron.ResidualBasis

universe u v

/--
A capability language generated compositionally from reusable observation
atoms. No finite list of completed candidate tests is primitive.
-/
inductive ObsExpr (Atom : Type u) where
  | atom : Atom → ObsExpr Atom
  | xor : ObsExpr Atom → ObsExpr Atom → ObsExpr Atom
  deriving Repr

def ObsExpr.eval
    {Atom : Type u} {State : Type v}
    (atomEval : Atom → State → Bool) :
    ObsExpr Atom → State → Bool
  | .atom a, s => atomEval a s
  | .xor e f, s =>
      Bool.xor (ObsExpr.eval atomEval e s)
        (ObsExpr.eval atomEval f s)

def exprSeparates
    {Atom : Type u} {State : Type v}
    (atomEval : Atom → State → Bool)
    (e : ObsExpr Atom)
    (x y : State) : Prop :=
  e.eval atomEval x ≠ e.eval atomEval y

def GeneratedCover
    {Atom : Type u} {State : Type v}
    (current target : Relation State)
    (atomEval : Atom → State → Bool)
    (basis : List (ObsExpr Atom)) : Prop :=
  CoversResidual current target
    (exprSeparates atomEval) basis

theorem generatedCover_iff_targetSufficient
    {Atom : Type u} {State : Type v}
    (current target : Relation State)
    (atomEval : Atom → State → Bool)
    (basis : List (ObsExpr Atom)) :
    GeneratedCover current target atomEval basis ↔
      TargetSufficient current target
        (exprSeparates atomEval) basis :=
  certifiedResidualBasis_closes
    current target (exprSeparates atomEval) basis

def GeneratedMinimum
    {Atom : Type u} {State : Type v}
    (current target : Relation State)
    (atomEval : Atom → State → Bool)
    (basis : List (ObsExpr Atom)) : Prop :=
  MinimumCoverByLength current target
    (exprSeparates atomEval) basis

theorem generatedMinimum_minimalSufficient
    {Atom : Type u} {State : Type v}
    (current target : Relation State)
    (atomEval : Atom → State → Bool)
    (basis : List (ObsExpr Atom))
    (hmin : GeneratedMinimum current target atomEval basis) :
    TargetSufficient current target
      (exprSeparates atomEval) basis ∧
    ∀ other : List (ObsExpr Atom),
      other.length < basis.length →
        ¬ TargetSufficient current target
          (exprSeparates atomEval) other :=
  minimumResidualBasis_minimalSufficient
    current target (exprSeparates atomEval) basis hmin

/-!
A generated-capability fixture.

The reusable atoms expose masked hidden bits and a reusable noise bit. Neither
hidden bit is supplied as a completed candidate observation. XOR composition
constructs them.
-/

structure GState where
  hiddenA : Bool
  hiddenB : Bool
  visible : Bool
  noise : Bool
  deriving DecidableEq, Repr

inductive GAtom where
  | maskedA
  | maskedB
  | noise
  | visible
  deriving DecidableEq, Repr

def gAtomEval : GAtom → GState → Bool
  | .maskedA, s => Bool.xor s.hiddenA s.noise
  | .maskedB, s => Bool.xor s.hiddenB s.noise
  | .noise, s => s.noise
  | .visible, s => s.visible

def inventedA : ObsExpr GAtom :=
  .xor (.atom .maskedA) (.atom .noise)

def inventedB : ObsExpr GAtom :=
  .xor (.atom .maskedB) (.atom .noise)

def currentRel : Relation GState :=
  fun x y => x.visible = y.visible

def targetRel : Relation GState :=
  fun x y =>
    x.visible = y.visible ∧
    x.hiddenA = y.hiddenA ∧
    x.hiddenB = y.hiddenB

theorem inventedA_recovers_hiddenA
    (s : GState) :
    inventedA.eval gAtomEval s = s.hiddenA := by
  simp [inventedA, ObsExpr.eval, gAtomEval, Bool.xor_assoc]

theorem inventedB_recovers_hiddenB
    (s : GState) :
    inventedB.eval gAtomEval s = s.hiddenB := by
  simp [inventedB, ObsExpr.eval, gAtomEval, Bool.xor_assoc]

theorem invented_pair_targetSufficient :
    TargetSufficient currentRel targetRel
      (exprSeparates gAtomEval)
      [inventedA, inventedB] := by
  intro x y hrefined
  have haNot :=
    hrefined.2 inventedA (by simp)
  have hbNot :=
    hrefined.2 inventedB (by simp)
  have haEval :
      inventedA.eval gAtomEval x =
        inventedA.eval gAtomEval y := by
    simpa [exprSeparates] using haNot
  have hbEval :
      inventedB.eval gAtomEval x =
        inventedB.eval gAtomEval y := by
    simpa [exprSeparates] using hbNot
  constructor
  · exact hrefined.1
  constructor
  · simpa [inventedA_recovers_hiddenA] using haEval
  · simpa [inventedB_recovers_hiddenB] using hbEval

theorem invented_pair_covers :
    GeneratedCover currentRel targetRel
      gAtomEval [inventedA, inventedB] :=
  (generatedCover_iff_targetSufficient
    currentRel targetRel gAtomEval
    [inventedA, inventedB]).2
    invented_pair_targetSufficient

end Metatron.ResidualGeneratedCapability
