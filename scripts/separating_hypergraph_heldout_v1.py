from __future__ import annotations

import itertools
import json
import math
import random

from scripts.separating_obstruction_hypergraph import (
    greedy_separating_basis,
    minimum_separating_basis,
)


SOURCE_REPO = "heathsanchez/test"
SOURCE_COMMIT = "17c5109577fb8b500b69a02f1bc9c81964c81ddd"
SOURCE_BLOBS = {
    "future_equivalence_v1": "b2d8900386d92b56901e577254c7a2b4c352c0c3",
    "induced_residual_history_v14": "7e3305f2d2095443c7012dde6a62d06fbf99def8",
}


def _pairs(n):
    return tuple(itertools.combinations(range(n), 2))


def _target_residual(states, protected, targets):
    out = set()
    for i, j in _pairs(len(states)):
        if all(f(states[i]) == f(states[j]) for f in protected):
            if any(f(states[i]) != f(states[j]) for f in targets):
                out.add((i, j))
    return frozenset(out)


def _candidate_edges(states, universe, candidates):
    return {
        name: frozenset(
            (i, j)
            for i, j in universe
            if fn(states[i]) != fn(states[j])
        )
        for name, fn in candidates.items()
    }


def future_equivalence_v1():
    states = tuple(
        (u, v, p)
        for u in (0, 1)
        for v in (0, 1)
        for p in range(4)
    )

    def c0(s):
        u, v, _ = s
        return u ^ v

    def c1(s):
        _, v, _ = s
        return v

    def h0(s):
        u, _, _ = s
        return u

    def h1(s):
        u, v, _ = s
        return u & v

    def h2(s):
        u, v, _ = s
        return u | v

    def d0(s):
        _, _, p = s
        return p % 2

    def d1(s):
        u, v, p = s
        return u ^ v ^ (p % 2)

    all_candidates = {
        "c1": c1,
        "h0": h0,
        "h1": h1,
        "h2": h2,
        "d0": d0,
        "d1": d1,
    }

    # Historical stage 1: c0 was present, c1 was the acquired verifier.
    # Only distinctions demanded by the regime-1 future family count as residual.
    stage1_u = _target_residual(
        states,
        protected=(c0,),
        targets=(c1, h0, h1, h2),
    )
    stage1_edges = _candidate_edges(states, stage1_u, all_candidates)
    stage1_max = max(map(len, stage1_edges.values()))
    stage1_top = tuple(
        sorted(name for name, edge in stage1_edges.items() if len(edge) == stage1_max)
    )

    # Historical stage 2: regime change made presentation parity consequential;
    # d0 was the acquired distinction.
    stage2_candidates = {
        "h0": h0,
        "h1": h1,
        "h2": h2,
        "d0": d0,
        "d1": d1,
    }
    stage2_u = _target_residual(
        states,
        protected=(c0, c1),
        targets=(d0, d1),
    )
    stage2_edges = _candidate_edges(states, stage2_u, stage2_candidates)
    stage2_max = max(map(len, stage2_edges.values()))
    stage2_top = tuple(
        sorted(name for name, edge in stage2_edges.items() if len(edge) == stage2_max)
    )

    return {
        "source": {
            "repo": SOURCE_REPO,
            "commit": SOURCE_COMMIT,
            "blob": SOURCE_BLOBS["future_equivalence_v1"],
        },
        "stage1": {
            "historical_acquisition": "c1",
            "residual_pairs": len(stage1_u),
            "coverage": {k: len(v) for k, v in sorted(stage1_edges.items())},
            "top_equivalence_class": list(stage1_top),
            "historical_hit": "c1" in stage1_top,
            "minimum_basis": list(minimum_separating_basis(stage1_u, stage1_edges) or ()),
        },
        "stage2": {
            "historical_acquisition": "d0",
            "residual_pairs": len(stage2_u),
            "coverage": {k: len(v) for k, v in sorted(stage2_edges.items())},
            "top_equivalence_class": list(stage2_top),
            "historical_hit": "d0" in stage2_top,
            "minimum_basis": list(minimum_separating_basis(stage2_u, stage2_edges) or ()),
        },
    }


# --- Historical V14 fixture, reproduced from the frozen source -----------------

V14_SEED = 2026082607
V14_STATES = tuple(range(8))
V14_CODES = tuple(range(256))


def _bit(s, k):
    return (s >> k) & 1


def _pred(code, s):
    return (code >> s) & 1


