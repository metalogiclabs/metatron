from __future__ import annotations
import argparse, json
from pathlib import Path
from scripts.blind_novel_capability_v0_predict import load, solve, sha, target_sufficient

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True)
    ap.add_argument("--hidden",required=True)
    ap.add_argument("--prediction",required=True)
    ap.add_argument("--report",required=True)
    a=ap.parse_args()

    public=load(a.public)
    hidden=load(a.hidden)
    pred=load(a.prediction)
    recomputed=solve(public)

    predicted_bases={tuple(x) for x in pred["exact_minimum_bases"]}
    planted=tuple(sorted(hidden["planted_minimum_basis"]))

    all_min_sufficient=all(
        target_sufficient(public,tuple(b))
        for b in pred["exact_minimum_bases"]
    )

    gates={
        "N1_hidden_commitment_matches":
            sha(a.hidden)==public["hidden_sha256"],
        "N2_prediction_bound_to_public":
            pred["public_sha256"]==sha(a.public)
            and pred["hidden_commitment"]==public["hidden_sha256"],
        "N3_current_quotient_correct":
            pred["current_block_sizes"]==[4,4],
        "N4_novel_candidate_set_matches_hidden":
            sorted(pred["novel_candidates"])==sorted(hidden["hidden_novel_candidates"]),
        "N5_no_singleton_novel_capability_sufficient":
            bool(pred["no_singleton_sufficient"]),
        "N6_minimum_acquisition_cardinality_two":
            pred["minimum_acquisition_size"]
            ==recomputed["minimum_acquisition_size"]
            ==2,
        "N7_planted_basis_in_predicted_minimum_family":
            planted in predicted_bases,
        "N8_every_predicted_minimum_basis_sufficient":
            all_min_sufficient,
        "N9_canonical_basis_irredundant":
            bool(pred["canonical_irredundant"]),
        "N10_state_relabel_invariant":
            bool(pred["relabel_control"]["invariant"]),
    }

    verdict=(
        "BLIND_NOVEL_CAPABILITY_PASS"
        if all(gates.values())
        else "BLIND_NOVEL_CAPABILITY_FAIL"
    )

    report={
        "schema":"metatron.blind.novel-capability.v0.reveal",
        "verdict":verdict,
        "current_block_sizes":pred["current_block_sizes"],
        "novel_candidate_count":pred["novel_candidate_count"],
        "novel_candidates":pred["novel_candidates"],
        "residual_pair_count":pred["residual_pair_count"],
        "minimum_acquisition_size":pred["minimum_acquisition_size"],
        "exact_minimum_basis_count":pred["exact_minimum_basis_count"],
        "canonical_basis":pred["canonical_basis"],
        "planted_minimum_basis":list(planted),
        "candidate_coverage":pred["candidate_coverage"],
        "gates":gates,
        "claim_boundary":(
            "Exact finite minimum novel interface-extension discovery inside "
            "a declared anonymous candidate test language."
        ),
    }

    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

    if verdict!="BLIND_NOVEL_CAPABILITY_PASS":
        raise SystemExit(1)

if __name__=="__main__":
    main()
