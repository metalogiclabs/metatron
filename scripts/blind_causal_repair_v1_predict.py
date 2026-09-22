from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def residual_pairs(public):
    protected = public["protected_observation"]
    target = public["target_future_class"]
    return tuple(
        (i, j)
        for i in range(len(protected))
        for j in range(i + 1, len(protected))
        if protected[i] == protected[j] and target[i] != target[j]
    )


def execute(public, repair, state):
    cur = state
    for aid in repair:
        cur = public["actions"][aid][cur]
    return cur


def repair_edge(public, repair, residual):
    observed = public["protected_observation"]
    covered = []
    for pair in residual:
        i, j = pair
        oi = observed[execute(public, repair, i)]
        oj = observed[execute(public, repair, j)]
        if oi != oj:
            covered.append(pair)
    return frozenset(covered)


def candidate_repairs(public):
    action_ids = tuple(sorted(public["actions"]))
    lang = public["repair_language"]
    out = []
    for k in range(lang["min_events"], lang["max_events"] + 1):
        for seq in itertools.product(action_ids, repeat=k):
            out.append(seq)
    return tuple(out)


def solve(public):
    residual = frozenset(residual_pairs(public))
    candidates = candidate_repairs(public)
    edges = {repair: repair_edge(public, repair, residual) for repair in candidates}

    sufficient = [r for r in candidates if edges[r] == residual]
    if not sufficient:
        raise RuntimeError("no sufficient repair in declared language")

    min_events = min(len(r) for r in sufficient)
    minimum_class = tuple(sorted(r for r in sufficient if len(r) == min_events))
    canonical = minimum_class[0]

    singleton_coverages = {
        r[0]: len(edges[r])
        for r in candidates
        if len(r) == 1
    }

    return {
        "residual_pair_count": len(residual),
        "candidate_repair_count": len(candidates),
        "minimum_event_count": min_events,
        "minimum_causal_class": [list(r) for r in minimum_class],
        "minimum_causal_class_count": len(minimum_class),
        "canonical_repair": list(canonical),
        "canonical_coverage": len(edges[canonical]),
        "singleton_coverages": singleton_coverages,
        "max_singleton_coverage": max(singleton_coverages.values()),
    }


def relabel_public(public):
    n = len(public["state_ids"])
    perm = sorted(
        range(n),
        key=lambda i: hashlib.sha256(f"blind-causal-repair-v1:{i}".encode()).digest(),
    )
    old_to_new = {old: new for new, old in enumerate(perm)}

    out = dict(public)
    out["state_ids"] = list(range(n))
    out["protected_observation"] = [
        public["protected_observation"][old] for old in perm
    ]
    out["target_future_class"] = [
        public["target_future_class"][old] for old in perm
    ]

    actions = {}
    for aid, table in public["actions"].items():
        actions[aid] = [
            old_to_new[table[old]]
            for old in perm
        ]
    out["actions"] = actions
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
        "schema": "metatron.blind.causal-repair.v1.prediction",
        "preregistration_commit": public["preregistration_commit"],
        "public_sha256": sha256(args.public),
        "hidden_commitment": public["hidden_sha256"],
        **primary,
        "relabel_control": {
            "minimum_event_count": relabelled["minimum_event_count"],
            "minimum_causal_class_count": relabelled["minimum_causal_class_count"],
            "invariant": (
                relabelled["minimum_event_count"] == primary["minimum_event_count"]
                and relabelled["minimum_causal_class_count"]
                    == primary["minimum_causal_class_count"]
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
        "minimum_event_count": prediction["minimum_event_count"],
        "minimum_causal_class_count": prediction["minimum_causal_class_count"],
        "canonical_repair": prediction["canonical_repair"],
        "max_singleton_coverage": prediction["max_singleton_coverage"],
        "relabel_invariant": prediction["relabel_control"]["invariant"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
