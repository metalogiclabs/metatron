# CLC Provenance Attestation V0

**Status:** CANDIDATE until exact-head hosted qualification is green.

A9d established a negative boundary: a pre-existing CLC certificate identity
does not determine a unique Metatron live warrant. Therefore provenance binding
is genuinely extra evidence.

This experiment tests the smallest non-trusted way to carry that evidence:
an external, source-pinned manifest that generates a Lean witness.

## Attested binding

The manifest binds:

- CLC certificate source:
  `heathsanchez/Minimal-Sufficient-Interface`
  at `900a73c1d386ee0eee1205a1cf31d270f3311ef7`,
  exact `qcklean/CLC/Fixtures.lean` blob
  `ead1d6f1da004770f93539f589acd83a35578a15`;
- pre-existing certificate identity: `CertId := Unit`,
  authority name `CLC.Fixtures.positiveAuthority`;
- certificate value: `()`;
- Metatron warrant source: unchanged
  `formal/Metatron/WarrantGraph.lean` blob
  `d2affc0a57a1815f303f6f1859941465c69e7d32`;
- frozen log: `Metatron.warrantBaseline`;
- attested live warrant index: `0`.

The manifest is external evidence. It does not modify the trusted Nucleus or
WarrantGraph.

## Generated witness

`scripts/generate_clc_provenance_attestation_v0.py` validates the frozen
manifest schema/pins and deterministically regenerates
`ProvenanceAttestationGenerated.lean`.

The generated Lean file constructs:

```lean
attestedUnitCertificateProvenance :
  CertificateProvenance Unit Metatron.warrantBaseline
```

whose target is exactly live warrant 0.

Hosted qualification regenerates the Lean file and requires zero diff before
building it. Thus the executable witness is mechanically tied to the attested
manifest.

## Scientific boundary

The result warrants only this explicit source-pinned attestation and its
generated Lean consistency/liveness witness. It does not prove that the
historical CLC author intended Unit certificate `()` to denote Metatron
warrant 0, and it does not authenticate arbitrary external provenance claims.

External provenance authority remains outside the trusted runtime.

No Python-runtime↔Lean universality, dynamic append/revoke commutation,
certificate synthesis, quotient preservation, causal ports, reclosure,
reversibility, or Nucleus enlargement is claimed.
