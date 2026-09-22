# Metatron V1 Integration

**Status:** integration seal / theorem line  
**Branch:** `metatron-v1-integration`

This branch joins the strongest qualified lines without enlarging the trusted
Nucleus.

## Pinned source lines

The exact source heads are recorded in
`evidence/integration/metatron-v1-sources.json`.

The four roles are:

1. **Minimal Warrant Log** — sole trusted runtime authority.
2. **CLC Port Event derived semantics** — future-safe identity and
   proof-relevant causal history.
3. **Blind-qualified separating hypergraph** — external repair/search policy.
4. **Lean Kernel eight-lane adapter** — external proof/measurement/promotion
   boundary.

Only (1) is runtime authority.

## Thin waist

The integration must preserve byte-identical trusted semantics:

```text
runtime/metatron/nucleus.py
  git blob d9d4293e54471714bf098593bf4018c3f6403273

formal/Metatron/WarrantGraph.lean
  git blob d2affc0a57a1815f303f6f1859941465c69e7d32
```

No residual store, hypergraph, port-event graph, benchmark frontier, search
controller, capability map, or external measurement state may become
authoritative runtime state.

## Integrated developmental picture

For append-only history (L_t),

[
Gamma_t = operatorname{Live}(L_t).
]

The derived semantics determines lawful future observations and the current
continuation-safe equivalence

[
R_t = alpha(mu mathcal L_t)=
u mathcal B_t,
]

with active interface

[
Q_t=X_t/R_t.
]

Given a frozen future-demand target family (T), define the consequential
residual

[
U(P,T)=
{{x,y}:xequiv_P ylandexists tin T,;t(x)
e t(y)}.
]

A candidate generator (g) induces the hyperedge

[
E_g={{x,y}in U(P,T):g(x)
e g(y)}.
]

The minimum missing behavioral basis is

[
	au(P,T)=
min{|B|:igcup_{gin B}E_g=U(P,T)}.
]

This determines a **behavioral capability class**, not a privileged syntactic
realizer. Search policy may retain multiple minimum bases. Independent
verification and the frozen admissibility order decide which realizer may be
warranted.

Installation appends warranted causal lineage and triggers derived reclosure.
For pure refinement, the new view canonically forgets to the old one:

[
Q_{t+1}	woheadrightarrow Q_t.
]

## Integration theorem target

The first theorem package on this branch is:

[
oxed{	exttt{certifiedResidualBasis\_closes}}
]

with the intended finite statement:

> A candidate basis covers every future-demanded residual pair iff adding the
> basis makes the resulting observational quotient sufficient for the frozen
> target family.

The minimum-cover corollary should then establish that no smaller candidate
basis from the declared language can yield target sufficiency.

This is a theorem about the **declared finite candidate language**. It is not a
claim of unrestricted generator invention.

## Representation discipline

The integration preserves the distinction between:

- warrant DAG — why a result is authorized;
- behavioral quotient — what may currently be identified;
- separating hypergraph — what future-demanded distinction is missing;
- port event structure — how warranted developmental histories compose;
- benchmark frontier — what external candidate should be tested.

No generic property of raw storage-graph geometry is promoted to semantics.

## Claim boundary

V1 integration does not claim:

- open-ended ontology invention;
- universal minimum repair outside a declared candidate language;
- generic finite-port-event category laws beyond the qualified fixtures;
- automatic promotion of benchmark candidates;
- a larger trusted runtime;
- empirical or ontological conclusions.
