#!/usr/bin/env python3

STATES=(
    "auth0","auth1","auth2",
    "unauth0","unauth1","unauth2",
)
FAILURES=(0,1)
CAPACITY=2
REPLENISH=1

BALANCED={0:1,1:1}
SKEWED={0:0,1:2}

def balanced_step(state,f):
    if state=="auth1" and f in FAILURES:
        return "auth1"
    if state=="auth2" and f in FAILURES:
        return "auth2"
    return None

def skewed_step(state,f):
    table={
        ("auth0",0):"auth1",
        ("auth1",0):"auth2",
        ("auth2",0):"auth2",
        ("auth2",1):"auth1",
    }
    return table.get((state,f))

def predecessor(step,subset):
    subset=set(subset)
    return {
        s for s in STATES
        if all((n:=step(s,f)) is not None and n in subset for f in FAILURES)
    }

def chain(step):
    cur=set(STATES)
    out=[set(cur)]
    while True:
        nxt=predecessor(step,cur)
        out.append(set(nxt))
        if nxt==cur:
            return out
        cur=nxt

def run(step,state,seq):
    cur=state
    for f in seq:
        cur=step(cur,f)
        if cur is None:
            return None
    return cur

def main():
    assert sum(BALANCED.values()) == sum(SKEWED.values()) == 2
    assert len(FAILURES)==2
    assert sum(BALANCED.values())/len(FAILURES) == 1
    assert sum(SKEWED.values())/len(FAILURES) == 1

    balanced=chain(balanced_step)
    skewed=chain(skewed_step)
    assert [len(x) for x in balanced] == [6,2,2]
    assert balanced[-1] == {"auth1","auth2"}
    assert [len(x) for x in skewed] == [6,1,0,0]
    assert skewed[-1] == set()
    assert run(balanced_step,"auth2",(1,1)) == "auth2"
    assert run(skewed_step,"auth2",(1,1)) is None

    print("capacity=2")
    print("replenishment=1")
    print("balanced_costs=1,1")
    print("skewed_costs=0,2")
    print("balanced_average_cost=1")
    print("skewed_average_cost=1")
    print("balanced_kernel_chain=6,2,2")
    print("balanced_kernel=auth1,auth2")
    print("skewed_kernel_chain=6,1,0,0")
    print("skewed_kernel_size=0")
    print("balanced_heavy_heavy_viable=True")
    print("skewed_heavy_heavy_viable=False")
    print("WARRANTED_CONTINUATION_VIABILITY_V8=PASS")

if __name__=="__main__":
    main()
