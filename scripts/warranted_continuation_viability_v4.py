from typing import Optional

def tower_step(depth: int, failure: int) -> Optional[int]:
    if depth == 0:
        return None
    if depth == 1:
        return None if failure == 0 else 1
    outer = depth - 1
    if failure == outer:
        return depth - 1
    return depth

def predecessor(candidate, encounters):
    return {
        s for s in candidate
        if all((n := tower_step(s, e)) is not None and n in candidate for e in encounters)
    }

def gfp(depth, include_outer):
    states = set(range(1, depth + 1))
    encounters = tuple(range(depth if include_outer else max(0, depth - 1)))
    chain = [set(states)]
    cur = states
    while True:
        nxt = predecessor(cur, encounters)
        chain.append(set(nxt))
        if nxt == cur:
            return nxt, chain
        cur = nxt

def cascade(depth):
    return tuple(range(depth - 1, -1, -1))

def run(depth, failures):
    state = depth
    for f in failures:
        state = tower_step(state, f)
        if state is None:
            return None
    return state

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

# Cross-layer fixture:
# 0 support, 1 protected consequence, 2 ordinary repair, 3 shared repair.
BASE = (
    ((), None),
    ((0,), None),
    ((), None),
    ((), None),
)
ORDINARY_REVOKED = BASE + (((), 2),)
ORDINARY_AND_SUPPORT_REVOKED = ORDINARY_REVOKED + (((), 0),)
CROSS_LAYER_SUPPORT_REPAIRED = ORDINARY_AND_SUPPORT_REVOKED + (
    ((3,), None),
    ((6,), None),
)

def main():
    rows = []
    for depth in range(1, 9):
        lower_kernel, lower_chain = gfp(depth, include_outer=False)
        full_kernel, full_chain = gfp(depth, include_outer=True)
        assert lower_kernel == {depth}
        assert full_kernel == set()
        assert run(depth, cascade(depth)) is None
        # Adding one outer layer absorbs the failure that was the old boundary.
        assert tower_step(depth + 1, depth - 1) == depth + 1
        rows.append((
            depth,
            tuple(sorted(lower_kernel)),
            tuple(len(x) for x in lower_chain),
            tuple(len(x) for x in full_chain),
        ))

    assert warrant_live(BASE) == (0, 1, 2, 3)
    assert warrant_live(ORDINARY_REVOKED) == (0, 1, 3)
    assert warrant_live(ORDINARY_AND_SUPPORT_REVOKED) == (3,)
    assert warrant_live(CROSS_LAYER_SUPPORT_REPAIRED) == (3, 6, 7)
    assert 2 not in warrant_live(CROSS_LAYER_SUPPORT_REPAIRED)

    print("WARRANTED_CONTINUATION_VIABILITY_V4=PASS")
    for row in rows:
        print("depth_row=", row)
    print(f"cross_layer_base={warrant_live(BASE)}")
    print(f"cross_layer_both_revoked={warrant_live(ORDINARY_AND_SUPPORT_REVOKED)}")
    print(f"cross_layer_support_repaired={warrant_live(CROSS_LAYER_SUPPORT_REPAIRED)}")
    print("ordinary_repair_remains_revoked=True")

if __name__ == "__main__":
    main()
