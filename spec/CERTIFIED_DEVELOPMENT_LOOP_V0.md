# Certified Development Loop V0

Status: CANDIDATE until exact-head hosted qualification is green.

## Objective

Formalize the smallest complete finite developmental loop already implicit
across the programme:

```
residual witness
→ independently qualified repair basis
→ promotion
→ protected/current refinement
→ target sufficiency
→ zero remaining target residual
```

This experiment does not add a new trusted runtime mechanism. It packages the
existing ResidualBasis theorem into a promotion object with an explicit
post-promotion closure theorem.

## Core object

`QualifiedRepair current target separates` contains only a candidate basis and
a proof that it covers every currently merged but target-distinguished pair.

`promote q` is exactly `RefinedBy current separates q.basis`.

The generic theorems are:

- `promote_refines_current`
- `promote_target_sufficient`
- `promote_closes_residual`
- `run : QualifiedRepair ... → CertifiedLoopResult ...`

A certified loop result records that promotion never leaves the previous
current relation, is sufficient for the frozen target relation, and leaves no
remaining target residual.

## Exact finite fixture

The frozen Boolean fixture reuses the already-qualified ResidualBasis model:

- current relation merges all Boolean states;
- target relation is equality;
- one Unit separator distinguishes unequal states;
- the singleton repair basis is certified;
- the empty basis is explicitly rejected;
- after promotion the relation is exactly the target relation;
- the residual is empty.

## Claim boundary

This is a finite declarative loop theorem. Qualification of a repair basis is a
premise; V0 does not discover repairs, authenticate external evidence, schedule
runtime actions, transport certificates, perform dynamic append/revoke
commutation, or prove universal developmental convergence.

The trusted `runtime/metatron/nucleus.py` and
`formal/Metatron/WarrantGraph.lean` remain unchanged.
