# Metatron Constitutional Closure V1

**Status:** qualification boundary  
**Branch:** \`metatron-constitutional-closure-v1\`

This checkpoint freezes Metatron's architecture at four constitutional objects:

\[
F,\qquad \Gamma_t,\qquad N_t,\qquad \mathcal D_F.
\]

- \(F\): frozen trust/food substrate.
- \(\Gamma_t\): append-only certified lineage.
- \(N_t\): current minimal warranted consequential state derived from \(\Gamma_t\).
- \(\mathcal D_F\): frozen developmental constitution governing lawful change.

The trusted runtime remains smaller than this vocabulary. Its sole authoritative
state is an immutable warrant log:

\`\`\`text
Log = tuple[Node, ...]
append(Log, Node) -> Log
\`\`\`

Everything else is a derived view or an external policy.

## Named developmental events

These names do not add runtime types.

### Nucleus

\[
N_t = \operatorname{Min}_{Q_t,W_t}\bigl(\operatorname{Cl}(\Gamma_t)\bigr).
\]

Nucleus is the current warranted normal form: exactly the distinctions and
capabilities that remain consequential under lawful protected continuations.

### Nebula

Nebula is the developmental dynamics that expose an exact residual and search
the frozen admissible possibility space. It is policy over warranted state, not
trusted runtime authority.

### Aha

For residual \(\rho_i\), Nucleus \(N_i\), and the frozen admissibility order:

\[
\operatorname{Aha}_i
=
\min\left\{
K_i :
K_i \models_F \mathcal D_F
\land
\operatorname{resolves}_F(K_i,\rho_i,N_i)
\right\}.
\]

"min" means first certified admissible realizer under the frozen experimental
order, not a claim of globally unique mathematical minimality.

Aha is the certified click where failure becomes reusable structure.

### Genesis

Genesis is lawful installation of the warranted realizer. A Genesis event
changes the active warranted normal form:

\[
N_i \not\cong N_{i+1}.
\]

Thus the causal cycle is:

\[
N_i
\xrightarrow{\mathrm{Nebula}}
\rho_i
\xrightarrow{\mathrm{Aha}_i}
K_i
\xrightarrow{\mathrm{Genesis}_i}
N_{i+1}.
\]

## Sustained Nebula ignition

Sustained ignition is not another subsystem. It is a qualification property:

\[
N_i
\Rightarrow
(\rho_i,K_i)
\Rightarrow
N_{i+1}
\Rightarrow
(\rho_{i+1},K_{i+1})
\]

under frozen \(F\) and frozen \(\mathcal D_F\).

The next pressure and the next means must both be newly available:

\[
\rho_{i+1}
\in
\operatorname{DetectCl}_F(N_{i+1})
\setminus
\operatorname{DetectCl}_F(N_i),
\]

\[
K_{i+1}
\in
\operatorname{ExecCl}_F(N_{i+1})
\setminus
\operatorname{ExecCl}_F(N_i).
\]

The bounded three-generation certificate is:

\[
G_1
\xRightarrow{\rho_2,K_2}
G_2
\xRightarrow{\rho_3,K_3}
G_3.
\]

Every arrow must carry novelty witnesses and the global controls:

\`\`\`text
WITHHOLDING | KNOCKOUT | SEMANTIC_SHAM | RESTART
SEALED_SEMANTICS=IDENTICAL
\`\`\`

## V41 boundary

The real-lineage V41 experiment in \`metalogiclabs/mathgraph-lean-kernel\` is
external evidence. No V41 result is promoted into Metatron's trusted runtime
until its causal certificate exists and passes its own qualification gate.

A positive V41 result may enter Metatron only as warranted lineage/evidence.
It does not justify adding Nebula, Aha, Genesis, residual families, constructors,
search policy, benchmark logic, or domain-specific semantics to the nucleus.

## Exact implementation qualification

The constitutional implementation is the pure immutable warrant-log runtime.
The qualification workflow pins its implementation SHA, verifies that all later
closure commits leave the runtime/formal semantics unchanged, and runs:

- exhaustive five-node DAG / revocation qualification;
- Python/Lean differential live-log semantics;
- canonical replay and tamper rejection;
- full retained test suite;
- Lean-core build with no proof placeholders;
- the 120 semantic-line hard budget.

This checkpoint adds no architectural layer beneath Nebula and no new trusted
runtime concept.
