from enum import Enum

class State(str, Enum):
    ADAPTIVE = "adaptive"
    NO_CAP_BOTH = "no_cap_both"
    PRIMARY_ONLY = "primary_only_no_cap"
    BACKUP_ONLY = "backup_only_no_cap"

class Encounter(str, Enum):
    REVOKE_PRIMARY = "revoke_primary"
    REVOKE_BACKUP = "revoke_backup"
    REVOKE_CAPABILITY = "revoke_capability"

STATES = tuple(State)
SUPPORT_ONLY = (Encounter.REVOKE_PRIMARY, Encounter.REVOKE_BACKUP)
WITH_CAPABILITY_LOSS = SUPPORT_ONLY + (Encounter.REVOKE_CAPABILITY,)

def step(state, encounter):
    if state is State.ADAPTIVE:
        if encounter is Encounter.REVOKE_CAPABILITY:
            return State.NO_CAP_BOTH
        # Verified repair capability restores either lost support.
        return State.ADAPTIVE
    if state is State.NO_CAP_BOTH:
        if encounter is Encounter.REVOKE_PRIMARY:
            return State.BACKUP_ONLY
        if encounter is Encounter.REVOKE_BACKUP:
            return State.PRIMARY_ONLY
        return State.NO_CAP_BOTH
    if state is State.PRIMARY_ONLY:
        if encounter is Encounter.REVOKE_PRIMARY:
            return None
        return State.PRIMARY_ONLY
    if state is State.BACKUP_ONLY:
        if encounter is Encounter.REVOKE_BACKUP:
            return None
        return State.BACKUP_ONLY
    raise AssertionError(state)

def predecessor(candidate, encounters):
    return {
        s for s in candidate
        if all(
            (nxt := step(s, e)) is not None and nxt in candidate
            for e in encounters
        )
    }

def gfp(encounters):
    current = set(STATES)
    chain = [set(current)]
    while True:
        nxt = predecessor(current, encounters)
        chain.append(set(nxt))
        if nxt == current:
            return current, chain
        current = nxt

# Exact WarrantGraph semantics.
def warrant_live(log):
    def revoked(i):
        return any(rev == i for _, rev in log)
    live = []
    for i, (premises, revokes) in enumerate(log):
        if revokes is not None:
            continue
        if revoked(i):
            continue
        if all(p in live for p in premises):
            live.append(i)
    return tuple(live)

# 0 primary root; 1 primary consequence; 2 backup root; 3 backup
# consequence; 4 verified repair capability.
BASE = (
    ((), None),
    ((0,), None),
    ((), None),
    ((2,), None),
    ((), None),
)

PRIMARY_REVOKED = BASE + (((), 0),)
PRIMARY_REPAIRED = PRIMARY_REVOKED + (((4,), None), ((6,), None))
PRIMARY_REPAIRED_CAP_REVOKED = PRIMARY_REPAIRED + (((), 4),)

CAP_REVOKED = BASE + (((), 4),)
CAP_REVOKED_PRIMARY_REVOKED = CAP_REVOKED + (((), 0),)
CAP_REVOKED_PRIMARY_REPAIR_ATTEMPT = (
    CAP_REVOKED_PRIMARY_REVOKED + (((4,), None), ((7,), None))
)

def main():
    support_kernel, support_chain = gfp(SUPPORT_ONLY)
    loss_kernel, loss_chain = gfp(WITH_CAPABILITY_LOSS)

    assert support_kernel == {State.ADAPTIVE}
    assert tuple(len(x) for x in support_chain) == (4, 1, 1)

    assert loss_kernel == set()
    assert tuple(len(x) for x in loss_chain) == (4, 2, 1, 0, 0)

    assert warrant_live(BASE) == (0, 1, 2, 3, 4)
    assert warrant_live(PRIMARY_REVOKED) == (2, 3, 4)
    assert warrant_live(PRIMARY_REPAIRED) == (2, 3, 4, 6, 7)
    # Revoking the capability invalidates the repair cone that depended on it.
    assert warrant_live(PRIMARY_REPAIRED_CAP_REVOKED) == (2, 3)

    assert warrant_live(CAP_REVOKED) == (0, 1, 2, 3)
    assert warrant_live(CAP_REVOKED_PRIMARY_REVOKED) == (2, 3)
    # Attempted replacement cannot become live because premise 4 is revoked.
    assert warrant_live(CAP_REVOKED_PRIMARY_REPAIR_ATTEMPT) == (2, 3)

    print("WARRANTED_CONTINUATION_VIABILITY_V2=PASS")
    print(f"support_only_kernel={tuple(sorted(s.value for s in support_kernel))}")
    print(f"support_only_round_sizes={tuple(len(x) for x in support_chain)}")
    print(f"capability_loss_kernel={tuple(sorted(s.value for s in loss_kernel))}")
    print(f"capability_loss_round_sizes={tuple(len(x) for x in loss_chain)}")
    print(f"base_live={warrant_live(BASE)}")
    print(f"primary_repaired_live={warrant_live(PRIMARY_REPAIRED)}")
    print(f"repair_capability_revoked_live={warrant_live(PRIMARY_REPAIRED_CAP_REVOKED)}")
    print(f"repair_attempt_after_capability_loss_live={warrant_live(CAP_REVOKED_PRIMARY_REPAIR_ATTEMPT)}")

if __name__ == "__main__":
    main()
