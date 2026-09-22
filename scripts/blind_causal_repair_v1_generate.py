from __future__ import annotations

import argparse
import hashlib
import json
import random
import secrets
from pathlib import Path

PREREG = "fe78b5bb256a20eecfe3195f4bed1a65f45ca1b9"


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def bits(x):
    return ((x >> 0) & 1, (x >> 1) & 1, (x >> 2) & 1, (x >> 3) & 1)


def pack(source, hidden, observed, noise):
    return source | (hidden << 1) | (observed << 2) | (noise << 3)


def latent_action(name, x):
    s, h, o, n = bits(x)
    if name == "A_source_to_hidden":
        return pack(s, s, o, n)
    if name == "B_hidden_to_observed":
        return pack(s, h, h, n)
    if name == "D_identity":
        return x
    if name == "D_toggle_noise":
        return pack(s, h, o, 1 - n)
    if name == "D_noise_to_hidden":
        return pack(s, n, o, n)
    if name == "D_hidden_to_noise":
        return pack(s, h, o, h)
    raise ValueError(name)


def build(seed=None):
    seed = secrets.randbits(256) if seed is None else int(seed)
    rng = random.Random(seed)

    latent_states = list(range(16))
    rng.shuffle(latent_states)
    public_of_latent = {latent: i for i, latent in enumerate(latent_states)}

    semantic_actions = [
        "A_source_to_hidden",
        "B_hidden_to_observed",
        "D_identity",
        "D_toggle_noise",
        "D_noise_to_hidden",
        "D_hidden_to_noise",
    ]
    shuffled = list(semantic_actions)
    rng.shuffle(shuffled)
    action_ids = [f"g{i:02d}" for i in range(len(shuffled))]
    id_to_semantic = dict(zip(action_ids, shuffled))
    semantic_to_id = {v: k for k, v in id_to_semantic.items()}

    actions = {}
    for aid, semantic in id_to_semantic.items():
        row = []
        for latent in latent_states:
            nxt = latent_action(semantic, latent)
            row.append(public_of_latent[nxt])
        actions[aid] = row

    protected = [bits(latent)[2] for latent in latent_states]
    target_keys = [(bits(latent)[2], bits(latent)[0]) for latent in latent_states]
    distinct = sorted(set(target_keys))
    labels = list(range(len(distinct)))
    rng.shuffle(labels)
    key_to_class = dict(zip(distinct, labels))
    target = [key_to_class[k] for k in target_keys]

    planted = [
        semantic_to_id["A_source_to_hidden"],
        semantic_to_id["B_hidden_to_observed"],
    ]
    reverse = list(reversed(planted))

    public = {
        "schema": "metatron.blind.causal-repair.v1.public",
        "preregistration_commit": PREREG,
        "state_ids": list(range(16)),
        "protected_observation": protected,
        "target_future_class": target,
        "actions": actions,
        "repair_language": {
            "kind": "ordered_chain",
            "min_events": 1,
            "max_events": 2,
            "allow_repeated_actions": True,
        },
    }

    hidden = {
        "schema": "metatron.blind.causal-repair.v1.hidden",
        "seed_hex": f"{seed:064x}",
        "public_state_to_latent": latent_states,
        "action_id_to_semantic": id_to_semantic,
        "planted_ordered_repair": planted,
        "reverse_ordered_repair": reverse,
        "target_key_to_public_class": {
            f"{a}{b}": c for (a, b), c in key_to_class.items()
        },
        "nonce": secrets.token_hex(32),
    }

    hidden_bytes = canonical_bytes(hidden)
    public["hidden_sha256"] = hashlib.sha256(hidden_bytes).hexdigest()

    return public, hidden_bytes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", required=True)
    ap.add_argument("--hidden", required=True)
    args = ap.parse_args()

    public, hidden_bytes = build()
    Path(args.public).parent.mkdir(parents=True, exist_ok=True)
    Path(args.hidden).parent.mkdir(parents=True, exist_ok=True)
    Path(args.public).write_bytes(canonical_bytes(public))
    Path(args.hidden).write_bytes(hidden_bytes)

    print(json.dumps({
        "status": "SEALED",
        "states": len(public["state_ids"]),
        "actions": len(public["actions"]),
        "hidden_sha256": public["hidden_sha256"],
        "preregistration_commit": public["preregistration_commit"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
