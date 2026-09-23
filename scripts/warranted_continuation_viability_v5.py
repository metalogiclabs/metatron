from itertools import combinations

CAPS = (0, 1, 2, 3)
ADMITTED = (0, 1)
PATHS = (
    (0, (0,)),
    (0, (1,)),
    (1, (1, 2)),
    (1, (3,)),
)

def path_live(live, requires):
    return all(c in live for c in requires)

def covered(live, failure):
    return any(f == failure and path_live(live, req) for f, req in PATHS)

def complete_cover(live):
    return all(covered(live, f) for f in ADMITTED)

def after_cut(cut):
    return tuple(c for c in CAPS if c not in cut)

def is_cut(cut):
    return not complete_cover(after_cut(cut))

def minimal_cuts():
    out = []
    for r in range(len(CAPS) + 1):
        for cut in combinations(CAPS, r):
            if is_cut(cut) and not any(set(prev).issubset(cut) for prev in out):
                out.append(cut)
    return tuple(out)

# Exact WarrantGraph semantics.
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

BASE_LOG = (((), None), ((), None), ((), None), ((), None))
CUT_13_LOG = BASE_LOG + (((), 1), ((), 3))

def main():
    assert complete_cover(CAPS)
    for c in CAPS:
        assert complete_cover(after_cut((c,)))
    mins = minimal_cuts()
    assert set(mins) == {(0, 1), (1, 3), (2, 3)}
    assert all(len(c) == 2 for c in mins)

    live_after = warrant_live(CUT_13_LOG)
    assert live_after == (0, 2)
    assert covered(live_after, 0)
    assert not covered(live_after, 1)
    assert not complete_cover(live_after)

    print("WARRANTED_CONTINUATION_VIABILITY_V5=PASS")
    print(f"base_complete_cover={complete_cover(CAPS)}")
    print(f"singleton_cuts_preserve={[complete_cover(after_cut((c,))) for c in CAPS]}")
    print(f"minimal_cuts={mins}")
    print(f"minimum_cut_size={min(len(c) for c in mins)}")
    print(f"warrant_live_after_cut_13={live_after}")
    print(f"failure0_covered_after_cut_13={covered(live_after, 0)}")
    print(f"failure1_covered_after_cut_13={covered(live_after, 1)}")
    print(f"complete_cover_after_cut_13={complete_cover(live_after)}")

if __name__ == "__main__":
    main()
