from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pair(a,b): return tuple(sorted((a,b)))

def exact_commute(public,a,b):
    A=public["actions"][a]; B=public["actions"][b]
    return all(B[A[s]]==A[B[s]] for s in public["state_ids"])

def behavioral_commute(public,a,b):
    A=public["actions"][a]; B=public["actions"][b]; cls=public["behavioral_class"]
    return all(cls[B[A[s]]]==cls[A[B[s]]] for s in public["state_ids"])

def behavioral_counterexample(public,a,b):
    A=public["actions"][a]; B=public["actions"][b]; cls=public["behavioral_class"]
    for s in public["state_ids"]:
        if cls[B[A[s]]]!=cls[A[B[s]]]: return s
    return None

def step_closed(public):
    cls=public["behavioral_class"]
    for a,T in public["actions"].items():
        for x in public["state_ids"]:
            for y in public["state_ids"]:
                if cls[x]==cls[y] and cls[T[x]]!=cls[T[y]]:
                    return False
    return True

def schedules(public):
    return tuple(itertools.permutations(sorted(public["actions"])))

def run(public,sched,s):
    x=s
    for a in sched: x=public["actions"][a][x]
    return x

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

def behavioral_partition(public):
    cls=public["behavioral_class"]; groups={}
    for s in schedules(public):
        sig=tuple(cls[run(public,s,x)] for x in public["state_ids"])
        groups.setdefault(sig,[]).append(s)
    return tuple(sorted((tuple(sorted(v)) for v in groups.values()),key=repr))

def solve(public):
    ids=sorted(public["actions"])
    allpairs=[pair(a,b) for i,a in enumerate(ids) for b in ids[i+1:]]
    exact=tuple(sorted(p for p in allpairs if exact_commute(public,*p)))
    behavioral=tuple(sorted(p for p in allpairs if behavioral_commute(public,*p)))
    rejected=tuple(sorted(p for p in allpairs if p not in behavioral))
    sempart=behavioral_partition(public)
    fullcomp=components(public,set(behavioral))
    minbasis=None
    for k in range(len(behavioral)+1):
        for sub in itertools.combinations(behavioral,k):
            if components(public,set(sub))==sempart:
                minbasis=tuple(sub); break
        if minbasis is not None: break
    if minbasis is None: raise RuntimeError("no behavioral basis recovers partition")
    irredundant=all(components(public,set(minbasis)-{p})!=sempart for p in minbasis)
    return {
      "step_closed":step_closed(public),
      "exact_pairs":[list(p) for p in exact],
      "behavioral_pairs":[list(p) for p in behavioral],
      "strict_gain_pairs":[list(p) for p in behavioral if p not in exact],
      "behaviorally_rejected_pairs":[list(p) for p in rejected],
      "behavioral_counterexamples":{"|".join(p):behavioral_counterexample(public,*p) for p in rejected},
      "schedule_count":len(schedules(public)),
      "component_count":len(fullcomp),
      "component_sizes":sorted(len(c) for c in fullcomp),
      "behavioral_class_count":len(sempart),
      "behavioral_class_sizes":sorted(len(c) for c in sempart),
      "trace_partition_equals_behavioral_semantics":fullcomp==sempart,
      "minimum_behavioral_basis":[list(p) for p in minbasis],
      "minimum_behavioral_basis_size":len(minbasis),
      "minimum_basis_irredundant":irredundant,
    }

def relabel(public):
    n=len(public["state_ids"])
    perm=sorted(range(n),key=lambda i:hashlib.sha256(f"behavioral-commute:{i}".encode()).digest())
    old_to_new={old:new for new,old in enumerate(perm)}
    out=dict(public); out["state_ids"]=list(range(n))
    out["behavioral_class"]=[public["behavioral_class"][old] for old in perm]
    out["actions"]={a:[old_to_new[table[old]] for old in perm] for a,table in public["actions"].items()}
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--public",required=True); ap.add_argument("--prediction",required=True)
    a=ap.parse_args(); public=load(a.public); primary=solve(public); rel=solve(relabel(public))
    pred={
      "schema":"metatron.blind.behavioral-commutation.v1.prediction",
      "preregistration_commit":public["preregistration_commit"],
      "public_sha256":sha(a.public),
      "hidden_commitment":public["hidden_sha256"],
      **primary,
      "relabel_control":{
        "exact_pairs":rel["exact_pairs"],
        "behavioral_pairs":rel["behavioral_pairs"],
        "behavioral_class_sizes":rel["behavioral_class_sizes"],
        "minimum_behavioral_basis_size":rel["minimum_behavioral_basis_size"],
        "invariant":(
          rel["exact_pairs"]==primary["exact_pairs"]
          and rel["behavioral_pairs"]==primary["behavioral_pairs"]
          and rel["behavioral_class_sizes"]==primary["behavioral_class_sizes"]
          and rel["minimum_behavioral_basis_size"]==primary["minimum_behavioral_basis_size"]
        )
      }
    }
    Path(a.prediction).parent.mkdir(parents=True,exist_ok=True)
    Path(a.prediction).write_text(json.dumps(pred,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":"PREDICTION_COMMITTED",
      "step_closed":pred["step_closed"],
      "exact_pairs":pred["exact_pairs"],
      "behavioral_pairs":pred["behavioral_pairs"],
      "strict_gain_pairs":pred["strict_gain_pairs"],
      "component_sizes":pred["component_sizes"],
      "minimum_behavioral_basis":pred["minimum_behavioral_basis"],
      "minimum_behavioral_basis_size":pred["minimum_behavioral_basis_size"],
      "trace_partition_equals_behavioral_semantics":pred["trace_partition_equals_behavioral_semantics"],
      "relabel_invariant":pred["relabel_control"]["invariant"],
    },sort_keys=True))
if __name__=="__main__": main()
