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
Mask = int


@dataclass(frozen=True)
class Witness:
    op: str
    coord: int
    table: tuple[int, int]

    def ast(self) -> dict:
        return {
            "op": self.op,
            "coord": self.coord,
            "table": list(self.table),
        }


def weight(x: int) -> int:
    return x.bit_count()


def closure_masks(dim: int, installed_local: tuple[int, ...]) -> tuple[Mask, ...]:
    # The pre-existing meta-language has one generator: global complement.
    # Concrete local rewrites, once warranted, are additional generators.
    generators = [((1 << dim) - 1)] + [1 << i for i in installed_local]
    seen = {0}
    frontier = [0]
    while frontier:
        m = frontier.pop()
        for g in generators:
            nxt = m ^ g
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    return tuple(sorted(seen))


def observation_signature(state: State, masks: tuple[Mask, ...]) -> tuple[int, ...]:
    return tuple(weight(state ^ m) for m in masks)


def residual(states: tuple[State, ...], dim: int, installed_local: tuple[int, ...]) -> tuple[Pair, ...]:
    masks = closure_masks(dim, installed_local)
    # Frozen future demand is full state identity. Therefore every distinct pair
    # still merged by the current observation language is consequential.
    return tuple(
        (x, y)
        for x in states
        for y in states
        if x < y
        and observation_signature(x, masks) == observation_signature(y, masks)
    )


def generated_gain(
    current_residual: tuple[Pair, ...],
    dim: int,
    installed_local: tuple[int, ...],
    witness: Witness,
) -> tuple[Pair, ...]:
    before = set(closure_masks(dim, installed_local))
    if witness.op != "LocalRewrite":
        raise ValueError("unknown generic-grammar op")
    if witness.table not in ((0, 1), (1, 0)):
        raise ValueError("witness must be a bijective unary Boolean table")
    if witness.table == (0, 1):
        after = before
    else:
        after = set(
            closure_masks(dim, tuple(sorted(set(installed_local) | {witness.coord})))
        )
    new_masks = tuple(sorted(after - before))
    return tuple(
        (x, y)
        for x, y in current_residual
        if any(weight(x ^ m) != weight(y ^ m) for m in new_masks)
    )


def current_meta_language_max_gain(
    current_residual: tuple[Pair, ...],
    dim: int,
    installed_local: tuple[int, ...],
) -> int:
    # The declared current meta-language contains only the global-complement
    # constructor, already fully closed. Reapplying it adds no observation.
    before = set(closure_masks(dim, installed_local))
    complemented = {m ^ ((1 << dim) - 1) for m in before}
    after = before | complemented
    if after != before:
        raise AssertionError("current meta-language closure was not saturated")
    return 0


def concrete_grammar(dim: int) -> tuple[Witness, ...]:
    # Generic meta-meta grammar: one-coordinate unary Boolean rewrites.
    # The grammar enumerates truth tables and filters for bijective local maps.
    tables = ((0, 0), (0, 1), (1, 0), (1, 1))
    out = []
    for coord in range(dim):
        for table in tables:
            if sorted(table) != [0, 1]:
                continue
            out.append(Witness("LocalRewrite", coord, table))
    return tuple(out)


def synthesize_concrete(
    current_residual: tuple[Pair, ...],
    dim: int,
    installed_local: tuple[int, ...],
) -> tuple[Witness, tuple[Pair, ...], tuple[Witness, ...]]:
    """Residual-driven generic synthesis.

    The synthesizer sees residual + installed language + generic grammar only.
    It receives no target relation and no predeclared Toggle/Flip schema.
    """
    scored = []
    for witness in concrete_grammar(dim):
        if witness.coord in installed_local and witness.table == (1, 0):
            continue
        gain = generated_gain(current_residual, dim, installed_local, witness)
        if gain:
            scored.append((len(gain), witness.coord, witness.table, witness, gain))
    if not scored:
        raise RuntimeError("META_META_STUCK: generic grammar has no positive witness")
    best = max(x[0] for x in scored)
    frontier = tuple(
        x[3]
        for x in sorted(scored, key=lambda z: (z[1], z[2]))
        if x[0] == best
    )
    chosen = frontier[0]
    return chosen, generated_gain(current_residual, dim, installed_local, chosen), frontier


def anti_unify_successes(successes: tuple[Witness, ...]) -> dict | None:
    """Promote a reusable constructor only from replicated concrete witnesses."""
    if len(successes) < 2:
        return None
    a, b = successes[-2], successes[-1]
    if a.op != b.op or a.table != b.table or a.coord == b.coord:
        return None
    return {
        "op": a.op,
        "coord": "$i",
        "table": list(a.table),
        "induced_from_coords": [a.coord, b.coord],
    }


