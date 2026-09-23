# Blind Behavioral Commutation V1 — Pre-Registration

**Frozen before the hidden V1 challenge is generated.**

## Objective

Test whether Metatron can discover a strictly larger safe-swap relation by
quotienting action commutation through a continuation-safe behavioral relation,
rather than requiring exact raw-state commutation.

The challenge must contain:

- a fresh anonymous finite state carrier;
- four anonymous transition actions;
- a public continuation-safe behavioral class for each state;
- at least one action pair that fails exact state commutation but commutes
  modulo the behavioral classes;
- at least one action pair that fails behavioral commutation.

## Public predictor

The predictor sees only:

1. anonymous state IDs;
2. anonymous action transition tables;
3. public behavioral class IDs;
4. a SHA-256 commitment to the hidden semantic interpretation.

For each unordered action pair {g,h}, compute:

- exact commutation:
    h(g(s)) = g(h(s)) for all states s;
- behavioral commutation:
    class(h(g(s))) = class(g(h(s))) for all states s.

The predictor must also verify the published class relation is step-closed under
every public action.

Then:

1. enumerate all 4! action schedules;
2. connect schedules by adjacent swaps of behaviorally commuting pairs;
3. compute connected components;
4. independently compute each schedule's behavioral execution vector across
   all states;
5. verify safe-swap components exactly equal behavioral execution classes;
6. find the minimum subset of behavioral pair certificates that preserves that
   partition.

## Hidden generator contract

The hidden carrier is a randomized relabeling of the 2-bit state

    (hidden, observed).

The hidden actions are a randomized relabeling of:

- H0: set hidden := false;
- HT: toggle hidden;
- O0: set observed := false;
- OT: toggle observed.

The protected behavioral quotient is equality of the observed bit.

All four actions preserve that quotient.

The pair {H0,HT} must:

- fail exact raw-state commutation;
- pass behavioral commutation.

The pair {O0,OT} must fail behavioral commutation.

## Reveal gates

B1. Hidden artifact matches public commitment.

B2. Prediction is bound to exact public artifact.

B3. Public behavioral classes are step-closed under every action.

B4. Predicted exact-commutation relation equals hidden exact relation.

B5. Predicted behavioral-commutation relation equals hidden behavioral relation.

B6. Behavioral relation strictly contains exact relation.

B7. Every behaviorally rejected pair has a public quotient counterexample.

B8. Behavioral safe-swap components equal exact behavioral execution classes.

B9. Minimum behavioral certificate basis cardinality is exact and irredundant.

B10. State relabeling preserves exact relation, behavioral relation, class
     partition, and minimum basis cardinality.

## Verdict

- BLIND_BEHAVIORAL_COMMUTATION_PASS: B1-B10 all pass.
- BLIND_BEHAVIORAL_COMMUTATION_FAIL: otherwise.

## Claim boundary

A pass establishes exact finite discovery of quotient-relative pairwise
commutation for a declared continuation-safe finite behavioral quotient. It
does not establish automatic discovery of the quotient itself, higher-order
independence, or symbolic proof synthesis on infinite carriers.
