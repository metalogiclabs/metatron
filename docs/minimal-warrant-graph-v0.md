# Minimal Warrant Graph V0

Metatron's semantic nucleus is reduced to two runtime concepts:

```text
Node(kind, payload, premises)
WarrantGraph.append(node)
```

Everything else is a derived view or an external policy.

## Law

Every accepted fact is a content-addressed node:

[
P_1,\ldots,P_n \Longrightarrow C
]

where `premises` are the IDs of the prerequisite nodes and the node itself is
the conclusion (C).

The authoritative state is only the append-only node sequence (L). The live
machine is derived:

[
M = \operatorname{Live}(L)
]

A normal node with `kind = "revoke"` and a `target` removes that target from
the live view. Any descendant whose premises are no longer live disappears from
the live view as well. Nothing is deleted from history.

## What disappeared from the nucleus

These remain useful domain words, but are no longer required as distinct kernel
types:

- residual certificate;
- capability certificate;
- relation certificate;
- measurement;
- candidate;
- promotion event;
- stage event;
- lineage event;
- dependency index;
- mutable serialization snapshot.

They are represented by `Node.kind`, `Node.payload`, and `Node.premises`.

For example:

```text
residual
   └── verification
          └── capability
                 └── relation verification
                        └── relation
```

is one ordinary dependency DAG. Revoking the capability invalidates the live
relation automatically while preserving every historical node.

## Persistence

The JSONL event log is the sole persisted authority. Startup is replay:

```text
events.jsonl -> WarrantGraph.loads -> derived live view
```

Indexes, snapshots, reverse dependencies, frontiers, and projections are
disposable caches.

## External systems

Lean, cvc5, egglog, LeanDojo, FloatLib, SAIR evaluators, agents, and laboratory
systems stay outside the nucleus. They may search, propose, verify, or measure.
Their accepted outputs become nodes.

The nucleus does not know how a theorem was discovered or how a benchmark was
run. It knows only the warranted record and its dependencies.

## Development policy stays outside

The Lean Kernel V8 -> V9 -> V10 staging controller remains valid, but it is a
policy over warranted candidate and measurement nodes, not a primitive semantic
object.

Thus:

```text
truth / warrant != search policy != execution strategy
```

Changing the policy does not rewrite history.

## Hard budget

`runtime/metatron/nucleus.py` is guarded by a test requiring:

- standard-library imports only;
- no more than 180 nonblank, noncomment lines.

The existing V0 runtime and Lean Kernel controller are retained on this branch
as compatibility/reference layers while the warrant graph is qualified. They
are not part of the proposed minimal trusted nucleus.

## Qualification target

This branch is successful when the full historical suite stays green and the
new tests establish:

1. canonical content addressing;
2. fail-closed unknown premises;
3. complete V0 lifecycle using one node type;
4. dependency-cone invalidation on revocation;
5. exact JSONL replay;
6. tamper detection;
7. Lean Kernel evidence represented without kernel-specific types;
8. the explicit size/dependency budget.
