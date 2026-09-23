from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import secrets
from pathlib import Path

PREREG = "1fbac081555f1af53327c17ea337db823cef6e08"
DIM = 6


def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parity(bits):
    return sum(bits) & 1


def table_index(controls, target):
    idx = 0
    for b in controls:
        idx = 2 * idx + b
    return 2 * idx + target


def candidate_observation(candidate, bits):
    controls = [bits[i] for i in candidate["controls"]]
    target = bits[candidate["target"]]
    out = candidate["truth_table"][table_index(controls, target)]
    return parity(bits) ^ target ^ out


def class_ids(signatures):
    ids = {}
    out = []
    for sig in signatures:
        key = tuple(sig)
        if key not in ids:
            ids[key] = len(ids)
        out.append(ids[key])
    return out


def residual_pairs(current, target):
    return [
        (i, j)
        for i in range(len(current))
        for j in range(i + 1, len(current))
        if current[i] == current[j] and target[i] != target[j]
    ]


def candidate_gain(candidate, vectors, residual):
    values = [candidate_observation(candidate, bits) for bits in vectors]
    return sum(values[i] != values[j] for i, j in residual)


def candidate_closes(candidate, vectors, residual):
    if not residual:
        return False
    values = [candidate_observation(candidate, bits) for bits in vectors]
    return all(values[i] != values[j] for i, j in residual)


def bijective_tables(arity):
    tables = []
    for table in itertools.product((0, 1), repeat=2 ** arity):
        ok = True
        for prefix in range(2 ** (arity - 1)):
            if table[2 * prefix] == table[2 * prefix + 1]:
                ok = False
                break
        if ok:
            tables.append(tuple(table))
    return tuple(tables)


def all_specs(arity):
    out = []
    for target in range(DIM):
        controls_count = arity - 1
        for controls in itertools.permutations(
            [i for i in range(DIM) if i != target],
            controls_count,
        ):
            for table in bijective_tables(arity):
                out.append((arity, controls, target, table))
    return tuple(out)


def make_candidate(spec, cid):
    arity, controls, target, table = spec
    return {
        "id": cid,
        "arity": arity,
        "controls": list(controls),
        "target": target,
        "truth_table": list(table),
    }


def fresh_ids(rng, n):
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    ids = set()
    while len(ids) < n:
        ids.add("g_" + "".join(rng.choice(alphabet) for _ in range(10)))
    return list(ids)


def build_once(rng, seed_hex):
    planted_arity = rng.choice((2, 3))

    # Unary grammar is complete: all six targets times identity/negation.
    unary_specs = list(all_specs(1))

    # Keep the binary public pool deliberately sparse enough that its full
    # common refinement cannot force six-bit identity in the arity-3 case.
    binary_all = list(all_specs(2))
    rng.shuffle(binary_all)
    binary_specs = []
    seen = set()
    for spec in binary_all:
        key = (spec[1], spec[2], spec[3])
        if key in seen:
            continue
        seen.add(key)
        binary_specs.append(spec)
        if len(binary_specs) == 4:
            break

    ternary_all = list(all_specs(3))
    rng.shuffle(ternary_all)
    ternary_specs = ternary_all[:16]

    specs = unary_specs + binary_specs + ternary_specs
    ids = fresh_ids(rng, len(specs))
    rng.shuffle(ids)
    candidates = [make_candidate(spec, cid) for spec, cid in zip(specs, ids)]
    rng.shuffle(candidates)

    vectors = [
        [(state >> i) & 1 for i in range(DIM)]
        for state in range(1 << DIM)
    ]
    order = list(range(len(vectors)))
    rng.shuffle(order)
    vectors = [vectors[i] for i in order]
    state_ids = list(range(len(vectors)))

    lower = [c for c in candidates if c["arity"] < planted_arity]
    current_sigs = []
    for bits in vectors:
        sig = [parity(bits)]
        sig.extend(candidate_observation(c, bits) for c in lower)
        current_sigs.append(sig)
    current = class_ids(current_sigs)

    planted_options = [c for c in candidates if c["arity"] == planted_arity]
    rng.shuffle(planted_options)
    for planted in planted_options:
        planted_values = [candidate_observation(planted, bits) for bits in vectors]
        target = class_ids([
            tuple(current_sigs[i]) + (planted_values[i],)
            for i in range(len(vectors))
        ])
        residual = residual_pairs(current, target)
        if not residual:
            continue

        lower_gains = [
            candidate_gain(c, vectors, residual)
            for c in candidates
            if c["arity"] < planted_arity
        ]
        if any(lower_gains):
            continue
        if not candidate_closes(planted, vectors, residual):
            continue

        exact = [
            c["id"] for c in candidates
            if c["arity"] == planted_arity
            and candidate_closes(c, vectors, residual)
        ]
        if not exact:
            continue

        hidden = {
            "schema": "metatron.blind.grammar_shape.v1.hidden",
            "preregistration_commit": PREREG,
            "generator_seed": seed_hex,
            "planted_minimum_arity": planted_arity,
            "planted_candidate_id": planted["id"],
            "planted_candidate": planted,
            "true_minimum_exact_closers": sorted(exact),
            "residual_pair_count": len(residual),
        }
        hidden_sha = hashlib.sha256(canonical_bytes(hidden)).hexdigest()

        public = {
            "schema": "metatron.blind.grammar_shape.v1.public",
            "preregistration_commit": PREREG,
            "dimension": DIM,
            "state_ids": state_ids,
            "state_vectors": vectors,
            "seed_observation": "bit_parity",
            "current_class": current,
            "target_future_class": target,
            "candidates": candidates,
            "hidden_sha256": hidden_sha,
        }
        return public, hidden

    return None


def generate():
    seed_hex = secrets.token_hex(32)
    seed = int(seed_hex, 16)
    for attempt in range(512):
        rng = random.Random(seed + attempt)
        built = build_once(rng, seed_hex)
        if built is not None:
            public, hidden = built
            hidden["resample_attempt"] = attempt
            # Recompute commitment after recording the accepted attempt.
            hidden_sha = hashlib.sha256(canonical_bytes(hidden)).hexdigest()
            public["hidden_sha256"] = hidden_sha
            return public, hidden
    raise RuntimeError("could not generate an eligible blind grammar-shape challenge")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--public", required=True)
    ap.add_argument("--hidden", required=True)
    args = ap.parse_args()

    public, hidden = generate()
    Path(args.public).parent.mkdir(parents=True, exist_ok=True)
    Path(args.hidden).parent.mkdir(parents=True, exist_ok=True)
    Path(args.public).write_bytes(canonical_bytes(public))
    Path(args.hidden).write_bytes(canonical_bytes(hidden))

    print(json.dumps({
        "status": "BLIND_GRAMMAR_CHALLENGE_SEALED",
        "preregistration_commit": PREREG,
        "candidate_count": len(public["candidates"]),
        "residual_pair_count": hidden["residual_pair_count"],
        "hidden_sha256": public["hidden_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
