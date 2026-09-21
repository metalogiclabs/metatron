import Metatron.Fixture

open Metatron

#check base_cannot_solve_step
#check step_idempotent
#check q0_merges_one_two
#check q1_separates_one_two
#check step_commutes_q0
#check compiled_step_exact
#check revoked_step_denied

example : step State.zero = State.one := rfl
example : projectQ0 State.one = projectQ0 State.two := rfl
example : execInstr Instr.step State.two = State.two := rfl
