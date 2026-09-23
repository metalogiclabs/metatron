# Residual-Generated Capability V0

**Status:** theorem + blind compositional synthesis experiment  
**Branch:** `residual-generated-capability-v0`

## Objective

Replace a supplied finite candidate list with a generative capability language.

The primitive data is now:

- reusable observation atoms;
- a constructor algebra;
- the current behavioral quotient;
- the target quotient.

Completed candidate observations are not primitive objects.

## Formal language

`ObsExpr Atom` is freely generated from atoms using XOR composition.

`ObsExpr.eval` gives its Boolean observation semantics.

`GeneratedCover` and `GeneratedMinimum` instantiate the existing residual
cover/sufficiency bridge at generated expressions rather than supplied
candidates.

Lean proves:

- `generatedCover_iff_targetSufficient`;
- `generatedMinimum_minimalSufficient`;
- `inventedA_recovers_hiddenA`;
- `inventedB_recovers_hiddenB`;
- `invented_pair_targetSufficient`;
- `invented_pair_covers`.

## Fixture

Reusable primitive observations expose:

- hiddenA XOR noise;
- hiddenB XOR noise;
- noise;
- visible.

The missing hidden observations are not supplied as candidates.

They are constructed:

[
hiddenA=(hiddenAoplus noise)oplus noise
]

and

[
hiddenB=(hiddenBoplus noise)oplus noise.
]

The generated pair is sufficient for the target relation.

## Blind test

The public challenge supplies only anonymous atoms and the XOR constructor.

The predictor must generate the extensional closure itself, then compare:

1. the minimum sufficient family made only from primitive atoms;
2. the minimum sufficient family from generated expressions.

The frozen fixture requires:

- primitive-only minimum acquisition size 3;
- no generated singleton sufficient;
- generated minimum acquisition size 2;
- minimum total constructor cost 2.

This establishes a strict representational gain from compositional invention.

## Interpretation

The search object becomes

[
	ext{residual}
	o
	ext{required observation semantics}
	o
	ext{free constructor completion}
	o
	ext{minimum sufficient generated basis}.
]

This is no longer “pick an unseen item from a larger list.” It is synthesis in a
declared algebra of reusable constructors.

## Claim boundary

The constructor algebra itself is still supplied. This experiment does not yet
invent new primitive constructors or prove unrestricted grammar growth.
