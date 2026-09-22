# CLC Fixed-Point / Reflection V0

**Status:** theorem experiment  
**Branch:** `clc-fixedpoint-reflection-v0`

This branch tests two questions left open by Future Observations Galois V0.

## A. Literal conjugate fixed-point theorem

Define a future observation as a finite lawful continuation path followed by a
test. Let `LOp` add either a protected base test or one lawful step in front of
an already available observation. `MuObs` is the inductively generated least
family.

Define `BOp` on state relations by requiring:

1. immediate protected agreement; and
2. preservation by every lawful one-step continuation.

`NuB` is the union of all post-fixed relations.

The target theorem is:

[
\alpha(\mu L)=\nu B.
]

In Lean this is named `alpha_mu_eq_nu_b`.

The branch also proves that `MuObs` is a fixed point and least pre-fixed
family, and that `NuB` is a fixed point of `BOp`.

## B. Does the full original CLC form reflect through the quotient?

CLC V1 continuation-safe equivalence protects only declared protected tests.
Therefore an unprotected test may still distinguish two states that the
behavioral quotient lawfully identifies.

The branch contains a two-state negative fixture. The only protected test is
constant, so `false` and `true` are continuation-safe equivalent. A second,
unprotected test distinguishes them.

The target theorem `fullEvaluatorDescent_impossible` proves that no evaluator
on the quotient can preserve **every original test** in this fixture.

Therefore the full original state-test form does not reflect through the
behavioral quotient in general.

## C. Repaired quotient interface

The compatible test language is

[
\{q\mid x\equiv^\infty y \Rightarrow Q(x,q)=Q(y,q)\}.
]

`CompatibleTest` and `compatibleQuotientEval` construct this quotient
interface, and every protected test embeds into it.

This identifies the correct next categorical target: reflection is expected not
in the category of arbitrary original forms, but in a behaviorally saturated /
Galois-closed interface whose tests are exactly those compatible with the
continuation-safe boundary.

## D. Strict transports do descend after saturation

For an exact transport with:

- a state map preserving continuation-safe equivalence;
- a contravariant test pullback;
- exact evaluation preservation;

the theorem `strictTransport_saturatedQuotient_naturality` proves that the
state map descends covariantly to behavioral quotients, compatible tests pull
back contravariantly, and quotient evaluation commutes with transport.

If the transport also carries a protected-test lift satisfying the CLC split
law, `saturatedProtected_split` proves that the split survives in the
compatible-test interface.

So the obstruction is now precise: arbitrary original test languages do not
reflect, but the behaviorally saturated interface supports the strict CLC
transport structure.

## Claim boundary

A green branch establishes:

- the literal deterministic same-form theorem
  `alpha(mu L) = nu B`;
- failure of evaluator descent for arbitrary unprotected tests;
- well-defined evaluator descent after restricting to compatible tests;
- descent/naturality of exact strict transports through the saturated quotient;
- preservation of the protected split law after saturation.

The branch also contains `laxRefinement_compatiblePullback_fails`: a concrete
information-gaining refinement satisfying a one-way information law whose
target-compatible test pulls back to a source test that is **not** compatible
with the source behavioral quotient. Thus ordinary saturated reflection does
not extend to lax developmental refinement merely by weakening equality to
information refinement.

It does **not** yet establish:

- the correct enriched/lax universal property for developmental refinements;
- certificate-object uniqueness/factorization;
- a reflection theorem for evolving authority snapshots;
- empirical or ontological conclusions.
