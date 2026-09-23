from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def xor_vectors(vectors):
    if not vectors:
        raise ValueError("empty expression")
    out=[0]*len(vectors[0])
    for vec in vectors:
        out=[a^b for a,b in zip(out,vec)]
    return tuple(out)

def generated_closure(public):
    atom_ids=tuple(sorted(public["primitive_atoms"]))
    by_truth={}
    for k in range(1,len(atom_ids)+1):
        for subset in itertools.combinations(atom_ids,k):
            truth=xor_vectors([public["primitive_atoms"][a] for a in subset])
            cost=k-1
            prev=by_truth.get(truth)
            rep={"atoms":list(subset),"cost":cost,"truth":list(truth)}
            if prev is None or (cost,subset)<(prev["cost"],tuple(prev["atoms"])):
                by_truth[truth]=rep
    return tuple(sorted(by_truth.values(),key=lambda e:(e["cost"],e["atoms"])))

def target_sufficient(public,exprs):
    seen={}
    for s in public["state_ids"]:
        sig=(public["protected_outcome"][s],)+tuple(e["truth"][s] for e in exprs)
        t=public["target_class"][s]
        if sig in seen and seen[sig]!=t:
            return False
        seen[sig]=t
    return True

def primitive_minimum(public):
    atom_ids=tuple(sorted(public["primitive_atoms"]))
    for k in range(len(atom_ids)+1):
        wins=[]
        for subset in itertools.combinations(atom_ids,k):
            exprs=[
                {"atoms":[a],"cost":0,"truth":public["primitive_atoms"][a]}
                for a in subset
            ]
            if target_sufficient(public,exprs):
                wins.append(tuple(subset))
        if wins:
            return k,tuple(wins)
    return None,tuple()

def current_residual(public):
    out=[]
    for i in public["state_ids"]:
        for j in public["state_ids"]:
            if i<j and public["protected_outcome"][i]==public["protected_outcome"][j] and public["target_class"][i]!=public["target_class"][j]:
                out.append((i,j))
    return tuple(out)

def coverage(expr,residual):
    truth=expr["truth"]
    return sum(truth[i]!=truth[j] for i,j in residual)

def basis_key(basis):
    return tuple(tuple(e["atoms"]) for e in basis)

def solve(public):
    closure=generated_closure(public)
    residual=current_residual(public)
    primitive_size,primitive_bases=primitive_minimum(public)

    singleton_sufficient=[
        tuple(e["atoms"]) for e in closure if target_sufficient(public,[e])
    ]

    best_size=None
    best_cost=None
    winners=[]
    for k in range(1,len(closure)+1):
        local=[]
        local_cost=None
        for idxs in itertools.combinations(range(len(closure)),k):
            basis=[closure[i] for i in idxs]
            if not target_sufficient(public,basis):
                continue
            cost=sum(e["cost"] for e in basis)
            if local_cost is None or cost<local_cost:
                local_cost=cost
                local=[basis]
            elif cost==local_cost:
                local.append(basis)
        if local:
            best_size=k
            best_cost=local_cost
            winners=local
            break

    if best_size is None:
        raise RuntimeError("generated closure cannot reach target")

    winner_keys=sorted(basis_key(b) for b in winners)
    canonical=winner_keys[0]

    closure_records=[
        {
            "atoms":e["atoms"],
            "cost":e["cost"],
            "coverage":coverage(e,residual),
        }
        for e in closure
    ]

    def key_sufficient(key):
        lookup={tuple(e["atoms"]):e for e in closure}
        return target_sufficient(public,[lookup[tuple(x)] for x in key])

    irredundant=all(
        not key_sufficient(canonical[:i]+canonical[i+1:])
        for i in range(len(canonical))
    )

    return {
        "generated_from_grammar_only":public.get("constructors")==["xor"],
        "closure_size":len(closure),
        "residual_pair_count":len(residual),
        "primitive_minimum_size":primitive_size,
        "primitive_minimum_basis_count":len(primitive_bases),
        "generated_singleton_sufficient_count":len(singleton_sufficient),
        "minimum_generated_size":best_size,
        "minimum_total_constructor_cost":best_cost,
        "exact_minimum_bases":[[list(expr) for expr in basis] for basis in winner_keys],
        "exact_minimum_basis_count":len(winner_keys),
        "canonical_basis":[list(expr) for expr in canonical],
        "canonical_irredundant":irredundant,
        "closure":closure_records,
    }

def relabel(public):
    n=len(public["state_ids"])
    perm=sorted(range(n),key=lambda i:hashlib.sha256(f"residual-generated:{i}".encode()).digest())
    out=dict(public)
    out["state_ids"]=list(range(n))
    out["protected_outcome"]=[public["protected_outcome"][old] for old in perm]
    out["target_class"]=[public["target_class"][old] for old in perm]
    out["primitive_atoms"]={
        a:[vals[old] for old in perm]
        for a,vals in public["primitive_atoms"].items()
    }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True)
    ap.add_argument("--prediction",required=True)
    a=ap.parse_args()

    public=load(a.public)
    primary=solve(public)
    rel=solve(relabel(public))

    pred={
        "schema":"metatron.blind.residual-generated-capability.v0.prediction",
        "preregistration_commit":public["preregistration_commit"],
        "public_sha256":sha(a.public),
        "hidden_commitment":public["hidden_sha256"],
        **primary,
        "relabel_control":{
            "closure_size":rel["closure_size"],
            "minimum_generated_size":rel["minimum_generated_size"],
            "minimum_total_constructor_cost":rel["minimum_total_constructor_cost"],
            "exact_minimum_basis_count":rel["exact_minimum_basis_count"],
            "invariant":(
                rel["closure_size"]==primary["closure_size"]
                and rel["minimum_generated_size"]==primary["minimum_generated_size"]
                and rel["minimum_total_constructor_cost"]==primary["minimum_total_constructor_cost"]
                and rel["exact_minimum_basis_count"]==primary["exact_minimum_basis_count"]
            ),
        },
    }

    Path(a.prediction).parent.mkdir(parents=True,exist_ok=True)
    Path(a.prediction).write_text(json.dumps(pred,indent=2,sort_keys=True)+"\n")

    print(json.dumps({
        "status":"PREDICTION_COMMITTED",
        "closure_size":pred["closure_size"],
        "residual_pair_count":pred["residual_pair_count"],
        "primitive_minimum_size":pred["primitive_minimum_size"],
        "generated_singleton_sufficient_count":pred["generated_singleton_sufficient_count"],
        "minimum_generated_size":pred["minimum_generated_size"],
        "minimum_total_constructor_cost":pred["minimum_total_constructor_cost"],
        "exact_minimum_basis_count":pred["exact_minimum_basis_count"],
        "canonical_basis":pred["canonical_basis"],
        "relabel_invariant":pred["relabel_control"]["invariant"],
    },sort_keys=True))

if __name__=="__main__":
    main()
