# CLC Monoidal / Deep Present V0

**Status:** theorem experiment  
**Branch:** `clc-monoidal-deep-present-v0`

This branch tests five consequences suggested by the recent CLC/Porter synthesis.

## 1. Parallel history tensor

The existing certificate trace is a flat ordered list. A naive tensor keeps
both traces by concatenation.

Lean first proves the expected trace projection, then tests interchange.

The result is negative for flat traces:

[
(f_1otimes f_2);(g_1otimes g_2)

eq
(f_1;g_1)otimes(f_2;g_2)
]

for a concrete four-certificate fixture. The state maps agree; only evidence
order differs.

This means flat lists are too strict to represent independent parallel history.

A concurrency-aware repair uses **layered traces**:

- outer list = causal stages;
- inner list = events treated as concurrent within a stage.

For synchronized one-step components, Lean proves exact serial/parallel
interchange.

A second falsifier then uses histories with different causal depths. Interchange
fails again even with layered traces. So global stage layers are sufficient for
the synchronized case but still too rigid for arbitrary asynchronous history.
The next candidate evidence object must preserve **partial order / independence**
rather than forcing every event into one total sequence of global layers.

## 2. Causal re-entry as feedback

A proof-relevant feedback operator is defined by existentially hiding a loop
state while requiring that the same loop state returns:

[
operatorname{Feedback}(E)(a,b)
=
sum_s E((a,s),(b,s)).
]

A finite fixture proves that a local false→true transition exists only through
a live loop state. This is the minimal traced/feedback witness.

## 3. Deep present as compatible cone

For protected languages

[
P_0subseteq P_1subseteq P_2
]

the previously proved forgetful maps give

[
Q_2	o Q_1	o Q_0.
]

`DeepCone3` packages a current fine view together with its compatible earlier
coarser views. `deepPresent_compatibleCone` proves every top-level view
canonically determines such a cone.

`deepPresent_direct_projection` proves that stepwise forgetting agrees with
direct forgetting.

This is a finite inverse-system model of a "deep present": one current state
carrying mutually compatible identities at several consequential depths.

## 4. Ostiary admission as Galois closure

For an observation family (S), define

[
operatorname{Cl}(S)=gamma(alpha(S)),
]

the observations constant on every current indistinguishability class.

Lean proves:

- extensivity;
- monotonicity;
- idempotence;
- exact preservation of the induced state boundary.

So the ostiary operator can be represented as a genuine Galois closure:
**admit every observation compatible with the current boundary, but do not
silently refine that boundary.**

## Interpretation

The experiment distinguishes three structures that should not be conflated:

1. serial causal composition;
2. parallel/concurrent integration;
3. feedback/re-entry.

Flat provenance lists are adequate for serial composition but fail monoidal
interchange. Concurrency-aware layers repair the simplest synchronized case,
but an asynchronous counterexample shows that layers are not the final
representation. The evidence semantics needs a finer notion of causal
independence, such as a partial-order/pomset-style trace or an equivalent
quotient by independent-event commutation.

The refinement tower supports a compatible-cone interpretation of temporal
depth, while the Galois closure supplies a mathematically exact candidate for
boundary-relative admission.

## Claim boundary

A green branch establishes only the theorem package above. It does **not** yet
establish:

- a general symmetric monoidal structure for arbitrary asynchronous histories;
- a quotient of layered histories by permutation/independence;
- full traced-monoidal axioms;
- an actual inverse limit over an infinite developmental tower;
- a monoidal bicategory/double category of full certificate-carrying CLC forms;
- empirical or ontological conclusions.
