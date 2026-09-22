# Separating Obstruction Hypergraph V0

**Status:** derived finite diagnostic experiment  
**Branch:** `separating-obstruction-hypergraph-v0`

## Question

Can Metatron turn a continuation-safe behavioral quotient into an exact,
provenance-independent description of the *minimum missing distinguishing
information*?

This experiment uses the existing three-state Nucleus Genesis / Future
Observations fixture:

- states: `0, 1, 2`;
- lawful step: `0 -> 1, 1 -> 1, 2 -> 2`;
- tests: `IS_ZERO` and `IS_ONE`.

No new runtime authority is introduced.

## Construction

For a protected test language `P`, define the unresolved-pair universe

[
U(P) = \{\{x,y\}:x\neq y, x\equiv_P^\infty y\}.
]

The scalar finite defect is

[
D(P)=|U(P)|.
]

For each candidate base test `q`, close it under **all finite lawful
continuations** in the finite transition semigroup. Its hyperedge is the subset
of `U(P)` separated by at least one resulting future observation.

The exact minimum separating basis is the minimum set of candidate generators
whose hyperedges cover `U(P)`.

## Retained fixture result

The existing Future Observations partitions are reproduced exactly:

- protect nothing: all three unordered state pairs are unresolved;
- protect `IS_ZERO`: only `{1,2}` remains unresolved;
- protect `IS_ZERO` and `IS_ONE`: no pair remains unresolved.

Therefore the exact scalar defect follows

[
3 \to 1 \to 0.
]

More strongly, `IS_ONE` has two distinct future-observation signatures:

- immediate: `(false, true, false)`;
- after the lawful step: `(true, true, false)`.

Together those two consequences of **one generator** separate all three state
pairs. Thus the minimum basis from the empty protected language has size one:

[
3\ \text{pairwise residuals}
\quad\rightsquigarrow\quad
1\ \text{missing generator}.
]

At the retained `IS_ZERO` boundary, the exact remaining residual
`{1,2}` is also closed by the single missing generator `IS_ONE`.

## Canonicality gate

The experiment exhaustively checks all six relabelings of the three-state
carrier. The unresolved-pair count, minimum basis size, and hyperedge coverage
sizes are invariant under every relabeling.

Unlike the rejected raw-warrant spectral diagnostic, this construction reads
behavioral consequences rather than provenance shape.

## Claim boundary

This experiment establishes an exact finite derived diagnostic on the retained
fixture. It does **not** establish that:

- greedy maximum coverage predicts discoveries on larger domains;
- minimum set cover should become Nucleus authority;
- finite pair count is a universal scalar Lyapunov function for arbitrary
  infinite systems;
- the candidate observation language is complete in open-ended discovery.

The next gate is empirical: run the diagnostic retrospectively on larger
historical fixtures with withheld successful capability additions and test
whether coverage/minimum-basis structure predicts the additions that actually
worked.
