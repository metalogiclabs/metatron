# Quotient Falsifier V0

## Objective

Promote one reusable representation-level law without enlarging Metatron's trusted
runtime:

> if two states are identical under a proposed representation q but differ under
> a protected target f, then f cannot be recovered from q alone.

Formally, a witness

    q(x) = q(y)  and  f(x) != f(y)

refutes the existence of any lift F with

    F(q(x)) = f(x)

for every x.

## Lineage

- Metatron source base: `b9d1b5cc10477188be6e55617699be60e70f6dad`.
- MSI implementation candidate: `af60141ab47a68c67f4c04d7ec6a9adb2a50776a`
  on `quotient-sufficiency-falsifier-v0`.
- External finite witness source supplied for this experiment:
  Quinn Porter, *Composition Does Not Determine Organization* (2026),
  SHA-256 `07116e8733c62a4f544599db087ed7d11bf9c5cd1fc2f558cd4f72d6a4fe17c8`.

The external source contributes only the exact finite pair encoded in MSI:
`(B4,B0,B4,B0)` and `(B4,B4,B0,B0)` share the stated coarse summaries but
have different staggered order. No physical dynamics or broader Period Lattice
interpretation is imported.

## Formal bridge

`formal/Metatron/QuotientFalsifier.lean` defines:

- `KernelOf q`: equality induced by a representation;
- `FactorsThrough q target`: recoverability of the target from q;
- `SeparatingWitness q target`: one same-q/different-target pair;
- `witness_refutes_factorization`;
- `residualPair_refutes_factorization`.

The last theorem is the programme bridge: Metatron's existing
`ResidualPair (KernelOf q) (KernelOf target) x y` is sufficient to refute the
proposed quotient.

## Verification boundary

This theorem is universal once its witness premise is proved.

Finite search for a witness is different: failure to find a witness establishes
factorization only on the enumerated finite boundary. It must not be promoted
to unrestricted sufficiency.

No new authority is added to `runtime/metatron/nucleus.py` or
`formal/Metatron/WarrantGraph.lean`.

## Intended use

For every proposed residual quotient:

1. declare the protected target consequence;
2. search the cheapest bounded boundary for same-quotient/different-target pairs;
3. if found, reject the quotient immediately;
4. split on the smallest causal distinction that separates the witness;
5. re-run the protected replay before promotion.

This is a falsification rule, not a licence to infer a missing feature from prose.
