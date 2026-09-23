from __future__ import annotations
import argparse, hashlib, json, random, secrets
from pathlib import Path

PREREG="484b14d0c9cfcc0440c4808acfe0951427005112"

def cb(o):
    return (json.dumps(o,sort_keys=True,separators=(",",":"))+"\n").encode()

def bits(x):
    return ((x>>0)&1,(x>>1)&1,(x>>2)&1)

def candidate_value(name,x):
    h,v,n=bits(x)
    if name=="noise": return n
    if name=="hidden_xor_noise": return h ^ n
    if name=="visible": return v
    if name=="visible_xor_noise": return v ^ n
    if name=="constant_false": return 0
    raise ValueError(name)

def build():
    seed=secrets.randbits(256)
    rng=random.Random(seed)

    latent=list(range(8))
    rng.shuffle(latent)

    candidate_names=[
        "noise",
        "hidden_xor_noise",
        "visible",
        "visible_xor_noise",
        "constant_false",
    ]
    shuffled=list(candidate_names)
    rng.shuffle(shuffled)
    ids=[f"c{i:02d}" for i in range(len(shuffled))]
    id_to_sem=dict(zip(ids,shuffled))
    sem_to_id={v:k for k,v in id_to_sem.items()}

    protected=[bits(x)[1] for x in latent]

    target_keys=[(bits(x)[1],bits(x)[0]) for x in latent]
    distinct=sorted(set(target_keys))
    labels=list(range(len(distinct)))
    rng.shuffle(labels)
    key_to_class=dict(zip(distinct,labels))
    target=[key_to_class[k] for k in target_keys]

    candidates={
        cid:[candidate_value(name,x) for x in latent]
        for cid,name in id_to_sem.items()
    }

    current_blocks={}
    for i,v in enumerate(protected):
        current_blocks.setdefault(v,[]).append(i)
    current_blocks=list(current_blocks.values())

    def novel(cid):
        vals=candidates[cid]
        return any(len({vals[s] for s in block})>1 for block in current_blocks)

    hidden_novel=sorted(cid for cid in ids if novel(cid))
    planted=sorted([
        sem_to_id["noise"],
        sem_to_id["hidden_xor_noise"],
    ])

    hidden={
        "schema":"metatron.blind.novel-capability.v0.hidden",
        "seed_hex":f"{seed:064x}",
        "public_state_to_latent":latent,
        "candidate_id_to_semantic":id_to_sem,
        "hidden_novel_candidates":hidden_novel,
        "planted_minimum_basis":planted,
        "nonce":secrets.token_hex(32),
    }
    hb=cb(hidden)

    public={
        "schema":"metatron.blind.novel-capability.v0.public",
        "preregistration_commit":PREREG,
        "state_ids":list(range(8)),
        "protected_outcome":protected,
        "target_class":target,
        "candidate_tests":candidates,
        "hidden_sha256":hashlib.sha256(hb).hexdigest(),
    }
    return public,hb

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--public",required=True)
    ap.add_argument("--hidden",required=True)
    a=ap.parse_args()
    public,hb=build()
    Path(a.public).parent.mkdir(parents=True,exist_ok=True)
    Path(a.hidden).parent.mkdir(parents=True,exist_ok=True)
    Path(a.public).write_bytes(cb(public))
    Path(a.hidden).write_bytes(hb)
    print(json.dumps({
        "status":"SEALED",
        "states":len(public["state_ids"]),
        "candidate_tests":len(public["candidate_tests"]),
        "hidden_sha256":public["hidden_sha256"],
    },sort_keys=True))

if __name__=="__main__":
    main()
