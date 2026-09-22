# Finite Poset Topological-Sort Connectivity V0

**Status:** combinatorial closure theorem experiment  
**Branch:** `finite-poset-toposort-connectivity-v0`

## Objective

Close the remaining finite-poset gap in V1.

Given a finite strict precedence relation (R), define a duplicate-free
topological schedule recursively: at each head event, no event remaining in the
tail is required to precede it.

Define `PosetTrace R` as the reflexive/symmetric/transitive closure of adjacent
swaps of incomparable events.

## Main combinatorial theorem

[
oxed{	exttt{all_topological_sorts_traceConnected}}
]

states:

> Any two topological schedules that are permutations of the same finite event
> multiset are connected by adjacent swaps of (R)-incomparable events.

The proof is constructive.

Take the head (x) of the first schedule. Find (x) in the second schedule and
bubble it left to the front. Every crossed event (y) must be incomparable
with (x):

- (y 
ot< x) because the first schedule has (x) before (y);
- (x 
ot< y) because the second schedule has (y) before (x).

After bubbling, cancel the common head and recurse on the remaining schedules.

No transitivity or totality assumption is needed beyond the schedules satisfying
the declared topological predicate.

## Semantic composition

[
oxed{	exttt{posetTrace_to_semanticTrace}}
]

maps the pure incomparable-swap trace into the already-qualified
`TraceEq` whenever every incomparable pair has a semantic `Commute`
certificate.

Therefore:

[
oxed{	exttt{all_topological_sorts_semantically_invariant}}
]

proves that all topological schedules over the same finite event multiset have
identical execution semantics whenever all incomparable event actions commute.

## PES specialization

`PESBefore p a b` interprets the PES Boolean causal relation as a proposition.

`TopologicalSchedule p xs` requires:

1. `xs` satisfies the topological predicate for `PESBefore p`;
2. `xs` is a permutation of the PES event list.

Then:

[
oxed{	exttt{pes_topological_sorts_traceConnected}}
]

and

[
oxed{	exttt{pes_all_topological_sorts_semantically_invariant}}
]

close the finite causal quotient under the explicit condition that every
incomparable event pair is semantically certified to commute.

## Positive fixture

A fork poset with

[
0<2,qquad 1<2,
]

and (0,1) incomparable has the legal schedules

[
[0,1,2],qquad [1,0,2].
]

The theorem proves they are trace-connected.

## Negative retention

A comparable pair (0<1) is explicitly proved not incomparable, so the trace
generator cannot swap it.

## Consequence for V1

The remaining separation between causal graph and serialized repair can now be
stated exactly:

[
oxed{
	ext{finite PES}
+
	ext{topological schedules}
+
	ext{commutation certificate for every incomparable pair}
Rightarrow
	ext{one semantic trace class}
}
]

Thus the canonical repair object is a finite causal presentation modulo its
certified commuting topological schedules.

## Claim boundary

This theorem is finite and list-based. It does not prove that arbitrary
real-world candidate generators expose decidable commutation certificates, nor
does it solve event-structure synthesis, conflict, synchronization, feedback,
or minimum trace-class search at scale. The trusted Nucleus is unchanged.
