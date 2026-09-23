from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.blind_grammar_shape_v1_predict import (
    closes,
    gain,
    load,
    public_digest,
    residual_pairs,
    solve,
)


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


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

    hidden_sha = hashlib.sha256(Path(args.hidden).read_bytes()).hexdigest()
    residual = residual_pairs(public)
    vectors = public["state_vectors"]
    candidates = {c["id"]: c for c in public["candidates"]}
    planted = candidates[hidden["planted_candidate_id"]]
    true = solve(public)

    planted_arity = hidden["planted_minimum_arity"]
    lower = [
        c for c in public["candidates"]
        if c["arity"] < planted_arity
    ]
    canonical_id = prediction["canonical_closer"]["id"]
    canonical = candidates[canonical_id]

    gates = {
        "R1_hidden_commitment_matches":
            hidden_sha == public["hidden_sha256"],
        "R2_prediction_bound_to_public":
            prediction["public_sha256"] == public_digest(args.public)
            and prediction["hidden_commitment"] == public["hidden_sha256"],
        "R3_residual_nonempty":
            len(residual) > 0,
        "R4_all_lower_arity_zero_gain":
            all(gain(c, vectors, residual) == 0 for c in lower),
        "R5_planted_closes_full_residual":
            closes(planted, vectors, residual),
        "R6_predicted_minimum_arity_correct":
            prediction["predicted_minimum_arity"]
                == true["predicted_minimum_arity"]
                == planted_arity,
        "R7_canonical_prediction_closes":
            canonical["arity"] == prediction["predicted_minimum_arity"]
            and closes(canonical, vectors, residual),
        "R8_no_lower_arity_closer":
            all(not closes(c, vectors, residual) for c in lower),
        "R9_planted_in_predicted_minimum_family":
            hidden["planted_candidate_id"]
                in prediction["minimum_arity_exact_closer_ids"],
        "R10_relabel_invariant":
            prediction["relabel_control"]["invariant"] is True,
    }

    verdict = (
        "BLIND_GRAMMAR_SHAPE_PASS"
        if all(gates.values())
        else "BLIND_GRAMMAR_SHAPE_FAIL"
    )

    report = {
        "schema": "metatron.blind.grammar_shape.v1.reveal",
        "preregistration_commit": hidden["preregistration_commit"],
        "public_sha256": public_digest(args.public),
        "hidden_sha256": hidden_sha,
        "planted_minimum_arity": planted_arity,
        "planted_candidate_id": hidden["planted_candidate_id"],
        "predicted_minimum_arity":
            prediction["predicted_minimum_arity"],
        "predicted_canonical_closer":
            prediction["canonical_closer"],
        "minimum_arity_exact_closer_count":
            prediction["minimum_arity_exact_closer_count"],
        "residual_pair_count": len(residual),
        "maximum_gain_by_arity":
            prediction["maximum_gain_by_arity"],
        "gates": gates,
        "verdict": verdict,
        "claim_boundary": (
            "Blind prospective minimum-arity and extensional-shape selection "
            "inside the preregistered finite arity-1/2/3 grammar."
        ),
    }

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(report, indent=2, sort_keys=True))

    if verdict != "BLIND_GRAMMAR_SHAPE_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
