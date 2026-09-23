from __future__ import annotations
import argparse, hashlib, json, random, secrets
from pathlib import Path

PREREG="ddc8e28f4b3b8862bcf158e5f07587e657e01fa5"

def cb(o): return (json.dumps(o,sort_keys=True,separators=(",",":"))+"\n").encode()
def bits(x): return ((x>>0)&1,(x>>1)&1,(x>>2)&1)
def pack(s,h,o): return s|(h<<1)|(o<<2)
def sem(name,x):
    s,h,o=bits(x)
    if name=="X_toggle_source": return pack(1-s,h,o)
    if name=="Y_toggle_observed": return pack(s,h,1-o)
    if name=="A_source_to_hidden": return pack(s,s,o)
    if name=="B_hidden_to_observed": return pack(s,h,h)
    raise ValueError(name)

def commute(a,b):
    return all(sem(b,sem(a,s))==sem(a,sem(b,s)) for s in range(8))

def build():
    seed=secrets.randbits(256); rng=random.Random(seed)
    latent=list(range(8)); rng.shuffle(latent)
    pub_of={x:i for i,x in enumerate(latent)}
    names=["X_toggle_source","Y_toggle_observed","A_source_to_hidden","B_hidden_to_observed"]
    shuffled=list(names); rng.shuffle(shuffled)
    ids=[f"g{i:02d}" for i in range(4)]
    id_to_sem=dict(zip(ids,shuffled)); sem_to_id={v:k for k,v in id_to_sem.items()}
    actions={}
    for aid,name in id_to_sem.items():
        actions[aid]=[pub_of[sem(name,x)] for x in latent]
    safe=[]
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            if commute(id_to_sem[a],id_to_sem[b]):
                safe.append(sorted([a,b]))
    hidden={
        "schema":"metatron.blind.earned-commutation.v1.hidden",
        "seed_hex":f"{seed:064x}",
        "public_state_to_latent":latent,
        "action_id_to_semantic":id_to_sem,
        "hidden_commuting_pairs":sorted(safe),
        "nonce":secrets.token_hex(32),
    }
    hb=cb(hidden)
    public={
        "schema":"metatron.blind.earned-commutation.v1.public",
        "preregistration_commit":PREREG,
        "state_ids":list(range(8)),
        "actions":actions,
        "hidden_sha256":hashlib.sha256(hb).hexdigest(),
    }
    return public,hb

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True); ap.add_argument("--hidden",required=True)
    a=ap.parse_args(); public,hb=build()
    Path(a.public).parent.mkdir(parents=True,exist_ok=True)
    Path(a.hidden).parent.mkdir(parents=True,exist_ok=True)
    Path(a.public).write_bytes(cb(public)); Path(a.hidden).write_bytes(hb)
    print(json.dumps({"status":"SEALED","states":8,"actions":4,"hidden_sha256":public["hidden_sha256"]},sort_keys=True))
if __name__=="__main__": main()
