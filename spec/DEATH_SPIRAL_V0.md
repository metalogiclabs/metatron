# Death Spiral V0

## Objective

Formalize the smallest exact claim extracted from the supplied AHQ death-spiral analogy:

> reducing the available action family can convert a previously escapable region into a closed recurrent trap.

This is a finite dynamical-systems theorem about action restriction, reachability and closed recurrence. It is not a theorem about consciousness, ants in general, agency, or psychological states.

## Generic law

For an action system act : Action -> State -> State, an available action list A, and a region R:

- ClosedUnder act A R means every available action preserves R.
- If a trajectory is in R and every future step is drawn from A, it remains in R.
- RestrictionCreatesTrap act full restricted R means R is closed under the restricted family while some action available in the full family leaves R.

The theorem closedUnder_run proves forward invariance of a closed region under all allowed finite continuations.

## Finite witness

The fixture has four states:

    start, left, right, out

and two actions:

    follow, escape

follow:
    start -> left
    left  -> right
    right -> left
    out   -> out

escape:
    every state -> out

Full action family:
    {follow, escape}

Restricted family:
    {follow}

Trap region:
    {left, right}

Exact consequences:

- under the full family, left/right each have two distinct successors and escape to out exists;
- under restriction, each trap state has one successor;
- the restricted trap is closed;
- start is funneled into the trap in one step;
- left/right form a two-cycle;
- every allowed continuation from inside the trap remains trapped.

The finite census additionally verifies that full reachability from start includes all four states, while restricted reachability excludes out.

## Lean theorems

formal/Metatron/DeathSpiral.lean proves:

- closedUnder_run
- restricted_trap_closed
- restriction_creates_trap
- restricted_start_enters_trap
- restricted_two_cycle
- restricted_no_escape_after_entry
- finite_constraint_collapse_witness

## Verification boundary

If qualification passes, the warranted statement is only:

> In deterministic finite action systems, a region closed under a restricted action family remains invariant under all restricted finite continuations. The declared four-state fixture shows that removing an escape action can reduce branching and turn a formerly escapable two-state region into a closed recurrent two-cycle reached from the start.

This does not establish:

- that reduced branching always creates a trap;
- that every closed SCC is caused by lost freedom;
- a general entropy theorem;
- ant behavior outside the declared analogy;
- psychological, cognitive, social or consciousness claims.

## Programme relation

This adds a new operator to the existing quotient/feedback toolkit:

    action restriction
      -> smaller reachable transition relation
      -> possible loss of escape
      -> closed recurrent consequence class

It complements ResidualSynergy, feedback, temporal concentration and quotient falsification without adding new trusted-runtime authority.
