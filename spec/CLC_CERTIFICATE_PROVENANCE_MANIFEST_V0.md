# CLC Source-Pinned Provenance Manifest V0

**Status:** CANDIDATE until exact-head hosted qualification is green.

A9d proved that certificate identity alone does not determine a Metatron
warrant. This experiment tests the smallest non-trusted evidence object that
can carry that missing information without enlarging the Nucleus or Lean
WarrantGraph.

## Evidence object

The committed JSON manifest binds:

- pinned CLC source head
  `900a73c1d386ee0eee1205a1cf31d270f3311ef7`;
- exact `CLC/Fixtures.lean` blob
  `ead1d6f1da004770f93539f589acd83a35578a15`;
- pre-existing certificate authority
  `CLC.Fixtures.positiveAuthority`;
- certificate type/literal `Unit / ()`;
- frozen Metatron log `Metatron.warrantBaseline`;
- live warrant index `0`.

The manifest is deliberately outside the trusted WarrantGraph. It is evidence
to be source-pinned, hashed, independently checked, and converted into a Lean
witness.

## Qualification

The hosted gate must:

1. verify exact A9d ancestry and unchanged trusted waist;
2. fetch and hash the exact CLC fixture source and confirm the Unit certificate
   authority;
3. validate the manifest schema and fixed source fields;
4. generate a Lean `CertificateProvenance Unit warrantBaseline` witness from
   the manifest;
5. compile that witness and audit its axioms;
6. require an otherwise identical sham manifest with warrant index 4 to fail
   Lean compilation;
7. rerun the retained 32-test Python authority suite;
8. retain the manifest, generated witness, audits and hosted attestation.

## Claim boundary

A green result warrants only that this exact manifest is a self-consistent,
source-pinned provenance attestation whose declared warrant index is live in
the frozen Lean WarrantGraph and whose generated binding composes through A9d.

It does **not** prove that the CLC authors intended this binding, authenticate
an external signer, establish arbitrary certificate identity mappings,
Python-runtime↔Lean universality, dynamic reclosure, quotient preservation,
causal ports, reversibility, or Nucleus enlargement.
