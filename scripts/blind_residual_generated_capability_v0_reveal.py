from __future__ import annotations
import argparse, json
from pathlib import Path
from scripts.blind_residual_generated_capability_v0_predict import load, solve, sha, generated_closure, target_sufficient

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True); ap.add_argument("--hidden",required=True)
    ap.add_argument("--prediction",required=True); ap.add_argument("--report",required=True)
    a=ap.parse_args()
    public=load(a.public); hidden=load(a.hidden); pred=load(a.prediction)
    recomputed=solve(public)
    predicted={tuple(tuple(x) for x in b) for b in pred["exact_minimum_bases"]}
    planted=tuple(tuple(x) for x in sorted(hidden["planted_generated_basis"]))
    closure={tuple(e["atoms"]):e for e in generated_closure(public)}
    all_sufficient=all(
        target_sufficient(public,[closure[tuple(expr)] for expr in b])
        for b in predicted
    )
    gates={
      "G1_hidden_commitment_matches":sha(a.hidden)==public["hidden_sha256"],
      "G2_prediction_bound_to_public":pred["public_sha256"]==sha(a.public) and pred["hidden_commitment"]==public["hidden_sha256"],
      "G3_generated_from_grammar_only":bool(pred["generated_from_grammar_only"]),
      "G4_primitive_minimum_size_three":pred["primitive_minimum_size"]==3,
      "G5_no_generated_singleton_sufficient":pred["generated_singleton_sufficient_count"]==0,
      "G6_minimum_generated_size_two":pred["minimum_generated_size"]==recomputed["minimum_generated_size"]==2,
      "G7_minimum_constructor_cost_two":pred["minimum_total_constructor_cost"]==recomputed["minimum_total_constructor_cost"]==2,
      "G8_planted_basis_in_minimum_family":planted in predicted,
      "G9_minimum_family_sufficient_and_irredundant":all_sufficient and bool(pred["canonical_irredundant"]),
      "G10_state_relabel_invariant":bool(pred["relabel_control"]["invariant"]),
    }
    verdict="BLIND_RESIDUAL_GENERATED_CAPABILITY_PASS" if all(gates.values()) else "BLIND_RESIDUAL_GENERATED_CAPABILITY_FAIL"
    report={
      "schema":"metatron.blind.residual-generated-capability.v0.reveal",
      "verdict":verdict,
      "closure_size":pred["closure_size"],
      "residual_pair_count":pred["residual_pair_count"],
      "primitive_minimum_size":pred["primitive_minimum_size"],
      "minimum_generated_size":pred["minimum_generated_size"],
      "minimum_total_constructor_cost":pred["minimum_total_constructor_cost"],
      "exact_minimum_basis_count":pred["exact_minimum_basis_count"],
      "canonical_basis":pred["canonical_basis"],
      "planted_generated_basis":[list(x) for x in planted],
      "gates":gates,
      "claim_boundary":"Finite synthesis from a declared XOR constructor algebra; no completed candidate observation list was supplied."
    }
    Path(a.report).parent.mkdir(parents=True,exist_ok=True)
    Path(a.report).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    if verdict!="BLIND_RESIDUAL_GENERATED_CAPABILITY_PASS": raise SystemExit(1)
if __name__=="__main__": main()
