STATES = ("start", "left", "right", "out")
FULL_ACTIONS = ("follow", "escape")
RESTRICTED_ACTIONS = ("follow",)
TRAP = {"left", "right"}

def act(action, state):
    if action == "follow":
        return {
            "start": "left",
            "left": "right",
            "right": "left",
            "out": "out",
        }[state]
    if action == "escape":
        return "out"
    raise ValueError(action)

def successors(state, actions):
    return {act(a, state) for a in actions}

def reachable(start, actions):
    seen = {start}
    frontier = [start]
    while frontier:
        s = frontier.pop()
        for t in successors(s, actions):
            if t not in seen:
                seen.add(t)
                frontier.append(t)
    return seen

def closed(subset, actions):
    return all(act(a, s) in subset for s in subset for a in actions)

def path(start, actions, n):
    if len(actions) != 1:
        raise ValueError("path fixture requires one deterministic allowed action")
    a = actions[0]
    out = [start]
    s = start
    for _ in range(n):
        s = act(a, s)
        out.append(s)
    return tuple(out)

def main():
    full_reach = reachable("start", FULL_ACTIONS)
    restricted_reach = reachable("start", RESTRICTED_ACTIONS)
    restricted_path = path("start", RESTRICTED_ACTIONS, 8)

    assert full_reach == set(STATES)
    assert restricted_reach == {"start", "left", "right"}

    assert closed(TRAP, RESTRICTED_ACTIONS)
    assert not closed(TRAP, FULL_ACTIONS)

    assert act("follow", "left") == "right"
    assert act("follow", "right") == "left"
    assert act("escape", "left") == "out"
    assert act("escape", "right") == "out"

    assert len(successors("left", FULL_ACTIONS)) == 2
    assert len(successors("left", RESTRICTED_ACTIONS)) == 1
    assert len(successors("right", FULL_ACTIONS)) == 2
    assert len(successors("right", RESTRICTED_ACTIONS)) == 1

    assert restricted_path == (
        "start", "left", "right", "left", "right",
        "left", "right", "left", "right"
    )

    print("DEATH_SPIRAL_V0=PASS")
    print(f"full_reachable={tuple(sorted(full_reach))}")
    print(f"restricted_reachable={tuple(sorted(restricted_reach))}")
    print("trap=('left','right')")
    print("restricted_trap_closed=True")
    print("full_trap_closed=False")
    print("trap_branching_full=2")
    print("trap_branching_restricted=1")
    print(f"restricted_path={restricted_path}")

if __name__ == "__main__":
    main()
