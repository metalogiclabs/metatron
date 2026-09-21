# Lean Kernel external residual adapter

This benchmark adapter is Metatron's first serious external wedge. It does not
turn the SAIR leaderboard into an oracle of truth and it never compares unlike
evaluation cohorts as though they were the same score.

The protected development consequence is externally measured kernel-replay
instruction cost **after** universal proof and canonical acceptance.

The first sealed trace is Partition V4→V7:

- V4 and V5 have comparable SAIR playground PMU measurements on the exact same
  deterministic practice plan (n=14,22,32). V5 strictly improves V4 by
  15.0842845%, so it is the protected externally measured champion.
- V6 is universally proved and canonically accepted, but regresses on the
  frozen local proxy. Its SAIR run request hit HTTP 429 before an evaluator run
  was created, so no external verdict is fabricated.
- V7 is universally proved and canonically accepted, but strongly regresses on
  the frozen local proxy and is rejected before spending scarce external
  measurement budget.
- The public leaderboard total is retained only as a qualitative frontier
  signal because it is not the same practice cohort/case plan.

This is the intended developmental discipline:

`verify -> compare like with like -> promote/reject -> retain the residual`.


## Two-tier external staging

The second Partition trace (V8→V10) exposed a necessary distinction between
an **externally warranted champion** and a **locally qualified contender**.

V5 remains the external champion because it is the newest candidate with a
comparable frozen SAIR PMU measurement. V8, V9, and V10 are all universally
proved and canonically accepted, but currently carry only the frozen local
wall-time proxy. They therefore cannot displace V5 externally.

The staging controller collapses the three local wins into one measurement
request:

`V8 STAGE_FOR_EXTERNAL → V9 REPLACE_STAGED → V10 REPLACE_STAGED`.

Thus only V10 should consume the next scarce external PMU run.


### V11 staging update

The universal part-size-1 identity was promoted into the local representation:

`partAux 1 m = 1`.

Partition V11 is universally proved and canonically accepted and reduces the
frozen local replay total from V10's 0.282958007s to 0.249743756s. This is
local proxy evidence only, so V5 remains the external PMU champion while V11
replaces V10 as the sole staged external-measurement contender.


### V12 staging update

A second universal early-row identity is now compiled into the local contender:

`partAux 2 m = m / 2 + 1`.

Partition V12 is universally proved and canonically accepted. Its frozen local
replay total is 0.206662600s, down from V11's 0.249743756s (17.2501% lower).
The external/local boundary is unchanged: V5 remains the external PMU champion,
while V12 replaces V11 as the sole staged external-measurement contender.
