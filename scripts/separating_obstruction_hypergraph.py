from __future__ import annotations

import itertools
import json
from collections import deque


def canonical_pair(a, b):
    return (a, b) if repr(a) <= repr(b) else (b, a)


def _compose(step_map, transform, states):
    # Apply transform first, then one lawful step.
    return tuple(step_map[transform[i]] for i in range(len(states)))


def reachable_transforms(states, actions):
    """Exact finite transition-semigroup closure from the identity."""
    index = {state: i for i, state in enumerate(states)}
    step_maps = {
        name: tuple(index[action[state]] for state in states)
        for name, action in actions.items()
    }
    identity = tuple(range(len(states)))
    seen = {identity}
    queue = deque([identity])

    while queue:
        transform = queue.popleft()
        for step_map in step_maps.values():
            nxt = _compose(step_map, transform, states)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    return tuple(sorted(seen))


def future_signatures(states, actions, test):
    """All distinct value-vectors produced by finite lawful continuations + test."""
    transforms = reachable_transforms(states, actions)
    return tuple(
        sorted(
            {
                tuple(test[states[i]] for i in transform)
                for transform in transforms
            },
            key=repr,
        )
    )


def separated_pairs(states, signatures):
    separated = set()
    for signature in signatures:
        for i, j in itertools.combinations(range(len(states)), 2):
            if signature[i] != signature[j]:
                separated.add(canonical_pair(states[i], states[j]))
    return frozenset(separated)


def unresolved_pairs(states, actions, tests, protected):
    protected_signatures = []
    for name in protected:
        protected_signatures.extend(
            future_signatures(states, actions, tests[name])
        )
    resolved = separated_pairs(states, protected_signatures)
    all_pairs = {
        canonical_pair(a, b)
        for a, b in itertools.combinations(states, 2)
    }
    return frozenset(all_pairs - set(resolved))


def generator_edges(states, actions, tests, protected, candidates):
    unresolved = unresolved_pairs(states, actions, tests, protected)
    edges = {}
    for name in candidates:
        signatures = future_signatures(states, actions, tests[name])
        edges[name] = frozenset(
            pair for pair in separated_pairs(states, signatures)
            if pair in unresolved
        )
    return unresolved, edges


def minimum_separating_basis(universe, edges):
    """Exact minimum set cover, lexicographically deterministic among ties."""
    universe = frozenset(universe)
    if not universe:
        return ()

    names = tuple(sorted(edges))
    for size in range(1, len(names) + 1):
        for combo in itertools.combinations(names, size):
            covered = frozenset().union(*(edges[name] for name in combo))
            if covered >= universe:
                return combo
    return None


def greedy_separating_basis(universe, edges):
    remaining = set(universe)
    chosen = []
    available = set(edges)

    while remaining:
        ranked = sorted(
            available,
            key=lambda name: (-len(edges[name] & remaining), name),
        )
        if not ranked:
            return None
        best = ranked[0]
        gain = edges[best] & remaining
        if not gain:
            return None
        chosen.append(best)
        remaining -= gain
        available.remove(best)

    return tuple(chosen)


def relabel_world(states, actions, tests, permutation):
    rename = dict(zip(states, permutation))
    inverse = {new: old for old, new in rename.items()}
    new_states = tuple(permutation)

    new_actions = {}
    for name, action in actions.items():
        new_actions[name] = {
            new: rename[action[inverse[new]]]
            for new in new_states
        }

    new_tests = {}
    for name, test in tests.items():
        new_tests[name] = {
            new: test[inverse[new]]
            for new in new_states
        }

    return new_states, new_actions, new_tests


def nucleus_genesis_fixture():
    states = (0, 1, 2)
    actions = {
        "step": {0: 1, 1: 1, 2: 2},
    }
    tests = {
        "IS_ZERO": {0: True, 1: False, 2: False},
        "IS_ONE": {0: False, 1: True, 2: False},
    }
    return states, actions, tests