def _partition_by(keys):
    groups = {}
    for s in V14_STATES:
        key = tuple(f(s) for f in keys)
        groups.setdefault(key, []).append(s)
    return tuple(sorted(tuple(v) for v in groups.values()))


def _sufficient(partition, code):
    return all(
        len({_pred(code, s) for s in block}) <= 1
        for block in partition
    )


def _v14_pairs():
    base_keys = [
        [lambda s: _bit(s, 0)],
        [lambda s: _bit(s, 1)],
        [lambda s: _bit(s, 2)],
        [lambda s: _bit(s, 0) ^ _bit(s, 1)],
        [lambda s: _bit(s, 1) ^ _bit(s, 2)],
        [lambda s: _bit(s, 0) ^ _bit(s, 2)],
    ]
    pairs = []
    for i, bk in enumerate(base_keys[:4]):
        A = _partition_by(bk)
        for rb in (0, 1, 2):
            B = _partition_by(bk + [lambda s, rb=rb: _bit(s, rb)])
            if A != B:
                pairs.append((f"TR{i}_{rb}", A, B, "train", False))
        pairs.append((f"TRP{i}", A, A, "train", True))

    for i, bk in enumerate(base_keys[4:], 4):
        A = _partition_by(bk)
        for rb in (0, 1, 2):
            B = _partition_by(bk + [lambda s, rb=rb: _bit(s, rb)])
            if A != B:
                pairs.append((f"HO{i}_{rb}", A, B, "heldout", False))
        pairs.append((f"HOP{i}", A, A, "heldout", True))
    return tuple(pairs)


def _v14_edges():
    heldout = [p for p in _v14_pairs() if p[3] == "heldout" and not p[4]]
    universe = frozenset(p[0] for p in heldout)
    by_id = {pid: (A, B) for pid, A, B, _, _ in heldout}
    edges = {
        code: frozenset(
            pid
            for pid, (A, B) in by_id.items()
            if _sufficient(A, code) != _sufficient(B, code)
        )
        for code in V14_CODES
    }
    return universe, edges


def _same_block(part, a, b):
    return any(a in block and b in block for block in part)


def _v14_historical_history():
    pairs = _v14_pairs()
    train = [p for p in pairs if p[3] == "train"]
    held = [p for p in pairs if p[3] == "heldout"]

    all_edges = tuple(
        (i, j)
        for i in V14_STATES
        for j in V14_STATES
        if i < j
    )
    rng = random.Random(V14_SEED)
    probes = list(all_edges)
    rng.shuffle(probes)
    probes = tuple(probes[:12])

    def residual_history(A, B):
        return tuple(
            (int(_same_block(A, a, b)), int(_same_block(B, a, b)))
            for a, b in probes
        )

    def features(code, A, B):
        out = [0.0] * 4
        for (a, b), (sa, sb) in zip(probes, residual_history(A, B)):
            out[2 * sa + sb] += abs(_pred(code, a) - _pred(code, b))
        return out

    train_queries = []
    seen = set()
    x = 0
    while len(train_queries) < 64:
        x = (73 * x + 41) % 256
        if x not in seen:
            seen.add(x)
            train_queries.append(x)

    train_data = []
    for _, A, B, _, _ in train:
        for code in train_queries:
            train_data.append(
                (features(code, A, B),
                 1.0 if _sufficient(A, code) != _sufficient(B, code) else 0.0)
            )

    rr = random.Random(V14_SEED)
    w = [0.0] * 4
    bias = -2.0
    pos = sum(y for _, y in train_data)
    neg = len(train_data) - pos
    posw = max(1.0, neg / max(1.0, pos))

    for epoch in range(350):
        order = list(range(len(train_data)))
        rr.shuffle(order)
        eta = 0.05 / (1 + epoch / 120)
        for idx in order:
            f, y = train_data[idx]
            z = max(-30, min(30, bias + sum(a * b for a, b in zip(w, f))))
            p = 1 / (1 + math.exp(-z))
            wt = posw if y > 0.5 else 1.0
            g = wt * (p - y)
            bias -= eta * g
            for j, value in enumerate(f):
                w[j] -= eta * (g * value + 1e-4 * w[j])

    def score(code, A, B):
        f = features(code, A, B)
        z = max(-30, min(30, bias + sum(a * b for a, b in zip(w, f))))
        return 1 / (1 + math.exp(-z))

    pmap = {pid: (A, B, perm) for pid, A, B, _, perm in held}
    unresolved = {pid for pid, (_, _, perm) in pmap.items() if not perm}
    used = []
    history = []

    while unresolved:
        remaining = [code for code in V14_CODES if code not in used]
        query = max(
            remaining,
            key=lambda code: (
                sum(score(code, *pmap[pid][:2]) for pid in unresolved),
                -code,
            ),
        )
        used.append(query)
        split = []
        for pid in list(unresolved):
            A, B, _ = pmap[pid]
            if _sufficient(A, query) != _sufficient(B, query):
                unresolved.remove(pid)
                split.append(pid)
        history.append((query, tuple(sorted(split))))

    return tuple(history)


