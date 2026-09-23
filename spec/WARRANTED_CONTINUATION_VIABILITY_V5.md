# Warranted Continuation Viability V5

## Objective

Replace scalar repair depth with the smallest general finite repair-coverage
object and test the cut/cover hypothesis:

> protected-objective viability holds exactly when every admitted failure class
> has at least one live warranted repair hyperedge; a consequential cut is one
> that destroys that complete cover.

Parent:
- Warranted Continuation Viability V4
- exact head: 911e37b4de153fae7f41dee10d246ae1617e2ea1
- qualification run: 35927220742
- artifact: 10779961303
- digest:
  sha256:7f38d0147365dc8509245fab0e84ac4ea7bc2f35916e6a657f01a06e312bc0e5

V5 is stacked directly on that exact head.

## Repair hypergraph

A repair hyperedge contains:

- a failure class it repairs;
- a finite list of warrant/capability identifiers that must all remain live.

This allows both ordinary singleton repair and conjunctive support.

Definitions:

- edgeLive
- CoversFailure
- CompleteCover
- repairStep
- RepairCut

A repair path/hyperedge is live only when all of its required warrant tokens are
live. Therefore one failure class may have several alternative repair paths,
and one path may require several capabilities jointly.

## Generic cut/cover theorem

Lean proves:

- complete_cover_implies_postfixed
- postfixed_implies_complete_cover
- complete_cover_iff_postfixed
- cut_breaks_viability_iff

For the declared one-step repair semantics:

    CompleteCover(live, edges, admitted)
      iff
    the singleton live state is post-fixed under every admitted failure.

Therefore a cut destroys viability exactly when it destroys complete live
repair coverage.

This is a theorem about the declared finite repair semantics. It is not yet a
theorem about arbitrary developmental systems.

## Redundant + conjunctive fixture

Capabilities:

    0,1,2,3

Admitted failure classes:

    0,1

Repair hyperedges:

    failure 0 <- {0}
    failure 0 <- {1}
    failure 1 <- {1,2}
    failure 1 <- {3}

This fixture includes:
- alternative redundancy for failure 0;
- conjunctive support for one failure-1 path;
- an independent alternate failure-1 path.

The full live set [0,1,2,3] is a complete cover.

Every singleton cut preserves complete cover.

The minimal cut census finds exactly three size-2 minimal cuts:

    {0,1}
    {1,3}
    {2,3}

Thus minimum cut size is 2 in this exact fixture.

Lean proves:
- fixture_complete_cover
- every_singleton_cut_preserves_cover
- three_pair_cuts_break_cover
- conjunctive_path_is_not_singleton_equivalent

## WarrantGraph cut

The authority fixture has four independent base warrants 0..3.

Appending revocations for 1 and 3 produces:

    warrantLive = [0,2]

Under that live view:
- failure 0 remains covered by repair {0};
- failure 1 is uncovered because {1,2} lost 1 and {3} was revoked.

Lean proves:
- coverage_base_live
- coverage_cut13_live
- cut13_preserves_failure0_but_breaks_failure1
- warrant_cut_breaks_complete_cover
- repair_cover_cut_characterization_fixture

So the consequential cut is not "depth loss." It is exactly loss of all live
repair alternatives for at least one admitted failure class.

## Relation to existing CausalRepairCover

CausalRepairCover already proves cover/sufficiency results for certified causal
repairs that separate residuals. V5 does not replace it.

V5 adds the missing authority-side object:
- which repair alternatives are still live under warrant/revocation;
- which admitted failure classes those live alternatives cover.

The two layers can later be composed: a repair must be both causally certified
and live-authorized.

## Programme interpretation

V4 showed scalar depth is not canonical because cross-layer repair can bypass a
missing intermediate layer.

V5 replaces depth with a coverage hypergraph.

The emerging viability invariant is:

    every admitted protected failure class has >= 1 live warranted repair path.

The corresponding failure boundary is a repair cut:

    some admitted failure class loses all live repair alternatives.

This is a stronger and more general object than scalar repair/disruption rate or
serial depth.

## Claim boundary

If qualification passes, V5 warrants only:

1. the generic complete-cover/post-fixed equivalence for the declared finite
   one-step repair semantics;
2. the cut/viability equivalence for that semantics;
3. the exact four-capability redundancy/conjunction fixture;
4. the exact WarrantGraph cut {1,3} and its resulting coverage loss.

It does not establish:
- arbitrary multi-step repair planning;
- causal ordering of repairs;
- stochastic/adversarial infinite-horizon viability;
- that cover cardinality alone determines robustness;
- a universal theorem for physical, biological, cognitive, consciousness or
  AHQ systems.

## Next residual

Compose authority coverage with certified causal repair paths from
CausalRepairCover. Then test whether viable coverage requires merely one live
repair hyperedge per failure class, or whether causal ordering / shared-resource
contention creates a higher-order obstruction.
