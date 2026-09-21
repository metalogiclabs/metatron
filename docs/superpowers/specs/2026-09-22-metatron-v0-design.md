# Metatron V0 — Clean Integration Design Specification

**Status:** Draft for user review  
**Repository:** \`metalogiclabs/metatron\`  
**Primary aim:** make Metatron the clean integration target for the proof-carrying developmental computer programme, while preserving the historical repositories as evidence and provenance rather than rewriting them.

## 1. Role of Metatron

Metatron is the place where the programme is rebuilt as if we were starting today with the benefit of the experiments, proofs, failures, and architectural corrections already learned.

It is **not** another experimental dumping ground.

The repository exists to integrate qualified mechanisms into one minimal developmental computer whose growth, compression, memory, and executable vocabulary are constrained by proof.

The product description is:

\[
\boxed{\textbf{Metatron — a proof-carrying developmental computer.}}
\]

## 2. Constitution

The governing rule is:

\[
\boxed{
\textbf{Never add structure merely because it is imaginable.
Add it only when the current system is certified insufficient.}
}
\]

The integrated mathematical core is:

\[
\boxed{
\begin{gathered}
\textbf{Residuals earn generators.}\\
\textbf{Warrant earns relations.}\\
\textbf{Free completion supplies consequences.}\\
\textbf{Quotient removes irrelevant distinctions.}\\
\textbf{Compilation turns the resulting presentation into executable capability.}
\end{gathered}
}
\]

This constitution is stronger than an informal preference for minimalism. Every new structural concept must have an explicit obstruction that requires it, a positive theorem or verified contract, a falsifier, and an ablation.

## 3. Ground zero

The minimal generative hypothesis is:

\[
\mathcal N=(R,\Delta),
\]

interpreted as directed generator data:

\[
G=(V,E,s,t).
\]

- \(V\): explicit references;
- \(E\): directed distinctions;
- \(s,t:E\to V\): endpoint incidence.

No initial assumption is made that references are propositions, programs, states, objects, people, or persistent substances.

No separate primitive assumption is made for identities, composition, or associativity.

Those arise by free categorical completion:

\[
\boxed{G\longmapsto F(G).}
\]

Reference + Directed Difference therefore supplies the underlying generating quiver, not a complete ontology.

## 4. Development law

The integrated developmental rule is:

\[
\boxed{
L_{t+1}
=
\operatorname{WarrantedQuotient}_{\Omega_t}
\left(
\operatorname{FreeExtend}(L_t,\rho_t)
\right).
}
\]

The intended sequence is:

\[
\boxed{
\text{exact obstruction}
\to
\text{least free extension}
\to
\text{independent verification}
\to
\text{greatest safe quotient}
\to
\text{compiled executable form}.
}
\]

A residual does not justify arbitrary redesign. It justifies the least new generator or attachment required to remove the certified obstruction.

An equation does not enter the active presentation because it is convenient. It enters only when warrant establishes the corresponding identification.

## 5. Search exhaustion is not insufficiency

Metatron must distinguish:

\[
\boxed{\text{search stopped}\neq\text{language insufficient}.}
\]

Timeout, budget exhaustion, heuristic failure, unavailable compute, or implementation failure must not be promoted into structural-growth certificates.

Growth requires an accepted no-resolution or incompleteness certificate under a frozen search/verifier contract.

If several minimal admissible repairs remain unresolved, Metatron returns:

\[
\boxed{\texttt{UNKNOWN\_CHOICE}}
\]

rather than inventing a narrative of inevitability.

## 6. Forced development

“Forced” is used only relative to a declared contract.

A structural extension is forced when:

1. the current presentation is certified inadequate;
2. the extension removes the certified obstruction;
3. the verifier accepts it;
4. the extension is universal/minimal under the declared structural order;
5. no unresolved tie remains.

Structural minimality and implementation cost are separate.

Universal constructions decide what abstract structure must be added.

Runtime cost, trusted-base size, or other frozen metrics select among concrete implementations of that structure.

## 7. History and active cognition

Metatron has two radically different stores.

### Immutable certified lineage

\[
\Gamma_t
=
\text{events}
+\text{certificates}
+\text{dependencies}
+\text{authority snapshots}
+\text{revocations}
+\text{provenance}
+\text{promotion lineage}.
\]

History is append-only or explicitly superseded. It is not silently rewritten because the active representation changed.

### Active consequential state

\[
\boxed{
M_t=\Pi_{Q_t,\Omega_t}(\Gamma_t).
}
\]

This is the minimum currently warranted operational projection needed for protected queries, executable capabilities, active support, current repair rules, and the active quotient/presentation.

The operational principle is:

\[
\boxed{\textbf{remember deep; execute shallow}.}
\]

## 8. Machine state

Conceptually:

\[
\boxed{
\mathcal S_t=
(\Gamma_t,P_t,M_t,\Omega_t,L_t).
}
\]

Where:

- \(\Gamma_t\): certified lineage/evidence;
- \(P_t\): current warranted presentation of generators and relations;
- \(M_t\): active minimum sufficient state;
- \(\Omega_t\): authority/verifier snapshot;
- \(L_t\): current executable capability language.

The accumulated generated capability structure may grow monotonically, while the active executable language need not. It may grow, collapse, recompile, revoke, split, or regrow.

## 9. Tiny trusted operations

The trusted runtime target is:

\[
\boxed{
\operatorname{Observe},
\operatorname{Execute},
\operatorname{Verify},
\operatorname{Promote},
\operatorname{Revoke},
\operatorname{Project}.
}
\]

Derived operations should include:

- Grow = Promote + free completion;
- Dissolve = Project + warranted congruence;
- Regrow = newly certified distinction invalidating a prior active quotient;
- Reclose = dependency propagation after new verified consequence.

Execution returns:

\[
\boxed{
(\mathcal S,P)
\longrightarrow
(\mathcal S',v,\kappa,\rho).
}
\]

with result \(v\), warrant \(\kappa\), unresolved residual \(\rho\), and new developmental state \(\mathcal S'\).

## 10. Capability promotion

Verified reusable programs become executable capabilities:

\[
\operatorname{verify}(c)
\Rightarrow
\operatorname{promote}(c).
\]

The promoted capability must retain a transparent expansion or certified lineage to the trusted substrate.

The target is:

\[
\boxed{
\text{deep proof lineage}
+
\text{shallow executable call}.
}
\]

Metatron should never require the full discovery history to remain operational merely because the history remains auditable.

## 11. Query-relative quotient and regrowth

Compression is never generic similarity reduction.

For declared protected query language \(Q_t\):

\[
x\sim_{Q_t,\Omega_t}y
\]

only when every accepted protected future cannot distinguish them.

At path level:

\[
p\approx_{Q_t,\Omega_t}q
\]

only when every accepted continuation preserves protected observational equality.

When \(Q_t\) expands, a previous class may split.

That is lawful regrowth:

\[
\boxed{
\text{compress while safe;
restore distinction when newly consequential}.
}
\]

## 12. Nonlinear lineage and reclosure

Metatron must support:

- one-to-many development;
- many-to-one recombination;
- many-to-many restructuring;
- alternative and conjunctive support;
- dormant alternatives;
- revocation;
- system-wide dependent reclosure.

The history graph and active executable presentation are not the same object.

This is where CLC, RealityGraph, and Flash contribute distinct mechanisms rather than competing top-level ontologies.

## 13. Qualification rule for abstractions

Every promoted abstraction requires:

\[
\boxed{
\text{positive theorem}
+
\text{negative fixture}
+
\text{ablation}.
}
\]

Examples include future separation, spurious path creation, joint-support failure, capability knockout, wrong-authority refusal, and fresh-arrow versus ambient-arrow controls.

An abstraction without a falsifier does not enter the constitutional core.

## 14. Convergence

Metatron does not converge because its own representations increasingly agree with one another.

Convergence is external:

\[
\boxed{\rho_{t+1}<\rho_t}
\]

under independent protected tests and a frozen residual order.

Useful signals include fewer unresolved protected cases, lower verified execution cost, smaller active state, greater held-out reuse, more exact prediction, perturbation survival, and successful independent verification.

## 15. Lean and runtime boundary

Lean defines the reference laws.

The production runtime is replaceable.

\[
\boxed{
\text{Lean reference semantics}
\leftrightarrow
\text{portable executable runtime}.
}
\]

Python remains acceptable for synthesis and experiments.

A later production runtime may use Rust or another implementation language, but V0 does not commit to one before the reference semantics are fixed.

Every runtime implementation must eventually satisfy differential tests:

\[
\operatorname{run}_{Lean}(x)
=
\operatorname{run}_{runtime}(x).
\]

## 16. Initial repository shape

The intended repository shape is:

\`\`\`text
spec/
  CONSTITUTION.md
  CLAIM_BOUNDARY.md

formal/Metatron/
  Quiver.lean
  Free.lean
  Warrant.lean
  Congruence.lean
  Nucleus.lean
  Residual.lean
  Quotient.lean
  Transport.lean
  Lineage.lean
  Support.lean
  Flash.lean
  Growth.lean
  Runtime.lean

runtime/
  core/
  verifier/
  executor/
  compiler/
  memory/

language/
  ast/
  parser/
  repl/
  stdlib/

memory/
  mg/

fixtures/
  future-separation/
  spurious-path/
  factorisation/
  revocation/
  ablation/

benchmarks/
  boolean/
  finite-state/
  lean/
  coding/

evidence/
  manifests/
  qualified-runs/
  hashes/

docs/superpowers/
  specs/
  plans/
\`\`\`

This layout is a target, not permission to scaffold everything immediately.

V0 should create only the directories/files required by the first complete lifecycle.

## 17. Historical repos remain authoritative provenance

Metatron integrates, but does not rewrite, the history.

Existing repos remain authoritative for the experiments and theorem developments that occurred there.

The initial evidence manifest should point to exact repo, branch, commit, workflow run, artifact/hash, and claim boundary for every imported dependency.

Primary source repos include:

- \`heathsanchez/Minimal-Sufficient-Interface\`;
- \`heathsanchez/triskelion\`;
- \`heathsanchez/realitygraph\`;
- \`metalogiclabs/mathgraph-lean-kernel\`;
- \`metalogiclabs/mathgraph\`;
- \`heathsanchez/lean-kernel-arena\`;
- \`heathsanchez/test\`.

Metatron must not copy claims forward without their qualification status.

## 18. Dependency classes

Every imported dependency is tagged as one of:

- **QUALIFIED** — exact formal/experimental gate has passed;
- **PARTIAL** — useful result with known failed gates;
- **PENDING** — active work not yet qualified;
- **HISTORICAL** — retained for provenance but not relied upon by V0;
- **CONJECTURAL** — design target or theorem programme, not established.

This status belongs in machine-readable evidence metadata as well as human-facing documentation.

## 19. Initial dependency status

The first manifest should include at minimum:

### QUALIFIED

CLC Nonlinear Lineage V0:
- repo: \`heathsanchez/Minimal-Sufficient-Interface\`;
- branch: \`clc-nonlinear-lineage-v0\`;
- qualified head: \`900a73c1d386ee0eee1205a1cf31d270f3311ef7\`;
- capstone: \`grow_dissolve_preserves_protected_queries\`.

Existing MSI theorem packages:
- \`TypedBehaviouralCongruence.lean\`;
- \`DevelopmentalCategory.lean\`;
- \`GeneratedStage.lean\`;
- \`MinimalRepair.lean\`.

### PENDING

Nucleus Universal Property V0:
- repo: \`heathsanchez/Minimal-Sufficient-Interface\`;
- branch: \`nucleus-universal-property-v0\`;
- qualification must not be upgraded until its dedicated final gate is green.

### DESIGN TARGET

Proof-Carrying Developmental Computer V0:
- source design branch: \`proof-carrying-developmental-computer-v0\`;
- this Metatron spec supersedes the repository-location aspect while preserving the architecture.

## 20. V0 stopping point

Metatron V0 is one complete executable developmental lifecycle, not the entire research programme.

The capstone must demonstrate:

\[
\boxed{
\begin{aligned}
&\text{frozen tiny substrate}\\
&\to\text{provably insufficient task}\\
&\to\text{exact obstruction}\\
&\to\text{fresh/free extension}\\
&\to\text{independent verification}\\
&\to\text{promotion}\\
&\to\text{reuse}\\
&\to\text{serialization}\\
&\to\text{restart}\\
&\to\text{warranted compression}\\
&\to\text{same protected answer}\\
&\to\text{new protected query}\\
&\to\text{regrowth/refinement}.
\end{aligned}
}
\]

No hidden generation-specific dispatch is permitted.

## 21. V0 capstone contracts

For a promoted capability \(c\):

\[
\boxed{
\operatorname{expand}(\operatorname{compiled}(c))
\equiv c.
}
\]

For protected query \(Q\) and compatible finite trace \(T\):

\[
\boxed{
\operatorname{Eval}_{\Gamma}
(Q,\operatorname{Develop}(\Gamma,T))
=
\operatorname{Eval}_{M}
(Q,\operatorname{Develop}(M,\Pi(T))).
}
\]

And the integrated executable target is:

\[
\boxed{
\operatorname{Eval}_{full}
=
\operatorname{Eval}_{compiled+quotiented}
}
\]

across promotion, restart, revocation, nonlinear growth, dissolution, and regrowth in the finite V0 fixture.

## 22. First external wedges

After the synthetic V0 lifecycle is qualified, the first serious domains are:

\[
\boxed{\text{formal mathematics}}
\qquad
\boxed{\text{software/code transformation}}.
\]

Both provide hard external verifiers.

For mathematics:

\[
\text{solve}
\to
\text{kernel verify}
\to
\text{compile lesson}
\to
\text{reuse}.
\]

For code:

\[
\text{repair}
\to
\text{test/formal verify}
\to
\text{compile transformation}
\to
\text{reuse}.
\]

## 23. Explicit non-goals

V0 does not establish:

- unrestricted self-improvement;
- arbitrary real-world ontology discovery;
- automatic discovery of correct residual endpoints;
- universal existence of a unique useful repair;
- completeness of locally earned equations for full behavioural equivalence;
- infinite/open-ended productivity;
- a metaphysics of identity;
- that every useful abstraction is categorical;
- a canonical production runtime language.

## 24. Deferred V1 theorem programmes

The following remain explicitly outside V0:

\[
\boxed{\texttt{generatedCongruence\_eq\_pathBehEq}}
\]

for completeness of the earned equation basis, and

\[
\boxed{\texttt{residualAdjoin\_strictLyapunov}}
\]

for strict potential descent after a genuinely separating fresh residual extension.

Also deferred:

- new-object attachment;
- multiple simultaneous generators;
- computads/polygraphs;
- higher categorical cells.

## 25. Initial seed files after spec approval

After this written spec is reviewed and approved, the implementation plan should begin with the smallest documentation/evidence seed:

1. \`README.md\` — concrete public description: “Metatron — a proof-carrying developmental computer.”
2. \`spec/CONSTITUTION.md\` — normative rules only.
3. \`spec/CLAIM_BOUNDARY.md\` — qualified / partial / pending / conjectural claims.
4. \`evidence/manifests/dependencies.yaml\` — exact repo/branch/commit/run/hash/status pointers.
5. only then the minimum formal/runtime files required for the first V0 lifecycle.

The historical repos are referenced, not bulk-copied.

## 26. Success criterion for the clean repo

Metatron succeeds as a clean integration repo only if a new reader can answer, from the repository alone:

- What is trusted?
- What is generated?
- What is warranted?
- What is merely active?
- What is historical?
- What is formally proved?
- What is experimentally supported?
- What is still conjectural?
- What exact external evidence supports each imported claim?
- What obstruction forced each structural addition?

If those answers become ambiguous, the repo is drifting back into an ontology-first architecture.

## 27. Build principle

\[
\boxed{
\begin{gathered}
\textbf{Start with the weakest executable distinction.}\\
\textbf{Let exact failure force every generator enlargement.}\\
\textbf{Let warrant earn every relation.}\\
\textbf{Promote only independently verified consequence.}\\
\textbf{Preserve every distinction a lawful future can still expose.}\\
\textbf{Collapse everything else.}\\
\textbf{Keep history for warrant, not for execution.}\\
\textbf{Let new consequence reclose the active present globally.}\\
\textbf{When compression becomes insufficient, regrow—not guess.}
\end{gathered}
}
\]
