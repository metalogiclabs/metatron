from __future__ import annotations

import argparse
import hashlib
import json
import random
import secrets
from pathlib import Path


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parity(x):
    return x.bit_count() & 1


def rank_gf2(masks, width=6):
    rows = [int(x) for x in masks if x]
    rank = 0
    for bit in reversed(range(width)):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def choose_independent(rng, count=4, width=6):
    chosen = []
    while len(chosen) < count:
        mask = rng.randrange(1, 1 << width)
        if rank_gf2(chosen + [mask], width) == len(chosen) + 1:
            chosen.append(mask)
    return tuple(chosen)


def build():
    seed = secrets.randbits(256)
    rng = random.Random(seed)
    width = 6
    latent_states = list(range(1 << width))
    rng.shuffle(latent_states)

    protected_mask, h1, h2, h3 = choose_independent(rng, 4, width)
    hidden_masks = (h1, h2, h3)

    target_keys = [
        (
            parity(latent & protected_mask),
            parity(latent & h1),
            parity(latent & h2),
            parity(latent & h3),
        )
        for latent in latent_states
    ]
    distinct_keys = sorted(set(target_keys))
    class_labels = list(range(len(distinct_keys)))
    rng.shuffle(class_labels)
    key_to_class = dict(zip(distinct_keys, class_labels))

    masks = list(range(1, 1 << width))
    rng.shuffle(masks)
    candidate_ids = [f"g{i:02d}" for i in range(len(masks))]
    id_to_mask = dict(zip(candidate_ids, masks))
    mask_to_id = {mask: cid for cid, mask in id_to_mask.items()}

    protected = [parity(latent & protected_mask) for latent in latent_states]
    target_class = [key_to_class[key] for key in target_keys]
    candidates = {
        cid: [parity(latent & mask) for latent in latent_states]
        for cid, mask in id_to_mask.items()
    }

    planted_ids = tuple(sorted(mask_to_id[m] for m in hidden_masks))

    hidden = {
        "schema": "metatron.blind.hypergraph.v3.hidden",
        "seed_hex": f"{seed:064x}",
        "width": width,
        "public_state_to_latent": latent_states,
        "protected_mask": protected_mask,
        "hidden_target_masks": list(hidden_masks),
        "candidate_id_to_mask": id_to_mask,
        "planted_candidate_ids": list(planted_ids),
        "target_key_to_public_class": {
            "".join(map(str, key)): value for key, value in key_to_class.items()
        },
        "nonce": secrets.token_hex(32),
    }
    hidden_bytes = canonical_bytes(hidden)
    hidden_sha256 = hashlib.sha256(hidden_bytes).hexdigest()

    public = {
        "schema": "metatron.blind.hypergraph.v3.public",
        "preregistration_commit": "dd372680c86c43c925c10fc228faac8af63bfc22",
        "state_ids": list(range(1 << width)),
        "protected_outcome": protected,
        "target_future_class": target_class,
        "candidate_outcomes": candidates,
        "hidden_sha256": hidden_sha256,
    }
    return public, hidden, hidden_bytes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", required=True)
    ap.add_argument("--hidden", required=True)
    args = ap.parse_args()
    public, hidden, hidden_bytes = build()

    Path(args.public).parent.mkdir(parents=True, exist_ok=True)
    Path(args.hidden).parent.mkdir(parents=True, exist_ok=True)
    Path(args.public).write_bytes(canonical_bytes(public))
    Path(args.hidden).write_bytes(hidden_bytes)

    print(json.dumps({
        "status": "SEALED",
        "public_states": len(public["state_ids"]),
        "candidate_count": len(public["candidate_outcomes"]),
        "hidden_sha256": public["hidden_sha256"],
        "preregistration_commit": public["preregistration_commit"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
