#!/usr/bin/env python3
"""Fail-closed validator for the preregistered G14-001 PProd replication record."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EXPECTED_VERSION = "g14-pprod-replication-v0"
EXPECTED_EXPERIMENT = "G14-001"
EXPECTED_G13_HEAD = "6b50ae9d3a5543528ca815b69b423978dee0ab08"
EXPECTED_G13_SEAL = {
    "run": 35668452215,
    "job": 106559301866,
    "artifact": 10670935477,
    "digest": "sha256:fe0207e05ffb8564ce7ff076250f482b69a58bd4928fe436204c2d62c038f556",
}
EXPECTED_DELTA = ["sort_polymorphic_parameter_and_result_levels"]
ALLOWED_PERF = {
    "DIAGNOSTIC_ONLY",
    "UNKNOWN_NO_SAME_COHORT_HARDWARE_COUNTERS",
}
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _need(obj, key, errors, where):
    if not isinstance(obj, dict) or key not in obj:
        errors.append(f"{where}.{key}: missing")
        return None
    return obj[key]


def validate(record):
    errors = []
    if not isinstance(record, dict):
        return ["record: expected object"]

    if record.get("version") != EXPECTED_VERSION:
        errors.append("version: wrong contract version")
    if record.get("experiment") != EXPECTED_EXPERIMENT:
        errors.append("experiment: must be G14-001")

    pred = _need(record, "predecessor", errors, "record") or {}
    if pred.get("g13_head") != EXPECTED_G13_HEAD:
        errors.append("predecessor.g13_head: does not bind sealed G13")
    if pred.get("external_seal") != EXPECTED_G13_SEAL:
        errors.append("predecessor.external_seal: does not match sealed G13 evidence")

    residual = _need(record, "residual", errors, "record") or {}
    if residual.get("tutorial") != 41:
        errors.append("residual.tutorial: must be 41")
    if residual.get("pre_verdict") != "UNKNOWN":
        errors.append("residual.pre_verdict: must remain UNKNOWN before G14")
    fixture = residual.get("fixture_sha256")
    if not isinstance(fixture, str) or not HEX64.fullmatch(fixture):
        errors.append("residual.fixture_sha256: expected 64 lowercase hex chars")

    hyp = _need(record, "hypothesis", errors, "record") or {}
    if hyp.get("proposed_delta") != EXPECTED_DELTA:
        errors.append("hypothesis.proposed_delta: differs from preregistered delta")

    result = _need(record, "result", errors, "record") or {}
    head = result.get("g14_head")
    if not isinstance(head, str) or not GIT_SHA.fullmatch(head):
        errors.append("result.g14_head: expected full 40-character lowercase git SHA")
    if result.get("exact_pprod") != "ACCEPT":
        errors.append("result.exact_pprod: must be ACCEPT")
    if result.get("malformed_recognized") != "REJECT":
        errors.append("result.malformed_recognized: must be REJECT")
    if result.get("unsupported_neighbors") != "UNKNOWN":
        errors.append("result.unsupported_neighbors: must be UNKNOWN")
    if result.get("existing_handlers_unchanged") is not True:
        errors.append("result.existing_handlers_unchanged: must be true")
    if result.get("shared_abstraction_promoted") is not False:
        errors.append("result.shared_abstraction_promoted: G14 cannot promote abstraction")
    if result.get("forbidden_authority_added") is not False:
        errors.append("result.forbidden_authority_added: must be false")
    observed = result.get("observed_delta")
    if not isinstance(observed, list) or not observed:
        errors.append("result.observed_delta: must record the mechanical structural diff")
    if not isinstance(result.get("replicated"), bool):
        errors.append("result.replicated: must explicitly record true or false")

    diff = result.get("differential")
    if not isinstance(diff, dict):
        errors.append("result.differential: missing")
    else:
        expected = {"identical": 40, "earned_delta": 1, "mismatches": 0}
        if diff != expected:
            errors.append(
                "result.differential: expected 40 identical + 1 earned delta + 0 mismatches"
            )

    formal = _need(record, "formal", errors, "record") or {}
    if formal.get("semantic_warrant") is not True:
        errors.append("formal.semantic_warrant: must be true")
    if formal.get("rust_refinement") is not False:
        errors.append("formal.rust_refinement: must be false")
    if formal.get("whole_checker_verification") is not False:
        errors.append("formal.whole_checker_verification: must be false")

    perf = _need(record, "performance", errors, "record") or {}
    if perf.get("status") not in ALLOWED_PERF:
        errors.append("performance.status: must remain diagnostic/UNKNOWN under this contract")
    if perf.get("promotion") is not False:
        errors.append("performance.promotion: must be false")

    ev = _need(record, "evidence", errors, "record") or {}
    for key in ("run", "job", "artifact"):
        if not isinstance(ev.get(key), int) or ev[key] <= 0:
            errors.append(f"evidence.{key}: expected positive integer")
    if not isinstance(ev.get("digest"), str) or not DIGEST.fullmatch(ev["digest"]):
        errors.append("evidence.digest: expected sha256:<64 lowercase hex>")

    return errors


def main(argv):
    if len(argv) != 2:
        print("usage: check_g14_replication.py RECORD.json", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        record = json.loads(path.read_text())
    except Exception as exc:
        print(f"{path}: {exc}", file=sys.stderr)
        return 2
    errors = validate(record)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("G14_REPLICATION_RECORD_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
