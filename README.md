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
  -> earned safe-swap relation from execution consequences
  -> minimum warranted commutation basis
  -> semantic trace components / finite causal quotient
  -> independent verification
  -> warranted promotion
  -> global reclosure

Blind V3 established the arity-one/separable minimum-basis law. Residual Synergy V0 proved composition can create distinctions absent from every singleton generator. Blind Causal Repair V1 recovered an exact hidden ordered repair from anonymous consequences.

Causal Linearization Invariance, Causal Trace Quotient, and Finite Poset Connectivity then removed arbitrary serialization: legal topological schedules are quotiented only through semantically warranted commuting swaps.

Earned Commutation Basis V0 now derives those swap certificates instead of assuming them. In a fresh anonymous four-action world it recovered the exact 3-pair commutation relation, split 24 schedules into the exact 8 execution-semantic classes, and found an irredundant minimum pair basis of size 3.

The Lean Kernel eight-lane controller remains the external engineering wedge: proof, measurement, promotion, rejection, and staging stay outside trusted semantics.

See:

- spec/METATRON_V1_INTEGRATION.md
- spec/EARNED_COMMUTATION_BASIS_V0.md
- spec/BLIND_EARNED_COMMUTATION_V1_PREREG.md
- spec/FINITE_POSET_TOPOSORT_CONNECTIVITY_V0.md
- spec/CAUSAL_TRACE_QUOTIENT_V0.md
- spec/CAUSAL_LINEARIZATION_INVARIANCE_V0.md
- spec/CAUSAL_REPAIR_COVER_V0.md
- spec/BLIND_CAUSAL_REPAIR_V1_PREREG.md
- benchmarks/lean_kernel/records/eight-lane-status-v1.json
