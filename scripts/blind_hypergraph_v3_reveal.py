from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.blind_hypergraph_v3_predict import (
    build_residual,
    edge_bits,
    solve,
)


def load(path):
    return json.loads(Path(path).read_text())


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
    residual = build_residual(public)
    edges = edge_bits(public, residual)
    universe = (1 << len(residual)) - 1

    planted = tuple(sorted(hidden["planted_candidate_ids"]))
    planted_bits = 0
    for cid in planted:
        planted_bits |= edges[cid]

    selected = tuple(prediction["canonical_exact_cover"])
    selected_bits = 0
    for cid in selected:
        selected_bits |= edges[cid]

    exact_family = {
        tuple(sorted(x)) for x in prediction["exact_minimum_covers"]
    }

    gates = {
        "R1_hidden_commitment_matches": sha256(args.hidden) == public["hidden_sha256"],
        "R1_prediction_bound_to_public": (
            prediction["public_sha256"] == sha256(args.public)
            and prediction["hidden_commitment"] == public["hidden_sha256"]
        ),
        "R2_planted_set_closes_residual": planted_bits == universe,
        "R3_tau_equals_true_and_planted_cardinality": (
            prediction["tau"] == recomputed["tau"] == len(planted) == 3
        ),
        "R4_predicted_exact_cover_closes_residual": selected_bits == universe,
        "R5_no_smaller_cover_exists": recomputed["tau"] == 3,
        "R6_planted_is_in_exact_minimum_family": planted in exact_family,
        "R7_greedy_matches_exact_cardinality": (
            prediction["greedy_size"] == prediction["tau"]
        ),
        "R8_relabel_invariant": bool(
            prediction["relabel_control"]["invariant"]
            and prediction["relabel_control"]["tau"] == prediction["tau"]
            and prediction["relabel_control"]["exact_minimum_cover_count"]
                == prediction["exact_minimum_cover_count"]
        ),
    }

    core = all(
        gates[name]
        for name in (
            "R1_hidden_commitment_matches",
            "R1_prediction_bound_to_public",
            "R2_planted_set_closes_residual",
            "R3_tau_equals_true_and_planted_cardinality",
            "R4_predicted_exact_cover_closes_residual",
            "R5_no_smaller_cover_exists",
            "R6_planted_is_in_exact_minimum_family",
            "R8_relabel_invariant",
        )
    )
    if not core:
        verdict = "BLIND_PROSPECTIVE_FAIL"
    elif gates["R7_greedy_matches_exact_cardinality"]:
        verdict = "BLIND_PROSPECTIVE_PASS"
    else:
        verdict = "BLIND_PROSPECTIVE_PASS_GREEDY_MISS"

    report = {
        "schema": "metatron.blind.hypergraph.v3.reveal",
        "verdict": verdict,
        "preregistration_commit": public["preregistration_commit"],
        "public_sha256": sha256(args.public),
        "hidden_sha256": sha256(args.hidden),
        "residual_pair_count": len(residual),
        "candidate_count": len(public["candidate_outcomes"]),
        "target_future_class_count": len(set(public["target_future_class"])),
        "predicted_tau": prediction["tau"],
        "true_tau": recomputed["tau"],
        "canonical_predicted_cover": list(selected),
        "planted_hidden_cover": list(planted),
        "exact_minimum_cover_count": prediction["exact_minimum_cover_count"],
        "greedy_cover": prediction["greedy_cover"],
        "gates": gates,
        "claim_boundary": (
            "Blind finite commit-predict-reveal inside a declared anonymous "
            "candidate generator language. This does not establish unrestricted "
            "open-ended generator invention."
        ),
    }

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))

    if verdict == "BLIND_PROSPECTIVE_FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
