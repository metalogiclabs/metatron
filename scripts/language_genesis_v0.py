from __future__ import annotations

import argparse
import inspect
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from runtime.metatron.nucleus import Node, append, dumps, live, loads


State = int
Pair = tuple[int, int]
Perm = tuple[int, ...]


@dataclass(frozen=True)
class Schema:
    schema_id: str
    swap: tuple[int, int]


def identity_perm(dim: int) -> Perm:
    return tuple(range(dim))


def swap_perm(dim: int, i: int, j: int) -> Perm:
    p = list(range(dim))
    p[i], p[j] = p[j], p[i]
    return tuple(p)


def compose(p: Perm, q: Perm) -> Perm:
    # T_q after T_p, where output bit k of T_p is input bit p[k].
    return tuple(p[q[k]] for k in range(len(p)))


def closure_group(generators: tuple[Perm, ...], dim: int) -> tuple[Perm, ...]:
    ident = identity_perm(dim)
    seen = {ident}
    frontier = [ident]
    while frontier:
        p = frontier.pop()
        for g in generators:
            for nxt in (compose(p, g), compose(g, p)):
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
    return tuple(sorted(seen))


def observed_coords(generators: tuple[Perm, ...], dim: int) -> tuple[int, ...]:
    return tuple(sorted({p[0] for p in closure_group(generators, dim)}))


def bit(coord: int, state: State) -> int:
    return (state >> coord) & 1


