from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.blind_causal_repair_v1_predict import (
    load,
    residual_pairs,
    repair_edge,
    solve,
)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", required=True)
    ap.add_argument("--hidden", required=True)
    ap.add_argument("--prediction", required=True)
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    public = load(args.public)
    hidden = load(args.hidden)
    prediction = load(args.prediction)

    recomputed = solve(public)
    residual = frozenset(residual_pairs(public))

    planted = tuple(hidden["planted_ordered_repair"])
    reverse = tuple(hidden["reverse_ordered_repair"])
    minimum_class = {
        tuple(x) for x in prediction["minimum_causal_class"]
    }
    canonical = tuple(prediction["canonical_repair"])

    planted_edge = repair_edge(public, planted, residual)
    reverse_edge = repair_edge(public, reverse, residual)
    canonical_edge = repair_edge(public, canonical, residual)

    singleton_full = any(
        coverage == len(residual)
        for coverage in prediction["singleton_coverages"].values()
    )

    gates = {
        "C1_hidden_commitment_matches":
            sha256(args.hidden) == public["hidden_sha256"],
        "C2_prediction_bound_to_public": (
            prediction["public_sha256"] == sha256(args.public)
            and prediction["hidden_commitment"] == public["hidden_sha256"]
        ),
        "C3_no_singleton_is_sufficient": not singleton_full,
        "C4_true_minimum_event_count_is_two":
            recomputed["minimum_event_count"] == 2,
        "C5_prediction_matches_true_minimum":
            prediction["minimum_event_count"] == recomputed["minimum_event_count"],
        "C6_predicted_class_contains_planted_ordered_repair":
            planted in minimum_class,
        "C7_reverse_order_is_not_minimum_sufficient":
            reverse not in minimum_class and reverse_edge != residual,
        "C8_canonical_prediction_closes_residual":
            canonical_edge == residual,
        "C9_relabel_invariant":
            bool(prediction["relabel_control"]["invariant"]),
    }

    verdict = (
        "BLIND_CAUSAL_REPAIR_PASS"
        if all(gates.values())
        else "BLIND_CAUSAL_REPAIR_FAIL"
    )

    report = {
        "schema": "metatron.blind.causal-repair.v1.reveal",
        "verdict": verdict,
        "preregistration_commit": public["preregistration_commit"],
        "public_sha256": sha256(args.public),
        "hidden_sha256": sha256(args.hidden),
        "residual_pair_count": len(residual),
        "candidate_repair_count": prediction["candidate_repair_count"],
        "minimum_event_count": prediction["minimum_event_count"],
        "minimum_causal_class_count": prediction["minimum_causal_class_count"],
        "canonical_predicted_repair": list(canonical),
        "planted_ordered_repair": list(planted),
        "reverse_ordered_repair": list(reverse),
        "planted_coverage": len(planted_edge),
        "reverse_coverage": len(reverse_edge),
        "max_singleton_coverage": prediction["max_singleton_coverage"],
        "gates": gates,
        "claim_boundary": (
            "Blind recovery of a minimum ordered causal repair inside a declared "
            "finite chain language only."
        ),
    }

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))

    if verdict != "BLIND_CAUSAL_REPAIR_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
