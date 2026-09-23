from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    failure: int
    requires: tuple[int, ...]
    repair_id: int

ORACLE_ROUTES = (
    Route(0, (0,), 0),  # abRepair
    Route(0, (1,), 1),  # baRepair
)

def oracle_valid(repair_id, failure):
    return repair_id == 0 and failure == 0

def authorized(live, route):
    return all(c in live for c in route.requires)

def authority_covers(live, routes, failure):
    return any(r.failure == failure and authorized(live, r) for r in routes)

def causal_covers(live, routes, valid, failure):
    return any(
        r.failure == failure
        and authorized(live, r)
        and valid(r.repair_id, failure)
        for r in routes
    )

def complete_causal_cover(live, routes, valid, admitted):
    return all(causal_covers(live, routes, valid, f) for f in admitted)

def warrant_live(log):
    def revoked(i):
        return any(rev == i for _, rev in log)
    live = []
    for i, (premises, revokes) in enumerate(log):
        if revokes is not None or revoked(i):
            continue
        if all(p in live for p in premises):
            live.append(i)
    return tuple(live)

ORACLE_BASE = (((), None), ((), None))
ORACLE_CUT0 = ORACLE_BASE + (((), 0),)

REPEATED_ROUTES = (
    Route(0, (0,), 0),
    Route(1, (0,), 0),
)

def repeated_valid(repair_id, failure):
    return repair_id == 0 and failure in (0, 1)

@dataclass(frozen=True)
class ResourceState:
    live: tuple[int, ...]
    fuel: bool

def contention_step(state, failure):
    if not state.fuel:
        return None
    if not causal_covers(state.live, REPEATED_ROUTES, repeated_valid, failure):
        return None
    return ResourceState(state.live, False)

def run(state, failures):
    for failure in failures:
        state = contention_step(state, failure)
        if state is None:
            return None
    return state

def main():
    assert complete_causal_cover((0,1), ORACLE_ROUTES, oracle_valid, (0,))
    cut_live = warrant_live(ORACLE_CUT0)
    assert cut_live == (1,)
    assert authority_covers(cut_live, ORACLE_ROUTES, 0)
    assert not causal_covers(cut_live, ORACLE_ROUTES, oracle_valid, 0)

    initial = ResourceState((0,), True)
    assert complete_causal_cover(initial.live, REPEATED_ROUTES, repeated_valid, (0,1))
    assert contention_step(initial, 0) == ResourceState((0,), False)
    assert contention_step(initial, 1) == ResourceState((0,), False)
    assert run(initial, (0,1)) is None
    assert run(initial, (1,0)) is None

    print("WARRANTED_CONTINUATION_VIABILITY_V6=PASS")
    print(f"oracle_base_complete={complete_causal_cover((0,1), ORACLE_ROUTES, oracle_valid, (0,))}")
    print(f"oracle_cut_live={cut_live}")
    print(f"authority_only_cover_after_cut={authority_covers(cut_live, ORACLE_ROUTES, 0)}")
    print(f"causal_cover_after_cut={causal_covers(cut_live, ORACLE_ROUTES, oracle_valid, 0)}")
    print(f"repeated_static_complete={complete_causal_cover(initial.live, REPEATED_ROUTES, repeated_valid, (0,1))}")
    print(f"failure0_individually_repairable={contention_step(initial, 0) is not None}")
    print(f"failure1_individually_repairable={contention_step(initial, 1) is not None}")
    print(f"sequence_01_viable={run(initial, (0,1)) is not None}")
    print(f"sequence_10_viable={run(initial, (1,0)) is not None}")

if __name__ == "__main__":
    main()
