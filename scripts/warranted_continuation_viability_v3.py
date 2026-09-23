from enum import Enum

class State(str, Enum):
    META_ADAPTIVE = "meta_adaptive"
    REPAIR_ONLY = "repair_only"
    NO_CAP_BOTH = "no_cap_both"
    PRIMARY_ONLY = "primary_only_no_cap"
    BACKUP_ONLY = "backup_only_no_cap"

class Encounter(str, Enum):
    REVOKE_PRIMARY = "revoke_primary"
    REVOKE_BACKUP = "revoke_backup"
    REVOKE_REPAIR = "revoke_repair"
    REVOKE_META = "revoke_meta"

STATES = tuple(State)
DEPTH1 = (Encounter.REVOKE_PRIMARY, Encounter.REVOKE_BACKUP, Encounter.REVOKE_REPAIR)
WITH_META_LOSS = DEPTH1 + (Encounter.REVOKE_META,)

def step(s, e):
    if s is State.META_ADAPTIVE:
        return State.REPAIR_ONLY if e is Encounter.REVOKE_META else State.META_ADAPTIVE
    if s is State.REPAIR_ONLY:
        return State.NO_CAP_BOTH if e is Encounter.REVOKE_REPAIR else State.REPAIR_ONLY
    if s is State.NO_CAP_BOTH:
        if e is Encounter.REVOKE_PRIMARY: return State.BACKUP_ONLY
        if e is Encounter.REVOKE_BACKUP: return State.PRIMARY_ONLY
        return State.NO_CAP_BOTH
    if s is State.PRIMARY_ONLY:
        return None if e is Encounter.REVOKE_PRIMARY else State.PRIMARY_ONLY
    if s is State.BACKUP_ONLY:
        return None if e is Encounter.REVOKE_BACKUP else State.BACKUP_ONLY
    raise AssertionError(s)

def predecessor(candidate, encounters):
    return {s for s in candidate if all((n := step(s,e)) is not None and n in candidate for e in encounters)}

def gfp(encounters):
    cur=set(STATES); chain=[set(cur)]
    while True:
        nxt=predecessor(cur,encounters); chain.append(set(nxt))
        if nxt==cur: return cur,chain
        cur=nxt

def warrant_live(log):
    def revoked(i): return any(rev==i for _,rev in log)
    live=[]
    for i,(premises,revokes) in enumerate(log):
        if revokes is not None or revoked(i): continue
        if all(p in live for p in premises): live.append(i)
    return tuple(live)

BASE=(((),None),((0,),None),((),None),((2,),None),((),None),((),None))
REPAIR_REVOKED=BASE+(((),4),)
REPAIR_RESTORED=REPAIR_REVOKED+(((5,),None),)
RESTORED_PRIMARY_REVOKED=REPAIR_RESTORED+(((),0),)
SUPPORT_REPAIRED=RESTORED_PRIMARY_REVOKED+(((7,),None),((9,),None))
RESTORED_META_REVOKED=REPAIR_RESTORED+(((),5),)
META_REVOKED=BASE+(((),5),)
META_THEN_REPAIR_REVOKED=META_REVOKED+(((),4),)
META_REPAIR_ATTEMPT=META_THEN_REPAIR_REVOKED+(((5,),None),)

def main():
    k1,c1=gfp(DEPTH1); k2,c2=gfp(WITH_META_LOSS)
    assert k1=={State.META_ADAPTIVE}
    assert k2==set()
    assert warrant_live(BASE)==(0,1,2,3,4,5)
    assert warrant_live(REPAIR_REVOKED)==(0,1,2,3,5)
    assert warrant_live(REPAIR_RESTORED)==(0,1,2,3,5,7)
    assert warrant_live(SUPPORT_REPAIRED)==(2,3,5,7,9,10)
    assert warrant_live(RESTORED_META_REVOKED)==(0,1,2,3)
    assert warrant_live(META_REPAIR_ATTEMPT)==(0,1,2,3)
    print("WARRANTED_CONTINUATION_VIABILITY_V3=PASS")
    print(f"depth1_kernel={tuple(sorted(s.value for s in k1))}")
    print(f"depth1_round_sizes={tuple(len(x) for x in c1)}")
    print(f"meta_loss_kernel={tuple(sorted(s.value for s in k2))}")
    print(f"meta_loss_round_sizes={tuple(len(x) for x in c2)}")
    print(f"base_live={warrant_live(BASE)}")
    print(f"repair_restored_live={warrant_live(REPAIR_RESTORED)}")
    print(f"support_repaired_by_restored_cap_live={warrant_live(SUPPORT_REPAIRED)}")
    print(f"restored_repair_then_meta_revoked_live={warrant_live(RESTORED_META_REVOKED)}")
    print(f"meta_repair_attempt_after_meta_loss_live={warrant_live(META_REPAIR_ATTEMPT)}")

if __name__=="__main__": main()
