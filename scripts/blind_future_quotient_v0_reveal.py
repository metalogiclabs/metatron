from __future__ import annotations
import argparse, json
from pathlib import Path
from scripts.blind_future_quotient_v0_predict import load, solve, sha

def canon_blocks(xs):
    return sorted((sorted(b) for b in xs), key=lambda b:(len(b),b))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True); ap.add_argument("--hidden",required=True)
    ap.add_argument("--prediction",required=True); ap.add_argument("--report",required=True)
    a=ap.parse_args()
    public=load(a.public); hidden=load(a.hidden); pred=load(a.prediction)
    recomputed=solve(public)
    rejected_ok=all(v is not None for v in pred["behavioral_counterexamples"].values())
    gates={
      "Q1_hidden_commitment_matches":sha(a.hidden)==public["hidden_sha256"],
      "Q2_prediction_bound_to_public":pred["public_sha256"]==sha(a.public) and pred["hidden_commitment"]==public["hidden_sha256"],
      "Q3_predicted_quotient_matches_hidden":canon_blocks(pred["future_blocks"])==canon_blocks(hidden["hidden_future_blocks"]),
      "Q4_quotient_protected_and_step_closed":bool(pred["respects_protected"]) and bool(pred["step_closed"]),
      "Q5_greatest_admissible_exhaustive":bool(pred["greatest_admissible_verified"]),
      "Q6_exact_relation_matches_hidden":sorted(pred["exact_pairs"])==sorted(hidden["hidden_exact_pairs"]),
      "Q7_behavioral_relation_matches_and_strictly_gains":(
        sorted(pred["behavioral_pairs"])==sorted(hidden["hidden_behavioral_pairs"])
        and set(map(tuple,pred["exact_pairs"])) < set(map(tuple,pred["behavioral_pairs"]))
      ),
      "Q8_every_behavioral_rejection_has_counterexample":rejected_ok,
      "Q9_schedule_partition_and_minimum_basis_exact":(
        bool(pred["trace_partition_equals_semantics"])
        and pred["minimum_basis_size"]==recomputed["minimum_basis_size"]
        and bool(pred["minimum_basis_irredundant"])
      ),
      "Q10_state_relabel_invariant":bool(pred["relabel_control"]["invariant"]),
    }
    verdict="BLIND_FUTURE_QUOTIENT_PASS" if all(gates.values()) else "BLIND_FUTURE_QUOTIENT_FAIL"
    report={
      "schema":"metatron.blind.future-quotient.v0.reveal",
      "verdict":verdict,
      "future_blocks":pred["future_blocks"],
      "future_block_sizes":pred["future_block_sizes"],
      "refinement_rounds":pred["refinement_rounds"],
      "admissible_partition_count":pred["admissible_partition_count"],
      "exact_pairs":pred["exact_pairs"],
      "behavioral_pairs":pred["behavioral_pairs"],
      "strict_gain_pairs":pred["strict_gain_pairs"],
      "schedule_count":pred["schedule_count"],
      "component_count":pred["component_count"],
      "component_sizes":pred["component_sizes"],
      "semantic_class_count":pred["semantic_class_count"],
      "semantic_class_sizes":pred["semantic_class_sizes"],
      "minimum_basis":pred["minimum_basis"],
      "minimum_basis_size":pred["minimum_basis_size"],
      "gates":gates,
      "claim_boundary":"Exact finite greatest continuation-safe quotient discovery plus quotient-relative commutation for a declared deterministic interface."
    }
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    if verdict!="BLIND_FUTURE_QUOTIENT_PASS": raise SystemExit(1)
if __name__=="__main__": main()
