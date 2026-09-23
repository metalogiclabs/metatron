from itertools import product

SYMMETRIES = {
    "identity": (0, 0),
    "reflection": (1, 0),
    "reversal": (0, 1),
    "compound": (1, 1),
}
STATES = tuple(product((0, 1), repeat=2))


def act(symmetry, state):
    dr, dv = SYMMETRIES[symmetry]
    return (state[0] ^ dr, state[1] ^ dv)


def coherent(state):
    # Minimal orientation model extracted from the prose:
    # glyph orientation and reading order must agree.
    return state[0] == state[1]


def preserves_coherence(symmetry):
    return all(not coherent(s) or coherent(act(symmetry, s)) for s in STATES)


def main():
    coherent_states = tuple(s for s in STATES if coherent(s))
    stabilizer = tuple(g for g in SYMMETRIES if preserves_coherence(g))

    rows = []
    for g in SYMMETRIES:
        rows.append({
            "symmetry": g,
            "toggle": SYMMETRIES[g],
            "preserves_coherence": preserves_coherence(g),
            "images": {str(s): act(g, s) for s in STATES},
        })

    assert coherent_states == ((0, 0), (1, 1))
    assert stabilizer == ("identity", "compound")
    assert not preserves_coherence("reflection")
    assert not preserves_coherence("reversal")
    assert preserves_coherence("compound")

    # The two involutions commute in this minimal model.
    for s in STATES:
        rv = act("reflection", act("reversal", s))
        vr = act("reversal", act("reflection", s))
        assert rv == vr == act("compound", s)

    print("ORIENTATION_STABILIZER_V0=PASS")
    print(f"states={STATES}")
    print(f"coherent_states={coherent_states}")
    print(f"stabilizer={stabilizer}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
