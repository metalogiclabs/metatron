from __future__ import annotations

from hashlib import sha256
import json
from typing import Iterable

from .nucleus import WarrantGraph


def dependents(graph: WarrantGraph) -> dict[str, tuple[str, ...]]:
    reverse: dict[str, list[str]] = {node_id: [] for node_id in graph.ids}
    for node_id in graph.ids:
        for premise in graph[node_id].premises:
            reverse[premise].append(node_id)
    return {key: tuple(value) for key, value in reverse.items()}


def affected(graph: WarrantGraph, seeds: Iterable[str]) -> tuple[str, ...]:
    """Derived dependency cone; never authoritative state."""
    reverse = dependents(graph)
    queue = list(dict.fromkeys(seeds))
    seen = set(queue)
    ordered = []

    while queue:
        current = queue.pop(0)
        if current not in graph:
            raise KeyError(current)
        ordered.append(current)
        for dependent in reverse[current]:
            if dependent not in seen:
                seen.add(dependent)
                queue.append(dependent)

    return tuple(ordered)


def root_digest(graph: WarrantGraph) -> str:
    """Digest of the append-only history; a view, not a second authority."""
    payload = json.dumps(
        graph.ids,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()
