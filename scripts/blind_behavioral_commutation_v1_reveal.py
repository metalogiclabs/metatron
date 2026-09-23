from __future__ import annotations
import argparse, json
from pathlib import Path
from scripts.blind_behavioral_commutation_v1_predict import load, solve, sha

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True); ap.add_argument("--hidden",required=True)
    ap.add_argument("--prediction",required=True); ap.add_argument("--report",required=True)
    a=ap.parse_args()
    public=load(a.public); hidden=load(a.hidden); pred=load(a.prediction)
    recomputed=solve(public)
    hidden_exact=sorted(hidden["hidden_exact_pairs"])
    hidden_behavioral=sorted(hidden["hidden_behavioral_pairs"])
    rejected_ok=all(v is not None for v in pred["behavioral_counterexamples"].values())
    gates={
      "B1_hidden_commitment_matches":sha(a.hidden)==public["hidden_sha256"],
      "B2_prediction_bound_to_public":pred["public_sha256"]==sha(a.public) and pred["hidden_commitment"]==public["hidden_sha256"],
      "B3_behavioral_relation_step_closed":bool(pred["step_closed"]),
      "B4_exact_relation_matches_hidden":sorted(pred["exact_pairs"])==hidden_exact,
      "B5_behavioral_relation_matches_hidden":sorted(pred["behavioral_pairs"])==hidden_behavioral,
      "B6_behavioral_strictly_contains_exact":set(map(tuple,pred["exact_pairs"])) < set(map(tuple,pred["behavioral_pairs"])),
      "B7_every_behavioral_rejection_has_counterexample":rejected_ok,
      "B8_trace_components_equal_behavioral_semantics":bool(pred["trace_partition_equals_behavioral_semantics"]),
      "B9_minimum_basis_exact_and_irredundant":(
        pred["minimum_behavioral_basis_size"]==recomputed["minimum_behavioral_basis_size"]
        and bool(pred["minimum_basis_irredundant"])
      ),
      "B10_state_relabel_invariant":bool(pred["relabel_control"]["invariant"]),
    }
    verdict="BLIND_BEHAVIORAL_COMMUTATION_PASS" if all(gates.values()) else "BLIND_BEHAVIORAL_COMMUTATION_FAIL"
    report={
      "schema":"metatron.blind.behavioral-commutation.v1.reveal",
      "verdict":verdict,
      "preregistration_commit":public["preregistration_commit"],
      "public_sha256":sha(a.public),"hidden_sha256":sha(a.hidden),
      "exact_pairs":pred["exact_pairs"],
      "behavioral_pairs":pred["behavioral_pairs"],
      "strict_gain_pairs":pred["strict_gain_pairs"],
      "schedule_count":pred["schedule_count"],
      "component_count":pred["component_count"],
      "component_sizes":pred["component_sizes"],
      "behavioral_class_count":pred["behavioral_class_count"],
      "behavioral_class_sizes":pred["behavioral_class_sizes"],
      "minimum_behavioral_basis":pred["minimum_behavioral_basis"],
      "minimum_behavioral_basis_size":pred["minimum_behavioral_basis_size"],
      "gates":gates,
      "claim_boundary":"Blind exact finite discovery of quotient-relative commutation for a declared continuation-safe behavioral quotient."
    }
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    if verdict!="BLIND_BEHAVIORAL_COMMUTATION_PASS": raise SystemExit(1)
if __name__=="__main__": main()
