from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pair(a,b): return tuple(sorted((a,b)))

def commute(public,a,b):
    A=public["actions"][a]; B=public["actions"][b]
    return all(B[A[s]]==A[B[s]] for s in public["state_ids"])

def counterexample(public,a,b):
    A=public["actions"][a]; B=public["actions"][b]
    for s in public["state_ids"]:
        if B[A[s]]!=A[B[s]]: return s
    return None

def run(public,sched,s):
    x=s
    for a in sched: x=public["actions"][a][x]
    return x

def schedules(public):
    return tuple(itertools.permutations(sorted(public["actions"])))

def components(public,allowed):
    scheds=schedules(public); graph={s:[] for s in scheds}
    for s in scheds:
        for i in range(len(s)-1):
            if pair(s[i],s[i+1]) in allowed:
                q=list(s); q[i],q[i+1]=q[i+1],q[i]; q=tuple(q)
                graph[s].append(q)
    seen=set(); comps=[]
    for s in scheds:
        if s in seen: continue
        stack=[s]; seen.add(s); c=[]
        while stack:
            x=stack.pop(); c.append(x)
            for y in graph[x]:
                if y not in seen: seen.add(y); stack.append(y)
        comps.append(tuple(sorted(c)))
    return tuple(sorted(comps,key=repr))

def semantic_partition(public):
    groups={}
    for s in schedules(public):
        sig=tuple(run(public,s,x) for x in public["state_ids"])
        groups.setdefault(sig,[]).append(s)
    return tuple(sorted((tuple(sorted(v)) for v in groups.values()),key=repr))

def solve(public):
    ids=sorted(public["actions"])
    allpairs=[pair(a,b) for i,a in enumerate(ids) for b in ids[i+1:]]
    safe=tuple(sorted(p for p in allpairs if commute(public,*p)))
    unsafe=tuple(sorted(p for p in allpairs if p not in safe))
    sempart=semantic_partition(public)
    fullcomp=components(public,set(safe))
    minbasis=None
    for k in range(len(safe)+1):
        for sub in itertools.combinations(safe,k):
            if components(public,set(sub))==sempart:
                minbasis=tuple(sub); break
        if minbasis is not None: break
    if minbasis is None: raise RuntimeError("no safe-pair basis recovers semantic partition")
    irredundant=all(components(public,set(minbasis)-{p})!=sempart for p in minbasis)
    return {
        "safe_pairs":[list(p) for p in safe],
        "unsafe_pairs":[list(p) for p in unsafe],
        "unsafe_counterexamples":{"|".join(p):counterexample(public,*p) for p in unsafe},
        "schedule_count":len(schedules(public)),
        "safe_component_count":len(fullcomp),
        "safe_component_sizes":sorted(len(c) for c in fullcomp),
        "semantic_class_count":len(sempart),
        "semantic_class_sizes":sorted(len(c) for c in sempart),
        "trace_partition_equals_semantics":fullcomp==sempart,
        "minimum_pair_basis":[list(p) for p in minbasis],
        "minimum_pair_basis_size":len(minbasis),
        "minimum_basis_irredundant":irredundant,
    }

def relabel(public):
    n=len(public["state_ids"])
    perm=sorted(range(n),key=lambda i:hashlib.sha256(f"earned-commute:{i}".encode()).digest())
    old_to_new={old:new for new,old in enumerate(perm)}
    out=dict(public); out["state_ids"]=list(range(n))
    out["actions"]={
        a:[old_to_new[table[old]] for old in perm]
        for a,table in public["actions"].items()
    }
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--public",required=True); ap.add_argument("--prediction",required=True)
    a=ap.parse_args(); public=load(a.public); primary=solve(public); rel=solve(relabel(public))
    prediction={
        "schema":"metatron.blind.earned-commutation.v1.prediction",
        "preregistration_commit":public["preregistration_commit"],
        "public_sha256":sha(a.public),
        "hidden_commitment":public["hidden_sha256"],
        **primary,
        "relabel_control":{
            "safe_pairs":rel["safe_pairs"],
            "semantic_class_sizes":rel["semantic_class_sizes"],
            "minimum_pair_basis_size":rel["minimum_pair_basis_size"],
            "invariant":(
                rel["safe_pairs"]==primary["safe_pairs"]
                and rel["semantic_class_sizes"]==primary["semantic_class_sizes"]
                and rel["minimum_pair_basis_size"]==primary["minimum_pair_basis_size"]
            )
        }
    }
    Path(a.prediction).parent.mkdir(parents=True,exist_ok=True)
    Path(a.prediction).write_text(json.dumps(prediction,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":"PREDICTION_COMMITTED",
        "safe_pairs":prediction["safe_pairs"],
        "component_sizes":prediction["safe_component_sizes"],
        "minimum_pair_basis":prediction["minimum_pair_basis"],
        "minimum_pair_basis_size":prediction["minimum_pair_basis_size"],
        "trace_partition_equals_semantics":prediction["trace_partition_equals_semantics"],
        "relabel_invariant":prediction["relabel_control"]["invariant"],
    },sort_keys=True))
if __name__=="__main__": main()
