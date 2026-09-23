from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def canonical_partition(blocks):
    return tuple(sorted((tuple(sorted(b)) for b in blocks),key=lambda b:(len(b),b)))

def current_partition(public):
    groups={}
    for s,v in enumerate(public["protected_outcome"]):
        groups.setdefault(v,[]).append(s)
    return canonical_partition(groups.values())

def class_map(partition):
    out={}
    for i,b in enumerate(partition):
        for x in b:
            out[x]=i
    return out

def novel_candidates(public):
    p=current_partition(public)
    out=[]
    for cid,vals in public["candidate_tests"].items():
        if any(len({vals[s] for s in block})>1 for block in p):
            out.append(cid)
    return tuple(sorted(out))

def signature(public,basis,s):
    return (
        public["protected_outcome"][s],
        *tuple(public["candidate_tests"][cid][s] for cid in basis),
    )

def target_sufficient(public,basis):
    seen={}
    for s in public["state_ids"]:
        sig=signature(public,basis,s)
        t=public["target_class"][s]
        if sig in seen and seen[sig]!=t:
            return False
        seen[sig]=t
    return True

def current_residual(public):
    p=current_partition(public)
    cm=class_map(p)
    target=public["target_class"]
    return tuple(
        (i,j)
        for i in public["state_ids"]
        for j in public["state_ids"]
        if i<j and cm[i]==cm[j] and target[i]!=target[j]
    )

def candidate_coverage(public,cid,residual):
    vals=public["candidate_tests"][cid]
    return tuple(pair for pair in residual if vals[pair[0]]!=vals[pair[1]])

def solve(public):
    p=current_partition(public)
    novel=novel_candidates(public)
    residual=current_residual(public)

    minsize=None
    bases=[]
    for k in range(len(novel)+1):
        for combo in itertools.combinations(novel,k):
            if target_sufficient(public,combo):
                minsize=k
                bases.append(combo)
        if bases:
            break

    if minsize is None:
        raise RuntimeError("no sufficient capability basis")

    canonical=bases[0]
    coverage={
        cid:len(candidate_coverage(public,cid,residual))
        for cid in sorted(public["candidate_tests"])
    }

    return {
        "current_blocks":[list(b) for b in p],
        "current_block_sizes":sorted(map(len,p)),
        "novel_candidates":list(novel),
        "novel_candidate_count":len(novel),
        "residual_pair_count":len(residual),
        "candidate_coverage":coverage,
        "minimum_acquisition_size":minsize,
        "exact_minimum_bases":[list(b) for b in bases],
        "exact_minimum_basis_count":len(bases),
        "canonical_basis":list(canonical),
        "canonical_basis_sufficient":target_sufficient(public,canonical),
        "canonical_irredundant":all(
            not target_sufficient(public,canonical[:i]+canonical[i+1:])
            for i in range(len(canonical))
        ),
        "no_singleton_sufficient":all(
            not target_sufficient(public,(cid,)) for cid in novel
        ),
    }

def relabel(public):
    n=len(public["state_ids"])
    perm=sorted(
        range(n),
        key=lambda i:hashlib.sha256(f"novel-capability:{i}".encode()).digest()
    )
    out=dict(public)
    out["state_ids"]=list(range(n))
    out["protected_outcome"]=[public["protected_outcome"][old] for old in perm]
    out["target_class"]=[public["target_class"][old] for old in perm]
    out["candidate_tests"]={
        cid:[vals[old] for old in perm]
        for cid,vals in public["candidate_tests"].items()
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
        "schema":"metatron.blind.novel-capability.v0.prediction",
        "preregistration_commit":public["preregistration_commit"],
        "public_sha256":sha(a.public),
        "hidden_commitment":public["hidden_sha256"],
        **primary,
        "relabel_control":{
            "current_block_sizes":rel["current_block_sizes"],
            "novel_candidate_count":rel["novel_candidate_count"],
            "minimum_acquisition_size":rel["minimum_acquisition_size"],
            "exact_minimum_basis_count":rel["exact_minimum_basis_count"],
            "invariant":(
                rel["current_block_sizes"]==primary["current_block_sizes"]
                and rel["novel_candidate_count"]==primary["novel_candidate_count"]
                and rel["minimum_acquisition_size"]==primary["minimum_acquisition_size"]
                and rel["exact_minimum_basis_count"]==primary["exact_minimum_basis_count"]
            ),
        },
    }

    Path(a.prediction).parent.mkdir(parents=True,exist_ok=True)
    Path(a.prediction).write_text(json.dumps(pred,indent=2,sort_keys=True)+"\n")

    print(json.dumps({
        "status":"PREDICTION_COMMITTED",
        "current_block_sizes":pred["current_block_sizes"],
        "novel_candidates":pred["novel_candidates"],
        "residual_pair_count":pred["residual_pair_count"],
        "minimum_acquisition_size":pred["minimum_acquisition_size"],
        "exact_minimum_basis_count":pred["exact_minimum_basis_count"],
        "canonical_basis":pred["canonical_basis"],
        "no_singleton_sufficient":pred["no_singleton_sufficient"],
        "relabel_invariant":pred["relabel_control"]["invariant"],
    },sort_keys=True))

if __name__=="__main__":
    main()
