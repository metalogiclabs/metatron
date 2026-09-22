# Metatron — Consolidated Current State

This branch is a non-destructive consolidation of the repository's 30 pre-existing branches.

## Present architecture

The current integrated line is `metatron-v1-integration` at `f4ed7b360c84bc971a0619c7a69de4586e73f3ac`, sealed by run **35789903190**. The integration does **not** enlarge the trusted Nucleus.

The sole trusted runtime authority remains the qualified Minimal Warrant Log:

- implementation: `13b1f6b52ee4724e33a6063c18c4a105f20bb0bc`
- qualification run: **35764668476**
- `runtime/metatron/nucleus.py` blob: `d9d4293e54471714bf098593bf4018c3f6403273`
- authoritative state: immutable `tuple[Node, ...]`
- only transition: `append(Log, Node) -> Log`
- 119 semantic lines under the 120-line budget

Everything else remains derived or external:

- CLC port-event semantics: derived formal semantics.
- interaction-aware residual basis semantics: derived formal semantics.
- separating hypergraph: external search/repair policy.
- Lean Kernel eight-lane adapter: external evidence/promotion policy.
- synergy counterexample: retained falsification evidence.

The blind prospective control passes: `BLIND_PROSPECTIVE_PASS`.

## Consolidation rule

A branch is not promoted merely because its workflow was green. Trusted authority, derived semantics, search policy, falsification evidence, and application adapters keep distinct roles.

Negative and failed experiments remain in history and in the branch inventory. In particular, the failed `nebula-ignition-v0` workflow is not interpreted or imported by this consolidation.

## Files

- `evidence/consolidation/all-branches.tsv` freezes every pre-existing branch head.
- `evidence/consolidation/manifest.json` records the retained authority/evidence structure.
- this document explains the human-readable present.

The consolidation itself changes no runtime or formal source.
