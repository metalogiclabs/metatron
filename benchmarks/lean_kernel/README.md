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

V5 remained the external champion while V8, V9, V10 and then V11 carried only
frozen local proxy evidence. Local wins can replace the staged contender, but
cannot displace the external champion without a comparable external PMU run.

The staging controller therefore compressed the local sequence to one scarce
measurement target:

`V8 STAGE_FOR_EXTERNAL → V9 REPLACE_STAGED → V10 REPLACE_STAGED → V11 REPLACE_STAGED`.


### V11 external adjudication

V11's generated source is sealed by SHA-256
`a34c08cabd7e33982dd1fc9549cf4289589a6bcb25f769e7f1c60bf75659b24f`.
The originally requested workflow run `35654150065` was retried after the SAIR
quota reset, but attempt 2 stopped before evaluator creation because the saved
solution name already existed. The retry harness was changed only to make the
solution name unique; the generated V11 source hash stayed identical.

The successful external measurement is GitHub Actions run `35670542314`, job
`106565780348`, SAIR playground run `205`. It was accepted on the exact frozen
grouped-practice plan:

- P1:0 at n=14: 89,551,151 instructions
- P2:0 at n=22: 228,568,046 instructions
- P3:0 at n=32: 503,669,677 instructions

V11's comparable three-case total is **821,788,874** instructions versus V5's
**4,546,112,652**, a reduction of **3,724,323,778 instructions (81.9233%)**.
The two-tier controller therefore records `EXTERNAL_PROMOTE`: V11 becomes the
externally warranted champion.

This claim is deliberately narrow. The evidence is practice-only, non-official
and non-scoreable; it says only that V11 strictly improves V5 on this exact
metric/cohort/case plan. It is not an official leaderboard claim and is not an
external verdict on V12.


### V12 staging update

A second universal early-row identity is compiled into the local contender:

`partAux 2 m = m / 2 + 1`.

Partition V12 is universally proved and canonically accepted. Its frozen local
replay total is 0.206662600s, down from V11's 0.249743756s (17.2501% lower).
After V11's external promotion, V12 remains the sole staged local contender and
next external-measurement candidate. No external performance claim is made for
V12 until it is measured on the same frozen boundary.
