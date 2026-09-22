# CLC Proof-Relevant Oplax V0

**Status:** theorem experiment  
**Branch:** `clc-proof-relevant-oplax-v0`

This branch tests whether the developmental quotient semantics can be upgraded
from bare relations to a proof-relevant oplax architecture.

## A. Certified raw maps form an ordinary category

A `CertifiedMap A B` carries:

- a state map (A\to B);
- an ordered certificate trace.

Identity has the empty trace. Composition composes state maps and concatenates
traces. Lean proves left identity, right identity, and associativity.

Two arrows with the same state map but different certificate traces remain
distinct. This is the first proof-relevance gate.

## B. Quotient relations admit an evidence lift

`QEvidence` is a Type-valued witness for the Prop-level
`QuotientRelation`. It retains:

- the concrete source representative;
- equality to the source quotient class;
- equality of its image to the target quotient class;
- the certificate trace supporting the event.

The theorem `qEvidence_nonempty_iff_relation` proves that forgetting evidence
recovers exactly the previously qualified relation semantics.

A direct composite witness embeds into a two-step evidence witness, and the
ordered certificate trace is preserved.

## C. Causal re-entry is strict and proof-relevant

The fixture uses three views of Bool:

- (A): all tests protected, so false/true are distinct;
- (B): only the constant protected test, so false/true collapse;
- (C): all tests protected again.

Both raw maps are identity maps.

At quotient level, relational composition can:

1. enter the single (B)-class using false;
2. leave the same (B)-class using true;
3. reach the true class of (C).

Lean proves that this composed developmental path exists while the direct
composite relation does not.

The evidence-level path carries trace `[101, 202]`, and Lean proves no direct
evidence witness exists for the same endpoints.

This is a precise finite witness of **causal re-entry**: an intermediate
boundary can hide a distinction which a later boundary reactivates.

## D. Flash-style proof-lifted closure

The causal-re-entry fixture is also lifted directly into the closure layer:
the two certified quotient edges form a `ProofClosure` path from source to
target with exact trace `[101,202]`. Thus the extra path exposed by oplax
composition is consumable by the same proof-lifted reclosure mechanism rather
than existing only as a bare relational artifact.

`ProofClosure` is an inductive Type-valued transitive closure of certified
edges. Its Prop support is proved to be the least transitive relation containing
the base edges.

Because derivations live in `Type`, alternative proofs with identical
endpoints remain distinct. A fixture contains two alternative first supports
followed by one shared second support:

- trace `[11,22]`;
- trace `[12,22]`.

Revoking certificate 11 invalidates the first derivation while the second
remains live.

This reproduces, at the minimal theorem level, the key Flash/RealityGraph rule:
alternative support must not be collapsed merely because the concluded fact is
the same.

## Interpretation

The tested structure is now:

[
	ext{certified raw maps}
\longrightarrow
	ext{proof-relevant quotient relations}
\longrightarrow
	ext{proof-lifted reclosure}.
]

The semantic support projection is oplax at quotient level, while certificate
traces preserve distinct developmental histories.

This is evidence for a proof-relevant oplax developmental architecture, but not
yet a bundled bicategory or complete CLC theorem.

## Claim boundary

A green branch establishes:

- categorical laws for raw certified maps;
- exact support/evidence correspondence;
- direct-to-composed evidence inclusion with trace preservation;
- a strict causal-re-entry counterexample to reverse inclusion;
- direct causal-re-entry integration into proof-lifted reclosure;
- least proof-lifted transitive closure;
- retention of alternative supports under selective revocation.

It does **not** yet establish:

- a fully bundled bicategory / profunctor category;
- general horizontal/vertical 2-cell coherence;
- certificate cryptography or authority semantics;
- Flash incremental-vs-batch exactness for arbitrary updates;
- heterogeneous CLC port-signature semantics;
- empirical or ontological conclusions.
