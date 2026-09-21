# Metatron

**Metatron is a proof-carrying developmental computer.**

Core rules:

- residuals earn generators;
- warrant earns relations;
- free completion supplies compositional consequence;
- quotient removes distinctions the protected future cannot expose;
- compilation makes the resulting presentation executable.

V0 is finite: exact obstruction → verified extension → promotion → reuse →
restart → query-relative compression → revocation → regrowth.


## Qualification

Metatron V0's qualified implementation head and successful implementation run
are recorded in evidence/qualified-runs/metatron-v0.json.

The later evidence-closure commit deliberately does not claim to contain its
own SHA. Its exact evidence_closure_sha is attested externally by the final
metatron-v0-evidence-closure GitHub Actions artifact.

The qualification is intentionally bounded. Nonlinear support/recombination,
dependency-driven Flash reclosure, the full execution-result interface,
earned-equation completeness, and the strict Lyapunov bridge remain outside V0.


## Minimal nucleus experiment

On `metatron-minimal-warrant-graph-v0`, the proposed trusted runtime reduces
to a content-addressed `Node(kind, payload, premises)` and one authoritative
mutation: `WarrantGraph.append(node)`.

Capabilities, residuals, relations, measurements, promotions, revocations,
staging and lineage become ordinary warranted nodes or derived views. The
canonical JSONL event log is the sole persisted authority; indexes, frontiers
and snapshots are disposable.

The existing V0 runtime and Lean Kernel controller remain on the branch only as
qualification/reference layers while this smaller nucleus is tested.

See `docs/minimal-warrant-graph-v0.md`.
