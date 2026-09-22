# Minimal Warrant Graph V0

Metatron's semantic nucleus has two public runtime concepts:

```text
Node(kind, payload, premises)
append(Log, Node) -> Log
```

Everything else is either a derived view or an external policy.

## Law

For a node with premise IDs `P₁ ... Pₙ`, the graph records the warranted edge

```text
P₁, ..., Pₙ  ->  C
```

where `C` is the content-addressed node itself.

The authoritative state is one append-only sequence `L`. The active machine
is derived:

```text
M = Live(L)
```

A `revoke` node names a target node. The target is absent from the live view,
and any descendant whose premises cease to be live is absent as well. Historical
nodes are never deleted.

## One authority, not mirrored stores

The in-memory authority is the immutable `Log = tuple[Node, ...]` itself.
The persisted authority is canonical JSONL replay of that same log.
There is no wrapper object with hidden mutable state.

There is no authoritative capability map, certificate map, residual store,
relation store, revocation set, lineage list, dependency index, frontier, or
snapshot. Such structures may be derived and discarded.

Reverse dependencies, affected cones, and history digests live in
`runtime/metatron/views.py`; they are explicitly not authority.

## What was removed

The earlier V0 runtime represented capabilities, certificates, residual
certificates, relations, lineage events, query state and serialization
snapshots as separate mutable structures.

A graph-backed compatibility implementation reduced all of those to derived
views over one warrant graph and passed the retained lifecycle and historical
suite at:

```text
commit 1191b06b17a28dbc29de37e8ba72f67cbe3d2598
run    35655948565
```

That result is sealed in
`evidence/qualified-runs/graph-backed-v0-compat.json`.

After that gate, the duplicated compatibility facade and its old finite-fixture
runtime were deleted from this branch. Git history remains the provenance.

## Formal reference

`formal/Metatron/WarrantGraph.lean` independently defines the live-log rule
using abstract numeric node positions and proves the retained fixture facts:

- without revocation, a dependency chain and an independent node are live;
- revoking the middle node cuts its dependent suffix from the live view;
- revocation appends history rather than deleting it.

The Python/Lean differential gate compares the two live views.

The formal reference uses Lean core only. Mathlib is not required.

## Hard budget

`runtime/metatron/nucleus.py` is guarded by CI:

- Python standard library only;
- at most 120 nonblank, noncomment lines.

The previously qualified implementation had 114 semantic lines and was 4,253
bytes. The current branch removes the `WarrantGraph` wrapper as a further
pure-functional reduction. Its exact source head is not called qualified until
the dedicated workflow records a fresh successful run in
`evidence/qualified-runs/minimal-warrant-graph-v0-latest.json`.

## External systems

LeanDojo, cvc5, egglog, FloatLib, SAIR evaluators, agents, theorem provers,
optimizers, and laboratory systems stay outside the nucleus.

They can search, propose, verify, or measure. Metatron stores only accepted
warranted consequences and dependencies.

Thus:

```text
truth / warrant != search policy != execution strategy
```

The Lean Kernel V8 -> V9 -> V10 controller remains a useful external example:
local contenders can be collapsed before spending scarce external measurement,
without turning staging policy into trusted semantics.

## Qualified implementation

The minimal implementation qualified at:

```text
commit 1d0d962fc3d8894804ced6b510cfaa0f25d10f06
run    35657194138
artifact metatron-minimal-nucleus-v0
```

The committed qualification record names that implementation head. A later
workflow artifact attests the evidence-closure head, avoiding self-reference.

## Nebula certificate boundary

Nebula ignition is not implemented by adding Nebula, Genesis, or Aha classes to
the nucleus. Those are derived developmental interpretations over warranted
history.

A sustained ignition claim is accepted only through the external causal
certificate gate in `scripts/check_nebula_certificate.py`. The certificate must
bind exact source/run/artifact hashes and establish:

`G1 -> (rho2,K2) -> G2 -> (rho3,K3) -> G3`

with future-withholding, knockout, semantic-sham, restart, and sealed-semantics
controls. Until such evidence exists, no Nebula claim is promoted into the
warrant log.
