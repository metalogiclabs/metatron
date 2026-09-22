import Metatron.WiredPomset

namespace Metatron.PortEventStructure

universe u v w z

/--
A finite port-aware causal presentation. The explicit event list is the finite
carrier. `beforeB` is interpreted as the already-closed strict causal relation
on those events.
-/
structure PES (E : Type u) where
  events : List E
  beforeB : E → E → Bool
  inputPort : E → Option Nat
  outputPort : E → Option Nat
  cert : E → Nat

def leB
    {E : Type u} [DecidableEq E]
    (p : PES E) (a b : E) : Bool :=
  decide (a = b) || p.beforeB a b

def portMatch (a b : Option Nat) : Bool :=
  match a, b with
  | some x, some y => x == y
  | _, _ => false

def wiredB
    {E : Type u} {F : Type v}
    [DecidableEq E] [DecidableEq F]
    (p : PES E) (q : PES F)
    (a : E) (b : F) : Bool :=
  p.events.any (fun o =>
    leB p a o &&
      q.events.any (fun i =>
        portMatch (p.outputPort o) (q.inputPort i) &&
          leB q i b))

/--
Serial gluing hides the internal interface. Causal influence crosses only when
a reachable left output matches a reachable right input.
-/
def serial
    {E : Type u} {F : Type v}
    [DecidableEq E] [DecidableEq F]
    (p : PES E) (q : PES F) :
    PES (Sum E F) where
  events := p.events.map Sum.inl ++ q.events.map Sum.inr
  beforeB := fun x y =>
    match x, y with
    | .inl a, .inl b => p.beforeB a b
    | .inr a, .inr b => q.beforeB a b
    | .inl a, .inr b => wiredB p q a b
    | .inr _, .inl _ => false
  inputPort := fun x =>
    match x with
    | .inl a => p.inputPort a
    | .inr _ => none
  outputPort := fun x =>
    match x with
    | .inl _ => none
    | .inr b => q.outputPort b
  cert := fun x =>
    match x with
    | .inl a => p.cert a
    | .inr b => q.cert b

def tagL (p : Nat) : Nat := 2 * p
def tagR (p : Nat) : Nat := 2 * p + 1

/--
Parallel composition namespaces the two port families and introduces no
cross-component causal relation.
-/
def tensor
    {E : Type u} {F : Type v}
    (p : PES E) (q : PES F) :
    PES (Sum E F) where
  events := p.events.map Sum.inl ++ q.events.map Sum.inr
  beforeB := fun x y =>
    match x, y with
    | .inl a, .inl b => p.beforeB a b
    | .inr a, .inr b => q.beforeB a b
    | _, _ => false
  inputPort := fun x =>
    match x with
    | .inl a => (p.inputPort a).map tagL
    | .inr b => (q.inputPort b).map tagR
  outputPort := fun x =>
    match x with
    | .inl a => (p.outputPort a).map tagL
    | .inr b => (q.outputPort b).map tagR
  cert := fun x =>
    match x with
    | .inl a => p.cert a
    | .inr b => q.cert b

def certBefore
    {E : Type u}
    (p : PES E) (ca cb : Nat) : Bool :=
  p.events.any (fun a =>
    (p.cert a == ca) &&
      p.events.any (fun b =>
        (p.cert b == cb) && p.beforeB a b))

def hasInput
    {E : Type u}
    (p : PES E) (c port : Nat) : Bool :=
  p.events.any (fun e =>
    (p.cert e == c) && decide (p.inputPort e = some port))

def hasOutput
    {E : Type u}
    (p : PES E) (c port : Nat) : Bool :=
  p.events.any (fun e =>
    (p.cert e == c) && decide (p.outputPort e = some port))

def causalSignature
    {E : Type u}
    (p : PES E) (ids : List Nat) : List Bool :=
  ids.flatMap (fun a => ids.map (fun b => certBefore p a b))

def isoCheck
    {E : Type u} {F : Type v}
    [DecidableEq E] [DecidableEq F]
    (p : PES E) (q : PES F)
    (f : E → F) (g : F → E) : Bool :=
  p.events.all (fun e =>
    decide (g (f e) = e) &&
    decide (p.cert e = q.cert (f e)) &&
    decide (p.inputPort e = q.inputPort (f e)) &&
    decide (p.outputPort e = q.outputPort (f e)) &&
    p.events.all (fun e' =>
      decide (p.beforeB e e' = q.beforeB (f e) (f e')))) &&
  q.events.all (fun x => decide (f (g x) = x))

/-!
Non-series-parallel finite DAG fixtures.
-/

