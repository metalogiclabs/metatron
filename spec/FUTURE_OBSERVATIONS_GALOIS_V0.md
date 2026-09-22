# Future Observations / Behavioral Quotient V0

**Status:** theorem experiment  
**Branch:** `future-observations-galois-v0`

This branch tests four claims that connect Metatron/CLC continuation-safe identity
to observation/equivalence duality and residual-driven refinement.

## 1. Observation/equivalence Galois law

For a family of observations (S), define

[
\alpha(S)(x,y) \iff \forall o\in S,\; o(x)=o(y).
]

For a relation (R), define the observations that respect it by

[
\gamma(R)=\{o\mid xRy \Rightarrow o(x)=o(y)\}.
]

The Lean theorem `futureObservations_galois` proves the elementary adjoint law:
a relation is contained in the indistinguishability kernel of (S) iff every
observation in (S) respects that relation.

## 2. Continuation-safe equivalence as greatest admissible relation

Given:

- lawful one-step continuations `act : Step -> State -> State`;
- protected tests `test : Test -> State -> Val`;
- a predicate selecting protected tests;

define `FutureEq x y` by quantifying over every finite continuation path and
every protected test.

A relation is admissible when:

1. it agrees on all immediately protected tests; and
2. it is closed under every lawful one-step continuation.

The theorem `continuationSafe_eq_gfp` proves that `FutureEq` is the greatest
admissible relation.

This is the finite-path theorem underlying the CLC statement that continuation-
safe equivalence is the largest protected agreement stable under lawful future
transport.

## 3. Behavioral quotient state-map reflection

`FutureEq` is proved reflexive, symmetric, and transitive, so it induces a
Lean `Quotient`.

The theorem `behavioralQuotient_reflection` proves:

[
\forall f:X\to Y,
\quad
(x\sim y \Rightarrow f(x)=f(y))
\Rightarrow
\exists!\bar f:X/{\sim}\to Y
\text{ with }\bar f\circ q=f.
]

This is deliberately a **state-map universal property only**.

It does **not** yet prove that the full CLC transport object reflects through the
quotient. The next question is whether backward test transformers, protected-test
lifts, and certificate-carrying transport also factor uniquely.

## 4. Residual-driven strict refinement

Let (P_{old}\subseteq P_{new}) be protected-test languages. Because
`FutureEq` quantifies over protected tests, enlarging the language can only
refine the continuation-safe relation.

The theorem `residualAdjoin_strictLyapunov` proves the stronger strict case:
if a newly protected test separates a pair that was continuation-safe equivalent
before, then

[
\operatorname{FutureEq}_{new}
\subsetneq
\operatorname{FutureEq}_{old}.
]

This is a genuine Lyapunov descent when the Lyapunov value is taken in the
poset of continuation-safe relations ordered by refinement.

It is **not yet** the stronger scalar theorem that a chosen natural-number
defect measure strictly decreases for every admissible residual repair. In finite
models such a scalar can be obtained from a strictly monotone rank, e.g. pair
count or partition defect, but that corollary remains a separate theorem.

## Finite differential fixture

CI independently computes, for the three-state Nucleus Genesis world:

1. the relation induced by all protected observations after all continuation
   closure; and
2. the greatest relation obtained by repeated immediate-agreement plus
   transition-stability refinement.

The two partitions must agree:

- with only `IS_ZERO`: `((0,), (1,2))`;
- after protecting `IS_ONE`: `((0,), (1,), (2,))`.

The second case is also the concrete strict-refinement witness.

## Claim boundary

This branch does not claim:

- a full heterogeneous CLC adjunction;
- categorical reflection of certificate-bearing transports;
- a universal theorem for arbitrary evolving test languages;
- a general scalar natural-number Lyapunov theorem for arbitrary repairs;
- empirical or ontological conclusions.

The proved core is the observation/equivalence law, greatest continuation-safe
relation theorem, ordinary quotient universal property, and strict
residual-driven refinement in the relation order.
