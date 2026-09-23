# CLC Certificate Provenance Binding V0

**Status:** CANDIDATE until exact-head hosted qualification is green.

This experiment tests the next identity boundary after A9c.

## Parents

- A9b: `e790de325a5a81dfb09371b69ea8a7eb8379714f`,
  run `35926089692`.
- A9c: `3b10b276f132600a2a51d0a8260c24a108fbd748`,
  run `35926898664`.

## Question

Does a pre-existing CLC certificate identifier determine which Metatron live
warrant carries its provenance?

The pinned CLC positive fixture at
`900a73c1d386ee0eee1205a1cf31d270f3311ef7` uses
`CertId := Unit` and `positiveAuthority : AuthoritySnapshot Unit`.

On Metatron's frozen baseline log there are multiple live warrant indices.
Therefore the CLC identifier `()` alone cannot select one uniquely.

## Minimal explicit object

```lean
structure CertificateProvenance (Cert) (L) where
  toLive : Cert → LiveWarrantCertificate L
```

Given this explicit binding, `certificateProvenanceSupport` canonically
creates A9b's support witness and
`certificateProvenance_verifiedTransport_decisive_preserved` inherits the
verified transport consequence.

## Decisive negative

For `Cert = Unit` and `Metatron.warrantBaseline`, both constant bindings to
live warrant 0 and live warrant 3 are lawful, and Lean proves:

```lean
unit_certificate_identity_does_not_determine_warrant :
  ∃ p q : CertificateProvenance Unit Metatron.warrantBaseline,
    p.toLive ≠ q.toLive
```

Thus the certificate identity alone does not determine warrant provenance.
The binding is genuinely additional evidence and must not be inferred.

## Positive boundary

Once an explicit binding is supplied, the existing CLC identity
`VerifiedTransport` fixture satisfies the live-support + decisive-preservation
consequence through the same checked path as A9b.

## Non-claims

This does not say every provenance binding is trustworthy. It identifies the
minimum extra datum that must be independently warranted when a CLC certificate
type is not already `LiveWarrantCertificate L`.

No external-certificate authentication, Python-runtime↔Lean universality,
dynamic append/revoke commutation, certificate synthesis, quotient
preservation, causal ports, reclosure, reversibility, or Nucleus enlargement
is claimed.
