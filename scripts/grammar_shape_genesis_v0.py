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
Table = tuple[int, ...]


@dataclass(frozen=True)
class UnaryProgram:
    coord: int
    table: Table


@dataclass(frozen=True)
class BinaryProgram:
    control: int
    target: int
    table: Table

    def ast(self) -> dict:
        return {
            "op": "LocalTruthTableRewrite",
            "arity": 2,
            "control": self.control,
            "target": self.target,
            "table": list(self.table),
        }


def parity(state: State) -> int:
    return state.bit_count() & 1


def get_bit(state: State, coord: int) -> int:
    return (state >> coord) & 1


def set_bit(state: State, coord: int, value: int) -> State:
    if value:
        return state | (1 << coord)
    return state & ~(1 << coord)


def apply_unary(state: State, p: UnaryProgram) -> State:
    x = get_bit(state, p.coord)
    return set_bit(state, p.coord, p.table[x])


def apply_binary(state: State, p: BinaryProgram) -> State:
    c = get_bit(state, p.control)
    t = get_bit(state, p.target)
    out = p.table[2 * c + t]
    return set_bit(state, p.target, out)


def unary_grammar(dim: int) -> tuple[UnaryProgram, ...]:
    out = []
    for coord in range(dim):
        for table in itertools.product((0, 1), repeat=2):
            # State transformations must be bijective on the rewritten bit.
            if sorted(table) == [0, 1]:
                out.append(UnaryProgram(coord, tuple(table)))
    return tuple(out)


def binary_grammar(dim: int) -> tuple[BinaryProgram, ...]:
    out = []
    for control in range(dim):
        for target in range(dim):
            if control == target:
                continue
            for table in itertools.product((0, 1), repeat=4):
                # For each fixed control bit, target->output must be bijective.
                if table[0] == table[1] or table[2] == table[3]:
                    continue
                out.append(BinaryProgram(control, target, tuple(table)))
    return tuple(out)


def binary_depends_on_control(table: Table) -> bool:
    # For a target-bijective table, rewriting changes parity by a Boolean
    # function of the control. Dependence is detected extensionally.
    delta0 = table[0] ^ 0
    delta1 = table[2] ^ 0
    return delta0 != delta1


def revealed_controls(installed: tuple[BinaryProgram, ...]) -> tuple[int, ...]:
    return tuple(sorted({
        p.control for p in installed if binary_depends_on_control(p.table)
    }))


def interface_signature(
    state: State,
    installed: tuple[BinaryProgram, ...],
) -> tuple[int, ...]:
    # Full reclosure of this restricted affine family induces the same
    # partition as parity plus every control coordinate revealed by a
    # control-dependent installed binary rewrite.
    return (parity(state),) + tuple(
        get_bit(state, i) for i in revealed_controls(installed)
    )


def residual(
    states: tuple[State, ...],
    installed: tuple[BinaryProgram, ...],
) -> tuple[Pair, ...]:
    return tuple(
        (x, y)
        for x in states
        for y in states
        if x < y and interface_signature(x, installed) == interface_signature(y, installed)
    )


def unary_gain(
    current_residual: tuple[Pair, ...],
    p: UnaryProgram,
) -> tuple[Pair, ...]:
    return tuple(
        (x, y)
        for x, y in current_residual
        if parity(apply_unary(x, p)) != parity(apply_unary(y, p))
    )


def unary_grammar_max_gain(
    current_residual: tuple[Pair, ...],
    dim: int,
) -> int:
    return max(
        (len(unary_gain(current_residual, p)) for p in unary_grammar(dim)),
        default=0,
    )


def binary_gain(
    current_residual: tuple[Pair, ...],
    installed: tuple[BinaryProgram, ...],
    p: BinaryProgram,
) -> tuple[Pair, ...]:
    if p.control in revealed_controls(installed):
        return ()
    return tuple(
        (x, y)
        for x, y in current_residual
        if parity(apply_binary(x, p)) != parity(apply_binary(y, p))
    )


def synthesize_binary_shape(
    current_residual: tuple[Pair, ...],
    installed: tuple[BinaryProgram, ...],
    dim: int,
) -> tuple[BinaryProgram, tuple[Pair, ...], tuple[BinaryProgram, ...]]:
    """Search the extensional arity-2 truth-table grammar.

    No named binary operation, target relation, or residual->repair map is
    supplied. The smallest new arity is fixed by the preceding proof that the
    complete arity-1 grammar has zero gain.
    """
    if unary_grammar_max_gain(current_residual, dim) != 0:
        raise AssertionError("arity-1 grammar is not exhausted")

    scored = []
    for p in binary_grammar(dim):
        gain = binary_gain(current_residual, installed, p)
        if gain:
            scored.append((
                len(gain),
                p.control,
                p.target,
                p.table,
                p,
                gain,
            ))
    if not scored:
        raise RuntimeError("ARITY2_STUCK: no binary truth table has positive gain")

    best = max(row[0] for row in scored)
    frontier = tuple(
        row[4]
        for row in sorted(scored, key=lambda z: (z[1], z[2], z[3]))
        if row[0] == best
    )
    chosen = frontier[0]
    return chosen, binary_gain(current_residual, installed, chosen), frontier


