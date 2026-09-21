# Metatron

**Metatron is a proof-carrying developmental computer.**

The minimal nucleus is intentionally tiny:

```text
Node(kind, payload, premises)
WarrantGraph.append(node)
```

A node is content-addressed. The authoritative state is one append-only log.
The current machine is the deterministic live view of that log: revoked nodes
and descendants whose premises are no longer live disappear from execution,
while history remains intact.

## Minimal Warrant Graph V0

Branch: `metatron-minimal-warrant-graph-v0`

Qualified implementation:

- commit: `1d0d962fc3d8894804ced6b510cfaa0f25d10f06`
- run: `35657194138`
- `runtime/metatron/nucleus.py`: 4,253 bytes / 114 nonblank, noncomment lines
- complete runtime package: 5,672 bytes
- Python standard library only
- Lean core only; Mathlib is not a dependency
- public runtime types: `Node`, `WarrantGraph`
- sole authoritative mutation: `WarrantGraph.append(Node)`

The qualification record is
`evidence/qualified-runs/minimal-warrant-graph-v0.json`.

## Compatibility evidence

Before deleting the duplicated V0 runtime facade, the graph-backed replacement
was run against the retained V0 lifecycle and historical suite. That bridge is
sealed at commit `1191b06b17a28dbc29de37e8ba72f67cbe3d2598`, run
`35655948565`, and recorded in
`evidence/qualified-runs/graph-backed-v0-compat.json`.

The old `Machine`, capability/certificate stores, mutable snapshot
serialization, and finite-fixture runtime have therefore been removed from this
branch. Their qualified history remains in Git and in the evidence records.

## Boundary

Search, theorem proving, optimization, benchmarking, staging, and policy stay
outside the nucleus. External systems may propose, verify, or measure; accepted
results enter as warranted nodes.

The Lean Kernel controller remains an external benchmark/policy example, not
part of Metatron's trusted semantics.

See `docs/minimal-warrant-graph-v0.md`.
