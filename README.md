# Metatron

**Metatron is a proof-carrying developmental computer.**

The trusted runtime is deliberately tiny:

```text
Node(kind, payload, premises)
Log = tuple[Node, ...]
append(Log, Node) -> Log
```

The append-only warrant log is the sole authority. `Live(Log)` derives the
current machine; revocation retracts authority and dependent consequences
without deleting history.

## V1 integrated architecture

Everything richer remains a derived semantic layer or external policy:

```text
warrant log
  -> lawful future observations
  -> continuation-safe behavioral quotient
  -> future-demanded consequential residual
  -> minimum separating generator frontier (tau)
  -> independent verification
  -> warranted promotion
  -> global reclosure
```

The formal CLC stack now reaches proof-relevant, port-aware finite causal event
structures. Developmental refinement is relational/oplax in general, with
canonical backward forgetting maps between refined quotient views.

The separating-hypergraph policy has passed historical, preregistered, and blind
commit-predict-reveal tests. It is a search policy, **not** trusted authority.

The Lean Kernel eight-lane controller is the current external engineering wedge:
proof, measurement, promotion, rejection, and staging remain cleanly separated
from semantics.

See:

- `docs/minimal-warrant-graph-v0.md`
- `spec/METATRON_V1_INTEGRATION.md`
- `spec/CONSTITUTION.md`
- `spec/CLC_PORT_EVENT_STRUCTURE_V0.md`
- `spec/SEPARATING_HYPERGRAPH_BLIND_V3_PREREG.md`
- `benchmarks/lean_kernel/records/eight-lane-status-v1.json`