def instantiate_induced(
    current_residual: tuple[Pair, ...],
    dim: int,
    installed_local: tuple[int, ...],
    schema: dict,
) -> tuple[Witness, tuple[Pair, ...], tuple[Witness, ...]]:
    if schema != {
        "op": "LocalRewrite",
        "coord": "$i",
        "table": [1, 0],
        "induced_from_coords": schema["induced_from_coords"],
    }:
        raise ValueError("unsupported induced schema")
    table = tuple(schema["table"])
    scored = []
    for coord in range(dim):
        if coord in installed_local:
            continue
        witness = Witness(schema["op"], coord, table)
        gain = generated_gain(current_residual, dim, installed_local, witness)
        if gain:
            scored.append((len(gain), coord, witness, gain))
    if not scored:
        raise RuntimeError("INDUCED_SCHEMA_STUCK")
    best = max(x[0] for x in scored)
    frontier = tuple(x[2] for x in sorted(scored, key=lambda z: z[1]) if x[0] == best)
    chosen = frontier[0]
    return chosen, generated_gain(current_residual, dim, installed_local, chosen), frontier


def verify_witness(
    current_residual: tuple[Pair, ...],
    dim: int,
    installed_local: tuple[int, ...],
    witness: Witness,
    frontier: tuple[Witness, ...],
) -> dict:
    if current_meta_language_max_gain(current_residual, dim, installed_local) != 0:
        raise AssertionError("current meta-language is not actually exhausted")
    gain = generated_gain(current_residual, dim, installed_local, witness)
    if not gain:
        raise AssertionError("witness has no consequential gain")
    max_gain = max(
        len(generated_gain(current_residual, dim, installed_local, w))
        for w in frontier
    )
    if len(gain) != max_gain:
        raise AssertionError("witness is not frontier-optimal")
    return {
        "current_meta_language_max_gain": 0,
        "selected_gain": len(gain),
        "frontier_size": len(frontier),
    }


def installed_coords(log) -> tuple[int, ...]:
    coords = []
    for _, node in live(log, "concrete_rewrite_warrant"):
        coords.append(int(node.payload["coord"]))
    return tuple(sorted(set(coords)))


def promoted_schema(log) -> dict | None:
    rows = live(log, "schema_constructor_warrant")
    if not rows:
        return None
    return rows[-1][1].payload["schema"]


def run_once() -> dict:
    dim = 5
    states = tuple(range(1 << dim))
    log = ()

    seed = Node(
        "seed_interface",
        {
            "observation": "hamming_weight",
            "current_meta_language": "global_complement_closure",
        },
    )
    log = append(log, seed)
    demand = Node("future_demand", {"relation": "full_five_bit_identity"}, (seed.id,))
    log = append(log, demand)

    successes: list[Witness] = []
    witness_warrant_ids: list[str] = []
    residual_trace = []
    generations = []
    generic_synthesis_calls = 0
    induced_instantiation_calls = 0
    parent = demand.id

    while True:
        installed = installed_coords(log)
        current = residual(states, dim, installed)
        residual_trace.append(len(current))
        if not current:
            break

        internal_gain = current_meta_language_max_gain(current, dim, installed)
        if internal_gain != 0:
            raise AssertionError("constructor genesis triggered before language exhaustion")

        obstruction = Node(
            "meta_language_insufficiency",
            {
                "residual_count": len(current),
                "current_meta_language_max_gain": internal_gain,
                "installed_local_rewrites": list(installed),
            },
            (parent,),
        )
        log = append(log, obstruction)

        schema = promoted_schema(log)
        if schema is None:
            witness, covered, frontier = synthesize_concrete(current, dim, installed)
            generic_synthesis_calls += 1
            mode = "generic_concrete_synthesis"
        else:
            witness, covered, frontier = instantiate_induced(
                current, dim, installed, schema
            )
            induced_instantiation_calls += 1
            mode = "induced_schema_instantiation"

        verification = verify_witness(current, dim, installed, witness, frontier)

        proposal = Node(
            "concrete_rewrite_candidate",
            {
                "witness": witness.ast(),
                "mode": mode,
                "selector_input": "residual_only",
                "frontier": [w.ast() for w in frontier],
            },
            (obstruction.id,),
        )
        log = append(log, proposal)

        verified = Node(
            "concrete_rewrite_verification",
            {**verification, "verified": True},
            (obstruction.id, proposal.id),
        )
        log = append(log, verified)

        warrant = Node(
            "concrete_rewrite_warrant",
            {
                "op": witness.op,
                "coord": witness.coord,
                "table": list(witness.table),
                "mode": mode,
            },
            (verified.id, parent),
        )
        log = append(log, warrant)
        witness_warrant_ids.append(warrant.id)
        successes.append(witness)

        schema_promoted_now = False
        if promoted_schema(log) is None:
            induced = anti_unify_successes(tuple(successes))
            if induced is not None:
                schema_candidate = Node(
                    "schema_constructor_candidate",
                    {
                        "schema": induced,
                        "method": "structural_anti_unification",
                    },
                    tuple(witness_warrant_ids[-2:]),
                )
                log = append(log, schema_candidate)
                schema_verify = Node(
                    "schema_constructor_verification",
                    {
                        "replicated_instances": 2,
                        "same_operator": True,
                        "same_truth_table": True,
                        "distinct_parameters": True,
                    },
                    (schema_candidate.id,) + tuple(witness_warrant_ids[-2:]),
                )
                log = append(log, schema_verify)
                schema_warrant = Node(
                    "schema_constructor_warrant",
                    {"schema": induced},
                    (schema_verify.id,) + tuple(witness_warrant_ids[-2:]),
                )
                log = append(log, schema_warrant)
                schema_promoted_now = True

        installed_after = installed_coords(log)
        next_residual = residual(states, dim, installed_after)
        if len(next_residual) >= len(current):
            raise AssertionError("warranted rewrite did not reduce residual")

        generations.append(
            {
                "generation": len(generations) + 1,
                "mode": mode,
                "residual_before": len(current),
                "residual_after": len(next_residual),
                "selected_witness": witness.ast(),
                "selected_gain": len(covered),
                "frontier_size": len(frontier),
                "current_meta_language_max_gain": internal_gain,
                "schema_promoted_now": schema_promoted_now,
                "schema_available_after": promoted_schema(log) is not None,
            }
        )
        parent = warrant.id

    final_coords = installed_coords(log)
    final_residual = residual(states, dim, final_coords)

    restarted = loads(dumps(log))
    restart_coords = installed_coords(restarted)
    restart_schema = promoted_schema(restarted)

    sham = append(log, Node("measurement", {"diagnostic_only": True}))
    sham_coords = installed_coords(sham)

    knocked = append(
        log,
        Node("revoke", {"target": witness_warrant_ids[0]}, (witness_warrant_ids[-1],)),
    )
    knockout_coords = installed_coords(knocked)
    knockout_schema = promoted_schema(knocked)
    knockout_residual = residual(states, dim, knockout_coords)

    synth_args = tuple(inspect.signature(synthesize_concrete).parameters)
    induce_args = tuple(inspect.signature(instantiate_induced).parameters)

    return {
        "status": "PASS_CONSTRUCTOR_GENESIS",
        "selector_parameters": list(synth_args),
        "instantiator_parameters": list(induce_args),
        "selector_has_target_argument": any("target" in p for p in synth_args),
        "generation_count": len(generations),
        "residual_trace": residual_trace,
        "generations": generations,
        "generic_synthesis_calls": generic_synthesis_calls,
        "induced_instantiation_calls": induced_instantiation_calls,
        "schema": promoted_schema(log),
        "final_installed_coords": list(final_coords),
        "final_residual_count": len(final_residual),
        "restart": {
            "same_coords": restart_coords == final_coords,
            "same_schema": restart_schema == promoted_schema(log),
        },
        "semantic_sham": {
            "same_coords": sham_coords == final_coords,
        },
        "knockout": {
            "coords": list(knockout_coords),
            "schema_live": knockout_schema is not None,
            "residual_count": len(knockout_residual),
            "restores_seed_interface": knockout_coords == ()
            and knockout_schema is None
            and len(knockout_residual) == residual_trace[0],
        },
        "log_node_count": len(log),
    }


