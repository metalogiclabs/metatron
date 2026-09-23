# Blind Earned Commutation V1 — Pre-Registration

**Frozen before the hidden V1 challenge is generated.**

## Objective

Test whether Metatron can discover the exact warranted commutation/independence
relation from anonymous finite transition consequences, rather than receiving
commutation certificates as input.

The challenge must contain:

- a finite anonymous state carrier;
- four anonymous reusable actions;
- a causal presentation with all four events incomparable;
- a hidden semantic interpretation of those actions;
- a nontrivial mixture of commuting and noncommuting action pairs.

The public predictor sees only the anonymous transition tables and carrier.

## Public prediction rule

For every unordered action pair {g,h}, predict it as warranted iff

    h(g(s)) = g(h(s))

for every public state s.

Using only those earned pair certificates:

1. enumerate all 4! legal schedules;
2. connect schedules by adjacent swaps whose action pair is predicted warranted;
3. compute the connected components;
4. independently compute the exact execution-semantics vector of each schedule
   on all public states;
5. compare safe-trace components with exact semantic equivalence classes;
6. search every subset of the predicted warranted pair relation and find the
   minimum subset that preserves the exact semantic schedule partition.

The prediction is committed before the hidden action interpretation is revealed.

## Hidden generator contract

The hidden semantic action family is an anonymous relabeling of:

- X: toggle source;
- Y: toggle observed;
- A: copy source -> hidden;
- B: copy hidden -> observed.

On the 3-bit carrier these have exactly three commuting unordered pairs:

- {X,Y};
- {X,B};
- {Y,A}.

The remaining three pairs do not commute.

The generator randomly relabels both states and action IDs before publishing
transition tables.

## Frozen gates

E1. Hidden artifact matches the public commitment.

E2. Prediction is cryptographically bound to the exact public challenge.

E3. Predicted warranted pair relation equals the hidden semantic commutation
    relation exactly.

E4. Every predicted warranted pair really commutes on every public state.

E5. Every rejected pair has an explicit public counterexample state.

E6. Safe-swap connected components equal exact execution-semantic classes of
    schedules.

E7. The minimum pair-certificate basis preserving the semantic partition has
    the predicted cardinality.

E8. On this fixture the minimum basis is irredundant: removing any basis pair
    splits at least one formerly unified semantic class.

E9. State relabeling preserves the warranted relation, semantic partition,
    and minimum basis cardinality.

## Verdict

- BLIND_EARNED_COMMUTATION_PASS: E1-E9 all pass.
- BLIND_EARNED_COMMUTATION_FAIL: any gate fails.

## Claim boundary

A pass establishes exact finite discovery of pairwise semantic commutation and
the minimum pair-certificate basis needed to recover the schedule semantics of
this declared finite action family. It does not establish automatic discovery
of higher-order independence, observational-only commutation, or scalable
search over arbitrary action languages.
