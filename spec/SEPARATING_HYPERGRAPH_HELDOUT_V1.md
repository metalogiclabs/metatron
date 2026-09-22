# Separating Hypergraph Held-Out V1

**Status:** retrospective held-out diagnostic  
**Branch:** `separating-hypergraph-heldout-v1`

## Purpose

V0 established on the retained three-state fixture that future-closed candidate
observations form a useful separating hypergraph. V1 asks the harder question:

> Given only the state before a historically successful acquisition, does exact
> residual coverage point toward the capability family that later closed the
> residual?

The historical data are copied semantically from frozen experiments in
`heathsanchez/test` at commit
`17c5109577fb8b500b69a02f1bc9c81964c81ddd`.

Source blobs are pinned in the executable report.

## Critical correction: consequential residual, not raw identity defect

A naive universe containing every pair still identified by the current quotient
is wrong in larger worlds: some currently identified pairs differ only in
presentation coordinates that the active future does not care about.

V1 therefore uses

[
U(P,T)=\{\{x,y\}:x\equiv_P y\ \land\
\exists t\in T, t(x)\ne t(y)\},
]

where `T` is the frozen held-out consequential family.

This counts only distinctions the future actually demands.

## Historical fixture A — Minimal Core Future Equivalence V1

The frozen 16-state world contains two semantic bits and a four-valued
presentation coordinate.

### Stage 1

With only `c0` present, the regime-1 consequential residual contains 32 pairs.

Candidate residual coverage is:

- `c1`: 32/32;
- `h0`: 32/32;
- `h1`: 16/32;
- `h2`: 16/32;
- `d0`: 16/32;
- `d1`: 16/32.

The historical acquisition was `c1`. It lies in the maximum-cover
behavioral class `{c1,h0}`, and one generator closes the entire consequential
residual.

### Stage 2

After `c0,c1`, the regime change makes presentation parity consequential.
The residual contains 16 pairs.

- `d0`: 16/16;
- `d1`: 16/16;
- `h0,h1,h2`: 0/16.

The historical acquisition was `d0`; again it lies in the maximum-cover
behavioral class, and one generator closes the residual.

The tie is informative rather than a failure: the hypergraph predicts a
behavioral capability class, not a privileged syntactic representative.

## Historical fixture B — Minimal Core Induced Residual History V14

V14 has:

- eight anonymous states;
- six held-out nonpermanent partition-transition residuals;
- two permanent `A=B` controls;
- 256 possible Boolean continuation queries.

The original learned history required 10 attempted queries, of which three
actually split new held-out residuals: `12, 85, 105`.

The exact separating hypergraph over the same frozen query language finds:

- maximum one-query coverage: 4/6, attained by complementary queries
  `15` and `240`;
- exact minimum cover size: 2;
- lexicographically canonical exact/greedy cover: `[15,105]`;
- all six nonpermanent residuals resolved;
- zero false splits on the permanent controls.

Thus the exact residual hypergraph compresses the historical search from 10
attempted queries (three successful split queries) to two diagnostic queries.

## Interpretation

This is the first evidence beyond the toy fixture that the construction can
recover **missing behavioral capability classes** and can compress a historical
held-out search.

It also falsifies the over-broad raw-pair defect. The correct object is the
**future-demanded consequential residual**.

## Claim boundary

This remains retrospective and finite. The candidate languages already exist in
the frozen historical experiments. It does not establish open-ended invention
of a new observation language, nor prospective performance on a genuinely
unseen domain. The next gate is prospective pre-registration: freeze a larger
world and candidate generator language before revealing the held-out residual
closures, then test whether hypergraph ranking predicts them.
