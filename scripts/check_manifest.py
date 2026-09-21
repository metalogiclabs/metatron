import json, re, sys
from pathlib import Path

STATUSES = {"QUALIFIED", "PARTIAL", "PENDING", "HISTORICAL", "CONJECTURAL"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")

def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text())

def validate_manifest(data: dict) -> list[str]:
    errors = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    deps = data.get("dependencies")
    if not isinstance(deps, list):
        return errors + ["dependencies must be a list"]
    seen = set()
    for dep in deps:
        ident = dep.get("id", "<missing>")
        if ident in seen:
            errors.append(f"{ident}: duplicate id")
        seen.add(ident)
        if dep.get("status") not in STATUSES:
            errors.append(f"{ident}: invalid status")
        if dep.get("status") == "QUALIFIED":
            if not HEX40.fullmatch(dep.get("commit", "")):
                errors.append(f"{ident}: QUALIFIED requires exact commit")
            blob_sha = dep.get("blob_sha")
            artifact_id = dep.get("artifact_id")
            if not (
                (isinstance(blob_sha, str) and HEX40.fullmatch(blob_sha))
                or isinstance(artifact_id, int)
            ):
                errors.append(f"{ident}: QUALIFIED requires exact blob_sha or artifact_id")
            run = dep.get("qualification_run")
            if not isinstance(run, dict):
                errors.append(f"{ident}: QUALIFIED requires qualification_run")
            else:
                if run.get("conclusion") != "success":
                    errors.append(f"{ident}: qualified run must succeed")
                if not isinstance(run.get("url"), str) or not run["url"]:
                    errors.append(f"{ident}: qualification_run requires URL")
    return errors

if __name__ == "__main__":
    errs = validate_manifest(load_manifest(Path("evidence/manifests/dependencies.yaml")))
    print("\n".join(errs))
    raise SystemExit(bool(errs))