def signature(state: State, coords: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(bit(i, state) for i in coords)


def current_residual(states: tuple[State, ...], installed: tuple[Perm, ...], dim: int) -> tuple[Pair, ...]:
    coords = observed_coords(installed, dim)
    # Frozen future demand is full state identity. Therefore every distinct pair
    # still merged by the current interface is consequentially unresolved.
    return tuple(
        (x, y)
        for x in states
        for y in states
        if x < y and signature(x, coords) == signature(y, coords)
    )


def schema_gain(
    residual: tuple[Pair, ...],
    installed: tuple[Perm, ...],
    schema: Schema,
    dim: int,
) -> tuple[Pair, ...]:
    before = set(observed_coords(installed, dim))
    candidate = swap_perm(dim, *schema.swap)
    after = set(observed_coords(installed + (candidate,), dim))
    gained = tuple(sorted(after - before))
    if not gained:
        return ()
    return tuple(
        (x, y)
        for x, y in residual
        if any(bit(i, x) != bit(i, y) for i in gained)
    )


def internal_process_gain(
    residual: tuple[Pair, ...],
    installed: tuple[Perm, ...],
    dim: int,
) -> int:
    # The active language is already closed under composition. Every internal
    # process is a member of this closure, so q0 after any such process is
    # already in the current observation set.
    current = set(observed_coords(installed, dim))
    best = 0
    for p in closure_group(installed, dim):
        coord = p[0]
        if coord in current:
            gain = 0
        else:
            gain = sum(bit(coord, x) != bit(coord, y) for x, y in residual)
        best = max(best, gain)
    return best


def choose_schema(
    residual: tuple[Pair, ...],
    installed: tuple[Perm, ...],
    schemas: tuple[Schema, ...],
    dim: int,
) -> tuple[Schema, tuple[Pair, ...], tuple[Schema, ...]]:
    """Choose a language extension from residual geometry only.

    No target relation or residual->repair mapping is accepted by this API.
    All schema instances have equal meta-cost. We maximize generated residual
    gain and retain the full equal-gain frontier. Canonical choice is by the
    schema's semantic swap pair, never its external name.
    """
    installed_swaps = {
        tuple(sorted((i, j)))
        for p in installed
        for i in range(dim)
        for j in range(i + 1, dim)
        if p == swap_perm(dim, i, j)
    }
    scored = []
    for schema in schemas:
        if schema.swap in installed_swaps:
            continue
        gain = schema_gain(residual, installed, schema, dim)
        if gain:
            scored.append((len(gain), schema.swap, schema, gain))
    if not scored:
        raise RuntimeError("LANGUAGE_STUCK: no declared schema extension has positive gain")
    max_gain = max(x[0] for x in scored)
    frontier = tuple(
        x[2] for x in sorted(scored, key=lambda z: z[1]) if x[0] == max_gain
    )
    chosen = frontier[0]
    gain = schema_gain(residual, installed, chosen, dim)
    return chosen, gain, frontier


def verify_schema(
    residual: tuple[Pair, ...],
    installed: tuple[Perm, ...],
    schemas: tuple[Schema, ...],
    selected: Schema,
    dim: int,
) -> dict:
    if not residual:
        raise AssertionError("language genesis requires a nonempty residual")
    if internal_process_gain(residual, installed, dim) != 0:
        raise AssertionError("current language is not actually insufficient")

    gain = schema_gain(residual, installed, selected, dim)
    if not gain:
        raise AssertionError("selected schema does not improve the residual")

    scored = [(len(schema_gain(residual, installed, s, dim)), s.swap, s) for s in schemas]
    best = max(n for n, _, _ in scored)
    frontier = tuple(s for n, _, s in sorted(scored, key=lambda z: z[1]) if n == best)
    if len(gain) != best:
        raise AssertionError("selected schema is not maximum-gain")
    if selected.swap != frontier[0].swap:
        raise AssertionError("selected schema violates semantic canonical order")

    return {
        "current_language_max_gain": 0,
        "selected_gain": len(gain),
        "frontier_swaps": [list(s.swap) for s in frontier],
        "frontier_size": len(frontier),
    }


def schema_family(dim: int, renamed: bool = False) -> tuple[Schema, ...]:
    swaps = tuple(itertools.combinations(range(dim), 2))
    ids = [f"swap_{i}_{j}" for i, j in swaps]
    if renamed:
        # Deliberately unrelated external names. Selection never uses them.
        names = ["zephyr", "quartz", "ember", "lumen", "nova", "rune"]
        ids = names[: len(swaps)]
    return tuple(Schema(name, pair) for name, pair in zip(ids, swaps))


def installed_from_log(log, dim: int) -> tuple[Perm, ...]:
    out = []
    for _, node in live(log, "schema_warrant"):
        i, j = node.payload["swap"]
        out.append(swap_perm(dim, i, j))
    return tuple(out)


def run_once(renamed: bool = False) -> dict:
    dim = 4
    states = tuple(range(1 << dim))
    schemas = schema_family(dim, renamed=renamed)
    log = ()

    seed = Node("seed_interface", {"protected_coordinate": 0})
    log = append(log, seed)
    demand = Node("future_demand", {"relation": "full_four_bit_identity"}, (seed.id,))
    log = append(log, demand)

    residual_trace = []
    generations = []
    schema_warrant_ids = []
    parent = demand.id

    while True:
        installed = installed_from_log(log, dim)
        residual = current_residual(states, installed, dim)
        residual_trace.append(len(residual))
        if not residual:
            break

        existing_gain = internal_process_gain(residual, installed, dim)
        if existing_gain != 0:
            raise AssertionError("expected active language closure to be stuck")

        obstruction = Node(
            "language_insufficiency",
            {
                "residual_count": len(residual),
                "current_observations": list(observed_coords(installed, dim)),
                "max_internal_process_gain": existing_gain,
            },
            (parent,),
        )
        log = append(log, obstruction)

        selected, covered, frontier = choose_schema(
            residual, installed, schemas, dim
        )
        verification = verify_schema(
            residual, installed, schemas, selected, dim
        )

        candidate = Node(
            "schema_candidate",
            {
                "schema_family": "coordinate_transposition",
                "schema_id": selected.schema_id,
                "swap": list(selected.swap),
                "selector_input": "residual_only",
                "equal_gain_frontier": [
                    {"schema_id": s.schema_id, "swap": list(s.swap)}
                    for s in frontier
                ],
            },
            (obstruction.id,),
        )
        log = append(log, candidate)

        verified = Node(
            "schema_verification",
            {
                **verification,
                "verified": True,
            },
            (obstruction.id, candidate.id),
        )
        log = append(log, verified)

        warrant = Node(
            "schema_warrant",
            {
                "schema_family": "coordinate_transposition",
                "schema_id": selected.schema_id,
                "swap": list(selected.swap),
            },
            (verified.id, parent),
        )
        log = append(log, warrant)
        schema_warrant_ids.append(warrant.id)

        installed_after = installed_from_log(log, dim)
        next_residual = current_residual(states, installed_after, dim)
        if len(next_residual) >= len(residual):
            raise AssertionError("schema genesis did not strictly refine interface")

        before_obs = set(observed_coords(installed, dim))
        after_obs = set(observed_coords(installed_after, dim))
        gained_obs = sorted(after_obs - before_obs)
        if not gained_obs:
            raise AssertionError("schema did not create a new observable continuation")

        generations.append(
            {
                "generation": len(generations) + 1,
                "residual_before": len(residual),
                "residual_after": len(next_residual),
                "selected_schema_id": selected.schema_id,
                "selected_swap": list(selected.swap),
                "selected_gain": len(covered),
                "observations_before": sorted(before_obs),
                "observations_after": sorted(after_obs),
                "new_observations": gained_obs,
                "current_language_max_gain": existing_gain,
                "frontier_size": len(frontier),
            }
        )
        parent = warrant.id

    final_installed = installed_from_log(log, dim)
    final_residual = current_residual(states, final_installed, dim)

    restarted = loads(dumps(log))
    restart_installed = installed_from_log(restarted, dim)
    restart_residual = current_residual(states, restart_installed, dim)

    sham_log = append(log, Node("measurement", {"diagnostic_only": True}))
    sham_installed = installed_from_log(sham_log, dim)
    sham_residual = current_residual(states, sham_installed, dim)

    knocked = append(
        log,
        Node("revoke", {"target": schema_warrant_ids[0]}, (schema_warrant_ids[-1],)),
    )
    knockout_installed = installed_from_log(knocked, dim)
    knockout_residual = current_residual(states, knockout_installed, dim)

    choose_args = tuple(inspect.signature(choose_schema).parameters)
    verify_args = tuple(inspect.signature(verify_schema).parameters)

    return {
        "status": "PASS_LANGUAGE_GENESIS",
        "renamed_schema_ids": renamed,
        "selector_parameters": list(choose_args),
        "verifier_parameters": list(verify_args),
        "selector_has_target_argument": any("target" in p for p in choose_args),
        "generation_count": len(generations),
        "residual_trace": residual_trace,
        "generations": generations,
        "selected_swaps": [g["selected_swap"] for g in generations],
        "final_observations": list(observed_coords(final_installed, dim)),
        "final_residual_count": len(final_residual),
        "restart": {
            "same_observations": observed_coords(restart_installed, dim)
            == observed_coords(final_installed, dim),
            "residual_count": len(restart_residual),
        },
        "semantic_sham": {
            "same_observations": observed_coords(sham_installed, dim)
            == observed_coords(final_installed, dim),
            "residual_count": len(sham_residual),
        },
        "knockout": {
            "observations": list(observed_coords(knockout_installed, dim)),
            "residual_count": len(knockout_residual),
            "restores_seed_interface": (
                observed_coords(knockout_installed, dim) == (0,)
                and len(knockout_residual) == residual_trace[0]
            ),
        },
        "log_node_count": len(log),
    }


def report() -> dict:
    primary = run_once(False)
    renamed = run_once(True)

    invariants = {
        "residual_trace": primary["residual_trace"] == renamed["residual_trace"],
        "selected_semantic_swaps": primary["selected_swaps"] == renamed["selected_swaps"],
        "generation_count": primary["generation_count"] == renamed["generation_count"],
        "final_observations": primary["final_observations"] == renamed["final_observations"],
    }
    if not all(invariants.values()):
        raise AssertionError(f"schema-name invariance failed: {invariants}")

    if primary["selector_has_target_argument"]:
        raise AssertionError("schema selector must not receive target")
    if primary["residual_trace"] != [56, 24, 8, 0]:
        raise AssertionError(primary["residual_trace"])
    if primary["selected_swaps"] != [[0, 1], [0, 2], [0, 3]]:
        raise AssertionError(primary["selected_swaps"])
    if any(g["current_language_max_gain"] != 0 for g in primary["generations"]):
        raise AssertionError("genesis occurred before language insufficiency")
    if primary["final_residual_count"] != 0:
        raise AssertionError("target future not reached")
    if not primary["restart"]["same_observations"]:
        raise AssertionError("restart mismatch")
    if not primary["semantic_sham"]["same_observations"]:
        raise AssertionError("semantic sham changed interface")
    if not primary["knockout"]["restores_seed_interface"]:
        raise AssertionError("G1 knockout did not retract descendants")

    return {
        "experiment": "language-genesis-v0",
        "claim_boundary": (
            "Finite declared meta-language of coordinate-transposition schemas. "
            "The experiment demonstrates residual-driven schema instantiation "
            "after exact language insufficiency, not unrestricted invention of "
            "the meta-language itself."
        ),
        "primary": primary,
        "schema_rename_control": {
            "invariants": invariants,
            "result": renamed,
        },
        "verdict": "PASS_RESIDUAL_DRIVEN_LANGUAGE_GENESIS",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    result = report()
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
