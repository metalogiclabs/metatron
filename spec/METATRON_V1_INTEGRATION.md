# Metatron V1 Integration

**Status:** integration candidate / theorem line  
**Branch:** `metatron-v1-integration`

This branch joins the strongest qualified lines without enlarging the trusted
Nucleus.

## Pinned source lines

Exact heads and qualification runs are recorded in
`evidence/integration/metatron-v1-sources.json`.

The four roles are:

1. **Minimal Warrant Log** — sole trusted runtime authority.
2. **CLC Port Event semantics** — future-safe identity and proof-relevant causal history.
3. **Blind-qualified separating hypergraph** — external repair/search policy.
4. **Lean Kernel eight-lane adapter** — external proof/measurement/promotion boundary.

Only (1) is runtime authority.

## Thin waist

The integration preserves byte-identical trusted semantics:

```text
runtime/metatron/nucleus.py
  git blob d9d4293e54471714bf098593bf4018c3f6403273

formal/Metatron/WarrantGraph.lean
  git blob d2affc0a57a1815f303f6f1859941465c69e7d32
```

The current pure-log qualification is pinned to implementation
`13b1f6b52ee4724e33a6063c18c4a105f20bb0bc`, run `35764668476`,
with 119 semantic lines under the 120-line budget.

No residual store, hypergraph, port-event graph, benchmark frontier, search
controller, capability map, or external measurement state becomes authoritative
runtime state.

## Integrated developmental picture

For append-only history (L_t),

[
Gamma_t=operatorname{Live}(L_t).
]

Derived CLC semantics determines lawful future observations and
continuation-safe equivalence

[
R_t=alpha(mumathcal L_t)=
umathcal B_t,
qquad
Q_t=X_t/R_t.
]

Given a frozen target future relation (T), the consequential residual is the
set of pairs still identified by the current view but separated by (T).

A candidate generator induces a hyperedge over the residual. Search policy may
retain multiple exact minimum bases; it does not privilege a syntactic realizer
unless later warranted evidence distinguishes them.

Independent verification is still required before installation. Installation
appends warrant lineage and triggers derived reclosure. Under pure refinement,
the new quotient canonically forgets to the old view:

[
Q_{t+1}	woheadrightarrow Q_t.
]

## Integration bridge theorem

`formal/Metatron/ResidualBasis.lean` now proves

[
oxed{	exttt{certifiedResidualBasis_closes}}
]

stating:

> A declared candidate basis covers every future-demanded residual pair iff the
> relation refined by that basis is sufficient for the frozen target relation.

It also proves

[
oxed{	exttt{minimumResidualBasis_minimalSufficient}}
]

so exact minimum residual cover transfers directly to minimum target
sufficiency by basis length.

A positive Boolean fixture and an empty-basis negative fixture are included.

This is the mathematical bridge between CLC's semantics of identity and the
blind-qualified (	au) search policy.

## Representation discipline

The integration preserves distinct roles:

- warrant DAG — why a result is authorized;
- behavioral quotient — what may currently be identified;
- separating hypergraph — what future-demanded distinction is missing;
- port event structure — how warranted histories compose;
- benchmark frontier — what external candidate should be tested.

No generic property of raw storage-graph geometry is promoted to semantics.

## Claim boundary

V1 integration does not claim:

- unrestricted generator invention outside a declared candidate language;
- universal minimum repair for arbitrary infinite systems;
- generic category laws for all finite port-event structures;
- automatic promotion of benchmark candidates;
- a larger trusted runtime;
- empirical or ontological universality.