def diamond
    (base inPort outPort : Nat) :
    PES (Fin 4) where
  events := [0, 1, 2, 3]
  beforeB := fun a b =>
    decide (
      (a.val = 0 ∧ b.val = 1) ∨
      (a.val = 0 ∧ b.val = 2) ∨
      (a.val = 0 ∧ b.val = 3) ∨
      (a.val = 1 ∧ b.val = 3) ∨
      (a.val = 2 ∧ b.val = 3))
  inputPort := fun a => if a.val = 0 then some inPort else none
  outputPort := fun a => if a.val = 3 then some outPort else none
  cert := fun a => base + a.val

def fork3
    (base inPort outPort : Nat) :
    PES (Fin 3) where
  events := [0, 1, 2]
  beforeB := fun a b =>
    decide (
      (a.val = 0 ∧ b.val = 1) ∨
      (a.val = 0 ∧ b.val = 2))
  inputPort := fun a => if a.val = 0 then some inPort else none
  outputPort := fun a => if a.val = 1 ∨ a.val = 2 then some outPort else none
  cert := fun a => base + a.val

def chain3
    (base inPort outPort : Nat) :
    PES (Fin 3) where
  events := [0, 1, 2]
  beforeB := fun a b =>
    decide (
      (a.val = 0 ∧ b.val = 1) ∨
      (a.val = 1 ∧ b.val = 2) ∨
      (a.val = 0 ∧ b.val = 2))
  inputPort := fun a => if a.val = 0 then some inPort else none
  outputPort := fun a => if a.val = 2 then some outPort else none
  cert := fun a => base + a.val

/-!
Associativity up to an explicit causal-structure isomorphism.
-/

def pA := diamond 100 10 20
def qA := fork3 200 20 30
def rA := diamond 300 30 40

def assocLeft := serial (serial pA qA) rA
def assocRight := serial pA (serial qA rA)

def reassoc
    {A : Type u} {B : Type v} {C : Type w} :
    Sum (Sum A B) C → Sum A (Sum B C)
  | .inl (.inl a) => .inl a
  | .inl (.inr b) => .inr (.inl b)
  | .inr c => .inr (.inr c)

def unreassoc
    {A : Type u} {B : Type v} {C : Type w} :
    Sum A (Sum B C) → Sum (Sum A B) C
  | .inl a => .inl (.inl a)
  | .inr (.inl b) => .inl (.inr b)
  | .inr (.inr c) => .inr c

theorem serial_assoc_explicit_iso :
    isoCheck assocLeft assocRight reassoc unreassoc = true := by
  decide

/-!
Interchange up to an explicit causal-structure isomorphism, using arbitrary
finite DAG components rather than lane-local chains.
-/

def pI := diamond 1000 1 7
def qI := fork3 1100 2 8
def rI := chain3 1200 7 9
def sI := diamond 1300 8 10

def interchangeLeft :=
  serial (tensor pI qI) (tensor rI sI)

def interchangeRight :=
  tensor (serial pI rI) (serial qI sI)

def interchangeMap
    {A : Type u} {B : Type v} {C : Type w} {D : Type z} :
    Sum (Sum A B) (Sum C D) → Sum (Sum A C) (Sum B D)
  | .inl (.inl a) => .inl (.inl a)
  | .inl (.inr b) => .inr (.inl b)
  | .inr (.inl c) => .inl (.inr c)
  | .inr (.inr d) => .inr (.inr d)

def interchangeInv
    {A : Type u} {B : Type v} {C : Type w} {D : Type z} :
    Sum (Sum A C) (Sum B D) → Sum (Sum A B) (Sum C D)
  | .inl (.inl a) => .inl (.inl a)
  | .inl (.inr c) => .inr (.inl c)
  | .inr (.inl b) => .inl (.inr b)
  | .inr (.inr d) => .inr (.inr d)

theorem serial_parallel_interchange_explicit_iso :
    isoCheck
      interchangeLeft interchangeRight
      interchangeMap interchangeInv = true := by
  decide

theorem interchange_no_false_cross_dependency :
    certBefore interchangeLeft 1003 1300 = false ∧
    certBefore interchangeLeft 1101 1200 = false := by
  decide

/-!
Proof-relevant lineage and selective revocation survive port-aware DAG
composition.
-/

def atomPES (cert inPort outPort : Nat) : PES Unit where
  events := [()]
  beforeB := fun _ _ => false
  inputPort := fun _ => some inPort
  outputPort := fun _ => some outPort
  cert := fun _ => cert

def supportA := serial (atomPES 11 1 2) (atomPES 22 2 3)
def supportB := serial (atomPES 12 1 2) (atomPES 22 2 3)

def liveB
    {E : Type u}
    (revoked : Nat) (p : PES E) : Bool :=
  p.events.all (fun e => decide (p.cert e ≠ revoked))

theorem revocation_selective :
    liveB 11 supportA = false ∧
    liveB 11 supportB = true := by
  decide

theorem alternative_support_causal_shape :
    causalSignature supportA [11, 22] = [false, true, false, false] ∧
    causalSignature supportB [12, 22] = [false, true, false, false] := by
  decide

end Metatron.PortEventStructure
