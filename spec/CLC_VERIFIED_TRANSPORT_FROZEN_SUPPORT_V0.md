# CLC VerifiedTransport ↔ Metatron Frozen Support V0

**Status:** CANDIDATE until the exact-head hosted gate is green.

This experiment is stacked on the independently qualified static A9 seam:
`d61b5bb6b8299f79ec44e359fb3723ce3f15f0e7`, run
`35924177681`, artifact `10778148087`.

## Frozen theorem boundary

The new adapter introduces only a declared certificate-support interpretation:

```lean
structure FrozenCertificateSupport (Ωauth) (L) where
  support : Cert → CLC.Support Nat
  live_support :
    ∀ c, Ωauth.live c = true →
      ∀ i ∈ support c, i ∈ Metatron.warrantLive L
```

From that static support-soundness premise and an existing CLC
`VerifiedTransport`, prove:

```lean
verifiedTransport_decisive_preserved_with_live_support :
  (CLC.liveView (snapshotOf L) {support a.cert}).Nonempty ∧
  B.eval (a.mapState x) (a.liftProtected p).1 = A.eval x p.1
```

for decisive protected source verdicts.

This theorem deliberately composes two already-separated authority facts:

1. Metatron-backed liveness of the transport certificate's declared support,
   via the qualified A9 `warrant_support_iff` seam; and
2. CLC's existing `decisive_preserved` theorem for a `VerifiedTransport`.

It does **not** claim that Metatron verifies transport semantics, that all CLC
certificates admit such a support interpretation, or that the Python runtime is
universally equivalent to the Lean WarrantGraph.

## Source pins

- A9 qualified parent:
  `d61b5bb6b8299f79ec44e359fb3723ce3f15f0e7`.
- A9 hosted run: `35924177681`.
- MSI/CLC source:
  `900a73c1d386ee0eee1205a1cf31d270f3311ef7`.
- CLC `Transport.lean` Git blob:
  `fd76f47aba3fcb37ff8d59a6deadd4848f5a239c`.
- CLC `Verdict.lean` Git blob:
  `47add0bc00e239cfa8dc0786e0f0031669ca04ac`.
- Mathlib:
  `44ba35c6daa9d69aff8fed9fff9bbde17ded774d`.
- Lean: `v4.35.0-rc2`.

## Positive and negative separators

The positive fixture uses the CLC identity `VerifiedTransport` with a live
certificate support `{0}` over Metatron's frozen baseline log.

The mandatory negative fixture attempts to assign live certificate support
`{1}` after the frozen Metatron revocation fixture has removed warrant 1 and
its dependency cone. Such a `FrozenCertificateSupport` must be impossible.

## Non-claims

No dynamic append/revoke commutation, certificate synthesis, certificate
authentication, arbitrary transport-to-runtime correspondence, quotient
preservation, causal-port theorem, reclosure theorem, reversibility theorem, or
Nucleus enlargement is claimed.
