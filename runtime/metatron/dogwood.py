from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .nucleus import Log, live_ids


ACTION_SCHEMA = """namespace MetatronDogwood {
  type NodeInput = { node: String };
  type StageOutput = { success: Bool };

  entity ResearchAgent = { id: String };
  entity Repository = { name: String };

  action "Admit" appliesTo {
    principal: [ResearchAgent],
    resource: [Repository],
    context: {
      input: NodeInput,
      output?: StageOutput
    }
  };

  action "Revoke" appliesTo {
    principal: [ResearchAgent],
    resource: [Repository],
    context: {
      input: NodeInput,
      output?: StageOutput
    }
  };

  action "Use" appliesTo {
    principal: [ResearchAgent],
    resource: [Repository],
    context: {
      input: NodeInput,
      output?: StageOutput
    }
  };
}
"""

EVENT_SCHEMA_TEMPLATE = """max_window = {window}

decision event <A>::request {{
    ...inputs(A),
    callerPrincipal: principalType(A),
    callerResource: resourceType(A),
    requestId: String,
}}

event <A>::response {{
    ...inputs(A),
    ...outputs(A),
    callerPrincipal: principalType(A),
    callerResource: resourceType(A),
    requestId: String,
}}
"""


def _sha256_text(text: str) -> str:
    return sha256(text.encode()).hexdigest()


def _node_maps(log: Log):
    ordered = [node.id for node in log if node.kind != "revoke"]
    by_id = {node.id: node for node in log if node.kind != "revoke"}
    order = {node_id: i for i, node_id in enumerate(ordered)}
    return ordered, by_id, order


def dependency_cone(log: Log, node_id: str) -> tuple[str, ...]:
    """Return transitive prerequisites plus the node, in log order."""
    _, by_id, order = _node_maps(log)
    if node_id not in by_id:
        raise KeyError(node_id)

    seen: set[str] = set()

    def visit(current: str) -> None:
        if current in seen:
            return
        node = by_id[current]
        for premise in node.premises:
            visit(premise)
        seen.add(current)

    visit(node_id)
    return tuple(sorted(seen, key=order.__getitem__))


def _live_atom(node_id: str, window: str) -> str:
    return (
        f'(!MetatronDogwood::Action::"Revoke"::response{{'
        f' input.node: "{node_id}", output.success: true }} '
        f'since within {window} '
        f'MetatronDogwood::Action::"Admit"::response{{'
        f' input.node: "{node_id}", output.success: true }})'
    )


def compile_policy(log: Log, *, window: str = "3650d") -> str:
    """Compile Metatron live-warrant semantics into Dogwood Use rules.

    The event projection is deliberately one-way: canonical Metatron history is
    logged as Admit/Revoke response events. Dogwood authorizes only Use requests.
    It is not a second warrant authority and cannot create or revoke warrants.
    """
    ordered, _, _ = _node_maps(log)
    rules = [
        "// Generated from canonical Metatron warrant history.",
        "// Dogwood is an enforcement backend, not warrant authority.",
        f"// Temporal projection window: {window}.",
        "",
    ]

    for node_id in ordered:
        cone = dependency_cone(log, node_id)
        conditions = "\n        && ".join(_live_atom(x, window) for x in cone)
        rules.extend([
            f'@id("use_{node_id[:16]}")',
            "permit (",
            "    principal,",
            '    action == MetatronDogwood::Action::"Use",',
            "    resource",
            ")",
            f'when {{ context.input.node == "{node_id}" }}',
            "when temporal {",
            f"    {conditions}",
            "};",
            "",
        ])

    return "\n".join(rules)


def compile_bundle(log: Log, *, window: str = "3650d") -> dict:
    policy = compile_policy(log, window=window)
    event_schema = EVENT_SCHEMA_TEMPLATE.format(window=window)
    ordered, _, _ = _node_maps(log)
    cones = {node_id: list(dependency_cone(log, node_id)) for node_id in ordered}
    manifest = {
        "schema": "metatron-dogwood-policy-compiler-v1",
        "window": window,
        "node_ids": ordered,
        "current_live_ids": list(live_ids(log)),
        "cones": cones,
        "action_schema_sha256": _sha256_text(ACTION_SCHEMA),
        "event_schema_sha256": _sha256_text(event_schema),
        "policy_sha256": _sha256_text(policy),
        "boundary": [
            "Metatron canonical log remains sole warrant authority",
            "Dogwood receives a trusted projection of canonical Admit/Revoke history",
            "generated policy authorizes Use only",
            "temporal persistence is bounded by the declared projection window",
        ],
    }
    return {
        "schema": ACTION_SCHEMA,
        "event_schema": event_schema,
        "policy": policy,
        "manifest": manifest,
    }


def write_bundle(log: Log, out_dir: Path, *, window: str = "3650d") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle = compile_bundle(log, window=window)
    (out_dir / "schema.cedarschema").write_text(bundle["schema"])
    (out_dir / "events.dwschema").write_text(bundle["event_schema"])
    (out_dir / "policy.dw").write_text(bundle["policy"])
    (out_dir / "manifest.json").write_text(
        json.dumps(bundle["manifest"], indent=2, sort_keys=True) + "\n"
    )
    return bundle["manifest"]
