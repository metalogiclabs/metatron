# Warranted Continuation Viability V0

## Objective

Test the missing local-to-global bridge in the current programme:

> when does local verifier-backed viable continuation compose through retention
> and reclosure into a globally viable finite developmental trajectory?

V0 also supplies the decisive bounded falsifier for a scalar restoration/disruption
summary: two systems may have the same aggregate repair capacity and face the
same encounter stream while differing in typed residual coverage and therefore
differing in protected-objective viability.

## Canonical lineage

This experiment is anchored to the user-supplied Certified Lineage Calculus V1
specification:

- source file: Certified_Lineage_Calculus_V1(5).docx
- SHA-256:
  161c6c41812124b4a114defe243c92fac03261d3921daddcf310dd0ca3769a88
- document date: 20 September 2026

CLC V1 states that continuity is certified transport of protected consequence
through changing forms, keeps UNKNOWN as a first-class verdict, separates
historical evidence from current acceptance, and places Flash reclosure above
recorded lineage. The source explicitly labels its Lean package as theorem
obligations rather than claiming the whole specification is already mechanized.

V0 does not claim to mechanize all of CLC. It instantiates only the smallest
finite continuation/UNKNOWN/reclosure boundary needed for this experiment.

## Generic formal law

formal/Metatron/WarrantedContinuationViability.lean defines:

- runViable: deterministic finite continuation with none as fail-closed UNKNOWN;
- StepPreserves: a successful local continuation preserves a declared protected invariant;
- runViable_preserves: local protected preservation composes across every successful finite stream;
- runViable_append: viable execution composes across concatenated encounter streams.

The generic theorem is intentionally finite and deterministic.

## Finite typed developmental fixture

Residual types:

    alpha
    beta

The developmental state records:

- typed acquisition budget for alpha and beta;
- compiled repair lineage for each type;
- the reclosed live repair view;
- a protected-consequence bit.

A successful first acquisition compiles the typed repair. Minimal reclosure then
makes compiled repairs live so later encounters of the same type are REUSED at
zero additional acquisition cost.

If no live repair exists and no typed acquisition budget exists, the total
authority runner records UNKNOWN and leaves the state unchanged. It does not
fabricate authority.

Encounter stream:

    alpha, beta, alpha, beta

Two initial systems:

Balanced:
    alpha budget = 1
    beta budget  = 1

Skewed:
    alpha budget = 2
    beta budget  = 0

Both have the same aggregate initial repair capacity: 2 units.
Both face the same four encounters.

Thus their bounded-horizon scalar summaries are identical:

    (aggregate repair units, disturbance count) = (2, 4)

but the typed geometry differs.

Expected exact traces:

Balanced:
    acquired, acquired, reused, reused
    objective viable = true

Skewed:
    acquired, unknown, reused, unknown
    objective viable = false

Both remain authority-safe and preserve the protected bit. The skewed system
never fabricates beta authority.

## Exact falsifier

The theorem same_scalar_different_typed_viability proves on the declared fixture:

    scalarSummary(balanced) = scalarSummary(skewed)

while

    objectiveViable(balanced) = true
    objectiveViable(skewed)   = false.

Therefore any viability law depending only on this aggregate scalar summary is
insufficient for the typed continuation problem.

This does not refute every possible scalar model. It refutes this class of
aggregate summaries on this exact finite boundary and establishes that residual
type can be consequential.

## Programme interpretation

V0 connects existing pieces without replacing them:

- Viability Geometry supplies constrained continuation and typed obstruction.
- Developmental Intelligence supplies local residual-relative viability fibres.
- CLC supplies protected transport, recorded lineage, authority snapshots and
  fail-closed UNKNOWN.
- Flash supplies reclosure after admitted change.
- Open Development supplies the rule that verified repairs are compiled for future use.

The new content is the finite composition/falsification boundary:

    local typed viability
      -> verified acquisition or reuse
      -> compiled lineage
      -> reclosed active repair
      -> next encounter

with a proof that aggregate capacity alone does not determine success.

## Claim boundary

If qualification passes, V0 warrants only:

1. the generic finite deterministic composition theorems stated above;
2. the exact balanced/skewed fixture;
3. the insufficiency of the declared aggregate scalar summary for that fixture;
4. fail-closed preservation of the protected boundary in the fixture.

It does not establish:

- a universal queueing or continuous-time threshold;
- a universal lambda_self/lambda_env law;
- stochastic or adversarial infinite-horizon viability;
- fairness or productivity for unbounded runs;
- the whole CLC V1 theorem package;
- physical, biological, cognitive, consciousness or AHQ claims.

## Next residual if V0 qualifies

The next strengthening is a finite greatest-fixed-point viability kernel over a
declared encounter alphabet and a nontrivial reclosure relation, followed by
revocation. The decisive question is whether the locally viable state set is
closed under every admitted encounter after proof-carrying reclosure.
