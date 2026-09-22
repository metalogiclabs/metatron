# Separating Hypergraph Blind Prospective V3 — Pre-Registration

**Frozen before any V3 hidden challenge exists.**

## Objective

Run a genuine commit–predict–reveal experiment on a brand-new finite hidden world.

The hidden challenge is generated inside GitHub Actions after this pre-registration
is committed. The prediction job never downloads the hidden artifact.

## Hidden generator

The challenge generator must:

1. sample a fresh random anonymous 6-bit carrier and random relabelling;
2. expose 64 anonymous states only through integer IDs;
3. choose one protected Boolean observation;
4. choose three additional hidden Boolean observations that are linearly
   independent modulo the protected observation;
5. define the target future quotient from the protected observation plus those
   three hidden observations;
6. expose an anonymous candidate generator language containing every nonzero
   linear Boolean observation plus random decoys, with candidate names shuffled;
7. reject/resample decoys until:
   - no singleton candidate closes the target residual;
   - no pair of candidates closes the target residual;
   - the planted three-generator set closes it exactly.

The hidden artifact contains the latent coordinate masks, planted anonymous
candidate IDs, random seed material, and the canonical hidden answer.

The public artifact contains only:

- anonymous state IDs;
- the currently protected outcome;
- the target future-equivalence class ID of each state;
- anonymous candidate outcome vectors;
- a SHA-256 commitment to the hidden artifact.

No latent coordinates or planted candidate IDs may appear in the public artifact.

## Consequential residual

The prediction job must construct

[
U=\{\{x,y\}:P(x)=P(y)\land T(x)\ne T(y)\},
]

where (P) is the public current protected signature and (T) is the public
target future quotient.

For each anonymous candidate (g), its hyperedge is

[
E_g=\{\{x,y\}\in U:g(x)\ne g(y)\}.
]

## Frozen prediction rule

Using public data only:

1. compute all candidate coverages;
2. compute the exact minimum set-cover cardinality (	au);
3. emit the lexicographically canonical exact minimum cover;
4. emit greedy maximum-residual-coverage cover independently;
5. emit the full count of exact minimum covers;
6. cryptographically bind the prediction to the public challenge digest.

No target-specific tuning is allowed after generation.

## Reveal gates

R1. The hidden artifact matches the public SHA-256 commitment.

R2. The planted hidden generator set closes every public consequential residual.

R3. The predictor's exact minimum cardinality equals the true minimum and equals
the planted cardinality 3.

R4. The predictor's selected exact cover closes all residuals.

R5. No candidate subset of cardinality 0, 1, or 2 closes the residual.

R6. The planted hidden set is among the exact minimum-cover family.

R7. Greedy is reported separately; it passes only if its cardinality equals the
exact minimum. A greedy miss does not invalidate exact prediction but is
recorded as a search-policy failure.

R8. All public state relabellings preserve (	au) and the number of exact
minimum covers on a fixed deterministic relabelling control.

## Verdict

- `BLIND_PROSPECTIVE_PASS`: R1–R6 and R8 pass.
- `BLIND_PROSPECTIVE_PASS_GREEDY_MISS`: R1–R6 and R8 pass but R7 fails.
- `BLIND_PROSPECTIVE_FAIL`: any of R1–R6 or R8 fails.

This experiment tests blind finite generator selection inside a declared
candidate language. It does not claim open-ended invention beyond that language.
