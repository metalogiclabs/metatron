# Temporal Timescale V1

## Objective

Close the remaining residual from Temporal Concentration V0:

> under an explicit operational definition of timescale, does causal concentration imply a slower-or-equal macroscopic timescale?

V1 defines the event-rate numerator on a fixed time grid as the number of observed state transitions across the same list of sampling intervals.

For a micro observation f : A -> B and deterministic macro readout g : B -> C, V1 asks whether

    transitions(g ∘ f) <= transitions(f)

on every fixed interval list.

## Generic theorem

formal/Metatron/TemporalTimescale.lean proves:

- downstream_change_requires_upstream_change
- transitionCount_postcompose_le
- deterministic_readout_slower_or_equal

A downstream transition can occur only on an interval where the upstream state already changed. Therefore deterministic postcomposition cannot increase the transition-event count on the same sampling grid.

This is the exact scoped sense in which the macro observation is "slower or equal" in V1.

## Strict finite descendant of V0

V1 reuses the exact qualified V0 traffic-style fixture and fixes the sampling intervals to

    t0->t1, t1->t2, t2->t3.

The counts are:

    raw departure identity: 3 transitions
    after gate1:           2 transitions
    after gate2∘gate1:     1 transition

The same fixture has the V0 kernel-pair counts:

    4 -> 6 -> 8

So on this exact finite boundary, history concentration and event-rate slowing occur together:

    more history identifications
    fewer same-horizon observable transition events.

Lean also proves concentration_with_strict_slowing for this fixture.

## Relation to V0

Source authority:
- Temporal Concentration V0 exact head:
  5ffad1c87769881b50e48b7865c75e47b6af414f
- V0 qualification run:
  35912669250
- V0 artifact:
  10773039201
- V0 digest:
  sha256:e953dab221184c30f799e32a49fe594e99129de64a93cb75086424cf4201ce83

V1 is a strict descendant. It does not redefine V0.

## Verification boundary

If qualification passes, the warranted statement is:

> On a common finite sampling grid, deterministic postcomposition cannot increase the number of observed state-transition events. The declared V0 traffic-style fixture exhibits strict transition-count reduction 3->2->1 alongside kernel growth 4->6->8.

This does not establish:

- slower wall-clock physical dynamics;
- a change in continuous-time frequency without a declared sampling/metric model;
- slower subjective time;
- that every strict kernel enlargement must reduce transition count on every possible trace;
- consciousness, autobiographical memory, life-review, biological development, or phenomenology.

Strict slowing is demonstrated on the declared fixture. The generic theorem guarantees only nonincrease.

## Programme relation

V0: deterministic causal maps can only coarsen history identity.

V1: deterministic readout can only remove, never invent, transition events on the same sampling grid.

Together:

    causal concentration
      -> fewer consequential distinctions
      -> no increase in observable event rate

within the declared deterministic, same-horizon boundary.

This is a reusable mathematical bridge to Deep Present, not a theory of subjective time.
