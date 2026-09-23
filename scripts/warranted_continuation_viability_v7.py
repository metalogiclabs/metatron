#!/usr/bin/env python3
from itertools import product

STATES = (
    "ready",
    "depleted",
    "unauthorized_ready",
    "unauthorized_depleted",
)
FAILURES = (0, 1)

LIVE = {
    "ready": (0,),
    "depleted": (0,),
    "unauthorized_ready": (),
    "unauthorized_depleted": (),
}
FUEL = {
    "ready": True,
    "depleted": False,
    "unauthorized_ready": True,
    "unauthorized_depleted": False,
}

def static_causal_cover(state):
    return LIVE[state] == (0,)

def contention_step(state, failure):
    if state == "ready" and failure in FAILURES:
        return "depleted"
    return None

def replenish_step(state, failure):
    if state == "ready" and failure in FAILURES:
        return "ready"
    return None

def predecessor(step, subset):
    subset=set(subset)
    out=set()
    for s in STATES:
        if all((nxt := step(s,f)) is not None and nxt in subset for f in FAILURES):
            out.add(s)
    return out

def kernel_chain(step):
    cur=set(STATES)
    chain=[set(cur)]
    while True:
        nxt=predecessor(step,cur)
        chain.append(set(nxt))
        if nxt == cur:
            return chain
        cur=nxt

def run(step, state, seq):
    cur=state
    for f in seq:
        cur=step(cur,f)
        if cur is None:
            return None
    return cur

def main():
    assert static_causal_cover("ready")
    assert static_causal_cover("depleted")
    assert not static_causal_cover("unauthorized_ready")
    no_replenish=kernel_chain(contention_step)
    replenished=kernel_chain(replenish_step)
    assert [len(x) for x in no_replenish] == [4,1,0,0]
    assert [len(x) for x in replenished] == [4,1,1]
    assert replenished[-1] == {"ready"}
    assert run(contention_step,"ready",(0,1)) is None
    assert run(contention_step,"ready",(1,0)) is None
    assert run(replenish_step,"ready",(0,1)) == "ready"
    assert run(replenish_step,"ready",(1,0)) == "ready"

    print("state_count=4")
    print("contention_kernel_chain=4,1,0,0")
    print("contention_kernel_size=0")
    print("replenished_kernel_chain=4,1,1")
    print("replenished_kernel=ready")
    print("schedule_01_without_replenishment=False")
    print("schedule_10_without_replenishment=False")
    print("schedule_01_with_replenishment=True")
    print("schedule_10_with_replenishment=True")
    print("WARRANTED_CONTINUATION_VIABILITY_V7=PASS")

if __name__ == "__main__":
    main()
