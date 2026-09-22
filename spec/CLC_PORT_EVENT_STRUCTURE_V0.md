# CLC Port Event Structure V0

**Status:** theorem experiment  
**Branch:** `clc-port-event-structure-v0`

This branch tests the next representation suggested by Wired Pomset V0:
arbitrary finite causal DAGs with explicit input/output ports, serial gluing
along matching ports, and parallel disjoint union.

## 1. Generic finite port event structure

A `PES E` carries:

- a finite event type `E`;
- a closed Boolean causal relation `beforeB`;
- input and output port labels;
- a certificate label on each event.

The constructors are generic over arbitrary finite event types.

Serial composition introduces cross-component causality only when a reachable
left output port matches a reachable right input port. The glued interface is
hidden.

Parallel composition namespaces the two port families and introduces no causal
relation between independent components.

## 2. Associativity up to explicit causal-structure isomorphism

The associativity fixture uses:

- a four-event diamond DAG;
- a three-event fork DAG;
- a second diamond DAG.

The two serial parenthesizations have different nested sum event types. An
explicit reassociator and inverse are supplied.

`serial_assoc_explicit_iso` exhaustively checks:

- round-trip bijection;
- certificate preservation;
- input-port preservation;
- output-port preservation;
- preservation of the full causal relation.

So associativity is tested at the causal-structure level, not by syntactic
equality of representations.

## 3. Serial/parallel interchange up to explicit isomorphism

The interchange fixture uses four nontrivial finite DAG components, including
diamonds, a fork, and a chain.

The theorem `serial_parallel_interchange_explicit_iso` exhaustively verifies
the standard interchange wiring permutation preserves certificates, exposed
ports, and every causal pair.

A separate falsifier verifies no spurious cross-channel dependencies are
created.

## 4. Proof relevance and revocation

Alternative two-event supports have the same causal shape but different first
certificates:

[
11\to22
qquad	ext{and}qquad
12\to22.
]

Revoking certificate 11 kills only the first. The second remains live.

Thus the event-structure representation preserves the alternative-support
semantics needed by Flash/RealityGraph.

## Result

A green branch supports the representation:

[
oxed{
	ext{typed ports}
+
	ext{finite proof-relevant causal event structure}
}
]

as a better native model of developmental history than serialized traces or
global causal layers.

For the tested finite DAGs, both associativity and monoidal interchange hold
**up to explicit causal-structure isomorphism**.

## Claim boundary

A green branch does **not** yet establish:

- a theorem for all possible `PES` values;
- generic preservation of acyclicity/transitivity by the constructors;
- port merging, fan-in/fan-out synchronization, or conflict;
- arbitrary hyperedges;
- quotienting event structures by isomorphism as a formal category;
- traced/feedback coherence for general port event structures;
- integration with full heterogeneous CLC transport certificates;
- empirical or ontological conclusions.
