# Warranted Continuation Viability V7

## Objective

Compute the greatest protected-objective viability kernel directly on the
smallest stateful repair transition system forced by the V6 contention
counterexample, then test whether replenishment can restore viability.

Parent:
- Warranted Continuation Viability V6
- exact head: `5d8e141f095c23e8ee2d8a3afd40e1264ae2965b`
- qualification run: `35929594852`
- artifact: `10781085097`
- digest:
  `sha256:12539c29ce2337f48ae2abc1d5dda1c4ee8782c33ce8090307769db17baa09e3`

V7 is stacked directly on that exact head.

## Finite full state

The state quotient has exactly four states and explicitly carries both
coordinates that V6 proved consequential:

1. whether certified repair warrant 0 is live;
2. whether the one-shot repair resource is available.

The constructors are:
- `ready`: warrant live, fuel available;
- `depleted`: warrant live, fuel unavailable;
- `unauthorizedReady`: warrant absent, fuel available;
- `unauthorizedDepleted`: warrant absent, fuel unavailable.

The admitted protected failures remain V6 failures 0 and 1, each using the same
existing causally certified AB repair route.

## No-replenishment kernel

Without replenishment, a successful repair from `ready` consumes the resource
and transitions to `depleted`. Every other state has no successful repair
transition.

Lean proves:
- `contention_no_postfixed_state`;
- `contention_empty_kernel_postfixed`;
- `contention_empty_kernel_greatest`.

Therefore the greatest post-fixed viability kernel is exactly empty.

The independent finite predecessor census is:

```
4 → 1 → 0 → 0
```

This converts V6's two failing length-2 schedules into an exact greatest-kernel
result over the full finite state.

## Replenishment intervention

The smallest intervention replenishes the resource immediately after every
successful certified repair. It does not add repair authority or change causal
validity.

Under that policy, `ready` maps back to `ready` for either admitted failure.

Lean proves:
- `replenished_kernel_postfixed`;
- `replenished_kernel_greatest`;
- `replenished_kernel_exact`;
- `replenishment_changes_empty_to_nonempty_kernel`.

The independent predecessor census becomes:

```
4 → 1 → 1
```

with exact greatest kernel `{ready}`.

Both schedules `[0,1]` and `[1,0]` still fail without replenishment and both
succeed with replenishment. Thus ordering alone does not rescue the V6 fixture;
resource restoration does.

## WarrantGraph projection

A one-entry concrete WarrantGraph has live view `[0]`. Revoking warrant 0
gives `[]`. V7 proves that the four finite states' authorization coordinate
matches these exact live views.

The trusted Nucleus and WarrantGraph remain unchanged.

## Programme consequence

V6 established that static live causal cover is not sequentially sufficient.
V7 earns the next canonical object on the exact counterexample: viability is the
greatest post-fixed region of the **stateful** repair transition system.

Resource policy changes that transition system. In this finite model,
replenishment changes the greatest kernel from empty to nonempty without
changing repair authority or causal validity.

## Claim boundary

V7 warrants only this four-state deterministic model, the inherited V6 AB
causal route, and the exact immediate-replenishment intervention.

It does not establish optimal replenishment, general scheduling, fairness,
resource quantities beyond one Boolean token, stochastic/adversarial
infinite-horizon viability, arbitrary concurrency, or physical/biological/
cognitive claims.

## Next residual

Generalize the resource coordinate minimally: finite resource capacity and
repair costs. Test whether viability is characterized by a resource-aware
greatest fixed point rather than any scalar average repair/disruption ratio.
