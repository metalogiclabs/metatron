from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def public_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parity(bits):
    return sum(bits) & 1


def table_index(controls, target):
    idx = 0
    for b in controls:
        idx = 2 * idx + b
    return 2 * idx + target


def candidate_observation(candidate, bits):
    controls = [bits[i] for i in candidate["controls"]]
    target = bits[candidate["target"]]
    out = candidate["truth_table"][table_index(controls, target)]
    return parity(bits) ^ target ^ out


def residual_pairs(public):
    c = public["current_class"]
    t = public["target_future_class"]
    return tuple(
        (i, j)
        for i in range(len(c))
        for j in range(i + 1, len(c))
        if c[i] == c[j] and t[i] != t[j]
    )


def gain(candidate, vectors, residual):
    vals = [candidate_observation(candidate, bits) for bits in vectors]
    return sum(vals[i] != vals[j] for i, j in residual)


def closes(candidate, vectors, residual):
    if not residual:
        return False
    vals = [candidate_observation(candidate, bits) for bits in vectors]
    return all(vals[i] != vals[j] for i, j in residual)


def semantic_key(candidate):
    return (
        candidate["arity"],
        tuple(candidate["controls"]),
        candidate["target"],
        tuple(candidate["truth_table"]),
        candidate["id"],
    )


def solve(public):
    vectors = public["state_vectors"]
    residual = residual_pairs(public)
    if not residual:
        raise RuntimeError("empty residual")

    by_arity = {}
    exact_by_arity = {}
    for candidate in public["candidates"]:
        a = candidate["arity"]
        by_arity.setdefault(a, []).append(
            (candidate["id"], gain(candidate, vectors, residual))
        )
        if closes(candidate, vectors, residual):
            exact_by_arity.setdefault(a, []).append(candidate)

    arities = sorted({c["arity"] for c in public["candidates"]})
    min_arity = None
    closers = []
    for a in arities:
        if exact_by_arity.get(a):
            min_arity = a
            closers = sorted(exact_by_arity[a], key=semantic_key)
            break
    if min_arity is None:
        raise RuntimeError("no exact closer in declared arity grammar")

    max_gain_by_arity = {
        str(a): max((g for _, g in by_arity.get(a, [])), default=0)
        for a in arities
    }

    canonical = closers[0]
    return {
        "residual_pair_count": len(residual),
        "predicted_minimum_arity": min_arity,
        "maximum_gain_by_arity": max_gain_by_arity,
        "minimum_arity_exact_closer_count": len(closers),
        "minimum_arity_exact_closer_ids": [c["id"] for c in closers],
        "canonical_closer": canonical,
    }


def relabel_public(public):
    n = len(public["state_ids"])
    perm = sorted(
        range(n),
        key=lambda i: hashlib.sha256(
            f"blind-grammar-shape-v1-relabel:{i}".encode()
        ).digest(),
    )
    out = dict(public)
    out["state_ids"] = list(range(n))
    out["state_vectors"] = [public["state_vectors"][i] for i in perm]
    out["current_class"] = [public["current_class"][i] for i in perm]
    out["target_future_class"] = [
        public["target_future_class"][i] for i in perm
    ]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", required=True)
    ap.add_argument("--prediction", required=True)
    args = ap.parse_args()

    public = load(args.public)
    primary = solve(public)
    relabel = solve(relabel_public(public))

    prediction = {
        "schema": "metatron.blind.grammar_shape.v1.prediction",
        "preregistration_commit": public["preregistration_commit"],
        "public_sha256": public_digest(args.public),
        "hidden_commitment": public["hidden_sha256"],
        **primary,
        "relabel_control": {
            "minimum_arity": relabel["predicted_minimum_arity"],
            "exact_closer_count": relabel[
                "minimum_arity_exact_closer_count"
            ],
            "invariant": (
                relabel["predicted_minimum_arity"]
                    == primary["predicted_minimum_arity"]
                and relabel["minimum_arity_exact_closer_count"]
                    == primary["minimum_arity_exact_closer_count"]
            ),
        },
    }

    Path(args.prediction).parent.mkdir(parents=True, exist_ok=True)
    Path(args.prediction).write_text(
        json.dumps(prediction, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({
        "status": "BLIND_GRAMMAR_PREDICTION_COMMITTED",
        "public_sha256": prediction["public_sha256"],
        "predicted_minimum_arity": prediction["predicted_minimum_arity"],
        "exact_closer_count": prediction["minimum_arity_exact_closer_count"],
        "canonical_closer_id": prediction["canonical_closer"]["id"],
        "relabel_invariant": prediction["relabel_control"]["invariant"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