def anti_unify_binary(successes: tuple[BinaryProgram, ...]) -> dict | None:
    if len(successes) < 2:
        return None
    a, b = successes[-2], successes[-1]
    if a.table != b.table:
        return None
    if a.control == b.control:
        return None

    control = "$control" if a.control != b.control else a.control
    target = "$target" if a.target != b.target else a.target
    return {
        "op": "LocalTruthTableRewrite",
        "arity": 2,
        "control": control,
        "target": target,
        "constraint": "control != target",
        "table": list(a.table),
        "induced_from": [a.ast(), b.ast()],
    }


def instantiate_constructor(
    current_residual: tuple[Pair, ...],
    installed: tuple[BinaryProgram, ...],
    schema: dict,
    dim: int,
) -> tuple[BinaryProgram, tuple[Pair, ...], tuple[BinaryProgram, ...]]:
    table = tuple(schema["table"])
    scored = []
    for control in range(dim):
        for target in range(dim):
            if control == target:
                continue
            p = BinaryProgram(control, target, table)
            gain = binary_gain(current_residual, installed, p)
            if gain:
                scored.append((len(gain), control, target, p, gain))
    if not scored:
        raise RuntimeError("INDUCED_BINARY_SCHEMA_STUCK")
    best = max(row[0] for row in scored)
    frontier = tuple(
        row[3] for row in sorted(scored, key=lambda z: (z[1], z[2]))
        if row[0] == best
    )
    chosen = frontier[0]
    return chosen, binary_gain(current_residual, installed, chosen), frontier


def verify_program(
    current_residual: tuple[Pair, ...],
    installed: tuple[BinaryProgram, ...],
    selected: BinaryProgram,
    frontier: tuple[BinaryProgram, ...],
    dim: int,
) -> dict:
    unary_max = unary_grammar_max_gain(current_residual, dim)
    if unary_max != 0:
        raise AssertionError("grammar-shape genesis attempted before unary exhaustion")

    gain = binary_gain(current_residual, installed, selected)
    if not gain:
        raise AssertionError("selected binary program has zero gain")
    frontier_gain = max(
        len(binary_gain(current_residual, installed, p)) for p in frontier
    )
    if len(gain) != frontier_gain:
        raise AssertionError("selected binary program is not frontier-optimal")

    return {
        "unary_grammar_max_gain": unary_max,
        "selected_gain": len(gain),
        "frontier_gain": frontier_gain,
        "frontier_size": len(frontier),
    }


def installed_programs(log) -> tuple[BinaryProgram, ...]:
    out = []
    for _, node in live(log, "binary_program_warrant"):
        payload = node.payload
        out.append(BinaryProgram(
            int(payload["control"]),
            int(payload["target"]),
            tuple(payload["table"]),
        ))
    return tuple(out)


def shape_warrant_live(log) -> bool:
    return bool(live(log, "grammar_shape_warrant"))


