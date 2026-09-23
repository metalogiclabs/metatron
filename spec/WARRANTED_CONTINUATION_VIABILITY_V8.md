# Warranted Continuation Viability V8

## Objective

Replace V7's Boolean resource with finite capacity and explicit repair costs,
then test whether a scalar average supply/demand summary determines the exact
resource-aware viability kernel.

Parent:
- Warranted Continuation Viability V7
- exact current head: `21923060852ed75311e15045ddab3673ae93db37`
- exact-head qualification run: `35930307507`
- artifact: `10780427461`
- digest:
  `sha256:b2abd37a8d331f3c02a5aa2b584de74c0b3674eb7e73b72177cc812b7956a382`

V8 is stacked directly on that qualified head.

## Full finite state

Resource capacity is 2. The state carries:
- inherited repair authorization: warrant 0 live or absent;
- exact resource level: 0, 1 or 2.

This yields six states.

Both compared systems have:
- the same two admitted protected failure classes;
- the same live repair authority;
- the same capacity 2;
- the same replenishment of 1 unit after a successful repair;
- the same total declared repair demand 2 over the two failure classes;
- therefore the same uniform-class average repair cost 1.

Only cost geometry differs.

## Balanced geometry

Costs are:
- failure 0 → 1
- failure 1 → 1

One unit is replenished after each successful repair, so authorized states with
resource 1 or 2 are self-sustaining.

Lean proves the exact greatest post-fixed kernel:

```
{auth1, auth2}
```

Independent predecessor census:

```
6 → 2 → 2
```

## Skewed geometry

Costs are:
- failure 0 → 0
- failure 1 → 2

The same one unit is replenished after success. From `auth2`, expensive
failure 1 moves to `auth1`; another expensive failure then has no lawful
successor. Lower authorized states cannot handle failure 1 at all.

Lean proves the greatest post-fixed kernel is empty.

Independent predecessor census:

```
6 → 1 → 0 → 0
```

The explicit sequence `[1,1]` survives under balanced costs and fails under
skewed costs.

## Scalar falsifier

The scalar summary deliberately remembers only:
- total cost over the declared failure classes;
- replenishment per successful repair;
- total capacity.

Balanced and skewed systems have exactly the same scalar summary:

```
(total demand = 2, replenishment = 1, capacity = 2)
```

yet their greatest viability kernels differ.

Lean theorem:

`scalar_average_summary_not_viability_sufficient`.

Therefore a scalar average repair/disruption or average supply/demand ratio is
not sufficient even in this six-state deterministic system. The typed/burst
cost geometry is consequential.

## Boundary

The scalar "average" is the uniform average over the two declared failure
classes. No stochastic encounter distribution is assumed. Greatest-kernel
viability remains universal over the admitted failure alphabet, so repeated
expensive failures are lawful.

V8 does not establish queueing theory, optimal capacity, arbitrary costs,
continuous time, stochastic/adversarial probability laws, economics, biology
or cognition.

Trusted Nucleus and WarrantGraph remain unchanged.

## Next residual

Allow replenishment itself to have a cost/delay or to be an action that
competes with repair. Compute viability on `(live authority, resource,
replenishment state)` and test whether timing/scheduling policy—not average
rate—becomes the next consequential coordinate.
