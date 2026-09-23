# Warranted Continuation Viability V6

## Objective

Compose V5's live-authority repair coverage with the existing certified causal
repair layer, then attack static per-failure cover with shared-resource
contention.

Parent:
- Warranted Continuation Viability V5
- exact head: 86ae67a0ffda901e78b4bd1f3050ba473129cb50
- qualification run: 35928378587
- artifact: 10779468575
- digest:
  sha256:5cb97d159886e6851c51745c75a641579d0c571adc2737ac98ca3b95fe6ff40a

V6 is stacked directly on that exact head.

## Part A — live authority + causal validity

A CausalRoute records:
- failure class;
- required live warrants;
- repair identifier.

An executable validity table determines whether that repair identifier is
causally valid for the failure class.

The one-step semantics requires both:
1. authority: every required warrant is live;
2. causal validity: the repair is valid for that failure.

Lean proves:
- complete_live_causal_cover_implies_postfixed
- postfixed_implies_complete_live_causal_cover
- complete_live_causal_cover_iff_postfixed

Thus, for this static one-step semantics:

    complete live-authorized causal cover
      iff
    singleton post-fixed viability.

## Exact CausalRepairCover oracle fixture

Route 0 corresponds to existing CausalRepairCover.abRepair.
Route 1 corresponds to existing CausalRepairCover.baRepair.

Existing Metatron theorems already prove:
- abRepair separates the protected residual pair x/y;
- baRepair does not.

V6 binds its executable validity table to those facts:
- oracleValidB 0 0 = true and abRepair is actually causal-valid;
- oracleValidB 1 0 = false and baRepair is actually rejected.

Authority fixture:
- base warrants [0,1];
- revoke warrant 0;
- warrantLive becomes [1].

After that cut, an authority-only route still exists through route 1, but the
remaining route is the causally wrong BA ordering. Therefore:
- authority-only cover = true;
- live causal cover = false.

Lean proves authority_alone_is_not_causal_cover.

This is the exact composition boundary between WarrantGraph authority and
CausalRepairCover semantics.

## Part B — shared-resource contention falsifier

The next attack asks whether complete static live causal cover is enough for
multi-step viability.

Failures 0 and 1 are two admitted occurrences of the same protected residual
class. Both are statically covered by the same existing certified causal
AB repair route.

A ResourceState carries:
- live warrants;
- one Boolean fuel token.

Executing either repair consumes the fuel token.

At the initial state:
- failure 0 is individually repairable;
- failure 1 is individually repairable;
- static complete live causal cover holds for both.

But:
- sequence [0,1] fails;
- sequence [1,0] fails.

Lean proves:
- repeated_static_complete_cover
- each_failure_individually_repairable
- shared_resource_breaks_sequence_01
- shared_resource_breaks_sequence_10
- static_live_causal_cover_not_sequentially_sufficient

Therefore:

> static per-failure live-authorized causal cover is not sufficient for
> multi-step viability when repair execution mutates shared resource state.

## Programme interpretation

V5 established the repair-cover/cut theorem for a static one-step authority
hypergraph.

V6 sharpens the object twice:

1. authority alone is insufficient: repair paths must also be causally valid;
2. even live + causally valid static cover is insufficient for sequential
   viability when repairs interfere through shared state.

The next canonical object is therefore not merely a coverage hypergraph. It is
a stateful repair transition system whose nodes include:
- current live warrants;
- resource/interference state;
- protected objective state;

and whose edges are live-authorized, causally certified repairs.

The viability question returns to a greatest fixed point over that full state.

## Claim boundary

If qualification passes, V6 warrants only:
1. the one-step live-authority + causal-validity cover equivalence;
2. the exact AB-vs-BA authority/cause fixture;
3. the exact one-shot shared-resource contention counterexample.

It does not establish:
- a general resource logic;
- optimal scheduling;
- fairness or replenishment;
- stochastic/adversarial infinite-horizon viability;
- arbitrary concurrency semantics;
- physical, biological, cognitive, consciousness or AHQ claims.

## Next residual

Build the smallest stateful repair-transition kernel:
- live warrant set;
- finite resource state;
- certified causal repair edges;
- admitted failures.

Then compute the greatest protected-objective viable set directly. Test whether
resource replenishment or scheduling can restore viability in the contention
fixture.
