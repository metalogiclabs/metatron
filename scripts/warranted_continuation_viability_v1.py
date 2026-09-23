from enum import Enum

class State(str, Enum):
    ADAPTIVE = "adaptive"
    PRIMARY_ONLY = "primary_only"
    BACKUP_ONLY = "backup_only"
    NONE = "none"

class Encounter(str, Enum):
    REVOKE_PRIMARY = "revoke_primary"
    REVOKE_BACKUP = "revoke_backup"

STATES = tuple(State)
ENCOUNTERS = tuple(Encounter)

def step(state, encounter):
    if state is State.ADAPTIVE:
        # Retained verified repair capability restores the revoked support
        # before the next admitted encounter.
        return State.ADAPTIVE
    if state is State.PRIMARY_ONLY:
        if encounter is Encounter.REVOKE_PRIMARY:
            return None
        return State.PRIMARY_ONLY
    if state is State.BACKUP_ONLY:
        if encounter is Encounter.REVOKE_BACKUP:
            return None
        return State.BACKUP_ONLY
    return None

def predecessor(candidate):
    return {
        s for s in candidate
        if all(
            (nxt := step(s, e)) is not None and nxt in candidate
            for e in ENCOUNTERS
        )
    }

def greatest_fixed_point():
    current = set(STATES)
    chain = [set(current)]
    while True:
        nxt = predecessor(current)
        chain.append(set(nxt))
        if nxt == current:
            return current, chain
        current = nxt

# Exact WarrantGraph semantics mirrored from formal/Metatron/WarrantGraph.lean.
# Each entry is (premises, revoked_index_or_None).
BASE_LOG = (
    ((), None),       # 0 primary root
    ((0,), None),     # 1 primary consequence
    ((), None),       # 2 backup root
    ((2,), None),     # 3 backup consequence
)

def warrant_revoked(log, i):
    return any(rev == i for _, rev in log)

def warrant_live(log):
    live = []
    for i, (premises, revokes) in enumerate(log):
        if revokes is not None:
            continue
        if warrant_revoked(log, i):
            continue
        if all(p in live for p in premises):
            live.append(i)
    return tuple(live)

def revoke_and_repair(target):
    # Index 4 records revocation. Index 5 is a fresh verified root and
    # index 6 is its reclosed consequence.
    return BASE_LOG + (((), target), ((), None), ((5,), None))

def main():
    kernel, chain = greatest_fixed_point()

    assert chain[0] == set(STATES)
    assert chain[1] == {State.ADAPTIVE}
    assert chain[2] == {State.ADAPTIVE}
    assert kernel == {State.ADAPTIVE}

    assert step(State.PRIMARY_ONLY, Encounter.REVOKE_PRIMARY) is None
    assert step(State.BACKUP_ONLY, Encounter.REVOKE_BACKUP) is None
    assert all(step(State.ADAPTIVE, e) is State.ADAPTIVE for e in ENCOUNTERS)

    base_live = warrant_live(BASE_LOG)
    primary_reclosed = warrant_live(revoke_and_repair(0))
    backup_reclosed = warrant_live(revoke_and_repair(2))

    assert base_live == (0, 1, 2, 3)
    assert primary_reclosed == (2, 3, 5, 6)
    assert backup_reclosed == (0, 1, 5, 6)

    print("WARRANTED_CONTINUATION_VIABILITY_V1=PASS")
    print(f"states={tuple(s.value for s in STATES)}")
    print(f"encounters={tuple(e.value for e in ENCOUNTERS)}")
    print(f"gfp_round0={tuple(sorted(s.value for s in chain[0]))}")
    print(f"gfp_round1={tuple(sorted(s.value for s in chain[1]))}")
    print(f"gfp_round2={tuple(sorted(s.value for s in chain[2]))}")
    print(f"viability_kernel={tuple(sorted(s.value for s in kernel))}")
    print(f"base_live={base_live}")
    print(f"primary_revoked_reclosed_live={primary_reclosed}")
    print(f"backup_revoked_reclosed_live={backup_reclosed}")

if __name__ == "__main__":
    main()
