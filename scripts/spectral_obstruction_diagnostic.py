from __future__ import annotations

import itertools
import json
import math

from runtime.metatron.nucleus import Node, append, live


def _add(log, kind, payload=None, premises=()):
    node = Node(kind, payload, premises)
    return append(log, node), node.id


def _edge_graph_from_live_warrants(log):
    active = dict(live(log))
    index = {node_id: i for i, node_id in enumerate(active)}
    edges = set()
    for node_id, node in active.items():
        j = index[node_id]
        for premise in node.premises:
            if premise in index:
                i = index[premise]
                edges.add((min(i, j), max(i, j)))
    return len(active), tuple(sorted(edges))


def _equivalence_graph(partition):
    vertices = sorted(v for block in partition for v in block)
    pos = {v: i for i, v in enumerate(vertices)}
    edges = set()
    for block in partition:
        for a, b in itertools.combinations(block, 2):
            i, j = pos[a], pos[b]
            edges.add((min(i, j), max(i, j)))
    return len(vertices), tuple(sorted(edges))


def _adjacency(n, edges):
    a = [[0.0 for _ in range(n)] for _ in range(n)]
    for i, j in edges:
        a[i][j] = 1.0
        a[j][i] = 1.0
    return a


def _jacobi_eigenvalues_symmetric(matrix, tol=1e-12, max_steps=10000):
    a = [row[:] for row in matrix]
    n = len(a)
    if n == 0:
        return []

    for _ in range(max_steps):
        p = q = 0
        off = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                value = abs(a[i][j])
                if value > off:
                    off = value
                    p, q = i, j

        if off <= tol:
            break

        app = a[p][p]
        aqq = a[q][q]
        apq = a[p][q]
        phi = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c = math.cos(phi)
        s = math.sin(phi)

        for k in range(n):
            if k == p or k == q:
                continue
            akp = a[k][p]
            akq = a[k][q]
            new_kp = c * akp - s * akq
            new_kq = s * akp + c * akq
            a[k][p] = a[p][k] = new_kp
            a[k][q] = a[q][k] = new_kq

        a[p][p] = c * c * app - 2.0 * s * c * apq + s * s * aqq
        a[q][q] = s * s * app + 2.0 * s * c * apq + c * c * aqq
        a[p][q] = a[q][p] = 0.0
    else:
        raise RuntimeError("Jacobi eigensolver did not converge")

    return sorted(a[i][i] for i in range(n))


def spectral_metrics(n, edges):
    edge_set = set(edges)
    eigs = _jacobi_eigenvalues_symmetric(_adjacency(n, edges))
    induced_p3 = 0
    triangles = 0
    for triple in itertools.combinations(range(n), 3):
        count = sum(
            (min(i, j), max(i, j)) in edge_set
            for i, j in itertools.combinations(triple, 2)
        )
        if count == 2:
            induced_p3 += 1
        elif count == 3:
            triangles += 1

    return {
        "vertices": n,
        "edges": len(edge_set),
        "lambda_min": eigs[0] if eigs else 0.0,
        "lambda_max": eigs[-1] if eigs else 0.0,
        "induced_p3": induced_p3,
        "triangles": triangles,
        "cluster_graph": induced_p3 == 0,
    }


def authority_signature(log):
    return tuple(
        sorted(
            (node.kind, node.id)
            for node_id, node in live(log)
            if node.kind in {"capability", "relation"}
        )
    )


def warrant_lifecycle():
    stages = {}
    log = ()

    log, genesis = _add(
        log, "capability", {"name": "id", "table": [0, 1, 2]}
    )
    stages["genesis"] = log

    log, residual = _add(
        log,
        "residual",
        {
            "target": [1, 1, 2],
            "closure_size": 1,
            "authority_digest": genesis,
        },
        (genesis,),
    )
    stages["residual"] = log

    log, verification = _add(
        log,
        "verification",
        {"subject": "step", "verdict": "accept"},
        (residual,),
    )
    stages["verification"] = log

    log, step = _add(
        log,
        "capability",
        {"name": "step", "table": [1, 1, 2]},
        (residual, verification),
    )
    stages["capability"] = log

    log, relation_verification = _add(
        log,
        "verification",
        {"subject": "step;step=step", "verdict": "accept"},
        (step,),
    )
    stages["relation_verification"] = log

    log, relation = _add(
        log,
        "relation",
        {"left": ["step", "step"], "right": "step"},
        (step, relation_verification),
    )
    stages["relation"] = log

    log, _ = _add(
        log,
        "measurement",
        {"subject": "step", "metric": "diagnostic-only", "value": 1},
        (relation,),
    )
    stages["measurement"] = log

    log, _ = _add(
        log,
        "revoke",
        {"target": step, "reason": "qualification withdrawn"},
    )
    stages["revoked"] = log

    return stages


def build_report():
    old_eq = _equivalence_graph(((0,), (1, 2)))
    new_eq = _equivalence_graph(((0,), (1,), (2,)))
    stages = warrant_lifecycle()
    stage_metrics = {
        name: spectral_metrics(*_edge_graph_from_live_warrants(log))
        for name, log in stages.items()
    }

    relation_sig = authority_signature(stages["relation"])
    measurement_sig = authority_signature(stages["measurement"])

    findings = {
        "equivalence_graph_is_cluster_by_construction": (
            spectral_metrics(*old_eq)["cluster_graph"]
            and spectral_metrics(*new_eq)["cluster_graph"]
        ),
        "successful_capability_does_not_reduce_negative_mode": (
            stage_metrics["capability"]["lambda_min"]
            < stage_metrics["verification"]["lambda_min"]
        ),
        "successful_relation_does_not_reduce_negative_mode": (
            stage_metrics["relation"]["lambda_min"]
            < stage_metrics["relation_verification"]["lambda_min"]
        ),
        "inert_measurement_changes_spectrum_without_authority_change": (
            relation_sig == measurement_sig
            and abs(
                stage_metrics["relation"]["lambda_min"]
                - stage_metrics["measurement"]["lambda_min"]
            )
            > 1e-6
        ),
    }

    return {
        "experiment": "spectral-obstruction-diagnostic-v0",
        "status": "FALSIFIED_FOR_CORE_PROMOTION",
        "equivalence_graph": {
            "before_residual_adjoin": spectral_metrics(*old_eq),
            "after_residual_adjoin": spectral_metrics(*new_eq),
        },
        "warrant_lifecycle": stage_metrics,
        "findings": findings,
        "verdict": (
            "Do not promote raw spectral/clique metrics into the Metatron core. "
            "On quotient equivalence they are tautological; on the raw warrant graph "
            "they are representation-sensitive and move in the wrong direction across "
            "successful repairs. Retain, at most, as an offline search heuristic for "
            "future large weighted/approximate graphs."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2, sort_keys=True))
