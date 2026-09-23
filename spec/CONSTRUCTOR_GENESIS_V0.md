# Constructor Genesis V0

**Status:** executable falsification experiment  
**Branch:** `constructor-genesis-v0`

## Question

Can Metatron go beyond selecting an instance of an already declared schema
family and instead **derive a new reusable parameterized constructor** from
residual-driven concrete successes, then use that constructor on held-out
parameters without returning to generic synthesis?

## Deliberate hierarchy

This experiment separates three levels.

### Current meta-language

The seed observation is five-bit Hamming weight.

The active meta-language initially contains only global complement and its
complete compositional closure.

Hamming weight after global complement is (5-w(x)), so it induces no
additional partition beyond Hamming weight itself.

Therefore the initial consequential residual is nonempty while the current
meta-language is exactly saturated and has zero gain.

### Generic meta-meta grammar

When the current meta-language is certified insufficient, Metatron may invoke
one generic finite program grammar:

[
operatorname{LocalRewrite}(i,f),
]

where (i) is a coordinate and (f:\{0,1\}\to\{0,1\}) is an arbitrary
unary Boolean truth table.

The grammar enumerates all four truth tables and admits only bijective local
state transformations. This leaves identity and negation, but there is no
predeclared `Toggle`, `Flip`, or coordinate-negation schema family.

Concrete programs are ranked only by generated consequential residual gain.

### Induced constructor

After two independently successful concrete programs share the same operation
and truth table but differ in coordinate, structural anti-unification may
promote

[
operatorname{LocalRewrite}(0,[1,0]),
qquad
operatorname{LocalRewrite}(1,[1,0])
]

to the new parameterized schema

[
oxed{
operatorname{LocalRewrite}(i,[1,0]).
}
]

The coordinate becomes a parameter because that is the only varying structural
position across the replicated witnesses.

After promotion, generic program synthesis is disabled. Later generations must
come from instantiating the induced schema on held-out coordinates.

## Expected trace

For all 32 five-bit states, Hamming weight alone leaves

[
110
]

future-demanded residual pairs.

The expected development is

[
oxed{110\to54\to24\to8\to0}.
]

The first two reductions must come from generic concrete synthesis.

The final two reductions must use the induced constructor without another
generic synthesis call.

## Warrant discipline

The lineage records:

[
	ext{meta-language insufficiency}
\to
	ext{concrete program}
\to
	ext{verification}
\to
	ext{concrete warrant}.
]

After two replicated witnesses:

[
	ext{two concrete warrants}
\to
	ext{schema candidate}
\to
	ext{replication verification}
\to
	ext{schema-constructor warrant}.
]

Held-out instances depend on that promoted constructor warrant.

## Controls

Qualification requires:

- exact current-meta-language stagnation before every concrete extension;
- the generic synthesizer receives no target relation;
- exactly two generic synthesis calls;
- exactly two held-out constructor instantiations;
- constructor promotion only after two structurally matching successes on
  distinct parameters;
- strict residual descent to zero;
- canonical restart preserves both concrete capabilities and induced schema;
- diagnostic sham changes nothing;
- revoking the first concrete warrant transitively removes the promoted
  constructor and every later dependent capability;
- trusted Nucleus blobs remain unchanged.

## Claim boundary

A positive result establishes **constructor genesis relative to a declared
generic grammar**:

> Metatron can synthesize concrete residual-closing programs, recognize a
> repeated structural law, warrant a parameterized constructor not present in
> the current meta-language, and successfully reuse it on held-out parameters.

It does **not** establish unrestricted invention outside the generic program
grammar, self-invention of the grammar syntax, or universal induction of the
correct abstraction.
