from __future__ import annotations
import argparse, hashlib, json, random, secrets
from pathlib import Path

PREREG="0681cc9b03d11df385fbd76d9c3c3e7b01de855f"

def cb(o): return (json.dumps(o,sort_keys=True,separators=(",",":"))+"\n").encode()
def bits(x): return ((x>>0)&1,(x>>1)&1)
def pack(h,o): return h|(o<<1)
def sem(name,x):
    h,o=bits(x)
    if name=="H0_hidden_false": return pack(0,o)
    if name=="HT_hidden_toggle": return pack(1-h,o)
    if name=="O0_observed_false": return pack(h,0)
    if name=="OT_observed_toggle": return pack(h,1-o)
    raise ValueError(name)
def exact_commute(a,b):
    return all(sem(b,sem(a,s))==sem(a,sem(b,s)) for s in range(4))
def behavioral_commute(a,b):
    return all(bits(sem(b,sem(a,s)))[1]==bits(sem(a,sem(b,s)))[1] for s in range(4))

def build():
    seed=secrets.randbits(256); rng=random.Random(seed)
    latent=list(range(4)); rng.shuffle(latent)
    public_of={x:i for i,x in enumerate(latent)}
    names=["H0_hidden_false","HT_hidden_toggle","O0_observed_false","OT_observed_toggle"]
    shuffled=list(names); rng.shuffle(shuffled)
    ids=[f"g{i:02d}" for i in range(4)]
    id_to_sem=dict(zip(ids,shuffled))
    actions={}
    for aid,name in id_to_sem.items():
        actions[aid]=[public_of[sem(name,x)] for x in latent]
    class_labels=[0,1]; rng.shuffle(class_labels)
    behavioral_class=[class_labels[bits(x)[1]] for x in latent]
    exact=[]; behavioral=[]
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            p=sorted([a,b])
            sa,sb=id_to_sem[a],id_to_sem[b]
            if exact_commute(sa,sb): exact.append(p)
            if behavioral_commute(sa,sb): behavioral.append(p)
    hidden={
      "schema":"metatron.blind.behavioral-commutation.v1.hidden",
      "seed_hex":f"{seed:064x}",
      "public_state_to_latent":latent,
      "action_id_to_semantic":id_to_sem,
      "hidden_exact_pairs":sorted(exact),
      "hidden_behavioral_pairs":sorted(behavioral),
      "nonce":secrets.token_hex(32),
    }
    hb=cb(hidden)
    public={
      "schema":"metatron.blind.behavioral-commutation.v1.public",
      "preregistration_commit":PREREG,
      "state_ids":list(range(4)),
      "actions":actions,
      "behavioral_class":behavioral_class,
      "hidden_sha256":hashlib.sha256(hb).hexdigest(),
    }
    return public,hb

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--public",required=True); ap.add_argument("--hidden",required=True)
    a=ap.parse_args(); public,hb=build()
    Path(a.public).parent.mkdir(parents=True,exist_ok=True)
    Path(a.hidden).parent.mkdir(parents=True,exist_ok=True)
    Path(a.public).write_bytes(cb(public)); Path(a.hidden).write_bytes(hb)
    print(json.dumps({"status":"SEALED","states":4,"actions":4,"hidden_sha256":public["hidden_sha256"]},sort_keys=True))
if __name__=="__main__": main()
