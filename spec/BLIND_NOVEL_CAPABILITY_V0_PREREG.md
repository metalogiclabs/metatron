# Blind Novel Capability Genesis V0 — Pre-Registration

**Frozen before the hidden V0 challenge is generated.**

## Objective

Test whether Metatron can identify the minimum genuinely novel observer-interface
extension required to refine the current observer-relative reality to a frozen
target quotient.

The current observer has only an old protected observation language. Candidate
capabilities are new anonymous tests not reachable in the old interface.

## Public interface

The predictor receives only:

1. anonymous finite world-state IDs;
2. the current protected-observation outcomes;
3. the target behavioral class ID of each world state;
4. anonymous candidate test outcome vectors;
5. a SHA-256 commitment to the hidden semantic interpretation.

The predictor does not receive candidate semantic names or the planted minimum
basis.

## Novelty

A candidate test is genuinely novel iff it is not constant on every class of
the current observer quotient. Equivalently, it can distinguish at least one
pair that the old interface identifies.

Only genuinely novel candidates may count toward the acquisition basis.

## Frozen search rule

For every subset B of novel candidate tests, form the refined observational
signature

    (old_protected_outcome, outcomes of every test in B).

B is target-sufficient iff equality of this signature implies equality of the
target class.

The predictor must compute:

1. the exact current observer quotient;
2. which candidate tests are genuinely novel;
3. the exact minimum cardinality of a target-sufficient novel capability family;
4. the full family of exact minimum bases;
5. a canonical minimum basis only for serialization;
6. the residual-pair coverage of each candidate and basis.

## Hidden generator contract

The hidden world is an anonymous relabeling of three Boolean coordinates:

    (hidden, visible, noise).

The old observer sees only visible.

The target quotient is equality of (visible, hidden).

The candidate language contains anonymous relabelings of:

- noise;
- hidden XOR noise;
- visible;
- visible XOR noise;
- constant false.

No single novel candidate is target-sufficient.

The pair {noise, hidden XOR noise} is target-sufficient because together they
determine hidden.

The generator must reject/resample if any singleton candidate is sufficient.

## Reveal gates

N1. Hidden artifact matches the public commitment.
N2. Prediction is bound to the exact public artifact.
N3. Predicted current quotient equals the old protected-observation quotient.
N4. Predicted novel candidate set equals the hidden novel set.
N5. No singleton novel capability is target-sufficient.
N6. Predicted minimum acquisition cardinality equals the true minimum and is 2.
N7. The hidden planted basis belongs to the predicted exact minimum family.
N8. Every predicted minimum basis is target-sufficient.
N9. Removing any member from the canonical basis destroys target sufficiency.
N10. State relabeling preserves current quotient block sizes, novel candidate
     count, minimum acquisition cardinality, and exact minimum-basis count.

## Verdict

- BLIND_NOVEL_CAPABILITY_PASS: N1-N10 all pass.
- BLIND_NOVEL_CAPABILITY_FAIL: otherwise.

## Claim boundary

A pass establishes exact finite minimum interface-extension discovery inside a
declared anonymous candidate test language. It does not establish unrestricted
invention of tests outside that language, semantic naming of the new capability,
or symbolic synthesis on infinite worlds.
