import Metatron.DevelopmentalRelation

namespace Metatron.ProofRelevantOplax

open Metatron.FutureObservations
open Metatron.FixedPointReflection
open Metatron.DevelopmentalRelation

universe u v w z

/-!
Certified raw maps form an ordinary category before quotienting.
The trace is proof-relevant data and is never erased by composition.
-/

structure CertifiedMap (A : Type u) (B : Type v) where
  map : A → B
  trace : List Nat

def cid (A : Type u) : CertifiedMap A A :=
  ⟨fun x => x, []⟩

def ccomp
    {A : Type u} {B : Type v} {C : Type w}
    (f : CertifiedMap A B)
    (g : CertifiedMap B C) :
    CertifiedMap A C :=
  ⟨fun x => g.map (f.map x), f.trace ++ g.trace⟩

theorem ccomp_id_left
    {A : Type u} {B : Type v}
    (f : CertifiedMap A B) :
    ccomp (cid A) f = f := by
  cases f
  rfl

theorem ccomp_id_right
    {A : Type u} {B : Type v}
    (f : CertifiedMap A B) :
    ccomp f (cid B) = f := by
  cases f with
  | mk map trace =>
      simp [ccomp, cid]

theorem ccomp_assoc
    {A : Type u} {B : Type v} {C : Type w} {D : Type z}
    (f : CertifiedMap A B)
    (g : CertifiedMap B C)
    (h : CertifiedMap C D) :
    ccomp (ccomp f g) h = ccomp f (ccomp g h) := by
  cases f with
  | mk fmap ftrace =>
      cases g with
      | mk gmap gtrace =>
          cases h with
          | mk hmap htrace =>
              simp [ccomp, List.append_assoc]

def certMapOne : CertifiedMap Bool Bool :=
  ⟨fun x => x, [11]⟩

def certMapTwo : CertifiedMap Bool Bool :=
  ⟨fun x => x, [12]⟩

theorem same_map_different_certificate :
    certMapOne.map = certMapTwo.map ∧ certMapOne ≠ certMapTwo := by
  constructor
  · rfl
  · intro h
    have ht := congrArg CertifiedMap.trace h
    simp [certMapOne, certMapTwo] at ht

/-!
Evidence-lifted quotient relation.

The Prop-level QuotientRelation says that a developmental possibility exists.
QEvidence retains the representative and exact certificate trace that supports
that possibility.
-/

structure QEvidence
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (f : CertifiedMap AState BState)
    (qa : BehavioralQuotient actA evalA protA)
    (qb : BehavioralQuotient actB evalB protB) where
  repr : AState
  source_eq : quotientMap actA evalA protA repr = qa
  target_eq : quotientMap actB evalB protB (f.map repr) = qb
  trace : List Nat
  trace_eq : trace = f.trace

