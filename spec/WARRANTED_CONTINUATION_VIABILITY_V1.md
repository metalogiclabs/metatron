# Warranted Continuation Viability V1

## Objective

Strengthen qualified V0 from one fixed encounter stream to a finite
greatest-fixed-point viability kernel over an admitted encounter alphabet, and
connect that kernel to existing Metatron revocation/reclosure machinery.

Parent:
- Warranted Continuation Viability V0
- exact head: 0c4141c106fb74e3b9340443cbbe525ab72b716f
- qualification run: 35922349272
- artifact: 10778150749
- digest:
  sha256:d4f695b79987bb1c050338930278ef7b3afd01ad662353cc1011e5a81c2a56b9

V1 is stacked directly on that exact head.

## Finite greatest viability kernel

The abstract developmental quotient has four states:

- adaptive
- primaryOnly
- backupOnly
- none

The admitted encounter alphabet is:

- revokePrimary
- revokeBackup

The adaptive state retains verified repair capability for either support loss.
After either admitted revocation, its repair/reclosure policy returns it to the
adaptive class before the next encounter.

primaryOnly and backupOnly lack a repair for loss of their last support.
none has no viable successor.

For a state set S, ViablePre(S) contains states for which every admitted
encounter has some successor in S.

A set is PostFixed when S is contained in ViablePre(S).

Lean proves:

- kernel_postfixed
- kernel_greatest
- kernel_exact

where Kernel(s) iff s = adaptive.

kernel_greatest proves that every post-fixed set is contained in Kernel.
Together with kernel_postfixed, this is the finite greatest-postfixed-set /
greatest-fixed-point viability characterization for the declared transition
system.

The exhaustive Python census starts from all four states and iterates the
predecessor operator:

    round 0: {adaptive, primaryOnly, backupOnly, none}
    round 1: {adaptive}
    round 2: {adaptive}

so the finite kernel is exactly {adaptive}.

## WarrantGraph revocation and reclosure

V1 uses the existing formal/Metatron/WarrantGraph.lean semantics rather than
inventing a second warrant authority.

The concrete base log contains two independent support chains:

    0 -> 1
    2 -> 3

Revoking root 0 re-evaluates the live view to:

    [2, 3]

Appending a fresh verified root and dependent consequence then re-evaluates to:

    [2, 3, 5, 6]

Symmetrically, revoking root 2 gives:

    [0, 1]

and verified repair/reclosure gives:

    [0, 1, 5, 6].

The history remains append-only: revocation and replacement are new entries;
old history is not deleted.

These are exact WarrantGraph computations, not a claim about every possible
Flash implementation.

## Proof-lifted Flash-style support

V1 also consumes existing ProofRelevantOplax theorems:

- flash_revocation_removes_one_support
- flash_alternative_support_survives

The theorem proof_lifted_revocation_preserves_alternative packages their exact
consequence: revoking certificate 11 kills one proof-closure trace while the
alternative certified trace remains live.

Thus V1 uses both:

1. WarrantGraph live-view recomputation under revocation and fresh repair;
2. the already-qualified proof-lifted Flash-style alternative-support result.

## Claim boundary

If qualification passes, V1 warrants only:

1. the finite greatest viability kernel of the declared four-state/two-encounter
   abstract system;
2. the exact WarrantGraph revocation/reclosure fixtures;
3. reuse of the existing proof-lifted alternative-support theorem;
4. the bridge that adaptive has a viable successor for every admitted
   revocation in the declared quotient.

It does not establish:

- an infinite-state or continuous viability kernel;
- stochastic/adversarial fairness or productivity;
- that every repair system admits a nonempty viability kernel;
- that WarrantGraph recomputation is identical to every Flash incremental
  implementation;
- arbitrary revocation/replacement policies;
- physical, biological, cognitive, consciousness or AHQ claims.

## Next residual

The remaining strengthening is to replace the abstract adaptive self-loop with
a proof-carrying transition whose successor is derived directly from the
concrete warrant/reclosure state, then add revocation of a repair capability
itself. That will test whether the viable kernel survives capability loss rather
than only support loss.
