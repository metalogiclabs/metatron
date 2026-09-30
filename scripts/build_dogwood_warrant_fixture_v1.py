#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.metatron.dogwood import write_bundle
from runtime.metatron.nucleus import Node, append, dumps, live_ids


PRINCIPAL = 'MetatronDogwood::ResearchAgent::"metatron"'
RESOURCE = 'MetatronDogwood::Repository::"metalogiclabs/metatron"'


def add(log, kind, payload=None, premises=()):
    node = Node(kind, payload, premises)
    return append(log, node), node.id


def response(ts: int, action: str, node: str, req: str) -> str:
    return (
        f'@{ts} scope(principal: {PRINCIPAL}, resource: {RESOURCE}) '
        f'MetatronDogwood::Action::"{action}"::response('
        f'input: {{ node: "{node}" }}, output: {{ success: true }}, '
        f'callerPrincipal: {PRINCIPAL}, callerResource: {RESOURCE}, '
        f'requestId: "{req}")'
    )


def use(ts: int, node: str, req: str) -> str:
    return (
        f'@{ts} scope(principal: {PRINCIPAL}, resource: {RESOURCE}) '
        f'request_context(input: {{ node: "{node}" }}) '
        f'MetatronDogwood::Action::"Use"::request('
        f'input: {{ node: "{node}" }}, callerPrincipal: {PRINCIPAL}, '
        f'callerResource: {RESOURCE}, requestId: "{req}")'
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    log = ()
    log, root = add(log, "fact", {"name": "root"})
    log, middle = add(log, "fact", {"name": "middle"}, (root,))
    log, dependent = add(log, "capability", {"name": "dependent"}, (middle,))
    log, independent = add(log, "fact", {"name": "independent"})
    pre_revoke = live_ids(log)
    log, revoke = add(log, "revoke", {"target": middle, "reason": "fixture"})
    final_live = live_ids(log)

    (args.out / "warrant.jsonl").write_text(dumps(log))
    manifest = write_bundle(log, args.out)

    trace = [
        response(0, "Admit", root, "admit-root"),
        response(10, "Admit", middle, "admit-middle"),
        response(20, "Admit", dependent, "admit-dependent"),
        response(30, "Admit", independent, "admit-independent"),
        use(35, dependent, "use-dependent-before"),
        response(40, "Revoke", middle, "revoke-middle"),
        use(50, dependent, "use-dependent-after"),
        use(60, independent, "use-independent-after"),
        use(70, middle, "use-middle-after"),
        use(80, root, "use-root-after"),
    ]
    (args.out / "trace.log").write_text("\n".join(trace) + "\n")
    expected = [
        "@35 (time point 0): ALLOW",
        "@50 (time point 1): DENY",
        "@60 (time point 2): ALLOW",
        "@70 (time point 3): DENY",
        "@80 (time point 4): ALLOW",
    ]
    (args.out / "expected.normalized.out").write_text("\n".join(expected) + "\n")

    oracle = {
        "schema": "metatron-dogwood-warrant-fixture-v1",
        "root": root,
        "middle": middle,
        "dependent": dependent,
        "independent": independent,
        "revoke": revoke,
        "pre_revoke_live_ids": list(pre_revoke),
        "final_live_ids": list(final_live),
        "generated_live_ids": manifest["current_live_ids"],
        "expected_verdicts": expected,
    }
    assert set(final_live) == {root, independent}
    assert manifest["current_live_ids"] == list(final_live)
    (args.out / "oracle.json").write_text(
        json.dumps(oracle, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