def constructor_schema(log) -> dict | None:
    rows = live(log, "binary_constructor_warrant")
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
            "observation": "bit_parity",
            "active_grammar_shape": "arity_1_local_truth_table_rewrite",
        },
    )
    log = append(log, seed)
    demand = Node("future_demand", {"relation": "full_five_bit_identity"}, (seed.id,))
    log = append(log, demand)

    successes: list[BinaryProgram] = []
    program_warrant_ids: list[str] = []
    residual_trace = []
    generations = []
    generic_binary_synthesis_calls = 0
    induced_constructor_calls = 0
    parent = demand.id
    shape_warrant_id: str | None = None

    while True:
        installed = installed_programs(log)
        current = residual(states, installed)
        residual_trace.append(len(current))
        if not current:
            break

        unary_max = unary_grammar_max_gain(current, dim)

        obstruction = Node(
            "grammar_insufficiency",
            {
                "residual_count": len(current),
                "current_arity": 1 if not shape_warrant_live(log) else 2,
                "complete_unary_grammar_max_gain": unary_max,
                "revealed_controls": list(revealed_controls(installed)),
            },
            (parent,),
        )
        log = append(log, obstruction)

        if not shape_warrant_live(log):
            if unary_max != 0:
                raise AssertionError("unary grammar was not actually insufficient")

            selected, covered, frontier = synthesize_binary_shape(
                current, installed, dim
            )
            generic_binary_synthesis_calls += 1

            shape_candidate = Node(
                "grammar_shape_candidate",
                {
                    "from_arity": 1,
                    "to_arity": 2,
                    "skeleton": "LocalTruthTableRewrite(control,target,table)",
                    "selected_witness": selected.ast(),
                    "selector_input": "residual_only",
                },
                (obstruction.id,),
            )
            log = append(log, shape_candidate)

            shape_verify = Node(
                "grammar_shape_verification",
                {
                    "arity_1_max_gain": unary_max,
                    "arity_2_selected_gain": len(covered),
                    "arity_2_frontier_size": len(frontier),
                    "verified": True,
                },
                (obstruction.id, shape_candidate.id),
            )
            log = append(log, shape_verify)

            shape_warrant = Node(
                "grammar_shape_warrant",
                {
                    "arity": 2,
                    "skeleton": "LocalTruthTableRewrite(control,target,table)",
                },
                (shape_verify.id,),
            )
            log = append(log, shape_warrant)
            shape_warrant_id = shape_warrant.id
            mode = "grammar_shape_genesis"
        else:
            schema = constructor_schema(log)
            if schema is None:
                selected, covered, frontier = synthesize_binary_shape(
                    current, installed, dim
                )
                generic_binary_synthesis_calls += 1
                mode = "generic_binary_synthesis"
            else:
                selected, covered, frontier = instantiate_constructor(
                    current, installed, schema, dim
                )
                induced_constructor_calls += 1
                mode = "induced_binary_constructor"

        verification = verify_program(
            current, installed, selected, frontier, dim
        )

        proposal_premises = [obstruction.id]
        if shape_warrant_id is not None:
            proposal_premises.append(shape_warrant_id)

        proposal = Node(
            "binary_program_candidate",
            {
                "program": selected.ast(),
                "mode": mode,
                "frontier_size": len(frontier),
            },
            tuple(proposal_premises),
        )
        log = append(log, proposal)

        verified = Node(
            "binary_program_verification",
            {**verification, "verified": True},
            (obstruction.id, proposal.id),
        )
        log = append(log, verified)

        warrant_premises = [verified.id, parent]
        if shape_warrant_id is not None:
            warrant_premises.append(shape_warrant_id)
        schema_now = constructor_schema(log)
        if mode == "induced_binary_constructor" and schema_now is not None:
            schema_rows = live(log, "binary_constructor_warrant")
            warrant_premises.append(schema_rows[-1][0])

        warrant = Node(
            "binary_program_warrant",
            {
                "control": selected.control,
                "target": selected.target,
                "table": list(selected.table),
                "mode": mode,
            },
            tuple(warrant_premises),
        )
        log = append(log, warrant)
        program_warrant_ids.append(warrant.id)
        successes.append(selected)

        constructor_promoted_now = False
        if constructor_schema(log) is None:
            induced = anti_unify_binary(tuple(successes))
            if induced is not None:
                constructor_candidate = Node(
                    "binary_constructor_candidate",
                    {
                        "schema": induced,
                        "method": "structural_anti_unification",
                    },
                    tuple(program_warrant_ids[-2:]),
                )
                log = append(log, constructor_candidate)

                constructor_verify = Node(
                    "binary_constructor_verification",
                    {
                        "replicated_instances": 2,
                        "same_arity": True,
                        "same_truth_table": True,
                        "distinct_controls": True,
                    },
                    (constructor_candidate.id,) + tuple(program_warrant_ids[-2:]),
                )
                log = append(log, constructor_verify)

                constructor_warrant = Node(
                    "binary_constructor_warrant",
                    {"schema": induced},
                    (constructor_verify.id,) + tuple(program_warrant_ids[-2:]),
                )
                log = append(log, constructor_warrant)
                constructor_promoted_now = True

        installed_after = installed_programs(log)
        next_residual = residual(states, installed_after)
        if len(next_residual) >= len(current):
            raise AssertionError("new grammar/program did not strictly reduce residual")

        generations.append(
            {
                "generation": len(generations) + 1,
                "mode": mode,
                "residual_before": len(current),
                "residual_after": len(next_residual),
                "selected_program": selected.ast(),
                "selected_gain": len(covered),
                "frontier_size": len(frontier),
                "unary_grammar_max_gain": unary_max,
                "constructor_promoted_now": constructor_promoted_now,
                "constructor_available_after": constructor_schema(log) is not None,
                "revealed_controls_after": list(revealed_controls(installed_after)),
            }
        )
        parent = warrant.id

    final_installed = installed_programs(log)
    final_residual = residual(states, final_installed)

    restarted = loads(dumps(log))
    restart_installed = installed_programs(restarted)

    sham = append(log, Node("measurement", {"diagnostic_only": True}))
    sham_installed = installed_programs(sham)

    knocked = append(
        log,
        Node("revoke", {"target": program_warrant_ids[0]}, (program_warrant_ids[-1],)),
    )
    knockout_installed = installed_programs(knocked)
    knockout_residual = residual(states, knockout_installed)

    synth_args = tuple(inspect.signature(synthesize_binary_shape).parameters)

    return {
        "status": "PASS_GRAMMAR_SHAPE_GENESIS",
        "selector_parameters": list(synth_args),
        "selector_has_target_argument": any("target" in p for p in synth_args),
        "generation_count": len(generations),
        "residual_trace": residual_trace,
        "generations": generations,
        "generic_binary_synthesis_calls": generic_binary_synthesis_calls,
        "induced_constructor_calls": induced_constructor_calls,
        "shape_warrant_live": shape_warrant_live(log),
        "constructor_schema": constructor_schema(log),
        "final_revealed_controls": list(revealed_controls(final_installed)),
        "final_residual_count": len(final_residual),
        "restart": {
            "same_interface": interface_signature(0, restart_installed)
            == interface_signature(0, final_installed)
            and revealed_controls(restart_installed) == revealed_controls(final_installed),
            "same_constructor": constructor_schema(restarted) == constructor_schema(log),
        },
        "semantic_sham": {
            "same_controls": revealed_controls(sham_installed)
            == revealed_controls(final_installed),
        },
        "knockout": {
            "revealed_controls": list(revealed_controls(knockout_installed)),
            "shape_live": shape_warrant_live(knocked),
            "constructor_live": constructor_schema(knocked) is not None,
            "residual_count": len(knockout_residual),
            "restores_seed_interface": (
                revealed_controls(knockout_installed) == ()
                and not shape_warrant_live(knocked)
                and constructor_schema(knocked) is None
                and len(knockout_residual) == residual_trace[0]
            ),
        },
        "log_node_count": len(log),
    }


