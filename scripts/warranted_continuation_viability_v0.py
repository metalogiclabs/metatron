from dataclasses import dataclass, replace
from enum import Enum

class Residual(str, Enum):
    ALPHA = "alpha"
    BETA = "beta"

class Outcome(str, Enum):
    REUSED = "reused"
    ACQUIRED = "acquired"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class State:
    budget_alpha: int
    budget_beta: int
    compiled_alpha: bool = False
    compiled_beta: bool = False
    live_alpha: bool = False
    live_beta: bool = False
    protected: bool = True

STREAM = (Residual.ALPHA, Residual.BETA, Residual.ALPHA, Residual.BETA)

def budget(s: State, r: Residual) -> int:
    return s.budget_alpha if r is Residual.ALPHA else s.budget_beta

def live(s: State, r: Residual) -> bool:
    return s.live_alpha if r is Residual.ALPHA else s.live_beta

def compile_repair(s: State, r: Residual) -> State:
    if r is Residual.ALPHA:
        return replace(s, budget_alpha=s.budget_alpha - 1, compiled_alpha=True)
    return replace(s, budget_beta=s.budget_beta - 1, compiled_beta=True)

def reclose(s: State) -> State:
    return replace(s, live_alpha=s.compiled_alpha, live_beta=s.compiled_beta)

def step(s: State, r: Residual):
    if live(s, r):
        return reclose(s), Outcome.REUSED
    if budget(s, r) > 0:
        return reclose(compile_repair(s, r)), Outcome.ACQUIRED
    return s, Outcome.UNKNOWN

def run(s: State, stream=STREAM):
    outcomes = []
    for r in stream:
        s, out = step(s, r)
        outcomes.append(out)
    return s, tuple(outcomes)

def objective_viable(outcomes):
    return Outcome.UNKNOWN not in outcomes

def scalar_summary(s: State, stream=STREAM):
    return (s.budget_alpha + s.budget_beta, len(stream))

def main():
    balanced = State(1, 1)
    skewed = State(2, 0)

    b_final, b_out = run(balanced)
    s_final, s_out = run(skewed)

    assert scalar_summary(balanced) == scalar_summary(skewed) == (2, 4)

    assert b_out == (
        Outcome.ACQUIRED,
        Outcome.ACQUIRED,
        Outcome.REUSED,
        Outcome.REUSED,
    )
    assert s_out == (
        Outcome.ACQUIRED,
        Outcome.UNKNOWN,
        Outcome.REUSED,
        Outcome.UNKNOWN,
    )

    assert objective_viable(b_out)
    assert not objective_viable(s_out)

    assert b_final.protected and s_final.protected
    assert b_final.live_alpha and b_final.live_beta
    assert s_final.live_alpha and not s_final.live_beta
    assert not s_final.compiled_beta

    print("WARRANTED_CONTINUATION_VIABILITY_V0=PASS")
    print(f"stream={tuple(x.value for x in STREAM)}")
    print(f"scalar_summary_balanced={scalar_summary(balanced)}")
    print(f"scalar_summary_skewed={scalar_summary(skewed)}")
    print(f"balanced_outcomes={tuple(x.value for x in b_out)}")
    print(f"skewed_outcomes={tuple(x.value for x in s_out)}")
    print(f"balanced_objective_viable={objective_viable(b_out)}")
    print(f"skewed_objective_viable={objective_viable(s_out)}")
    print(f"balanced_final={b_final}")
    print(f"skewed_final={s_final}")

if __name__ == "__main__":
    main()
