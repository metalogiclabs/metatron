# Warranted Continuation Viability V3

## Objective
Test recursive developmental depth. V2 showed that admitting loss of the ordinary repair capability collapses the declared viability kernel when no meta-repair exists. V3 adds a separately warranted meta-repair capability and asks two questions:

1. Does one extra repair layer restore a nonempty kernel for support loss plus ordinary repair-capability loss?
2. If loss of the meta-repair capability is also admitted, does the boundary move outward and collapse again?

Parent V2 exact head: 6d40b505c1a113da6d3cd1340f752c1fdbf83557.
Parent qualification: run 35924173950, artifact 10777714588,
sha256:d955cf33017bd658dc6e4afc78a95ca5fa1e0f67613841930c1855b59b0c1689.

## Abstract finite result
States are metaAdaptive, repairOnly, noCapBoth, primaryOnlyNoCap, backupOnlyNoCap.

For the encounter alphabet {revokePrimary,revokeBackup,revokeRepair}, metaAdaptive repairs support loss using ordinary repair and repairs ordinary-repair loss using meta-repair. The expected greatest post-fixed kernel is exactly {metaAdaptive}.

For the enlarged alphabet also containing revokeMeta, there is no meta-meta repair. The expected greatest post-fixed kernel is empty.

Lean theorem surface:
- depth_one_kernel_postfixed
- depth_one_kernel_greatest
- meta_repair_restores_nonempty_kernel
- meta_loss_no_postfixed_state
- one_more_repair_layer_moves_the_boundary

## Concrete proof-carrying authority
Warrant entries:
0 primary support; 1 primary consequence; 2 backup support; 3 backup consequence; 4 ordinary repair capability; 5 meta-repair capability.

After revoking capability 4, a fresh replacement repair capability is appended with premise 5. It becomes live only because meta-repair 5 is live. A later support repair is explicitly premised on that replacement capability.

Expected exact live views:
- base: [0,1,2,3,4,5]
- repair 4 revoked: [0,1,2,3,5]
- repair capability restored by meta: [0,1,2,3,5,7]
- primary support then repaired by replacement 7: [2,3,5,7,9,10]
- meta 5 revoked after restoration: [0,1,2,3]
- attempted meta-backed restoration after meta loss: [0,1,2,3]

Thus recursive repair is warrant-dependent, not magical. Revoking the meta warrant invalidates the replacement capability that depended on it while preserving append-only history.

## Claim boundary
If qualified, V3 warrants only the declared finite recursive-repair model and exact WarrantGraph fixtures. It does not prove an infinite hierarchy is necessary, that every system needs meta-repair, or any physical/biological/consciousness claim.

The precise lesson is relative: adding one independently warranted repair layer can move the viability boundary outward by one declared failure class; admitting failure of that new outer layer with no further repair can collapse it again.

## Next residual
If V3 qualifies, test whether recursive depth can be represented generically as a finite capability tower and prove the depth-n boundary law without hand-writing each layer.