def report() -> dict:
    result = run_once()

    if result["residual_trace"] != [240, 112, 48, 16, 0]:
        raise AssertionError(result["residual_trace"])
    if result["generic_binary_synthesis_calls"] != 2:
        raise AssertionError("expected shape genesis + one replication synthesis")
    if result["induced_constructor_calls"] != 2:
        raise AssertionError("held-out binary constructor reuse failed")
    if result["final_residual_count"] != 0:
        raise AssertionError("target not reached")
    if not result["shape_warrant_live"]:
        raise AssertionError("arity-2 shape was not warranted")

    modes = [g["mode"] for g in result["generations"]]
    if modes != [
        "grammar_shape_genesis",
        "generic_binary_synthesis",
        "induced_binary_constructor",
        "induced_binary_constructor",
    ]:
        raise AssertionError(modes)

    first = result["generations"][0]
    if first["unary_grammar_max_gain"] != 0:
        raise AssertionError("unary grammar was not exhausted")
    if first["selected_program"]["arity"] != 2:
        raise AssertionError("new grammar shape is not binary")

    schema = result["constructor_schema"]
    if schema is None:
        raise AssertionError("binary constructor was not induced")
    if schema["arity"] != 2:
        raise AssertionError(schema)
    if schema["table"] != [0, 1, 1, 0]:
        raise AssertionError(schema)

    if not result["restart"]["same_interface"] or not result["restart"]["same_constructor"]:
        raise AssertionError("restart failed")
    if not result["semantic_sham"]["same_controls"]:
        raise AssertionError("semantic sham changed interface")
    if not result["knockout"]["restores_seed_interface"]:
        raise AssertionError("knockout failed")
    if result["selector_has_target_argument"]:
        raise AssertionError("binary shape synthesizer received target")

    return {
        "experiment": "grammar-shape-genesis-v0",
        "claim_boundary": (
            "The complete unary truth-table grammar is exhaustively shown to have "
            "zero gain, after which residual pressure selects arity 2 from a declared "
            "finite arity-2 extensional truth-table meta-meta grammar. A reusable "
            "binary constructor is then induced and reused on held-out coordinates. "
            "This does not invent arbitrary syntax outside the declared arity search."
        ),
        "result": result,
        "verdict": "PASS_RESIDUAL_DRIVEN_GRAMMAR_SHAPE_GENESIS",
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
