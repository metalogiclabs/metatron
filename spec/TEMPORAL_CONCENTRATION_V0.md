# Temporal Concentration V0

## Objective

Formalize the smallest exact law extracted from the supplied traffic-light / present-time prose:

> successive deterministic gates can identify previously distinct histories, but once two histories have been mapped to the same intermediate event, no deterministic downstream continuation can separate them again.

This is a theorem about kernels of functions under postcomposition. It is not a theorem about consciousness, memory, subjective time, biological organization, or physical traffic networks in general.

## Generic law

For f : A -> B and g : B -> C, define the history kernel

    x ~_f y  iff  f(x) = f(y).

Then

    ker(f) ⊆ ker(g ∘ f).

Equivalently, deterministic postcomposition is monotone toward coarser history identity.

A strict temporal concentration witness is a pair x,y such that

    f(x) != f(y)
    g(f(x)) = g(f(y)).

Such a witness proves that the downstream kernel contains a new identification not present upstream.

## Finite traffic-style witness

scripts/temporal_concentration_v0.py uses four departure states.

Stage 0:
    0,1,2,3

Gate 1:
    0,0,1,2

Gate 2 after Gate 1:
    0,0,1,1

Exact finite result:
    image sizes: 4 -> 3 -> 2
    kernel-pair counts: 4 -> 6 -> 8

Thus each gate strictly concentrates the declared finite timing history.

## Lean theorems

formal/Metatron/TemporalConcentration.lean proves:

- kernel_postcompose_mono
- strict_witness_adds_identification
- first_gate_strictly_concentrates
- second_gate_strictly_concentrates
- first_merge_survives_second_gate
- second_gate_adds_new_merge
- no_reseparation_after_merge

## Programme relation

This is a temporal specialization of the same quotient logic used by MSI and Metatron:

- earlier histories are identified relative to their current protected consequence;
- deterministic causal postcomposition can erase distinctions;
- erased distinctions cannot be recovered from the downstream state alone.

This complements MonoidalDeepPresent's compatible-cone result by supplying an explicit history-to-present coarsening mechanism.

## Verification boundary

If qualification passes, the warranted claim is only:

> For deterministic maps, kernel inclusion is monotone under postcomposition; and the declared four-departure/two-gate fixture exhibits strict stepwise concentration.

This does not establish:

- that real traffic lights always produce strict concentration;
- that departure time alone is a sufficient traffic state when queues exist;
- that fewer distinguishable downstream events imply a slower physical or subjective timescale;
- that the present literally contains the whole past;
- autobiographical-memory, life-review, classical-work, biological-development, or phenomenological claims.

A stronger "concentration implies slower timescale" theorem requires an explicit metric or event-rate assumption and remains outside V0.
