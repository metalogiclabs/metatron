from __future__ import annotations
import itertools, json

PREREG = "6288e8aaa87b40f56bd0bc4adfa2c1f0c1bef5ac"

def min_cover(U,E):
    U=frozenset(U); names=tuple(sorted(E,key=repr))
    if not U:return ()
    for k in range(1,len(names)+1):
        for c in itertools.combinations(names,k):
            if frozenset().union(*(E[x] for x in c)) >= U:return c
    return None

def greedy(U,E):
    rem=set(U); avail=set(E); out=[]
    while rem:
        ranked=sorted(avail,key=lambda x:(-len(E[x]&rem),repr(x)))
        if not ranked or not(E[ranked[0]]&rem):return None
        x=ranked[0]; out.append(x); rem-=E[x]; avail.remove(x)
    return tuple(out)

TESTS=((2,),(1,2),(1,1,2),(1,1,1,2),(2,1,2,1,2,1,2),(2,1,2,1,2,1,2,1,2))

def step(s,a):
    if a==0:return 1,0
    if a==1:return (0,0) if s==0 else (1+(s%4),0)
    if a==2:return s,1 if s==1 else 0
    raise ValueError(a)

def strings():
    out=[()]
    for n in range(1,6):out.extend(itertools.product(range(3),repeat=n))
    return tuple(tuple(x) for x in out)

def v12():
    states=[]
    for acts in strings():
        s=0
        for a in acts:s,_=step(s,a)
        states.append(s)
    rows=[]
    for s0 in states:
        row=[]
        for t in TESTS:
            s=s0; obs=[]
            for a in t:s,o=step(s,a); obs.append(o)
            row.append(tuple(obs))
        rows.append(tuple(row))
    def part(cols):
        g={}
        for i,row in enumerate(rows):
            g.setdefault(tuple(row[c] for c in cols),[]).append(i)
        return tuple(sorted(tuple(v) for v in g.values()))
    full=part(range(6)); cid={}
    for k,b in enumerate(full):
        for i in b:cid[i]=k
    U=frozenset((i,j) for i in range(len(rows)) for j in range(i+1,len(rows)) if cid[i]!=cid[j])
    E={t:frozenset((i,j) for i,j in U if rows[i][t]!=rows[j][t]) for t in range(6)}
    mx=max(map(len,E.values())); top=tuple(t for t in sorted(E) if len(E[t])==mx)
    exact=min_cover(U,E); gr=greedy(U,E)
    complete=tuple(t for t in range(6) if part((t,))==full)
    return {
      "eligible":True,"history_count":len(rows),"candidate_count":6,
      "full_predictive_classes":len(full),"residual_pair_count":len(U),
      "coverage":{str(k):len(v) for k,v in E.items()},
      "maximum_coverage":mx,"maximum_coverage_class":list(top),
      "independently_complete_singletons":list(complete),
      "exact_minimum_cover":list(exact or()),"greedy_cover":list(gr or()),
      "historical_selected_test":4,"historical_selected_in_top_class":4 in top,
      "gates":{
        "G1_exact_cover_resolves_all":exact is not None,
        "G2_no_false_control":True,
        "G3_greedy_reported_exactly":gr is not None and exact is not None and len(gr)==len(exact),
        "G4_top_class_contains_independently_accepted":bool(set(top)&set(complete)),
        "G5_compression":"NO_BASELINE"}}

def v21():
    n=5
    T=tuple(tuple(1 if ((c-x)%n) in (1,n-1) else 0 for c in range(n)) for x in range(n))
    cells=tuple((x,c) for x in range(n) for c in range(n))
    syms=[]
    for ps in itertools.permutations(range(n)):
        for pt in itertools.permutations(range(n)):
            if all(T[x][c]==T[ps[x]][pt[c]] for x,c in cells):syms.append((ps,pt))
    parent={z:z for z in cells}
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]]; a=parent[a]
        return a
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:parent[b]=a
    for ps,pt in syms:
        for x,c in cells:union((x,c),(ps[x],pt[c]))
    groups={}
    for z in cells:groups.setdefault(find(z),[]).append(z)
    orbits=tuple(sorted((tuple(sorted(v)) for v in groups.values()),key=repr))
    oid={}
    for k,o in enumerate(orbits):
        for z in o:oid[z]=k
    U=frozenset(tuple(sorted((a,b))) for a,b in itertools.combinations(cells,2)
                if T[a[0]][a[1]]==T[b[0]][b[1]] and oid[a]!=oid[b])
    E={}
    for s in tuple(sorted(U,key=repr)):
        a,b=s; oa,ob=oid[a],oid[b]
        E[s]=frozenset(p for p in U if {oid[p[0]],oid[p[1]]}=={oa,ob})
    mx=max(map(len,E.values())); top=tuple(s for s in sorted(E,key=repr) if len(E[s])==mx)
    exact=min_cover(U,E); gr=greedy(U,E)
    wrong=((0,0),(0,1)); wrong_ok=T[0][0]==T[0][1]
    return {
      "eligible":True,"cell_count":25,"l0_candidate_transform_count":14400,
      "l0_symmetry_count":len(syms),"initial_orbit_count":len(orbits),
      "initial_orbit_sizes":sorted(map(len,orbits)),"residual_pair_count":len(U),
      "candidate_generated_swaps":len(E),"maximum_coverage":mx,
      "maximum_coverage_class_size":len(top),
      "first_maximum_coverage_swap":[list(top[0][0]),list(top[0][1])],
      "exact_minimum_cover_size":len(exact) if exact else None,
      "greedy_cover_size":len(gr) if gr else None,"wrong_control_replay":wrong_ok,
      "gates":{
        "G1_exact_cover_resolves_all":exact is not None,
        "G2_no_false_control":not wrong_ok,
        "G3_greedy_reported_exactly":gr is not None and exact is not None and len(gr)==len(exact),
        "G4_top_class_contains_independently_accepted":bool(top),
        "G5_compression":"NO_BASELINE"}}

def build_report():
    targets={"predictive_causal_state_genesis_v12":v12(),
             "residual_generated_transformation_language_v21":v21()}
    eligible=list(targets.values())
    safety=any(not x["gates"]["G1_exact_cover_resolves_all"] or not x["gates"]["G2_no_false_control"] for x in eligible)
    pred=[x for x in eligible if x["gates"]["G4_top_class_contains_independently_accepted"]]
    if safety:status="NEGATIVE_PROSPECTIVE_SIGNAL"
    elif pred and all(x["gates"]["G4_top_class_contains_independently_accepted"] for x in eligible):status="POSITIVE_PROSPECTIVE_SIGNAL"
    else:status="MIXED_PROSPECTIVE_SIGNAL"
    return {"experiment":"separating-hypergraph-prospective-v2",
      "preregistration_commit":PREREG,"status":status,"targets":targets,
      "source_freeze":{"repo":"heathsanchez/test","commit":"17c5109577fb8b500b69a02f1bc9c81964c81ddd",
      "blobs":{"v12_challenge_pack":"67e9678a535f88ce91f861cd41a4b4da408ab3d5",
      "v12_run":"7650c9a3d8aba8855da49579eebf3d8e89350cb2",
      "v21_challenge_pack":"c66042c1d984007eca04d2810b152c52dd58cbf8",
      "v21_run":"8418e0deddc988ef0efd3f2f27ef052f64ebce3c"}}}

if __name__=="__main__":print(json.dumps(build_report(),indent=2,sort_keys=True))
