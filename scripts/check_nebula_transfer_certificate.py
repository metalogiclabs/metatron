from __future__ import annotations

import json
import re
import sys
from pathlib import Path


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ARMS = ("cold", "warm12", "warm123", "sham123")


def validate_transfer_certificate(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("status") != "BOUNDED_POSITIVE":
        errors.append("status must be BOUNDED_POSITIVE")
    if data.get("target_independent_of_source_lineage") is not True:
        errors.append("target_independent_of_source_lineage must be true")

    source = data.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        if not isinstance(source.get("repo"), str) or "/" not in source["repo"]:
            errors.append("source.repo must be owner/repo")
        if not isinstance(source.get("branch"), str) or not source["branch"]:
            errors.append("source.branch is required")
        if not HEX40.fullmatch(source.get("commit", "")):
            errors.append("source.commit must be exact 40-hex SHA")
        if not isinstance(source.get("run_id"), int) or source["run_id"] <= 0:
            errors.append("source.run_id must be positive integer")
        if not HEX64.fullmatch(source.get("artifact_sha256", "")):
            errors.append("source.artifact_sha256 must be 64-hex")

    inherited = data.get("inherited")
    if not isinstance(inherited, dict):
        errors.append("inherited must be an object")
    else:
        if not HEX40.fullmatch(inherited.get("ignition_source_sha", "")):
            errors.append("inherited.ignition_source_sha must be 40-hex")
        if inherited.get("products") != ["K1:sort", "K2:pi", "K3:pi_continuation"]:
            errors.append("inherited.products must be frozen V41R1 lineage")

    metrics = data.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("metrics must be an object")
    else:
        for corpus in ("acquisition", "heldout"):
            group = metrics.get(corpus)
            if not isinstance(group, dict):
                errors.append(f"metrics.{corpus} must be an object")
                continue
            for arm in ARMS:
                row = group.get(arm)
                if not isinstance(row, dict):
                    errors.append(f"metrics.{corpus}.{arm} is required")
                    continue
                force = row.get("force_calls")
                if not isinstance(force, int) or force <= 0:
                    errors.append(f"metrics.{corpus}.{arm}.force_calls must be positive int")
                witness = row.get("dominant_witness")
                if not isinstance(witness, str) or not witness:
                    errors.append(f"metrics.{corpus}.{arm}.dominant_witness is required")

    controls = data.get("controls")
    expected = {
        "acquisition_semantics": "IDENTICAL",
        "heldout_semantics": "IDENTICAL",
        "same_target_witness": "PASS",
        "causal_marginal": "PASS",
        "k3_real_vs_sham": "PASS",
        "heldout_nonreversal": "PASS",
    }
    if not isinstance(controls, dict):
        errors.append("controls must be an object")
    else:
        for key, value in expected.items():
            if controls.get(key) != value:
                errors.append(f"controls.{key} must be {value}")

    if isinstance(metrics, dict):
        acq = metrics.get("acquisition")
        held = metrics.get("heldout")
        if isinstance(acq, dict) and all(isinstance(acq.get(a), dict) for a in ARMS):
            try:
                cold = acq["cold"]["force_calls"]
                w12 = acq["warm12"]["force_calls"]
                w123 = acq["warm123"]["force_calls"]
                sham = acq["sham123"]["force_calls"]
                if not (w123 < cold):
                    errors.append("warm123 must strictly beat cold on acquisition")
                if not ((w12 < cold) or (w123 < w12)):
                    errors.append("at least one inherited generation must have strict causal marginal")
                if not (w123 < sham):
                    errors.append("semantic K3 must strictly beat sham K3")
                witnesses = {acq[a]["dominant_witness"] for a in ARMS}
                if len(witnesses) != 1:
                    errors.append("acquisition arms must expose same dominant target witness")
            except (KeyError, TypeError):
                pass
        if isinstance(held, dict) and all(isinstance(held.get(a), dict) for a in ARMS):
            try:
                if not (held["warm123"]["force_calls"] <= held["cold"]["force_calls"]):
                    errors.append("heldout transfer advantage must not reverse")
            except (KeyError, TypeError):
                pass

    return errors


def main(path: Path) -> int:
    data = json.loads(path.read_text())
    errors = validate_transfer_certificate(data)
    if errors:
        print("\n".join(errors))
        return 1
    print("NEBULA_TRANSFER_CERTIFICATE=VALID")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_nebula_transfer_certificate.py CERTIFICATE.json")
    raise SystemExit(main(Path(sys.argv[1])))
