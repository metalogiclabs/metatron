from __future__ import annotations
import argparse, hashlib, itertools, json
from pathlib import Path

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pair(a,b): return tuple(sorted((a,b)))

def canonical_partition(blocks):
    return tuple(sorted((tuple(sorted(b)) for b in blocks),key=lambda b:(len(b),b)))

def class_map(partition):
    out={}
    for i,b in enumerate(partition):
        for x in b: out[x]=i
    return out

def initial_partition(public):
    groups={}
    for s,v in enumerate(public["protected_outcome"]):
        groups.setdefault(v,[]).append(s)
    return canonical_partition(groups.values())

def refine_once(public,partition):
    cm=class_map(partition); aids=sorted(public["actions"])
    groups={}
    for s in public["state_ids"]:
        sig=(public["protected_outcome"][s],)+tuple(cm[public["actions"][a][s]] for a in aids)
        groups.setdefault(sig,[]).append(s)
    return canonical_partition(groups.values())

def future_partition(public):
    p=initial_partition(public)
    rounds=0
    while True:
        q=refine_once(public,p); rounds+=1
        if q==p: return p,rounds
        p=q

def respects_protected(public,p):
    out=public["protected_outcome"]
    return all(len({out[s] for s in b})==1 for b in p)

def step_closed(public,p):
    cm=class_map(p)
    for table in public["actions"].values():
        for b in p:
            if len({cm[table[s]] for s in b})!=1: return False
    return True

def all_partitions(items):
    items=list(items)
    if not items:
        yield tuple(); return
    first=items[0]
    for rest in all_partitions(items[1:]):
        yield canonical_partition(((first,),)+rest)
        for i in range(len(rest)):
            blocks=[list(b) for b in rest]
            blocks[i].append(first)
            yield canonical_partition(blocks)

def refines(p,q):
    # p refines q
    qmap=class_map(q)
    return all(len({qmap[x] for x in b})==1 for b in p)

def admissible_partitions(public):
    seen=set(); out=[]
    for p in all_partitions(public["state_ids"]):
        if p in seen: continue
        seen.add(p)
        if respects_protected(public,p) and step_closed(public,p): out.append(p)
    return tuple(sorted(out,key=repr))

def exact_commute(public,a,b):
    A=public["actions"][a]; B=public["actions"][b]
    return all(B[A[s]]==A[B[s]] for s in public["state_ids"])

def quotient_commute(public,p,a,b):
    cm=class_map(p); A=public["actions"][a]; B=public["actions"][b]
    return all(cm[B[A[s]]]==cm[A[B[s]]] for s in public["state_ids"])

def quotient_counterexample(public,p,a,b):
    cm=class_map(p); A=public["actions"][a]; B=public["actions"][b]
    for s in public["state_ids"]:
        if cm[B[A[s]]]!=cm[A[B[s]]]: return s
    return None

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
                q=list(s); q[i],q[i+1]=q[i+1],q[i]; q=tuple(q); graph[s].append(q)
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

def quotient_schedule_partition(public,p):
    cm=class_map(p); groups={}
    for sched in schedules(public):
        sig=tuple(cm[run(public,sched,s)] for s in public["state_ids"])
        groups.setdefault(sig,[]).append(sched)
    return tuple(sorted((tuple(sorted(v)) for v in groups.values()),key=repr))

