# Causal Trace Quotient V0

**Status:** finite trace-quotient theorem experiment  
**Branch:** `causal-trace-quotient-v0`

## Objective

Lift the qualified two-event swap law to arbitrary finite schedules.

The primitive equivalence step is an adjacent swap

[
pre ++ g :: h :: post
;longleftrightarrow;
pre ++ h :: g :: post
]

backed by a semantic commutation certificate

[
orall s,; act(h,act(g,s)) = act(g,act(h,s)).
]

The finite causal trace relation is the reflexive/symmetric/transitive closure
of these certified adjacent swaps.

## Main theorem

[
oxed{	exttt{traceEq_preserves_run}}
]

proves that any two finite schedules connected by this trace relation produce
identical final states for every initial state.

Therefore

[
oxed{	exttt{traceEq_preserves_observation}}
]

gives observational invariance immediately.

## Topological repair theorem

For two certified repairs over the same causal presentation, if their supports
are connected by the certified trace relation, Lean proves

[
oxed{	exttt{topological_linearizations_equivalent_if_traceConnected}}.
]

This is the finite generalization of the two-event swap law.

It deliberately separates two facts:

1. being legal topological schedules of the same causal presentation;
2. being connected by swaps that are semantically certified safe.

The theorem does not identify schedules merely because they are topological
sorts of the same PES.

## Three-event positive fixture

A three-event schedule is transformed by two certified adjacent swaps:

[
[sourceFlip,noiseFlip,observedFlip]
	o
[noiseFlip,sourceFlip,observedFlip]
	o
[noiseFlip,observedFlip,sourceFlip].
]

Each swap is independently certified by commutation on different state fields.

Lean proves equal final state and equal observation across the whole trace.

## Negative retention

The earlier A/B same-PES noncommuting fixture remains outside the quotient:

[
oxed{	exttt{ab_same_pes_not_trace_quotiented}}.
]

Thus finite trace canonicalization removes only serialization distinctions
earned by semantic commutation evidence.

## Interpretation

The native causal repair representation is now:

[
oxed{
	ext{certified causal presentation}
;/;
	ext{finite certified commuting trace equivalence}
}
]

rather than a privileged total order or raw partial-order isomorphism.

## Claim boundary

This V0 theorem proves invariance for any explicit finite chain of certified
adjacent swaps. It does not yet prove the separate combinatorial theorem that
all topological sorts of every finite poset are connected by adjacent swaps of
incomparable events, nor does it automatically produce commutation certificates
for those incomparable events. It also does not claim confluence, conflict
semantics, feedback, or tractable trace-class enumeration at scale.
