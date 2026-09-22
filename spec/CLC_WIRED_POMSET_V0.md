# CLC Wired Pomset V0

**Status:** theorem experiment  
**Branch:** `clc-wired-pomset-v0`

This branch tests the representation suggested by the failure of flat and
layered certificate traces: a finite causal history should preserve partial
order / independence rather than force all evidence into one global sequence.

## Representation

A causal event carries:

- certificate label;
- wire/port lane;
- local causal tick.

The induced strict order is

[
e < e'
iff
operatorname{lane}(e)=operatorname{lane}(e')
land
operatorname{tick}(e)<operatorname{tick}(e').
]

Lean proves irreflexivity and transitivity.

Parallel tensor places the right history on fresh lanes and creates no
cross-lane causal order. Serial composition preserves lanes and moves the
second history later on those lanes.

This is a deliberately tiny **wired pomset**: a finite disjoint union of
lane-local causal chains. It is not yet a general event structure with arbitrary
joins, conflicts, or synchronization.

## Interchange

Two tests are run.

### Synchronized

For four one-step histories,

[
(f_1otimes f_2);(g_1otimes g_2)
]

and

[
(f_1;g_1)otimes(f_2;g_2)
]

have the same induced causal relation on certificate occurrences.

### Asynchronous

One lane has two events before the boundary while the other has one; after the
boundary the depths are reversed.

The earlier layered-trace representation failed this case because a global
stage index introduced false synchronization.

The wired pomset passes: both constructions induce the same partial order,
including

- (1<2<4) on the first lane;
- (3<5<6) on the second lane;
- no false cross-lane order such as (2<5) or (3<4).

This is the main test.

## Canonical level

The two constructions can store events in different list orders. A separate
permutation fixture proves storage order does not affect the induced causal
signature.

Therefore the correct equality target is not equality of serialized provenance
bytes. It is equality/isomorphism of the **causal event structure**.

## Revocation

Two same-shaped histories carry traces corresponding to `[11,22]` and
`[12,22]`.

Revoking certificate 11 kills the first history while the second remains live.

Thus the representation preserves the proof-relevant alternative-support
property required by Flash/RealityGraph.

## Result sought

A green branch supports the hypothesis:

[
oxed{
	ext{developmental history should be represented by causal structure,
not a total serialization.}
}
]

More specifically, the simplest successful representation is already
**port-aware**. Bare series/parallel pomsets with global sequential composition
would add cross-component causal edges and fail interchange. The wires tell the
composition law which causal dependencies should actually be introduced.

## Claim boundary

A green branch does **not** establish:

- arbitrary finite posets or general event structures;
- conflict/concurrency choice;
- general synchronization or merging of ports;
- a categorical quotient by pomset isomorphism;
- full symmetric monoidal or traced axioms;
- interaction with heterogeneous CLC port signatures;
- empirical or ontological conclusions.
