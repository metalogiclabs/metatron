# Separating Hypergraph Prospective V2 — Pre-Registration

**Frozen before reading target experiment contents.**

## Source freeze

Repository: `heathsanchez/test`  
Commit: `17c5109577fb8b500b69a02f1bc9c81964c81ddd`

Two untouched target experiment families are selected from tree metadata only:

1. `experiments/predictive_causal_state_genesis_v12/`
   - `challenge_pack.py` blob `67e9678a535f88ce91f861cd41a4b4da408ab3d5`
   - `run.py` blob `7650c9a3d8aba8855da49579eebf3d8e89350cb2`
2. `experiments/residual_generated_transformation_language_v21/`
   - `challenge_pack.py` blob `c66042c1d984007eca04d2810b152c52dd58cbf8`
   - `run.py` blob `8418e0deddc988ef0efd3f2f27ef052f64ebce3c`

No content from these experiment files has been read in this V2 test before this
pre-registration commit.

## Frozen diagnostic

For every eligible target world:

1. use only the source's already-declared finite state/challenge objects;
2. use only the source's already-declared finite candidate query/action/generator
   language;
3. define the consequential residual as held-out distinctions/failures that the
   source's exact verifier says must be resolved;
4. for every candidate, compute exact residual coverage without using the
   historical successful choice/order as a ranking feature;
5. compute maximum coverage, greedy cover, and exact minimum cover where
   exhaustive search is tractable.

## Eligibility

A target is eligible iff the frozen source exposes:
- a finite held-out residual/challenge set;
- a finite candidate query/action/generator language;
- an exact deterministic success/separation predicate.

If one target lacks these three ingredients, it is reported `INELIGIBLE`,
not silently reformulated. At least one of the two frozen targets must be
eligible for V2 to yield a scientific verdict.

## Frozen gates

For each eligible target:

G1. Exact cover resolves every nonpermanent/solvable held-out residual.

G2. Exact cover produces no false resolution on permanent/negative controls
when the source supplies such controls.

G3. Greedy cover has the same cardinality as the exact minimum cover, or is
explicitly reported as larger; no success is awarded merely for greedy.

G4. The first maximum-coverage equivalence class contains at least one
candidate that is independently accepted by the source's held-out verifier.

G5. If the source records a historical/baseline search length, exact minimum
cover must use strictly fewer selections to count as a compression win.
Absence of such a baseline is reported `NO_BASELINE` and does not fabricate a
compression claim.

## Overall verdict

- `POSITIVE_PROSPECTIVE_SIGNAL`: at least one eligible target passes G1-G4,
  no eligible target violates G1/G2, and every stated compression claim passes G5.
- `MIXED_PROSPECTIVE_SIGNAL`: at least one eligible target passes but another
  eligible target fails a non-safety predictive gate.
- `NEGATIVE_PROSPECTIVE_SIGNAL`: an eligible target fails exact resolution or
  creates a false positive on supplied controls.
- `NO_ELIGIBLE_TARGET`: neither source exposes the frozen finite interface.

No gate or target may be replaced after source contents are opened.
