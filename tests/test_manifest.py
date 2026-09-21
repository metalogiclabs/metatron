import unittest
from pathlib import Path
from scripts.check_manifest import load_manifest, validate_manifest

class ManifestTests(unittest.TestCase):
    def test_repo_manifest(self):
        self.assertEqual(
            validate_manifest(load_manifest(Path("evidence/manifests/dependencies.yaml"))),
            [],
        )

    def test_qualified_requires_exact_commit_and_evidence(self):
        base = {
            "id": "x",
            "status": "QUALIFIED",
            "repo": "a/b",
            "commit": "c" * 40,
            "blob_sha": "b" * 40,
            "qualification_run": {
                "id": 1,
                "conclusion": "success",
                "url": "https://example.invalid/run/1",
            },
        }
        self.assertEqual(
            validate_manifest({"schema_version": 1, "dependencies": [base]}),
            [],
        )

        for field in ("commit", "blob_sha", "qualification_run"):
            bad = dict(base)
            bad.pop(field)
            self.assertTrue(
                validate_manifest({"schema_version": 1, "dependencies": [bad]}),
                field,
            )

        bad_run = dict(base)
        bad_run["qualification_run"] = {"id": 1, "conclusion": "success"}
        self.assertTrue(
            validate_manifest({"schema_version": 1, "dependencies": [bad_run]}),
            "qualification_run.url",
        )

if __name__ == "__main__":
    unittest.main()
