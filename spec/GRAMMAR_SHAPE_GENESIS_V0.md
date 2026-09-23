# Grammar Shape Genesis V0

**Status:** executable falsification experiment  
**Branch:** `grammar-shape-genesis-v0`

## Question

Can exact residual pressure force a change in the **arity and structural shape**
of the available program grammar when the entire current unary grammar is
exhausted?

## Seed interface

The carrier contains all 32 five-bit states.

The protected seed observation is bit parity.

The current grammar shape is every bijective unary local Boolean rewrite:

[
operatorname{LocalRewrite}(i,f),
qquad
f:\{0,1\}\to\{0,1\}.
]

Every such rewrite either preserves parity or complements it. Therefore the
complete unary grammar, including all coordinates and both bijective unary truth
tables, adds no new partition at all.

The initial consequential residual is therefore nonempty while

[
oxed{
max_{p\in G_1}\operatorname{gain}(p,U_0)=0.
}
]

This is the grammar-shape insufficiency certificate.

## Extensional arity-2 search

Only after the unary-zero-gain certificate is established may the meta-meta
search inspect arity 2.

The arity-2 grammar is completely extensional:

[
operatorname{LocalTruthTableRewrite}(i,j,T),
]

where (i\ne j) and (T:\{0,1\}^2\to\{0,1\}) is an arbitrary four-entry
Boolean truth table subject only to target-bit bijectivity.

No named binary Boolean operation is supplied to the search.

The synthesizer receives:

[
(U_t,;\text{installed programs},;\text{dimension})
]

and no target relation.

The first positive arity-2 witness earns a `grammar_shape_warrant` for the
binary local truth-table skeleton.

## Constructor induction

Two independently synthesized binary programs must then replicate the same
truth table on distinct control coordinates.

Structural anti-unification may only then promote a parameterized binary
constructor:

[
operatorname{LocalTruthTableRewrite}
($control,$target,T).
]

After promotion, later generations must use this induced constructor on
held-out coordinates rather than invoking generic arity-2 truth-table search.

## Expected developmental trace

Parity alone partitions the 32 states into two classes of 16, yielding

[
240
]

future-demanded unresolved pairs.

Each independent control distinction halves the remaining class size, giving

[
oxed{
240\to112\to48\to16\to0.
}
]

Required execution modes:

[
oxed{
	ext{shape genesis},
	ext{binary replication synthesis},
	ext{held-out constructor reuse},
	ext{held-out constructor reuse}.
}
]

## Warrant lineage

The first generation records:

[
	ext{grammar insufficiency}
\to
	ext{arity-2 shape candidate}
\to
	ext{shape verification}
\to
	ext{grammar-shape warrant}.
]

Concrete binary programs are separately proposed, verified, and warranted.

After two replicated concrete witnesses, constructor induction uses the same
replication discipline as Constructor Genesis V0.

## Controls

Qualification requires:

- exhaustive unary grammar maximum gain exactly zero before shape expansion;
- no target argument in the shape synthesizer;
- no named binary operation in the declared search grammar;
- strict residual descent to zero;
- exactly two generic binary synthesis calls;
- exactly two held-out induced-constructor calls;
- restart preserves the final interface and constructor;
- semantic sham changes nothing;
- revoking the first concrete binary warrant transitively removes the shape,
  constructor, and all dependent later capabilities;
- trusted Nucleus blobs remain byte-identical.

## Claim boundary

A positive result establishes **grammar-shape genesis relative to a declared
finite arity search**:

> when the complete unary grammar is consequentially exhausted, Metatron can
> use residual evidence to warrant an arity-2 extensional grammar shape,
> discover a useful concrete binary truth table without a named operator,
> induce a reusable binary constructor from replication, and reuse it on
> held-out parameters.

It does not establish unrestricted invention of arbitrary syntax or unbounded
arity.
