# Nebula Ignition V0

**Status:** executable experiment  
**Branch:** \`nebula-ignition-v0\`

Nebula Ignition is the next experiment after Nucleus Genesis.

Nucleus Genesis establishes:

\[
\boxed{
\text{the machine can lawfully change the representation in which it reasons}
}
\]

Nebula asks for the stronger event:

\[
\boxed{
\text{one warranted representational change makes the next obstruction
derivable without another semantic instruction}
}
\]

## Ignition criterion

Let \(\Gamma_i\) be the warranted state before generation \(i\), and let
\(o_i\) be its current exact obstruction.

A developmental generation is:

\[
\Gamma_i
\xrightarrow{o_i}
L_i
\xrightarrow{\kappa_i}
\Gamma_{i+1}.
\]

Nebula ignition requires the next obstruction to be newly derivable:

\[
\boxed{
o_{i+1}
\in
\operatorname{Derivable}(\Gamma_{i+1})
\setminus
\operatorname{Derivable}(\Gamma_i)
}
\]

The implementation must not preload the intermediate obstruction blocks,
queries, or generation schedule.

## One external perturbation

The unperturbed machine contains only:

- carrier states \(0,1,2,3,4\);
- the seed distinction \`is_0\`;
- exact quotient/reclosure;
- exact obstruction certification;
- a generic block-relative lift law;
- warrant, promotion, revocation, and causal dependency rules.

The sole external perturbation is:

\[
T=\text{singleton partition}.
\]

No caller supplies \`is_1\`, \`is_2\`, \`is_3\`, or the intermediate blocks.

At genesis the live quotient is

\[
\{\{0\},\{1,2,3,4\}\}.
\]

The unique active obstruction is therefore the non-singleton block
\(\{1,2,3,4\}\).

## Generic developmental law

For an exact unresolved block \(B\), V0 admits the minimal block-relative
distinction

\[
q_B(x)=[x=\min(B)].
\]

This is a generic law over the currently existing obstruction object. It does
not name any later state or generation in advance.

Promotion of \(q_B\) triggers reclosure. In the chosen five-state world this
creates the chain

\[
\begin{aligned}
\{\{0\},\{1,2,3,4\}\}
&\to
\{\{0\},\{1\},\{2,3,4\}\}\\
&\to
\{\{0\},\{1\},\{2\},\{3,4\}\}\\
&\to
\{\{0\},\{1\},\{2\},\{3\},\{4\}\}.
\end{aligned}
\]

Thus the obstruction objects

\[
\{2,3,4\}
\quad\text{and}\quad
\{3,4\}
\]

do not exist in the active quotient before the generations that create them.

## Exact potential

For partition \(P\), define

\[
D(P)=\sum_{B\in P}\max(0,|B|-1).
\]

The V0 ignition trace must satisfy exactly

\[
\boxed{3\to2\to1\to0}.
\]

This is a fixture-level descent result only; no general Lyapunov theorem is
claimed.

## Anti-cheating gates

### Future withholding

Before generation \(G_i\), the obstruction block produced by \(G_i\) must not
be certifiable from the current quotient.

### Causal knockout

Every learned warrant records the active prior learned warrants on which its
developmental episode depended.

Revoking \(G_1\) must transitively revoke \(G_2\) and \(G_3\), restoring the
coarse genesis quotient while preserving the lineage events.

### Ambiguous repair control

If the declared admissibility/cost contract has more than one equally minimal
repair, the selector returns \`UNKNOWN_CHOICE\` rather than choosing silently.

## Success gate

A qualifying run must obtain, from one call supplying only \(T\):

\[
\boxed{
G_1
\to
o_2
\to
G_2
\to
o_3
\to
G_3
\to
T
}
\]

with:

- three promotions;
- exact potential \(3,2,1,0\);
- pre-generation non-derivability of \(o_2\) and \(o_3\);
- causal parentage in the warrant graph;
- G1 knockout retracting all descendants;
- ambiguous repair failing closed.

## Claim boundary

Nebula Ignition V0 demonstrates self-propagating representational morphogenesis
inside one finite, deliberately constructed developmental world.

It does **not** establish open-ended self-improvement, arbitrary ontology
discovery, general unique repair, environmental autonomy, or a universal
Nebula theorem.

The conceptual threshold is narrower:

\[
\boxed{
\text{a warranted change of representation creates the exact representational
condition from which the next developmental obstruction becomes derivable}
}
\]

Three generations are used so the result is a chain rather than a single
two-step coincidence.