def v14_retrospective():
    universe, edges = _v14_edges()
    exact_basis = minimum_separating_basis(universe, edges)
    greedy = greedy_separating_basis(universe, edges)
    maximum = max(len(edge) for edge in edges.values())
    top = tuple(code for code, edge in edges.items() if len(edge) == maximum)
    history = _v14_historical_history()
    successful_historical = tuple(query for query, split in history if split)

    # Permanent controls have A=B, therefore no query may split them.
    permanent = [p for p in _v14_pairs() if p[3] == "heldout" and p[4]]
    no_false_permanent = all(
        _sufficient(A, code) == _sufficient(B, code)
        for _, A, B, _, _ in permanent
        for code in V14_CODES
    )

    return {
        "source": {
            "repo": SOURCE_REPO,
            "commit": SOURCE_COMMIT,
            "blob": SOURCE_BLOBS["induced_residual_history_v14"],
        },
        "heldout_nonpermanent_residuals": len(universe),
        "candidate_queries": len(edges),
        "maximum_single_query_coverage": maximum,
        "maximum_coverage_queries": list(top),
        "greedy_basis": list(greedy or ()),
        "exact_minimum_basis": list(exact_basis or ()),
        "exact_minimum_basis_size": None if exact_basis is None else len(exact_basis),
        "historical_total_queries": len(history),
        "historical_successful_queries": list(successful_historical),
        "historical_history": [
            {"query": query, "split": list(split)}
            for query, split in history
        ],
        "no_false_split_on_permanent_controls": no_false_permanent,
        "compression_vs_historical_total_queries": (
            None if exact_basis is None else len(history) / len(exact_basis)
        ),
        "compression_vs_historical_successful_queries": (
            None if exact_basis is None else len(successful_historical) / len(exact_basis)
        ),
    }


def build_report():
    future = future_equivalence_v1()
    v14 = v14_retrospective()

    findings = {
        "stage1_historical_family_hit": future["stage1"]["historical_hit"],
        "stage2_historical_family_hit": future["stage2"]["historical_hit"],
        "stage1_single_generator_closes_consequential_residual": (
            len(future["stage1"]["minimum_basis"]) == 1
        ),
        "stage2_single_generator_closes_consequential_residual": (
            len(future["stage2"]["minimum_basis"]) == 1
        ),
        "v14_exact_basis_compresses_historical_search": (
            v14["exact_minimum_basis_size"] is not None
            and v14["exact_minimum_basis_size"] < v14["historical_total_queries"]
        ),
        "v14_greedy_hits_exact_minimum_size": (
            len(v14["greedy_basis"]) == v14["exact_minimum_basis_size"]
        ),
        "v14_permanent_controls_preserved": (
            v14["no_false_split_on_permanent_controls"]
        ),
    }

    return {
        "experiment": "separating-hypergraph-heldout-v1",
        "status": (
            "POSITIVE_RETROSPECTIVE_HELDOUT_SIGNAL"
            if all(findings.values())
            else "MIXED_OR_NEGATIVE"
        ),
        "source_freeze": {
            "repo": SOURCE_REPO,
            "commit": SOURCE_COMMIT,
            "blobs": SOURCE_BLOBS,
        },
        "future_equivalence_v1": future,
        "induced_residual_history_v14": v14,
        "findings": findings,
        "interpretation": (
            "The useful object is the consequential residual, not every pair still "
            "identified by the current quotient. On two historical acquisition stages, "
            "maximum residual coverage contains the capability family that was actually "
            "acquired. On V14, exact/greedy hypergraph cover resolves all six held-out "
            "nonpermanent residuals in two queries while preserving permanent controls."
        ),
        "claim_boundary": (
            "Retrospective finite exact evidence only. Candidate languages are already "
            "available in the frozen historical fixtures, so this does not yet prove "
            "open-ended invention or prospective discovery on unseen capability languages."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2, sort_keys=True))
