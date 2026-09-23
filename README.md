# Metatron

**Metatron is a proof-carrying developmental computer.**

The trusted runtime remains deliberately tiny:

Node(kind, payload, premises)
Log = tuple[Node, ...]
append(Log, Node) -> Log

Everything richer is derived semantics or external policy.

## V1 architecture

warrant log
  -> lawful future observations
  -> continuation-safe behavioral quotient
  -> future-demanded residual
  -> minimum certified causal repair frontier
  -> earn safe swaps modulo FutureEq
  -> minimum behavioral commutation basis
  -> behavioral trace components / finite causal quotient
  -> independent verification
  -> warranted promotion
  -> global reclosure

Blind V3 established the arity-one minimum-basis law. Residual Synergy and Blind Causal Repair established order-sensitive compositional repair. Finite Poset Connectivity removed arbitrary serialization. Earned Commutation discovered exact safe swaps from anonymous transition consequences.

Behavioral Commutation V0 now goes further: raw states need not commute. If two action orders differ only inside the continuation-safe behavioral quotient, Metatron may lawfully identify them.

In the blind quotient-relative test, 4 raw-state commuting pairs expanded to 5 behaviorally commuting pairs; the extra pair changed internal state but no lawful future observation could expose the difference. The 24 schedules collapsed into exactly two behavioral trace classes of size 12, matching independently computed behavioral semantics.

The Lean Kernel controller remains an external engineering wedge; none of this enlarges Nucleus authority.

See:

- spec/METATRON_V1_INTEGRATION.md
- spec/BEHAVIORAL_COMMUTATION_V0.md
- spec/BLIND_BEHAVIORAL_COMMUTATION_V1_PREREG.md
- spec/EARNED_COMMUTATION_BASIS_V0.md
- spec/FINITE_POSET_TOPOSORT_CONNECTIVITY_V0.md
- spec/CAUSAL_TRACE_QUOTIENT_V0.md
- spec/CAUSAL_REPAIR_COVER_V0.md
