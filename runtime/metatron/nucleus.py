from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any


Json = type(None) | bool | int | float | str | list["Json"] | dict[str, "Json"]


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
    """One append-only log; every other structure is a derived view."""

    def __init__(self) -> None:
        self._log: tuple[Node, ...] = ()

    def __len__(self) -> int:
        return len(self._log)

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(node.id for node in self._log)

    def __contains__(self, node_id: str) -> bool:
        return node_id in self.ids

    def __getitem__(self, node_id: str) -> Node:
        for node in reversed(self._log):
            if node.id == node_id:
                return node
        raise KeyError(node_id)

    def append(self, node: Node) -> str:
        if not isinstance(node.kind, str) or not node.kind:
            raise ValueError("node kind must be a non-empty string")
        if len(set(node.premises)) != len(node.premises):
            raise ValueError("duplicate premises are not allowed")

        known = set(self.ids)
        missing = [premise for premise in node.premises if premise not in known]
        if missing:
            raise KeyError(f"unknown premises: {missing}")

        if node.kind == "revoke":
            target = node.payload.get("target")
            if not isinstance(target, str) or target not in known:
                raise KeyError("revocation target must be an existing node id")

        node_id = node.id
        if node_id in known:
            if self[node_id] != node:
                raise ValueError("content-address collision")
            return node_id

        self._log += (node,)
        return node_id

    def live_ids(self) -> tuple[str, ...]:
        revoked = {
            str(node.payload["target"])
            for node in self._log
            if node.kind == "revoke"
        }
        live: set[str] = set()
        ordered = []

        for node in self._log:
            node_id = node.id
            if node.kind == "revoke" or node_id in revoked:
                continue
            if all(premise in live for premise in node.premises):
                live.add(node_id)
                ordered.append(node_id)

        return tuple(ordered)

    def live(self, kind: str | None = None) -> tuple[tuple[str, Node], ...]:
        live = set(self.live_ids())
        return tuple(
            (node.id, node)
            for node in self._log
            if node.id in live and (kind is None or node.kind == kind)
        )

    def dumps(self) -> str:
        lines = []
        for node in self._log:
            record = node.record()
            record["id"] = node.id
            lines.append(_canonical(record).decode("utf-8"))
        return "\n".join(lines) + ("\n" if lines else "")

    @classmethod
    def loads(cls, payload: str) -> "WarrantGraph":
        graph = cls()
        for lineno, line in enumerate(payload.splitlines(), 1):
            if not line.strip():
                continue
            record = json.loads(line)
            expected = record.pop("id", None)
            node = Node(
                str(record["kind"]),
                record.get("payload", {}),
                tuple(record.get("premises", [])),
            )
            actual = graph.append(node)
            if expected != actual:
                raise ValueError(
                    f"line {lineno}: node id mismatch "
                    f"(expected {expected!r}, got {actual!r})"
                )
        return graph
