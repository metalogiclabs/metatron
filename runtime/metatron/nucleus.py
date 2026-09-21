from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


def _canonical(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


@dataclass(frozen=True, init=False)
class Node:
    """Immutable canonical content plus prerequisite node IDs."""

    body: str
    premises: tuple[str, ...]

    def __init__(self, kind: str, payload=None, premises=()):
        if not isinstance(kind, str) or not kind:
            raise ValueError("node kind must be a non-empty string")
        body = _canonical({
            "kind": kind,
            "payload": {} if payload is None else payload,
        })
        object.__setattr__(self, "body", body)
        object.__setattr__(self, "premises", tuple(premises))

    @property
    def value(self) -> dict:
        return json.loads(self.body)

    @property
    def kind(self) -> str:
        return self.value["kind"]

    @property
    def payload(self):
        return self.value["payload"]

    def record(self) -> dict:
        value = self.value
        return {
            "kind": value["kind"],
            "payload": value["payload"],
            "premises": list(self.premises),
        }

    @property
    def id(self) -> str:
        return sha256(_canonical(self.record()).encode()).hexdigest()


Log = tuple[Node, ...]


def ids(log: Log) -> tuple[str, ...]:
    return tuple(node.id for node in log)


def _get(log: Log, node_id: str) -> Node:
    for node in reversed(log):
        if node.id == node_id:
            return node
    raise KeyError(node_id)


def append(log: Log, node: Node) -> Log:
    if len(set(node.premises)) != len(node.premises):
        raise ValueError("duplicate premises are not allowed")

    known = set(ids(log))
    missing = [premise for premise in node.premises if premise not in known]
    if missing:
        raise KeyError(f"unknown premises: {missing}")

    if node.kind == "revoke":
        payload = node.payload
        target = payload.get("target") if isinstance(payload, dict) else None
        if not isinstance(target, str) or target not in known:
            raise KeyError("revocation target must be an existing node id")

    if node.id in known:
        if _get(log, node.id) != node:
            raise ValueError("content-address collision")
        return log

    return log + (node,)


def live_ids(log: Log) -> tuple[str, ...]:
    revoked = {
        node.payload["target"]
        for node in log
        if node.kind == "revoke"
    }
    live_set: set[str] = set()
    ordered = []

    for node in log:
        node_id = node.id
        if node.kind == "revoke" or node_id in revoked:
            continue
        if all(premise in live_set for premise in node.premises):
            live_set.add(node_id)
            ordered.append(node_id)

    return tuple(ordered)


def live(log: Log, kind: str | None = None) -> tuple[tuple[str, Node], ...]:
    active = set(live_ids(log))
    return tuple(
        (node.id, node)
        for node in log
        if node.id in active and (kind is None or node.kind == kind)
    )


def dumps(log: Log) -> str:
    lines = []
    for node in log:
        record = node.record()
        record["id"] = node.id
        lines.append(_canonical(record))
    return "\n".join(lines) + ("\n" if lines else "")


def loads(payload: str) -> Log:
    log: Log = ()
    for lineno, line in enumerate(payload.splitlines(), 1):
        if not line.strip():
            continue
        record = json.loads(line)
        expected = record.pop("id", None)
        node = Node(
            record["kind"],
            record.get("payload", {}),
            tuple(record.get("premises", [])),
        )
        if node.id != expected:
            raise ValueError(
                f"line {lineno}: node id mismatch "
                f"(expected {expected!r}, got {node.id!r})"
            )
        log = append(log, node)
    return log
