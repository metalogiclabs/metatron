DEPARTURES = (0, 1, 2, 3)
INTERVALS = ((0, 1), (1, 2), (2, 3))

def identity(t):
    return t

def gate1(t):
    return {0: 0, 1: 0, 2: 1, 3: 2}[t]

def gate2(x):
    return {0: 0, 1: 1, 2: 1}[x]

def downstream(t):
    return gate2(gate1(t))

def transition_count(f):
    return sum(f(a) != f(b) for a, b in INTERVALS)

def kernel_pairs(f):
    return {(a, b) for a in DEPARTURES for b in DEPARTURES if f(a) == f(b)}

def main():
    counts = (
        transition_count(identity),
        transition_count(gate1),
        transition_count(downstream),
    )
    kernels = (
        len(kernel_pairs(identity)),
        len(kernel_pairs(gate1)),
        len(kernel_pairs(downstream)),
    )

    assert counts == (3, 2, 1)
    assert kernels == (4, 6, 8)
    assert counts[0] > counts[1] > counts[2]
    assert kernels[0] < kernels[1] < kernels[2]

    for a, b in INTERVALS:
        if gate1(a) == gate1(b):
            assert downstream(a) == downstream(b)

    print("TEMPORAL_TIMESCALE_V1=PASS")
    print(f"transition_counts={counts}")
    print(f"kernel_pair_counts={kernels}")
    print("same_horizon_event_rate=strictly_decreasing")

if __name__ == "__main__":
    main()
