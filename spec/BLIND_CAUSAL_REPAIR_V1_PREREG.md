# Blind Causal Repair V1 — Pre-Registration

**Frozen before the V1 hidden challenge is generated.**

## Objective

Test whether Metatron can recover a minimum **causal repair** rather than merely
a minimum set of singleton generators.

The challenge must contain a fresh hidden finite world in which:

- no one-event repair is target-sufficient;
- one ordered two-event repair is target-sufficient;
- reversing those same two reusable generators is not sufficient.

The predictor must commit before the hidden latent interpretation and planted
causal repair are revealed.

## Public interface

The prediction job may receive only:

1. anonymous state IDs;
2. the current protected observation of each state;
3. the frozen target future-class ID of each state;
4. anonymous action transition tables;
5. the declared candidate repair language:
   - every one-event repair;
   - every ordered two-event chain;
6. a SHA-256 commitment to the hidden artifact.

It may not receive latent state coordinates, semantic action names, the planted
ordered repair, or the hidden random seed.

## Consequential residual

For public states x,y:

    U = {{x,y}: protected(x)=protected(y)
                 and target_class(x) != target_class(y)}.

For a candidate causal repair C, execute its ordered event schedule and observe
the protected output after execution. Its residual edge is

    E_C = {{x,y} in U : obs(C(x)) != obs(C(y))}.

## Frozen prediction rule

1. evaluate every declared repair from public transition tables only;
2. compute exact residual coverage;
3. choose the minimum event-count repair that covers U completely;
4. preserve the full minimum causal capability class when several repairs tie;
5. choose a canonical representative lexicographically only for serialization;
6. bind the prediction cryptographically to the public challenge digest.

The predictor must report singleton coverage independently, so the reveal can
verify that no arity-one repair is sufficient.

## Hidden generator contract

The hidden world uses an anonymous relabeling of a Boolean carrier containing
at least:

- a source distinction;
- an intermediate hidden wire;
- a protected observed bit.

Two hidden reusable actions A and B obey:

    A: source -> hidden
    B: hidden -> observed

and therefore:

    A alone: insufficient
    B alone: insufficient
    A -> B: sufficient
    B -> A: insufficient.

Additional anonymous decoy actions are included. The generator must reject and
resample any challenge in which a one-event repair becomes sufficient or a
two-event repair outside the intended minimum causal capability class becomes
target-sufficient.

## Reveal gates

C1. Hidden artifact matches the public SHA-256 commitment.

C2. Prediction is bound to the exact public artifact.

C3. No one-event repair covers the complete consequential residual.

C4. The true minimum causal repair event count is exactly 2.

C5. The predictor's minimum event count equals the true minimum.

C6. The predicted minimum causal capability class contains the planted ordered
repair.

C7. The planted reverse-order repair is not in the minimum sufficient class.

C8. The canonical predicted repair closes every residual pair.

C9. Relabeling anonymous states preserves the minimum event count and minimum
repair-class cardinality.

## Verdict

- BLIND_CAUSAL_REPAIR_PASS: C1-C9 all pass.
- BLIND_CAUSAL_REPAIR_FAIL: any gate fails.

## Claim boundary

A pass establishes blind recovery of a minimum ordered causal repair inside a
declared finite repair language. It does not establish unrestricted causal
program synthesis, arbitrary DAG discovery, or tractable search over large
event-structure languages.
