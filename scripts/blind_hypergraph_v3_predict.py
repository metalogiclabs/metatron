from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def public_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_residual(public):
    p = public["protected_outcome"]
    t = public["target_future_class"]
    return tuple(
        (i, j)
        for i in range(len(p))
        for j in range(i + 1, len(p))
        if p[i] == p[j] and t[i] != t[j]
    )


def edge_bits(public, residual):
    edges = {}
    for cid, values in public["candidate_outcomes"].items():
        bits = 0
        for k, (i, j) in enumerate(residual):
            if values[i] != values[j]:
                bits |= 1 << k
        edges[cid] = bits
    return edges


def exact_minimum(universe_bits, edges):
    names = tuple(sorted(edges))
    covers = []
    for size in range(0, len(names) + 1):
        for combo in itertools.combinations(names, size):
            bits = 0
            for name in combo:
                bits |= edges[name]
            if bits == universe_bits:
                covers.append(combo)
        if covers:
            return size, tuple(covers)
    return None, tuple()


def greedy(universe_bits, edges):
    remaining = universe_bits
    available = set(edges)
    chosen = []
    while remaining:
        ranked = sorted(
            available,
            key=lambda name: (
                -(edges[name] & remaining).bit_count(),
                name,
            ),
        )
        if not ranked:
            return None
        best = ranked[0]
        gain = edges[best] & remaining
        if gain == 0:
            return None
        chosen.append(best)
        remaining &= ~edges[best]
        available.remove(best)
    return tuple(chosen)


def solve(public):
    residual = build_residual(public)
    edges = edge_bits(public, residual)
    universe = (1 << len(residual)) - 1

    tau, covers = exact_minimum(universe, edges)
    if tau is None:
        raise RuntimeError("no exact cover")

    canonical = covers[0]
    greedy_cover = greedy(universe, edges)
    coverage = {name: bits.bit_count() for name, bits in edges.items()}
    max_cov = max(coverage.values()) if coverage else 0
    top = sorted(name for name, cov in coverage.items() if cov == max_cov)

    return {
        "residual_pair_count": len(residual),
        "tau": tau,
        "canonical_exact_cover": list(canonical),
        "exact_minimum_cover_count": len(covers),
        "exact_minimum_covers": [list(c) for c in covers],
        "greedy_cover": list(greedy_cover) if greedy_cover is not None else None,
        "greedy_size": len(greedy_cover) if greedy_cover is not None else None,
        "coverage": coverage,
        "maximum_coverage": max_cov,
        "maximum_coverage_class": top,
    }


def relabel_public(public):
    n = len(public["state_ids"])
    perm = sorted(
        range(n),
        key=lambda i: hashlib.sha256(f"blind-v3-relabel:{i}".encode()).digest(),
    )
    out = dict(public)
    out["state_ids"] = list(range(n))
    out["protected_outcome"] = [public["protected_outcome"][i] for i in perm]
    out["target_future_class"] = [public["target_future_class"][i] for i in perm]
    out["candidate_outcomes"] = {
        cid: [vals[i] for i in perm]
        for cid, vals in public["candidate_outcomes"].items()
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", required=True)
    ap.add_argument("--prediction", required=True)
    args = ap.parse_args()

    public = load(args.public)
    primary = solve(public)
    relabelled = solve(relabel_public(public))

    prediction = {
        "schema": "metatron.blind.hypergraph.v3.prediction",
        "preregistration_commit": public["preregistration_commit"],
        "public_sha256": public_digest(args.public),
        "hidden_commitment": public["hidden_sha256"],
        **primary,
        "relabel_control": {
            "tau": relabelled["tau"],
            "exact_minimum_cover_count": relabelled["exact_minimum_cover_count"],
            "invariant": (
                relabelled["tau"] == primary["tau"]
                and relabelled["exact_minimum_cover_count"]
                    == primary["exact_minimum_cover_count"]
            ),
        },
    }

    Path(args.prediction).parent.mkdir(parents=True, exist_ok=True)
    Path(args.prediction).write_text(
        json.dumps(prediction, indent=2, sort_keys=True) + "\n"
    )

    print(json.dumps({
        "status": "PREDICTION_COMMITTED",
        "public_sha256": prediction["public_sha256"],
        "hidden_commitment": prediction["hidden_commitment"],
        "residual_pair_count": prediction["residual_pair_count"],
        "tau": prediction["tau"],
        "canonical_exact_cover": prediction["canonical_exact_cover"],
        "exact_minimum_cover_count": prediction["exact_minimum_cover_count"],
        "greedy_size": prediction["greedy_size"],
        "relabel_invariant": prediction["relabel_control"]["invariant"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
