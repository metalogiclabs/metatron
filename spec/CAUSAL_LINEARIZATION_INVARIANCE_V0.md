# Causal Linearization Invariance V0

**Status:** theorem boundary experiment  
**Branch:** `causal-linearization-invariance-v0`

## Question

Can certified causal repairs be quotiented by causal structure rather than by one
privileged serialized schedule?

The answer is conditional.

A partial order by itself is not enough. Two causally incomparable events may
still interfere semantically. Linearizations may be identified only when the
swaps relating them are backed by a semantic independence law.

## Minimal positive theorem

For two events with no causal edge, define two certified linearizations:

- left-to-right: [g0,g1]
- right-to-left: [g1,g0]

If the actions commute pointwise,

[
act(g_1,act(g_0,s)) = act(g_0,act(g_1,s))
]

for every state s, then Lean proves

[
oxed{	exttt{independentSwap_invariant_of_commute}}
]

and therefore the two linearizations produce the same state and every
observation agrees.

`independent_swapSafe_of_commute` packages this as the minimal quotient law.

## Positive fixture

Two independent updates on different state fields commute. Their two legal
linearizations have the same final state and observation.

## RED falsifier

Reuse the qualified synergy actions A and B:

- A: source -> hidden
- B: hidden -> observed

Place them in the same two-event PES with **no causal edge**. The two schedules
have the same event carrier and the same causal signature.

But:

[
A	o B
]

separates the witness, while

[
B	o A
]

does not.

Lean proves:

[
oxed{	exttt{causalStructureAlone_not_enough}}
]

and

[
oxed{	exttt{ab_not_swapSafe}}.
]

Thus raw partial-order isomorphism does not by itself justify execution
quotienting.

## Correct boundary

The next representation is not simply

[
	ext{PES}/cong.
]

It is a PES equipped with enough semantic independence evidence to justify
commuting incomparable events.

For the two-event case:

[
oxed{
	ext{causal independence}
+
	ext{semantic commutation}
Rightarrow
	ext{linearization invariance}
}
]

while failure of commutation preserves the serialized distinction.

## Consequence for V1

The minimum certified causal repair frontier remains correct, but repair
canonicalization should quotient only by **certified swap-safe
linearizations**, not all topological sorts of the same causal graph.

This keeps causal structure canonical only to the extent warranted by execution
semantics.

## Claim boundary

A green branch establishes the two-event swap law and its counterexample. It
does not yet prove the general theorem for arbitrary finite partial orders,
Mazurkiewicz trace equivalence, Church-Rosser/confluence, conflict,
synchronization, or feedback.
