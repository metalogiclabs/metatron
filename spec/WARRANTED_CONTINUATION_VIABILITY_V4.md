# Warranted Continuation Viability V4

## Objective

Generalize the hand-built V2/V3 recursive-repair pattern to a finite depth-n
strict repair tower, then actively attack the tower as a universal model using a
cross-layer WarrantGraph repair.

Parent:
- Warranted Continuation Viability V3
- exact head: 61a8388caecce031123307cf8debade9dfeda79c
- qualification run: 35925633029
- artifact: 10778389564
- digest:
  sha256:ad5ecbc4adae1e8daf3d6683da0035a54d89afb5d558daea4e5c7368cf638bbe

V4 is stacked directly on that exact head.

## Part A — Generic strict depth law

The generic tower state is a natural number:

    0 = failed
    1 = base support only
    2 = support + one repair layer
    ...
    n = n live serial layers

At depth d+2:
- failure class d+1 removes the current outermost layer, yielding d+1;
- any lower failure class is absorbed by the live tower and the state remains d+2.

Lean proves:

- lower_failure_absorbed
- outer_failure_removes_one_layer
- one_more_layer_moves_boundary
- base_support_failure_unrepairable
- descending_boundary_cascade_fails
- top_depth_postfixed_under_lower_failures

The central parametric result is:

> Adding one fresh outer repair layer turns the previous outer failure class
> into an absorbed lower failure.

The descending cascade theorem proves for every n that a tower of depth n+1
fails under the sequence n,n-1,...,0 when no further outer repair exists.

The post-fixed theorem proves that every positive full-depth state is viable
under all failure classes strictly below its current outermost layer.

## Finite census

The Python census exhaustively checks depths 1 through 8.

For each depth d:
- with admitted failures 0..d-2, the finite bounded greatest kernel is exactly {d};
- with admitted failures 0..d-1, the greatest kernel is empty;
- the descending cascade fails;
- adding one layer absorbs the old outer boundary failure.

This finite census is supporting evidence for the generic Lean laws; it is not
used as a substitute for them.

## Part B — Cross-layer falsifier

The strict serial tower is then attacked.

Concrete WarrantGraph fixture:

    0 support root
    1 protected consequence
    2 ordinary repair capability
    3 shared cross-layer repair capability

Both ordinary repair 2 and support 0 are revoked.

Without repair, the live view is:

    [3]

Then shared capability 3 directly warrants a fresh support root 6 and protected
consequence 7:

    [3,6,7]

Ordinary repair capability 2 remains revoked.

Lean proves:

- cross_layer_base_live
- cross_layer_both_revoked
- shared_capability_repairs_across_missing_layer
- ordinary_repair_remains_revoked
- strict_serial_tower_not_necessary

Therefore the universal claim

> every viable recursive repair architecture must be a strict serial tower

is refuted by an exact WarrantGraph counterexample.

## Programme interpretation

The depth-n theorem is real but architecture-relative.

For a strict serial dependency chain, adding a warranted layer moves the failure
boundary outward by one level.

But the cross-layer fixture proves that developmental repair geometry need not
be linear. A higher capability may cover multiple lower failure classes or
bypass a missing intermediate layer.

The stronger candidate object is therefore not scalar "depth" alone. It is a
repair dependency/coverage graph (or hypergraph) whose viability depends on the
admitted failure family, live warrant support, and available repair paths.

Depth remains one useful coordinate of that geometry.

## Claim boundary

If qualification passes, V4 warrants only:

1. the generic strict-tower Nat laws above;
2. the finite depth 1..8 census;
3. the exact cross-layer WarrantGraph counterexample;
4. the conclusion that strict serial depth is sufficient in that model but not
   necessary for viable repair architecture in general.

It does not establish:
- a complete graph-theoretic characterization of viability;
- stochastic, continuous, infinite-state or adversarial viability;
- that every cross-layer repair is desirable or safe;
- physical, biological, cognitive, consciousness or AHQ claims.

## Next residual

Replace scalar depth with the smallest general repair-coverage object:

    failure class -> set of warranted repair capabilities / repair paths

Then compute the protected-objective viability kernel on that finite repair
graph and test whether the decisive invariant is a cut/cover condition rather
than linear depth.
