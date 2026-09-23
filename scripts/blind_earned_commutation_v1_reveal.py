from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from scripts.blind_earned_commutation_v1_predict import load, solve, sha, commute

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True); ap.add_argument("--hidden",required=True)
    ap.add_argument("--prediction",required=True); ap.add_argument("--report",required=True)
    a=ap.parse_args()
    public=load(a.public); hidden=load(a.hidden); pred=load(a.prediction)
    recomputed=solve(public)
    hidden_pairs=sorted(hidden["hidden_commuting_pairs"])
    pred_pairs=sorted(pred["safe_pairs"])
    all_safe_valid=all(commute(public,*p) for p in map(tuple,pred_pairs))
    all_unsafe_witnessed=all(v is not None for v in pred["unsafe_counterexamples"].values())
    gates={
      "E1_hidden_commitment_matches":sha(a.hidden)==public["hidden_sha256"],
      "E2_prediction_bound_to_public":pred["public_sha256"]==sha(a.public) and pred["hidden_commitment"]==public["hidden_sha256"],
      "E3_predicted_relation_equals_hidden":pred_pairs==hidden_pairs,
      "E4_every_predicted_pair_commutes":all_safe_valid,
      "E5_every_rejected_pair_has_counterexample":all_unsafe_witnessed,
      "E6_trace_components_equal_semantic_classes":bool(pred["trace_partition_equals_semantics"]),
      "E7_minimum_basis_cardinality_exact":pred["minimum_pair_basis_size"]==recomputed["minimum_pair_basis_size"],
      "E8_minimum_basis_irredundant":bool(pred["minimum_basis_irredundant"]),
      "E9_state_relabel_invariant":bool(pred["relabel_control"]["invariant"]),
    }
    verdict="BLIND_EARNED_COMMUTATION_PASS" if all(gates.values()) else "BLIND_EARNED_COMMUTATION_FAIL"
    report={
      "schema":"metatron.blind.earned-commutation.v1.reveal",
      "verdict":verdict,
      "preregistration_commit":public["preregistration_commit"],
      "public_sha256":sha(a.public),"hidden_sha256":sha(a.hidden),
      "safe_pairs":pred["safe_pairs"],"unsafe_pairs":pred["unsafe_pairs"],
      "schedule_count":pred["schedule_count"],
      "safe_component_count":pred["safe_component_count"],
      "safe_component_sizes":pred["safe_component_sizes"],
      "semantic_class_count":pred["semantic_class_count"],
      "semantic_class_sizes":pred["semantic_class_sizes"],
      "minimum_pair_basis":pred["minimum_pair_basis"],
      "minimum_pair_basis_size":pred["minimum_pair_basis_size"],
      "gates":gates,
      "claim_boundary":"Blind exact finite discovery of pairwise semantic commutation and the minimum pair-certificate basis for this declared anonymous action family."
    }
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    if verdict!="BLIND_EARNED_COMMUTATION_PASS": raise SystemExit(1)
if __name__=="__main__": main()
