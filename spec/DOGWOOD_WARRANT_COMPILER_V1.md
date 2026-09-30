# Dogwood Warrant Compiler V1

## Status

Candidate until the dedicated hosted qualification gate is green.

## Objective

Compile Metatron's canonical append-only warrant graph into a Dogwood runtime
policy that controls whether an external agent may **use** a warranted node.

Metatron remains the sole warrant authority. Dogwood receives only a projection
of canonical history:

- each non-revocation Metatron node becomes an `Admit::response` event;
- each Metatron revocation becomes a `Revoke::response` event;
- `Use::request` is the only decision point this compiler authorizes.

For a node `n`, the generated `Use` rule requires `n` and every transitive
premise of `n` to have an admitted event with no later revocation. Thus a
revocation cuts the same dependent cone from runtime use that `live_ids` cuts
from Metatron's derived live view.

## Protected equivalence

On a canonical event projection and within the declared Dogwood history window:

```text
Dogwood permits Use(n)  <=>  n is in Metatron live_ids(history)
```

V1 qualifies this law on a dependency-chain + independent-node fixture with a
middle-node revocation. The dependent must move ALLOW -> DENY while the
independent node stays ALLOW.

## Boundary

This is not a second warrant store and does not authorize warrant creation.
Event provenance is trusted input. Dogwood temporal history is bounded; V1 emits
an explicit 3650-day event-schema/window contract rather than claiming
unbounded persistence. Full semantic equivalence for arbitrary histories,
clock horizons, malformed projections, and authenticated external events
remains UNKNOWN.
