from __future__ import annotations
import argparse, hashlib, json, random, secrets
from pathlib import Path

PREREG="5303b4001852b890692737536a36c802d1cb4cc0"

def cb(o):
    return (json.dumps(o,sort_keys=True,separators=(",",":"))+"\n").encode()

def bits(x):
    return ((x>>0)&1,(x>>1)&1,(x>>2)&1,(x>>3)&1)

def atom_value(name,x):
    h1,h2,v,n=bits(x)
    if name=="maskedA": return h1 ^ n
    if name=="maskedB": return h2 ^ n
    if name=="noise": return n
    if name=="visible": return v
    raise ValueError(name)

def build():
    seed=secrets.randbits(256)
    rng=random.Random(seed)

    latent=list(range(16))
    rng.shuffle(latent)

    atom_names=["maskedA","maskedB","noise","visible"]
    shuffled=list(atom_names)
    rng.shuffle(shuffled)
    atom_ids=[f"a{i:02d}" for i in range(4)]
    id_to_sem=dict(zip(atom_ids,shuffled))
    sem_to_id={v:k for k,v in id_to_sem.items()}

    atoms={
        aid:[atom_value(name,x) for x in latent]
        for aid,name in id_to_sem.items()
    }

    protected=[bits(x)[2] for x in latent]

    target_keys=[(bits(x)[2],bits(x)[0],bits(x)[1]) for x in latent]
    distinct=sorted(set(target_keys))
    labels=list(range(len(distinct)))
    rng.shuffle(labels)
    key_to_class=dict(zip(distinct,labels))
    target=[key_to_class[k] for k in target_keys]

    planted=[
        sorted([sem_to_id["maskedA"],sem_to_id["noise"]]),
        sorted([sem_to_id["maskedB"],sem_to_id["noise"]]),
    ]

    hidden={
        "schema":"metatron.blind.residual-generated-capability.v0.hidden",
        "seed_hex":f"{seed:064x}",
        "public_state_to_latent":latent,
        "atom_id_to_semantic":id_to_sem,
        "planted_generated_basis":sorted(planted),
        "nonce":secrets.token_hex(32),
    }
    hb=cb(hidden)

    public={
        "schema":"metatron.blind.residual-generated-capability.v0.public",
        "preregistration_commit":PREREG,
        "state_ids":list(range(16)),
        "protected_outcome":protected,
        "target_class":target,
        "primitive_atoms":atoms,
        "constructors":["xor"],
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
        "states":16,
        "primitive_atoms":4,
        "constructors":public["constructors"],
        "hidden_sha256":public["hidden_sha256"],
    },sort_keys=True))

if __name__=="__main__":
    main()
