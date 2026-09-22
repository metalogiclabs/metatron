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
  -> finite certified commuting trace quotient
  -> independent verification
  -> warranted promotion
  -> global reclosure

Blind V3 established the arity-one/separable minimum-basis law. Residual Synergy V0 proved that composition can create distinctions absent from every singleton generator. Blind Causal Repair V1 then recovered the exact planted ordered repair prospectively from anonymous consequences alone.

Causal Linearization Invariance V0 proved the primitive two-event rule: independent serializations may be identified only when semantic commutation warrants the swap.

Causal Trace Quotient V0 now lifts that law to arbitrary finite chains of certified adjacent swaps. Execution and observation are invariant across the whole trace equivalence class, while the noncommuting A/B same-PES counterexample remains distinct.

So the repair representation is no longer a privileged total schedule. It is a certified causal presentation modulo finite certified commuting trace equivalence.

The Lean Kernel eight-lane controller remains the external engineering wedge: proof, measurement, promotion, rejection, and staging stay outside trusted semantics.

See:

- spec/METATRON_V1_INTEGRATION.md
- spec/CAUSAL_TRACE_QUOTIENT_V0.md
- spec/CAUSAL_LINEARIZATION_INVARIANCE_V0.md
- spec/CAUSAL_REPAIR_COVER_V0.md
- spec/BLIND_CAUSAL_REPAIR_V1_PREREG.md
- spec/RESIDUAL_SYNERGY_FALSIFIER_V0.md
- spec/CLC_PORT_EVENT_STRUCTURE_V0.md
- benchmarks/lean_kernel/records/eight-lane-status-v1.json
