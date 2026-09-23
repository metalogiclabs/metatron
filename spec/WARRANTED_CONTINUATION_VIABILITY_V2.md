# Warranted Continuation Viability V2

## Objective

Close the V1 residual:

1. admit revocation of the repair capability itself;
2. derive the repair/no-repair separator from concrete WarrantGraph premises;
3. compare the greatest viability kernel before and after capability loss is
   admitted.

Parent:
- Warranted Continuation Viability V1
- exact head: bf71eafec63511a47a351cc2c95b8b239b37e6d5
- qualification run: 35923675108
- artifact: 10778525989
- digest:
  sha256:0f9ff4ddc47056bd79f24458fbfa1698106842e764e37341e911b13319438500

V2 is stacked directly on that exact head.

## Kernel comparison

V2 uses four semantic states:

- adaptive
- noCapBoth
- primaryOnlyNoCap
- backupOnlyNoCap

With support revocations only:

    {revokePrimary, revokeBackup}

the exact greatest post-fixed viability kernel is:

    {adaptive}

The exhaustive predecessor iteration is:

    4 -> 2 -> 1 -> 1 states.

When capability revocation is added:

    {revokePrimary, revokeBackup, revokeCapability}

the predecessor iteration is:

    4 -> 2 -> 1 -> 0 -> 0 states.

Thus the greatest post-fixed viability kernel is empty.

Lean proves:

- support_kernel_postfixed
- support_kernel_greatest
- capability_loss_no_postfixed_state
- capability_loss_empty_kernel_postfixed
- capability_loss_empty_kernel_greatest
- admitting_capability_loss_collapses_kernel

The empty-kernel result is exact only for this declared encounter alphabet and
repair policy.

## Concrete WarrantGraph authority

The abstract collapse is paired with a concrete append-only authority fixture.

Indices:

    0 primary support root
    1 primary protected consequence
    2 backup support root
    3 backup protected consequence
    4 verified repair capability

A primary repair is appended with premise 4:

    6 repair root, premises [4]
    7 repaired consequence, premises [6]

So the repair is not magic: its authority explicitly depends on the live repair
capability.

Exact WarrantGraph results:

Base:
    [0,1,2,3,4]

Revoke primary:
    [2,3,4]

Repair while capability 4 is live:
    [2,3,4,6,7]

Then revoke capability 4:
    [2,3]

Because WarrantGraph recomputes liveness from the append-only log, revoking the
capability invalidates the dependent repair cone 6->7 while retaining its
history.

A second fixture revokes capability first, then primary, then appends the same
would-be repair pattern with premise 4. The live view remains:

    [2,3]

The attempted repair does not become live because its authority premise is
revoked.

Lean proves:

- capability_base_live
- primary_repair_is_capability_backed
- capability_revocation_cuts_repair_cone
- capability_revocation_preserves_history
- no_repair_after_capability_loss
- concrete_capability_separator

## Programme meaning

V1 established a nonempty global finite viability region under support loss
when repair capability remained available.

V2 identifies a sharper boundary:

> viability depends not only on redundant support, but on the continued warrant
> of the capability that performs lawful repair.

When capability loss is itself an admitted encounter and there is no
meta-repair for that capability, the declared infinite-repeat viability kernel
collapses to the empty set.

This is a precise finite form of "the system can cease to be able to remain
viable": not merely because current support is damaged, but because the
warranted means of restoring support has itself left the live authority view.

## Claim boundary

If qualification passes, V2 warrants only:

1. the exact finite kernel comparison above;
2. the exact concrete WarrantGraph capability-dependency fixtures;
3. the conclusion that capability loss collapses viability in this declared
   system with no capability-restoration action.

It does not establish:

- that every real developmental system has an empty kernel after capability loss;
- that repair capabilities cannot themselves be repaired;
- infinite-state, stochastic or continuous viability;
- a universal self/environment rate threshold;
- physical, biological, cognitive, consciousness or AHQ claims.

## Next residual

The obvious next layer is meta-repair: add a separately warranted capability
that can restore the repair capability itself, then compute whether the
viability kernel reappears. This tests recursive developmental depth rather than
assuming an unbreakable repair layer.
