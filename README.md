# Metatron

**Metatron is a proof-carrying developmental computer.**

The trusted runtime is deliberately tiny:

Node(kind, payload, premises)
Log = tuple[Node, ...]
append(Log, Node) -> Log

The append-only warrant log is the sole authority. Live(Log) derives the current machine; revocation retracts authority and dependent consequences without deleting history.

## V1 integrated architecture

warrant log
  -> lawful future observations
  -> continuation-safe behavioral quotient
  -> future-demanded consequential residual
  -> minimum certified causal repair frontier
  -> quotient by certified swap-safe linearizations
  -> independent verification
  -> warranted promotion
  -> global reclosure

The CLC stack reaches proof-relevant, port-aware finite causal event structures. Developmental refinement is relational/oplax in general, with canonical backward forgetting for pure refinement.

Blind V3 established the arity-one/separable minimum-basis law. Residual Synergy V0 proved that composition can create distinctions absent from every singleton generator, so the general repair unit carries certified causal structure and executable order.

Blind Causal Repair V1 then showed prospectively that Metatron can recover the exact minimum ordered repair from anonymous consequences alone.

Causal Linearization Invariance V0 now sharpens canonicalization: different topological orders may be identified only when semantic commutation certifies the swap. The same PES with noncommuting A/B actions remains order-sensitive, so raw partial-order isomorphism is not enough.

The Lean Kernel eight-lane controller remains the external engineering wedge: proof, measurement, promotion, rejection, and staging stay outside trusted semantics.

See:

- spec/METATRON_V1_INTEGRATION.md
- spec/CAUSAL_REPAIR_COVER_V0.md
- spec/CAUSAL_LINEARIZATION_INVARIANCE_V0.md
- spec/BLIND_CAUSAL_REPAIR_V1_PREREG.md
- spec/RESIDUAL_SYNERGY_FALSIFIER_V0.md
- spec/CLC_PORT_EVENT_STRUCTURE_V0.md
- benchmarks/lean_kernel/records/eight-lane-status-v1.json
