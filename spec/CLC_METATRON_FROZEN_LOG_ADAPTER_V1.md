# CLC ↔ Metatron Frozen-Log Support Adapter V1

Status: CANDIDATE until exact-head hosted qualification is green.

This is a reconstructed successor to the unrecoverable local candidate
`d32b7227e323c99dc53139045c6604259bfa678e`. It is deliberately a new
Git lineage and must never be represented as byte-identical to that lost local
candidate.

## Frozen theorem

```lean
warrant_support_iff (L) (F) :
  (CLC.liveView (snapshotOf L) F).Nonempty ↔
    ∃ s ∈ F, ∀ i ∈ s, i ∈ Metatron.warrantLive L
```

The adapter maps the frozen Lean `List WarrantEntry` semantics into a CLC
`TokenSnapshot Nat`. Every raw `some` revocation target is retained in the
snapshot, including out-of-range targets. `live_revoked_disjoint` is proved
from the WarrantGraph fold semantics.

## Source boundary

- Metatron base: `b9d1b5cc10477188be6e55617699be60e70f6dad`.
- Metatron WarrantGraph git blob: `d2affc0a57a1815f303f6f1859941465c69e7d32`.
- Metatron WarrantGraph SHA-256: `0625dd2c9d9af3c6900faf0a37da8011d9a1a3a0eef63f7664530eaeabc80b7b`.
- MSI CLC source: `900a73c1d386ee0eee1205a1cf31d270f3311ef7`.
- CLC Support SHA-256: `accef51e223c081947794e26f8f5f4bc36217308ea759ec7baa7042408819ae5`.
- Mathlib: `44ba35c6daa9d69aff8fed9fff9bbde17ded774d`.
- Lean: `v4.35.0-rc2`.

The trusted `runtime/metatron/nucleus.py` and root
`formal/Metatron/WarrantGraph.lean` are not modified.

## Required checks

Hosted qualification must source-check the vendored formal inputs, build the
unchanged root Metatron targets, build the isolated adapter, reject proof
placeholders, audit theorem axioms, run the complete retained Python suite,
and independently enumerate exactly 2,048 support-family cases.

The historical Triskelion adapter failure (run `35552653057`, job
`106190153436`) remains a negative lineage constraint. The current Boolean
flip regression says only that the same-form lawful flip is not
continuation-neutral.

## Non-claims

No claim is made about CLC certificates or VerifiedTransport, Python-runtime ↔
Lean universality, dynamic append/revoke commutation, behavioral quotients,
causal ports, authentication, reclosure, reversibility, or enlargement of the
trusted Nucleus.
