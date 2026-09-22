from __future__ import annotations

import argparse
import inspect
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from runtime.metalogic.nucleus import Node, append, dumps, live, loads


State = int
Pair = tuple[int, int]
Process = tuple[str, ...]


@dataclass(frozen=True)
class Semantics:
    atoms: tuple[str, ...]
    # Each rule is (required atom family, generated observation bit index).
    rules: tuple[tuple[frozenset[str], int], ...]


def bit(bit_index: int, state: State) -> int:
    return (state >> bit_index) & 1


def observations(installed: frozenset[str], semantics: Semantics) -> tuple[int, ...]:
    # bit 0 is the seed observation. Every later observation must be earned by
    # closure of the installed candidate family.
    out = [0]
    for required, bit_index in semantics.rules:
        if required <= installed:
            out.append(bit_index)
    return tuple(sorted(set(out)))


def signature(state: State, obs: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(bit(i, state) for i in obs)


def current_relation(states: tuple[State, ...], installed: frozenset[str], semantics: Semantics):
    obs = observations(installed, semantics)
    return {
        (x, y)
        for x in states
        for y in states
        if x < y and signature(x, obs) == signature(y, obs)
    }


def target_relation(states: tuple[State, ...]) -> set[Pair]:
    # The frozen target future distinguishes all 4-bit states.
    return set()


def residual_from_target(
    states: tuple[State, ...],
    installed: frozenset[str],
    semantics: Semantics,
) -> tuple[Pair, ...]:
    current = current_relation(states, installed, semantics)
    target = target_relation(states)
    return tuple(sorted(current - target))


def process_coverage(
    residual: tuple[Pair, ...],
    installed: frozenset[str],
    process: Process,
    semantics: Semantics,
) -> tuple[Pair, ...]:
    before = observations(installed, semantics)
    after = observations(installed | frozenset(process), semantics)
    gained = tuple(i for i in after if i not in before)
    if not gained:
        return ()
    return tuple(
        (x, y)
        for x, y in residual
        if any(bit(i, x) != bit(i, y) for i in gained)
    )


def choose_next_process(
    residual: tuple[Pair, ...],
    installed: frozenset[str],
    semantics: Semantics,
) -> tuple[Process, tuple[Pair, ...]]:
    """Select from the current residual only.

    Policy is frozen and generic:
      1. smallest candidate-family cardinality with positive generated gain;
      2. within that size, maximum residual coverage;
      3. lexicographically first tie-break.

    There is no residual->repair lookup and no target argument.
    """
    remaining = tuple(a for a in semantics.atoms if a not in installed)
    for size in range(1, len(remaining) + 1):
        scored = []
        for combo in itertools.combinations(remaining, size):
            covered = process_coverage(residual, installed, combo, semantics)
            if covered:
                scored.append((len(covered), combo, covered))
        if scored:
            scored.sort(key=lambda item: (-item[0], item[1]))
            _, combo, covered = scored[0]
            return combo, covered
    raise RuntimeError("residual is nonempty but declared candidate language has no improving process")


def independently_verify_choice(
    residual: tuple[Pair, ...],
    installed: frozenset[str],
    selected: Process,
    semantics: Semantics,
) -> dict:
    selected_coverage = process_coverage(residual, installed, selected, semantics)
    if not selected_coverage:
        raise AssertionError("selected process has no residual effect")

    remaining = tuple(a for a in semantics.atoms if a not in installed)

    # Fail if any smaller family generates any consequential distinction.
    for size in range(1, len(selected)):
        for combo in itertools.combinations(remaining, size):
            if process_coverage(residual, installed, combo, semantics):
                raise AssertionError(f"smaller improving process exists: {combo}")

    # At the selected cardinality, fail if another process covers more.
    max_same_size = 0
    best = []
    for combo in itertools.combinations(remaining, len(selected)):
        cov = process_coverage(residual, installed, combo, semantics)
        n = len(cov)
        if n > max_same_size:
            max_same_size = n
            best = [combo]
        elif n == max_same_size and n:
            best.append(combo)

    if len(selected_coverage) != max_same_size:
        raise AssertionError("selected process is not maximum-coverage at minimum size")
    if selected != sorted(best)[0]:
        raise AssertionError("selected process violates frozen canonical tie-break")

    return {
        "minimum_positive_size": len(selected),
        "selected_coverage": len(selected_coverage),
        "max_same_size_coverage": max_same_size,
        "same_size_optima": [list(x) for x in sorted(best)],
    }


def installed_from_log(log) -> frozenset[str]:
    out = set()
    for _, node in live(log, "capability"):
        payload = node.payload
        for atom in payload["atoms"]:
            out.add(atom)
    return frozenset(out)


def run_once(semantics: Semantics) -> dict:
    states = tuple(range(16))
    log = ()

    seed = Node("seed_interface", {"protected_observations": [0]})
    log = append(log, seed)
    target = Node("future_demand", {"target": "four_bit_identity"}, (seed.id,))
    log = append(log, target)

    residual_counts = []
    generations = []
    promotion_ids = []
    parent = target.id

    # One generic developmental loop. No generation-specific repair is named.
    while True:
        installed = installed_from_log(log)
        residual = residual_from_target(states, installed, semantics)
        residual_counts.append(len(residual))
        if not residual:
            break

        selected, covered = choose_next_process(residual, installed, semantics)
        verification = independently_verify_choice(
            residual, installed, selected, semantics
        )

        residual_node = Node(
            "residual_certificate",
            {
                "count": len(residual),
                "pairs_sha_basis": [list(p) for p in residual],
            },
            (parent,),
        )
        log = append(log, residual_node)

        proposal = Node(
            "candidate_process",
            {
                "atoms": list(selected),
                "event_structure": {
                    "events": list(selected),
                    "causal_edges": [],
                    "input_port": "current_residual",
                    "output_port": "next_interface",
                },
                "selector_input": "residual_only",
            },
            (residual_node.id,),
        )
        log = append(log, proposal)

        verified = Node(
            "verification",
            {
                "minimum_positive_size": verification["minimum_positive_size"],
                "selected_coverage": verification["selected_coverage"],
                "max_same_size_coverage": verification["max_same_size_coverage"],
                "verified": True,
            },
            (residual_node.id, proposal.id),
        )
        log = append(log, verified)

        capability = Node(
            "capability",
            {
                "atoms": list(selected),
                "generated_observations": list(
                    observations(installed | frozenset(selected), semantics)
                ),
            },
            (verified.id, parent),
        )
        log = append(log, capability)
        promotion_ids.append(capability.id)

        installed_after = installed_from_log(log)
        next_residual = residual_from_target(states, installed_after, semantics)
        if len(next_residual) >= len(residual):
            raise AssertionError("warranted process did not strictly reduce residual")

        generations.append(
            {
                "generation": len(generations) + 1,
                "residual_before": len(residual),
                "selected_process": list(selected),
                "process_size": len(selected),
                "covered_pairs": len(covered),
                "residual_after": len(next_residual),
                "generated_observations": list(
                    observations(installed_after, semantics)
                ),
                "verification": verification,
                "capability_id": capability.id,
            }
        )
        parent = capability.id

    final_installed = installed_from_log(log)
    final_residual = residual_from_target(states, final_installed, semantics)
    assert not final_residual

    # Restart: the derived interface must be reconstructed from persisted history.
    restarted = loads(dumps(log))
    restart_installed = installed_from_log(restarted)
    restart_residual = residual_from_target(states, restart_installed, semantics)

    # Semantic sham: inert evidence must not change the interface.
    sham_log = append(log, Node("measurement", {"diagnostic_only": True}))
    sham_installed = installed_from_log(sham_log)
    sham_residual = residual_from_target(states, sham_installed, semantics)

    # Knockout: revoking G1 must cut all causally downstream generations.
    knocked = append(
        log,
        Node("revoke", {"target": promotion_ids[0]}, (promotion_ids[-1],)),
    )
    knockout_installed = installed_from_log(knocked)
    knockout_residual = residual_from_target(states, knockout_installed, semantics)

    selector_params = tuple(inspect.signature(choose_next_process).parameters)

    return {
        "status": "PASS_RESIDUAL_DRIVEN_INTERFACE",
        "state_count": len(states),
        "candidate_atom_count": len(semantics.atoms),
        "selector_parameters": list(selector_params),
        "selector_has_target_argument": any("target" in p for p in selector_params),
        "generation_count": len(generations),
        "residual_counts": residual_counts,
        "process_sizes": [g["process_size"] for g in generations],
        "generations": generations,
        "final_installed": sorted(final_installed),
        "final_residual_count": len(final_residual),
        "restart": {
            "installed_equal": restart_installed == final_installed,
            "residual_count": len(restart_residual),
        },
        "semantic_sham": {
            "installed_equal": sham_installed == final_installed,
            "residual_count": len(sham_residual),
        },
        "knockout": {
            "live_installed": sorted(knockout_installed),
            "residual_count": len(knockout_residual),
            "restores_seed_interface": len(knockout_installed) == 0
            and len(knockout_residual) == residual_counts[0],
        },
        "log_node_count": len(log),
    }


def canonical_semantics() -> Semantics:
    return Semantics(
        atoms=("a", "b", "c", "d", "e", "f", "g", "h"),
        rules=(
            (frozenset(("a", "b")), 1),
            (frozenset(("c", "d")), 2),
            (frozenset(("e", "f")), 3),
        ),
    )


def renamed_semantics() -> Semantics:
    # Same world under an unrelated candidate vocabulary. The policy receives no
    # knowledge of the original names or expected sequence.
    rename = {
        "a": "q7",
        "b": "m2",
        "c": "x9",
        "d": "b4",
        "e": "r1",
        "f": "k8",
        "g": "d6",
        "h": "p3",
    }
    base = canonical_semantics()
    atoms = tuple(sorted(rename[a] for a in base.atoms))
    rules = tuple(
        (frozenset(rename[a] for a in required), bit_index)
        for required, bit_index in base.rules
    )
    return Semantics(atoms=atoms, rules=rules)


def report() -> dict:
    primary = run_once(canonical_semantics())
    renamed = run_once(renamed_semantics())

    invariants = {
        "residual_trace": primary["residual_counts"] == renamed["residual_counts"],
        "process_sizes": primary["process_sizes"] == renamed["process_sizes"],
        "generation_count": primary["generation_count"] == renamed["generation_count"],
        "final_closure": primary["final_residual_count"] == renamed["final_residual_count"] == 0,
    }

    if not all(invariants.values()):
        raise AssertionError(f"rename invariance failed: {invariants}")

    if primary["selector_has_target_argument"]:
        raise AssertionError("selector must not receive target information")

    expected_trace = [56, 24, 8, 0]
    if primary["residual_counts"] != expected_trace:
        raise AssertionError(
            f"unexpected developmental trace: {primary['residual_counts']}"
        )
    if primary["process_sizes"] != [2, 2, 2]:
        raise AssertionError(f"unexpected process sizes: {primary['process_sizes']}")
    if not primary["restart"]["installed_equal"] or primary["restart"]["residual_count"] != 0:
        raise AssertionError("restart failed")
    if not primary["semantic_sham"]["installed_equal"] or primary["semantic_sham"]["residual_count"] != 0:
        raise AssertionError("semantic sham changed interface")
    if not primary["knockout"]["restores_seed_interface"]:
        raise AssertionError("causal knockout did not restore seed interface")

    return {
        "experiment": "residual-driven-interface-v0",
        "claim_boundary": (
            "Finite declared candidate semantics. The selector receives current "
            "consequential residual plus candidate closure semantics, but no target "
            "labels and no residual-to-repair mapping. This is not unrestricted "
            "open-ended generator invention."
        ),
        "primary": primary,
        "rename_control": {
            "invariants": invariants,
            "result": renamed,
        },
        "verdict": "PASS_RESIDUAL_ONLY_NEXT_INTERFACE",
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
