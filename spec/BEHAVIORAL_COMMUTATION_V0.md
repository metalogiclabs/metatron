# Behavioral Commutation V0

**Status:** theorem + blind quotient-relative discovery  
**Branch:** `behavioral-commutation-v0`

## Formal law

Exact state commutation is stronger than necessary.

For a relation R, define `RelCommute R act g h` by

[
R(h(g(s)),g(h(s)))
]

for every state s.

If R is step-closed, then an adjacent swap that commutes modulo R remains
R-equivalent after any continuation. `BehavioralTrace` closes these swaps
under reflexivity, symmetry, and transitivity.

For the continuation-safe relation `FutureEq`, Lean proves:

- `behavioral_adjacent_swap_preserves`;
- `behavioralTrace_preserves`;
- `futureBehavioralTrace_preserves`;
- `futureBehavioralTrace_preserves_protected_observation`.

## Strict-gain fixture

A hidden-state setter and hidden-state toggle do **not** commute as raw states,
but all future protected observations ignore their internal ordering.

Lean proves:

- `hidden_pair_not_exact_commute`;
- `hidden_pair_futureCommute`;
- `behavioral_commutation_strictly_extends_exact`.

A protected-observation setter/toggle pair remains unsafe even modulo FutureEq.

## Blind qualification

Blind Behavioral Commutation V1 exposes only anonymous transition tables and a
public step-closed behavioral quotient.

The predictor must independently recover:

- exact commutation;
- quotient-relative commutation;
- at least one strict behavioral gain;
- safe-swap components over all 24 schedules;
- exact behavioral schedule classes;
- the minimum behavioral certificate basis preserving that partition.

## Interpretation

Metatron may erase an internal ordering distinction when the future behavioral
quotient cannot expose it, even if the raw machine states differ.

This strengthens the constitutional rule:

> Never preserve implementation distinctions that no lawful future can expose.

## Claim boundary

The quotient is supplied and finite in V1. This does not yet discover FutureEq
itself from scratch, synthesize symbolic quotient-commutation proofs on infinite
carriers, or establish higher-order independence.
