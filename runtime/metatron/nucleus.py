from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any, Iterable


Json = None | bool | int | float | str | list["Json"] | dict[str, "Json"]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class Node:
    """One content-addressed warranted fact.

    Meaning lives in kind/payload. Dependency semantics live only in premises.
    The nucleus intentionally has no separate Capability, Certificate,
    Measurement, Relation, Promotion, or Lineage event types.
    """

    kind: str
    payload: dict[str, Json] = field(default_factory=dict)
    premises: tuple[str, ...] = ()

    def record(self) -> dict[str, Json]:
        return {
            "kind": self.kind,
            "payload": self.payload,
            "premises": list(self.premises),
        }

    @property
    def id(self) -> str:
        return sha256(_canonical(self.record())).hexdigest()


class WarrantGraph:
    """Append-only content-addressed warrant DAG.

    The log is authoritative. Every other view is derived and disposable.

    Revocation is represented by a normal node:
        Node("revoke", {"target": <node-id>, ...})

    A revoked node is absent from the live view, and so are all descendants
    whose premises no longer remain live. History is never deleted.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._order: list[str] = []

    def __len__(self) -> int:
        return len(self._order)

    def __contains__(self, node_id: str) -> bool:
        return node_id in self._nodes

    def __getitem__(self, node_id: str) -> Node:
        return self._nodes[node_id]

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(self._order)

    def append(self, node: Node) -> str:
        """Append exactly one warranted fact; duplicate content is idempotent."""
        if not node.kind or not isinstance(node.kind, str):
            raise ValueError("node kind must be a non-empty string")

        if len(set(node.premises)) != len(node.premises):
            raise ValueError("duplicate premises are not allowed")

        missing = [premise for premise in node.premises if premise not in self._nodes]
        if missing:
            raise KeyError(f"unknown premises: {missing}")

        if node.kind == "revoke":
            target = node.payload.get("target")
            if not isinstance(target, str) or target not in self._nodes:
                raise KeyError("revocation target must be an existing node id")

        node_id = node.id
        existing = self._nodes.get(node_id)
        if existing is not None:
            if existing != node:
                raise ValueError("content-address collision")
            return node_id

        self._nodes[node_id] = node
        self._order.append(node_id)
        return node_id

    def revoked_ids(self) -> frozenset[str]:
        return frozenset(
            node.payload["target"]
            for node in self._nodes.values()
            if node.kind == "revoke"
        )

    def live_ids(self) -> tuple[str, ...]:
        """Derive the current live consequential view from the append-only log."""
        revoked = self.revoked_ids()
        live: set[str] = set()
        ordered: list[str] = []

        for node_id in self._order:
            node = self._nodes[node_id]
            if node.kind == "revoke" or node_id in revoked:
                continue
            if all(premise in live for premise in node.premises):
                live.add(node_id)
                ordered.append(node_id)

        return tuple(ordered)

    def live(self, kind: str | None = None) -> tuple[tuple[str, Node], ...]:
        result = []
        for node_id in self.live_ids():
            node = self._nodes[node_id]
            if kind is None or node.kind == kind:
                result.append((node_id, node))
        return tuple(result)

    def dependents(self) -> dict[str, tuple[str, ...]]:
        reverse: dict[str, list[str]] = {node_id: [] for node_id in self._order}
        for node_id in self._order:
            for premise in self._nodes[node_id].premises:
                reverse[premise].append(node_id)
        return {key: tuple(value) for key, value in reverse.items()}

    def affected(self, seeds: Iterable[str]) -> tuple[str, ...]:
        """Return the dependency cone that an authority change can invalidate."""
        reverse = self.dependents()
        queue = list(dict.fromkeys(seeds))
        seen = set(queue)
        ordered = []

        while queue:
            current = queue.pop(0)
            if current not in self._nodes:
                raise KeyError(current)
            ordered.append(current)
            for dependent in reverse[current]:
                if dependent not in seen:
                    seen.add(dependent)
                    queue.append(dependent)

        return tuple(ordered)

    def root_digest(self) -> str:
        """Digest the authoritative history without creating another authority."""
        return sha256(_canonical(self._order)).hexdigest()

    def dumps(self) -> str:
        """Canonical JSONL history. No mutable machine snapshot is serialized."""
        lines = []
        for node_id in self._order:
            record = self._nodes[node_id].record()
            record["id"] = node_id
            lines.append(_canonical(record).decode("utf-8"))
        return "\n".join(lines) + ("\n" if lines else "")

    @classmethod
    def loads(cls, payload: str) -> "WarrantGraph":
        graph = cls()
        for lineno, line in enumerate(payload.splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            expected_id = record.pop("id", None)
            node = Node(
                kind=record["kind"],
                payload=record.get("payload", {}),
                premises=tuple(record.get("premises", [])),
            )
            actual_id = graph.append(node)
            if expected_id != actual_id:
                raise ValueError(
                    f"line {lineno}: node id mismatch "
                    f"(expected {expected_id!r}, got {actual_id!r})"
                )
        return graph
