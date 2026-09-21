from __future__ import annotations

import json
import re
import sys
from pathlib import Path


HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def validate_certificate(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("status") != "BOUNDED_POSITIVE":
        errors.append("status must be BOUNDED_POSITIVE")

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

    frozen = data.get("frozen")
    if not isinstance(frozen, dict):
        errors.append("frozen must be an object")
    else:
        for key in ("food_sha256", "developmental_law_sha256"):
            if not HEX64.fullmatch(frozen.get(key, "")):
                errors.append(f"frozen.{key} must be 64-hex")

    chain = data.get("chain")
    if not isinstance(chain, list) or len(chain) < 2:
        errors.append("chain must contain at least two recurrence arrows")
    else:
        for i, step in enumerate(chain, 1):
            if not isinstance(step, dict):
                errors.append(f"chain[{i}] must be an object")
                continue
            for key in (
                "genesis",
                "nucleus_before",
                "nucleus_after",
                "next_residual",
                "next_realizer",
            ):
                if not isinstance(step.get(key), str) or not step[key]:
                    errors.append(f"chain[{i}].{key} is required")
            if step.get("residual_newly_available") is not True:
                errors.append(
                    f"chain[{i}].residual_newly_available must be true"
                )
            if step.get("realizer_newly_available") is not True:
                errors.append(
                    f"chain[{i}].realizer_newly_available must be true"
                )
            if step.get("realizer_satisfies_developmental_law") is not True:
                errors.append(
                    "chain["
                    f"{i}].realizer_satisfies_developmental_law must be true"
                )

    controls = data.get("controls")
    expected_controls = {
        "future_withholding": "PASS",
        "knockout": "PASS",
        "semantic_sham": "PASS",
        "restart": "PASS",
        "sealed_semantics": "IDENTICAL",
    }
    if not isinstance(controls, dict):
        errors.append("controls must be an object")
    else:
        for key, expected in expected_controls.items():
            if controls.get(key) != expected:
                errors.append(f"controls.{key} must be {expected}")

    return errors


def main(path: Path) -> int:
    data = json.loads(path.read_text())
    errors = validate_certificate(data)
    if errors:
        print("\n".join(errors))
        return 1
    print("NEBULA_CAUSAL_CERTIFICATE=VALID")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_nebula_certificate.py CERTIFICATE.json")
    raise SystemExit(main(Path(sys.argv[1])))
