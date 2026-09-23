from itertools import product

DEPARTURES = (0, 1, 2, 3)

def gate1(t):
    # First fixed gate: two nearby arrivals are released together.
    return {0: 0, 1: 0, 2: 1, 3: 2}[t]

def gate2(x):
    # Second gate acts on already-compressed event times.
    return {0: 0, 1: 1, 2: 1}[x]

def identity(t):
    return t

def compose(g, f):
    return lambda x: g(f(x))

def kernel_pairs(f):
    return {(x, y) for x, y in product(DEPARTURES, repeat=2) if f(x) == f(y)}

def image(f):
    return {f(x) for x in DEPARTURES}

def main():
    f0 = identity
    f1 = gate1
    f2 = compose(gate2, gate1)

    images = tuple(len(image(f)) for f in (f0, f1, f2))
    kernels = tuple(kernel_pairs(f) for f in (f0, f1, f2))
    kernel_sizes = tuple(len(k) for k in kernels)

    assert images == (4, 3, 2)
    assert kernels[0] < kernels[1] < kernels[2]
    assert kernel_sizes == (4, 6, 8)

    # Generic postcomposition law, checked exhaustively on this finite fixture.
    for x, y in product(DEPARTURES, repeat=2):
        if f1(x) == f1(y):
            assert f2(x) == f2(y)

    print("TEMPORAL_CONCENTRATION_V0=PASS")
    print(f"image_sizes={images}")
    print(f"kernel_sizes={kernel_sizes}")
    print(f"stage0={tuple(f0(x) for x in DEPARTURES)}")
    print(f"stage1={tuple(f1(x) for x in DEPARTURES)}")
    print(f"stage2={tuple(f2(x) for x in DEPARTURES)}")

if __name__ == "__main__":
    main()