def solve(public):
    p,rounds=future_partition(public)
    admissible=admissible_partitions(public)
    greatest=all(refines(q,p) for q in admissible)
    ids=sorted(public["actions"]); allpairs=[pair(a,b) for i,a in enumerate(ids) for b in ids[i+1:]]
    exact=tuple(sorted(x for x in allpairs if exact_commute(public,*x)))
    behavioral=tuple(sorted(x for x in allpairs if quotient_commute(public,p,*x)))
    rejected=tuple(sorted(x for x in allpairs if x not in behavioral))
    sempart=quotient_schedule_partition(public,p); fullcomp=components(public,set(behavioral))
    minbasis=None
    for k in range(len(behavioral)+1):
        for sub in itertools.combinations(behavioral,k):
            if components(public,set(sub))==sempart:
                minbasis=tuple(sub); break
        if minbasis is not None: break
    if minbasis is None: raise RuntimeError("no basis")
    return {
      "future_blocks":[list(b) for b in p],
      "future_block_sizes":sorted(map(len,p)),
      "refinement_rounds":rounds,
      "respects_protected":respects_protected(public,p),
      "step_closed":step_closed(public,p),
      "admissible_partition_count":len(admissible),
      "greatest_admissible_verified":greatest,
      "exact_pairs":[list(x) for x in exact],
      "behavioral_pairs":[list(x) for x in behavioral],
      "strict_gain_pairs":[list(x) for x in behavioral if x not in exact],
      "behavioral_rejected_pairs":[list(x) for x in rejected],
      "behavioral_counterexamples":{"|".join(x):quotient_counterexample(public,p,*x) for x in rejected},
      "schedule_count":len(schedules(public)),
      "component_count":len(fullcomp),
      "component_sizes":sorted(len(c) for c in fullcomp),
      "semantic_class_count":len(sempart),
      "semantic_class_sizes":sorted(len(c) for c in sempart),
      "trace_partition_equals_semantics":fullcomp==sempart,
      "minimum_basis":[list(x) for x in minbasis],
      "minimum_basis_size":len(minbasis),
      "minimum_basis_irredundant":all(components(public,set(minbasis)-{x})!=sempart for x in minbasis),
    }

def relabel(public):
    n=len(public["state_ids"])
    perm=sorted(range(n),key=lambda i:hashlib.sha256(f"future-q:{i}".encode()).digest())
    old_to_new={old:new for new,old in enumerate(perm)}
    out=dict(public); out["state_ids"]=list(range(n))
    out["protected_outcome"]=[public["protected_outcome"][old] for old in perm]
    out["actions"]={a:[old_to_new[t[old]] for old in perm] for a,t in public["actions"].items()}
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--public",required=True); ap.add_argument("--prediction",required=True)
    a=ap.parse_args(); public=load(a.public); primary=solve(public); rel=solve(relabel(public))
    pred={
      "schema":"metatron.blind.future-quotient.v0.prediction",
      "preregistration_commit":public["preregistration_commit"],
      "public_sha256":sha(a.public),"hidden_commitment":public["hidden_sha256"],**primary,
      "relabel_control":{
        "future_block_sizes":rel["future_block_sizes"],
        "exact_pairs":rel["exact_pairs"],"behavioral_pairs":rel["behavioral_pairs"],
        "semantic_class_sizes":rel["semantic_class_sizes"],
        "minimum_basis_size":rel["minimum_basis_size"],
        "invariant":(
          rel["future_block_sizes"]==primary["future_block_sizes"]
          and rel["exact_pairs"]==primary["exact_pairs"]
          and rel["behavioral_pairs"]==primary["behavioral_pairs"]
          and rel["semantic_class_sizes"]==primary["semantic_class_sizes"]
          and rel["minimum_basis_size"]==primary["minimum_basis_size"]
        )
      }
    }
    Path(a.prediction).parent.mkdir(parents=True,exist_ok=True)
    Path(a.prediction).write_text(json.dumps(pred,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":"PREDICTION_COMMITTED","future_blocks":pred["future_blocks"],
      "future_block_sizes":pred["future_block_sizes"],"refinement_rounds":pred["refinement_rounds"],
      "admissible_partition_count":pred["admissible_partition_count"],
      "greatest_admissible_verified":pred["greatest_admissible_verified"],
      "exact_pairs":pred["exact_pairs"],"behavioral_pairs":pred["behavioral_pairs"],
      "strict_gain_pairs":pred["strict_gain_pairs"],"component_sizes":pred["component_sizes"],
      "minimum_basis":pred["minimum_basis"],"minimum_basis_size":pred["minimum_basis_size"],
      "relabel_invariant":pred["relabel_control"]["invariant"]
    },sort_keys=True))
if __name__=="__main__": main()
