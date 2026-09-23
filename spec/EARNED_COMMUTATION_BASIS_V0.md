# Earned Commutation Basis V0

**Status:** theorem + blind discovery experiment  
**Branch:** `earned-commutation-basis-v0`

## Formal object

A pair certificate is not assumed. It is earned only when two requirements hold:

1. the events are causally incomparable;
2. their labeled actions commute semantically.

`EarnedTrace` is generated only by adjacent swaps carrying such an
`EarnedPair` certificate.

Lean proves:

- `earnedTrace_to_posetTrace`;
- `earnedTrace_to_semanticTrace`;
- `earnedTrace_preserves_run`;
- `sameEarnedComponent_semantically_equal`;
- `all_incomparables_earned_traceConnected`;
- `all_topological_sorts_equal_if_all_incomparables_earned`.

Thus schedule components are derived from actually warranted commutation, not
from graph incomparability alone.

## Discovery target

For anonymous finite transition actions, the exact pairwise warrant is

[
orall s,quad h(g(s))=g(h(s)).
]

This is `ExactWarrantedCommute`, proved definitionally equivalent to the
previous `Commute` law.

## Blind V1 fixture

The hidden challenge uses a randomly relabeled three-bit carrier and four
randomly relabeled actions:

- X: toggle source;
- Y: toggle observed;
- A: copy source -> hidden;
- B: copy hidden -> observed.

Exactly three unordered action pairs commute.

All four events are causally incomparable, so there are 24 legal schedules.

The public predictor receives only anonymous transition tables. It must:

- discover the exact commuting relation;
- build the safe-swap schedule graph;
- compute its connected components;
- independently compute exact schedule execution semantics on every state;
- prove the two partitions coincide;
- find the minimum subset of pair certificates that preserves that semantic
  partition.

## Scientific boundary

The result distinguishes three notions:

- **causal incomparability**: the graph permits reordering;
- **semantic commutation**: execution warrants reordering;
- **basis necessity**: the pair certificate is actually needed to recover the
  semantic quotient of schedules.

The general V1 quotient should retain only the earned relation required by
consequence.

## Claim boundary

This finite experiment does not establish higher-order independence,
observational-only commutation, symbolic commutation inference, or scalable
discovery over large action languages. Nucleus authority remains unchanged.