def build_report():
    states, actions, tests = nucleus_genesis_fixture()

    empty_unresolved, empty_edges = generator_edges(
        states, actions, tests, protected=(), candidates=tests
    )
    zero_unresolved, zero_edges = generator_edges(
        states,
        actions,
        tests,
        protected=("IS_ZERO",),
        candidates=("IS_ONE",),
    )
    full_unresolved, _ = generator_edges(
        states,
        actions,
        tests,
        protected=("IS_ZERO", "IS_ONE"),
        candidates=(),
    )

    empty_exact = minimum_separating_basis(empty_unresolved, empty_edges)
    empty_greedy = greedy_separating_basis(empty_unresolved, empty_edges)
    zero_exact = minimum_separating_basis(zero_unresolved, zero_edges)

    relabel_invariant = True
    relabel_snapshots = []
    for permutation in itertools.permutations(states):
        rs, ra, rt = relabel_world(states, actions, tests, permutation)
        unresolved, edges = generator_edges(
            rs, ra, rt, protected=("IS_ZERO",), candidates=("IS_ONE",)
        )
        basis = minimum_separating_basis(unresolved, edges)
        snapshot = {
            "defect": len(unresolved),
            "basis_size": None if basis is None else len(basis),
            "coverage_sizes": sorted(len(edge) for edge in edges.values()),
        }
        relabel_snapshots.append(snapshot)
        if snapshot != {
            "defect": len(zero_unresolved),
            "basis_size": len(zero_exact),
            "coverage_sizes": sorted(len(edge) for edge in zero_edges.values()),
        }:
            relabel_invariant = False

    is_one_signatures = future_signatures(states, actions, tests["IS_ONE"])

    return {
        "experiment": "separating-obstruction-hypergraph-v0",
        "status": "POSITIVE_FINITE_SIGNAL_NOT_CORE_AUTHORITY",
        "fixture": "existing three-state Nucleus Genesis / Future Observations fixture",
        "transition_semigroup_size": len(reachable_transforms(states, actions)),
        "is_one_future_signatures": [list(sig) for sig in is_one_signatures],
        "snapshots": {
            "no_protected_tests": {
                "defect_unresolved_pairs": len(empty_unresolved),
                "unresolved_pairs": sorted(map(list, empty_unresolved)),
                "generator_coverage": {
                    name: len(edge) for name, edge in sorted(empty_edges.items())
                },
                "minimum_basis": list(empty_exact) if empty_exact is not None else None,
                "minimum_basis_size": None if empty_exact is None else len(empty_exact),
                "greedy_basis": list(empty_greedy) if empty_greedy is not None else None,
            },
            "protect_is_zero": {
                "defect_unresolved_pairs": len(zero_unresolved),
                "unresolved_pairs": sorted(map(list, zero_unresolved)),
                "generator_coverage": {
                    name: len(edge) for name, edge in sorted(zero_edges.items())
                },
                "minimum_basis": list(zero_exact) if zero_exact is not None else None,
                "minimum_basis_size": None if zero_exact is None else len(zero_exact),
            },
            "protect_is_zero_and_is_one": {
                "defect_unresolved_pairs": len(full_unresolved),
                "unresolved_pairs": sorted(map(list, full_unresolved)),
            },
        },
        "findings": {
            "strict_scalar_descent_on_retained_fixture": (
                len(zero_unresolved) < len(empty_unresolved)
                and len(full_unresolved) < len(zero_unresolved)
            ),
            "one_generator_closes_current_residual": (
                len(zero_unresolved) == 1
                and zero_exact == ("IS_ONE",)
                and len(full_unresolved) == 0
            ),
            "future_closure_adds_separation_power": (
                len(is_one_signatures) > 1
                and len(empty_edges["IS_ONE"]) == len(empty_unresolved)
            ),
            "minimum_basis_compresses_pairwise_residuals": (
                len(empty_unresolved) == 3
                and empty_exact == ("IS_ONE",)
            ),
            "canonical_under_all_state_relabelings": relabel_invariant,
            "greedy_matches_exact_on_fixture": empty_greedy == empty_exact,
        },
        "claim_boundary": (
            "This is an exact finite combinatorial diagnostic on the retained fixture. "
            "It does not prove that greedy coverage predicts discoveries on larger or "
            "open-ended domains, nor that minimum set cover should enter Nucleus authority."
        ),
        "verdict": (
            "Keep as a derived diagnostic: unresolved-pair count is an exact finite "
            "scalar defect, and generator-level future-closure hyperedges expose the "
            "minimum missing distinguishing information without reading provenance. "
            "Next gate is held-out predictive value on larger historical fixtures."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2, sort_keys=True))