theorem qEvidence_nonempty_iff_relation
    {AState : Type u} {BState : Type v}
    {AStep : Type w} {BStep : Type z}
    {ATest BTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (f : CertifiedMap AState BState)
    (qa : BehavioralQuotient actA evalA protA)
    (qb : BehavioralQuotient actB evalB protB) :
    Nonempty
      (QEvidence
        actA evalA protA actB evalB protB f qa qb) ↔
    QuotientRelation
      actA evalA protA actB evalB protB f.map qa qb := by
  constructor
  · intro h
    rcases h with ⟨e⟩
    exact ⟨e.repr, e.source_eq, e.target_eq⟩
  · intro h
    rcases h with ⟨x, hqa, hqb⟩
    exact ⟨{
      repr := x
      source_eq := hqa
      target_eq := hqb
      trace := f.trace
      trace_eq := rfl
    }⟩

def QEvidenceComp
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (actC : CStep → CState → CState)
    (evalC : CTest → CState → Val)
    (protC : CTest → Prop)
    (f : CertifiedMap AState BState)
    (g : CertifiedMap BState CState)
    (qa : BehavioralQuotient actA evalA protA)
    (qc : BehavioralQuotient actC evalC protC) :=
  Σ qb : BehavioralQuotient actB evalB protB,
    QEvidence actA evalA protA actB evalB protB f qa qb ×
    QEvidence actB evalB protB actC evalC protC g qb qc

def directEvidenceToComposed
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (actC : CStep → CState → CState)
    (evalC : CTest → CState → Val)
    (protC : CTest → Prop)
    (f : CertifiedMap AState BState)
    (g : CertifiedMap BState CState)
    (qa : BehavioralQuotient actA evalA protA)
    (qc : BehavioralQuotient actC evalC protC)
    (e :
      QEvidence
        actA evalA protA actC evalC protC
        (ccomp f g) qa qc) :
    QEvidenceComp
      actA evalA protA
      actB evalB protB
      actC evalC protC
      f g qa qc :=
  ⟨quotientMap actB evalB protB (f.map e.repr),
    {
      repr := e.repr
      source_eq := e.source_eq
      target_eq := rfl
      trace := f.trace
      trace_eq := rfl
    },
    {
      repr := f.map e.repr
      source_eq := rfl
      target_eq := e.target_eq
      trace := g.trace
      trace_eq := rfl
    }⟩

def composedEvidenceTrace
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    {actA : AStep → AState → AState}
    {evalA : ATest → AState → Val}
    {protA : ATest → Prop}
    {actB : BStep → BState → BState}
    {evalB : BTest → BState → Val}
    {protB : BTest → Prop}
    {actC : CStep → CState → CState}
    {evalC : CTest → CState → Val}
    {protC : CTest → Prop}
    {f : CertifiedMap AState BState}
    {g : CertifiedMap BState CState}
    {qa : BehavioralQuotient actA evalA protA}
    {qc : BehavioralQuotient actC evalC protC}
    (e :
      QEvidenceComp
        actA evalA protA
        actB evalB protB
        actC evalC protC
        f g qa qc) : List Nat :=
  e.2.1.trace ++ e.2.2.trace

theorem directEvidence_trace_preserved
    {AState : Type u} {BState : Type v} {CState : Type w}
    {AStep BStep CStep ATest BTest CTest Val : Type}
    (actA : AStep → AState → AState)
    (evalA : ATest → AState → Val)
    (protA : ATest → Prop)
    (actB : BStep → BState → BState)
    (evalB : BTest → BState → Val)
    (protB : BTest → Prop)
    (actC : CStep → CState → CState)
    (evalC : CTest → CState → Val)
    (protC : CTest → Prop)
    (f : CertifiedMap AState BState)
    (g : CertifiedMap BState CState)
    (qa : BehavioralQuotient actA evalA protA)
    (qc : BehavioralQuotient actC evalC protC)
    (e :
      QEvidence
        actA evalA protA actC evalC protC
        (ccomp f g) qa qc) :
    composedEvidenceTrace
      (directEvidenceToComposed
        actA evalA protA
        actB evalB protB
        actC evalC protC
        f g qa qc e) =
    (ccomp f g).trace := by
  simp [composedEvidenceTrace, directEvidenceToComposed, ccomp]

/-!
Concrete causal re-entry fixture.

A and C distinguish Bool completely; B protects only the constant test, so its
behavioral quotient collapses false and true. Relational composition can enter
B through false and leave through true. The direct composite cannot.
-/

def reentryF : CertifiedMap Bool Bool :=
  ⟨fun x => x, [101]⟩

def reentryG : CertifiedMap Bool Bool :=
  ⟨fun x => x, [202]⟩

def qAFalse :
    BehavioralQuotient tinyAct tinyEval allTinyProtected :=
  quotientMap tinyAct tinyEval allTinyProtected false

def qBFalse :
    BehavioralQuotient tinyAct tinyEval tinyProtected :=
  quotientMap tinyAct tinyEval tinyProtected false

def qCTrue :
    BehavioralQuotient tinyAct tinyEval allTinyProtected :=
  quotientMap tinyAct tinyEval allTinyProtected true

theorem allTiny_quotient_ne :
    quotientMap tinyAct tinyEval allTinyProtected false ≠
    quotientMap tinyAct tinyEval allTinyProtected true := by
  intro h
  exact tinyAll_not_futureEq (Quotient.exact h)

theorem reentry_composed_relation :
    RelComp
      (QuotientRelation
        tinyAct tinyEval allTinyProtected
        tinyAct tinyEval tinyProtected
        reentryF.map)
      (QuotientRelation
        tinyAct tinyEval tinyProtected
        tinyAct tinyEval allTinyProtected
        reentryG.map)
      qAFalse qCTrue := by
  refine ⟨qBFalse, ?_, ?_⟩
  · exact ⟨false, rfl, rfl⟩
  · refine ⟨true, ?_, rfl⟩
    exact (Quotient.sound tinyFutureEq).symm

theorem reentry_not_direct :
    ¬ QuotientRelation
      tinyAct tinyEval allTinyProtected
      tinyAct tinyEval allTinyProtected
      (ccomp reentryF reentryG).map
      qAFalse qCTrue := by
  intro h
  rcases h with ⟨x, hA, hC⟩
  cases x with
  | false =>
      exact allTiny_quotient_ne hC
  | true =>
      exact allTiny_quotient_ne hA.symm

theorem reentry_evidence_path :
    Nonempty
      (QEvidenceComp
        tinyAct tinyEval allTinyProtected
        tinyAct tinyEval tinyProtected
        tinyAct tinyEval allTinyProtected
        reentryF reentryG qAFalse qCTrue) := by
  exact ⟨
    ⟨qBFalse,
      {
        repr := false
        source_eq := rfl
        target_eq := rfl
        trace := [101]
        trace_eq := rfl
      },
      {
        repr := true
        source_eq := (Quotient.sound tinyFutureEq).symm
        target_eq := rfl
        trace := [202]
        trace_eq := rfl
      }⟩
  ⟩

theorem reentry_evidence_trace :
    ∃ e :
      QEvidenceComp
        tinyAct tinyEval allTinyProtected
        tinyAct tinyEval tinyProtected
        tinyAct tinyEval allTinyProtected
        reentryF reentryG qAFalse qCTrue,
      composedEvidenceTrace e = [101, 202] := by
  refine ⟨
    ⟨qBFalse,
      {
        repr := false
        source_eq := rfl
        target_eq := rfl
        trace := [101]
        trace_eq := rfl
      },
      {
        repr := true
        source_eq := (Quotient.sound tinyFutureEq).symm
        target_eq := rfl
        trace := [202]
        trace_eq := rfl
      }⟩,
    rfl
  ⟩

theorem reentry_no_direct_evidence :
    ¬ Nonempty
      (QEvidence
        tinyAct tinyEval allTinyProtected
        tinyAct tinyEval allTinyProtected
        (ccomp reentryF reentryG)
        qAFalse qCTrue) := by
  intro h
  apply reentry_not_direct
  exact
    (qEvidence_nonempty_iff_relation
      tinyAct tinyEval allTinyProtected
      tinyAct tinyEval allTinyProtected
      (ccomp reentryF reentryG)
      qAFalse qCTrue).1 h

/-!
Proof-lifted Flash-style closure.

The closure object lives in Type, so two derivations with identical endpoints
remain distinct when their certificate traces differ. Its support projection is
the least transitive relation containing the certified edges.
-/

inductive ProofClosure
    {Node : Type u}
    (Edge : Node → Node → Type v) :
    Node → Node → Type (max u v)
  | edge {a b} : Edge a b → ProofClosure Edge a b
  | comp {a b c} :
      ProofClosure Edge a b →
      ProofClosure Edge b c →
      ProofClosure Edge a c

def closureTrace
    {Node : Type u}
    {Edge : Node → Node → Type v}
    (cert : ∀ {a b}, Edge a b → Nat) :
    ∀ {a b}, ProofClosure Edge a b → List Nat
  | _, _, ProofClosure.edge e => [cert e]
  | _, _, ProofClosure.comp p q =>
      closureTrace cert p ++ closureTrace cert q

def ClosureSupport
    {Node : Type u}
    (Edge : Node → Node → Type v)
    (a b : Node) : Prop :=
  Nonempty (ProofClosure Edge a b)

theorem closure_contains
    {Node : Type u}
    {Edge : Node → Node → Type v}
    {a b : Node}
    (e : Edge a b) :
    ClosureSupport Edge a b := by
  exact ⟨ProofClosure.edge e⟩

theorem closure_trans
    {Node : Type u}
    {Edge : Node → Node → Type v}
    {a b c : Node} :
    ClosureSupport Edge a b →
    ClosureSupport Edge b c →
    ClosureSupport Edge a c := by
  intro hab hbc
  rcases hab with ⟨p⟩
  rcases hbc with ⟨q⟩
  exact ⟨ProofClosure.comp p q⟩

theorem closure_least
    {Node : Type u}
    {Edge : Node → Node → Type v}
    (S : Node → Node → Prop)
    (hedge : ∀ {a b}, Edge a b → S a b)
    (htrans : ∀ {a b c}, S a b → S b c → S a c) :
    ∀ {a b}, ClosureSupport Edge a b → S a b := by
  intro a b h
  rcases h with ⟨p⟩
  induction p with
  | edge e =>
      exact hedge e
  | comp p q ihp ihq =>
      exact htrans ihp ihq

/-!
The re-entry witness can itself be consumed as a proof-lifted closure path.
This is the explicit bridge from quotient-level causal re-entry to Flash-style
reclosure.
-/

def reentryFEvidence :
    QEvidence
      tinyAct tinyEval allTinyProtected
      tinyAct tinyEval tinyProtected
      reentryF qAFalse qBFalse :=
  {
    repr := false
    source_eq := rfl
    target_eq := rfl
    trace := [101]
    trace_eq := rfl
  }

def reentryGEvidence :
    QEvidence
      tinyAct tinyEval tinyProtected
      tinyAct tinyEval allTinyProtected
      reentryG qBFalse qCTrue :=
  {
    repr := true
    source_eq := (Quotient.sound tinyFutureEq).symm
    target_eq := rfl
    trace := [202]
    trace_eq := rfl
  }

inductive ReentryNode
  | source | middle | target

inductive ReentryEdge : ReentryNode → ReentryNode → Type
  | first : QEvidence
      tinyAct tinyEval allTinyProtected
      tinyAct tinyEval tinyProtected
      reentryF qAFalse qBFalse →
      ReentryEdge .source .middle
  | second : QEvidence
      tinyAct tinyEval tinyProtected
      tinyAct tinyEval allTinyProtected
      reentryG qBFalse qCTrue →
      ReentryEdge .middle .target

def reentryEdgeCert :
    ∀ {a b}, ReentryEdge a b → Nat
  | _, _, ReentryEdge.first _ => 101
  | _, _, ReentryEdge.second _ => 202

def reentryFlashPath :
    ProofClosure ReentryEdge .source .target :=
  ProofClosure.comp
    (ProofClosure.edge (ReentryEdge.first reentryFEvidence))
    (ProofClosure.edge (ReentryEdge.second reentryGEvidence))

theorem flash_reclosure_carries_reentry :
    closureTrace reentryEdgeCert reentryFlashPath = [101, 202] := by
  rfl

inductive FlashNode
  | a | b | c
  deriving DecidableEq

inductive FlashEdge : FlashNode → FlashNode → Type
  | ab₁ : FlashEdge .a .b
  | ab₂ : FlashEdge .a .b
  | bc : FlashEdge .b .c

def flashCert :
    ∀ {a b}, FlashEdge a b → Nat
  | _, _, FlashEdge.ab₁ => 11
  | _, _, FlashEdge.ab₂ => 12
  | _, _, FlashEdge.bc => 22

def flashPath₁ : ProofClosure FlashEdge .a .c :=
  ProofClosure.comp
    (ProofClosure.edge FlashEdge.ab₁)
    (ProofClosure.edge FlashEdge.bc)

def flashPath₂ : ProofClosure FlashEdge .a .c :=
  ProofClosure.comp
    (ProofClosure.edge FlashEdge.ab₂)
    (ProofClosure.edge FlashEdge.bc)

theorem flash_alternative_traces :
    closureTrace flashCert flashPath₁ = [11, 22] ∧
    closureTrace flashCert flashPath₂ = [12, 22] := by
  constructor <;> rfl

def TraceLive (revoked : Nat) (trace : List Nat) : Prop :=
  ∀ c, c ∈ trace → c ≠ revoked

theorem flash_revocation_removes_one_support :
    ¬ TraceLive 11 (closureTrace flashCert flashPath₁) := by
  change ¬ TraceLive 11 [11, 22]
  intro h
  have hm : 11 ∈ [11, 22] := by decide
  exact (h 11 hm) rfl

theorem flash_alternative_support_survives :
    TraceLive 11 (closureTrace flashCert flashPath₂) := by
  change TraceLive 11 [12, 22]
  intro c hc
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hc
  rcases hc with h | h
  · subst c
    decide
  · subst c
    decide

end Metatron.ProofRelevantOplax
