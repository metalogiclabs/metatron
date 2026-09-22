# Metatron

**Metatron is a proof-carrying developmental computer.**

The trusted runtime is deliberately tiny:

Node(kind, payload, premises)
Log = tuple[Node, ...]
append(Log, Node) -> Log

The append-only warrant log is the sole authority. Live(Log) derives the current machine; revocation retracts authority and dependent consequences without deleting history.

## V1 integrated architecture

Everything richer remains derived semantics or external policy:

warrant log
  -> lawful future observations
  -> continuation-safe behavioral quotient
  -> future-demanded consequential residual
  -> minimum certified causal repair frontier
  -> independent verification
  -> warranted promotion
  -> global reclosure

The formal CLC stack reaches proof-relevant, port-aware finite causal event structures. Developmental refinement is relational/oplax in general, with canonical backward forgetting maps for pure refinement.

The blind separating-hypergraph policy remains the arity-one/separable search special case. Residual Synergy V0 proves that composition can create distinctions absent from every singleton generator, so the general repair unit now carries certified causal structure and executable order.

The Lean Kernel eight-lane controller remains the external engineering wedge: proof, measurement, promotion, rejection, and staging stay outside trusted semantics.

See:

- docs/minimal-warrant-graph-v0.md
- spec/METATRON_V1_INTEGRATION.md
- spec/CAUSAL_REPAIR_COVER_V0.md
- spec/RESIDUAL_SYNERGY_FALSIFIER_V0.md
- spec/CLC_PORT_EVENT_STRUCTURE_V0.md
- benchmarks/lean_kernel/records/eight-lane-status-v1.json
