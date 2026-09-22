import Metatron.MonoidalDeepPresent

namespace Metatron.WiredPomset

universe u v w z

/-!
A tiny finite causal-poset representation.

Events carry a certificate label, a wire/port lane, and a local causal tick.
Causality is lane-local: events on different lanes are independent unless a
later construction explicitly connects those lanes. This is the minimum repair
suggested by the asynchronous interchange falsifier.
-/

structure Event where
  cert : Nat
  lane : Nat
  tick : Nat
  deriving DecidableEq, Repr

structure History where
  width : Nat
  duration : Nat
  events : List Event
  deriving DecidableEq, Repr

def Before (a b : Event) : Prop :=
  a.lane = b.lane ∧ a.tick < b.tick

theorem before_irrefl (e : Event) :
    ¬ Before e e := by
  intro h
  exact Nat.lt_irrefl e.tick h.2

theorem before_trans {a b c : Event}
    (hab : Before a b)
    (hbc : Before b c) :
    Before a c := by
  constructor
  · exact hab.1.trans hbc.1
  · exact Nat.lt_trans hab.2 hbc.2

def shiftLane (k : Nat) (e : Event) : Event :=
  { e with lane := e.lane + k }

def shiftTick (k : Nat) (e : Event) : Event :=
  { e with tick := e.tick + k }

def atom (cert : Nat) : History :=
  {
    width := 1
    duration := 1
    events := [{ cert := cert, lane := 0, tick := 0 }]
  }

/--
Parallel tensor places the right history on fresh lanes. No causal edges are
introduced between the two sides.
-/
def tensor (p q : History) : History :=
  {
    width := p.width + q.width
    duration := Nat.max p.duration q.duration
    events := p.events ++ q.events.map (shiftLane p.width)
  }

/--
Serial composition preserves lane identity and shifts the second history later
in local causal time. The experiment uses histories with matching widths.
-/
def serial (p q : History) : History :=
  {
    width := p.width
    duration := p.duration + q.duration
    events := p.events ++ q.events.map (shiftTick p.duration)
  }

def beforeB (a b : Event) : Bool :=
  (a.lane == b.lane) && decide (a.tick < b.tick)

def certBefore (h : History) (ca cb : Nat) : Bool :=
  h.events.any (fun a =>
    (a.cert == ca) &&
      h.events.any (fun b =>
        (b.cert == cb) && beforeB a b))

def signature (h : History) (ids : List Nat) : List Bool :=
  ids.flatMap (fun a => ids.map (fun b => certBefore h a b))

theorem parallel_atoms_independent :
    certBefore (tensor (atom 1) (atom 2)) 1 2 = false ∧
    certBefore (tensor (atom 1) (atom 2)) 2 1 = false := by
  decide

theorem serial_atoms_ordered :
    certBefore (serial (atom 1) (atom 2)) 1 2 = true := by
  decide

/-!
Synchronized interchange.
-/

def f₁ := atom 1
def f₂ := atom 2
def g₁ := atom 3
def g₂ := atom 4

def syncLeft : History :=
  serial (tensor f₁ f₂) (tensor g₁ g₂)

def syncRight : History :=
  tensor (serial f₁ g₁) (serial f₂ g₂)

theorem wired_interchange_sync :
    signature syncLeft [1, 2, 3, 4] =
    signature syncRight [1, 2, 3, 4] := by
  decide

/-!
Asynchronous interchange.

The two parallel components have different causal depths. Unlike the layered
trace representation, the wired poset keeps each lane's causal clock separate,
so no fake cross-lane order is introduced.
-/

def af₁ : History :=
  serial (atom 1) (atom 2)

def af₂ : History :=
  atom 3

def ag₁ : History :=
  atom 4

def ag₂ : History :=
  serial (atom 5) (atom 6)

def asyncLeft : History :=
  serial (tensor af₁ af₂) (tensor ag₁ ag₂)

def asyncRight : History :=
  tensor (serial af₁ ag₁) (serial af₂ ag₂)

theorem wired_interchange_async :
    signature asyncLeft [1, 2, 3, 4, 5, 6] =
    signature asyncRight [1, 2, 3, 4, 5, 6] := by
  decide

theorem async_expected_order :
    certBefore asyncLeft 1 2 = true ∧
    certBefore asyncLeft 2 4 = true ∧
    certBefore asyncLeft 3 5 = true ∧
    certBefore asyncLeft 5 6 = true ∧
    certBefore asyncLeft 2 5 = false ∧
    certBefore asyncLeft 3 4 = false := by
  decide

/-!
Storage order is not causal order.

Reordering the event list without changing event lane/tick coordinates leaves
the observable causal signature unchanged.
-/

def syncPermuted : History :=
  {
    width := syncLeft.width
    duration := syncLeft.duration
    events := [
      { cert := 4, lane := 1, tick := 1 },
      { cert := 1, lane := 0, tick := 0 },
      { cert := 3, lane := 0, tick := 1 },
      { cert := 2, lane := 1, tick := 0 }
    ]
  }

theorem storage_order_irrelevant :
    signature syncPermuted [1, 2, 3, 4] =
    signature syncLeft [1, 2, 3, 4] := by
  decide

/-!
Alternative support and selective revocation survive the new representation.
-/

def Live (revoked : Nat) (h : History) : Prop :=
  ∀ e, e ∈ h.events → e.cert ≠ revoked

def support₁ : History :=
  serial (atom 11) (atom 22)

def support₂ : History :=
  serial (atom 12) (atom 22)

theorem alternative_support_same_shape :
    support₁.width = support₂.width ∧
    support₁.duration = support₂.duration := by
  decide

theorem revocation_removes_first_support :
    ¬ Live 11 support₁ := by
  intro h
  have hm :
      ({ cert := 11, lane := 0, tick := 0 } : Event) ∈ support₁.events := by
    decide
  exact
    (h { cert := 11, lane := 0, tick := 0 } hm) rfl

theorem alternative_support_survives :
    Live 11 support₂ := by
  intro e he
  change e.cert ≠ 11
  have hcases :
      e = ({ cert := 12, lane := 0, tick := 0 } : Event) ∨
      e = ({ cert := 22, lane := 0, tick := 1 } : Event) := by
    simpa [support₂, serial, atom, shiftTick] using he
  rcases hcases with h | h
  · subst e
    decide
  · subst e
    decide

/-!
A small canonicality statement: serial/parallel construction may store events
in different list orders, but the induced causal relation on certificate labels
is identical. This is the level at which interchange should be required.
-/

theorem causal_not_serialization_is_canonical :
    syncLeft.events ≠ syncRight.events ∧
    signature syncLeft [1, 2, 3, 4] =
      signature syncRight [1, 2, 3, 4] := by
  constructor
  · decide
  · exact wired_interchange_sync

end Metatron.WiredPomset