def report() -> dict:
    result = run_once()
    if result["residual_trace"] != [110, 54, 24, 8, 0]:
        raise AssertionError(result["residual_trace"])
    if result["generic_synthesis_calls"] != 2:
        raise AssertionError("schema promotion did not stop generic synthesis after replication")
    if result["induced_instantiation_calls"] != 2:
        raise AssertionError("held-out generations did not use induced schema")
    if result["schema"] is None:
        raise AssertionError("constructor schema was not promoted")
    if result["schema"]["op"] != "LocalRewrite":
        raise AssertionError(result["schema"])
    if result["schema"]["coord"] != "$i":
        raise AssertionError(result["schema"])
    if result["schema"]["table"] != [1, 0]:
        raise AssertionError(result["schema"])
    if result["final_residual_count"] != 0:
        raise AssertionError("target not reached")
    if not result["restart"]["same_coords"] or not result["restart"]["same_schema"]:
        raise AssertionError("restart failed")
    if not result["semantic_sham"]["same_coords"]:
        raise AssertionError("semantic sham changed interface")
    if not result["knockout"]["restores_seed_interface"]:
        raise AssertionError("knockout failed")
    if result["selector_has_target_argument"]:
        raise AssertionError("generic synthesizer must not receive target")

    # Held-out check: generations 3 and 4 must be schema instances, not fresh
    # generic synthesis.
    modes = [g["mode"] for g in result["generations"]]
    if modes != [
        "generic_concrete_synthesis",
        "generic_concrete_synthesis",
        "induced_schema_instantiation",
        "induced_schema_instantiation",
    ]:
        raise AssertionError(modes)

    return {
        "experiment": "constructor-genesis-v0",
        "claim_boundary": (
            "A reusable parameterized schema constructor is induced from two "
            "independently successful residual-driven concrete programs inside "
            "a declared generic local-rewrite grammar, then used on held-out "
            "parameters without further generic synthesis. This is not invention "
            "outside the generic grammar."
        ),
        "result": result,
        "verdict": "PASS_RESIDUAL_DRIVEN_CONSTRUCTOR_GENESIS",
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
