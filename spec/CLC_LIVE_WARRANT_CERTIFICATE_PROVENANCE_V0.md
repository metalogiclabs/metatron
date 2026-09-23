# CLC Live-Warrant Certificate Provenance V0

**Status:** CANDIDATE until exact-head hosted qualification is green.

This experiment removes the remaining external support-map premise from A9b
for one intentionally narrow certificate representation.

## Parent boundary

- A9 static support seam:
  `d61b5bb6b8299f79ec44e359fb3723ce3f15f0e7`,
  run `35924177681`.
- A9b VerifiedTransport support bridge:
  `e790de325a5a81dfb09371b69ea8a7eb8379714f`,
  run `35926089692`.

## Provenance representation

```lean
abbrev LiveWarrantCertificate (L) :=
  {i : Nat // i ∈ Metatron.warrantLive L}
```

A certificate of this type literally carries a proof that its underlying
warrant index is live in the frozen Metatron log. Its support is therefore not
supplied by an external map: it is canonically the singleton containing the
carried warrant index.

The key equivalence is:

```lean
liveWarrantCertificate_exists_iff (L) (i) :
  (∃ c : LiveWarrantCertificate L, c.1 = i) ↔
    i ∈ Metatron.warrantLive L
```

From this, `liveWarrantCertificateSupport` canonically instantiates A9b's
`FrozenCertificateSupport` for any CLC authority whose certificate type is
`LiveWarrantCertificate L`.

The promoted transport consequence is then:

```lean
liveWarrantCertificate_verifiedTransport_decisive_preserved
```

which requires no separately supplied certificate→support function.

## Positive and negative separators

The positive fixture uses a one-entry frozen warrant log, the unique live
certificate index 0, a minimal always-live CLC authority fixture, and the
identity `VerifiedTransport`.

The negative theorem
`revoked_fixture_has_no_certificate_one` proves that warrant index 1 cannot
even inhabit `LiveWarrantCertificate Metatron.warrantRevokedFixture` after
the frozen revocation fixture removes warrant 1 and its dependency cone.

## Claim boundary

This is a type-level provenance law for certificates represented by live
Metatron warrant indices. It does not show that arbitrary existing CLC
certificate identifiers are warrant indices, does not authenticate external
certificates, and does not derive a mapping for arbitrary certificate types.

No Python-runtime↔Lean universality, dynamic append/revoke commutation,
certificate synthesis, quotient preservation, causal-port theorem, reclosure,
reversibility, or Nucleus enlargement is claimed.
