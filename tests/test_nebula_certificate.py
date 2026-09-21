import unittest

from scripts.check_nebula_certificate import validate_certificate


def good():
    return {
        "schema_version": 1,
        "status": "BOUNDED_POSITIVE",
        "source": {
            "repo": "metalogiclabs/mathgraph-lean-kernel",
            "branch": "msi-sustained-nebula-ignition-v41",
            "commit": "a" * 40,
            "run_id": 1,
            "artifact_sha256": "b" * 64,
        },
        "frozen": {
            "food_sha256": "c" * 64,
            "developmental_law_sha256": "d" * 64,
        },
        "chain": [
            {
                "genesis": "G1",
                "nucleus_before": "N0",
                "nucleus_after": "N1",
                "next_residual": "rho2",
                "next_realizer": "K2",
                "residual_newly_available": True,
                "realizer_newly_available": True,
                "realizer_satisfies_developmental_law": True,
            },
            {
                "genesis": "G2",
                "nucleus_before": "N1",
                "nucleus_after": "N2",
                "next_residual": "rho3",
                "next_realizer": "K3",
                "residual_newly_available": True,
                "realizer_newly_available": True,
                "realizer_satisfies_developmental_law": True,
            },
        ],
        "controls": {
            "future_withholding": "PASS",
            "knockout": "PASS",
            "semantic_sham": "PASS",
            "restart": "PASS",
            "sealed_semantics": "IDENTICAL",
        },
    }


class NebulaCertificateTests(unittest.TestCase):
    def test_complete_certificate_is_valid(self):
        self.assertEqual(validate_certificate(good()), [])

    def test_each_counterfactual_is_mandatory(self):
        for key in (
            "future_withholding",
            "knockout",
            "semantic_sham",
            "restart",
            "sealed_semantics",
        ):
            data = good()
            data["controls"].pop(key)
            self.assertTrue(
                any(f"controls.{key}" in e for e in validate_certificate(data)),
                key,
            )

    def test_chronology_without_novelty_does_not_count(self):
        data = good()
        data["chain"][0]["residual_newly_available"] = False
        data["chain"][1]["realizer_newly_available"] = False
        errors = validate_certificate(data)
        self.assertTrue(any("residual_newly_available" in e for e in errors))
        self.assertTrue(any("realizer_newly_available" in e for e in errors))

    def test_realizer_must_satisfy_frozen_developmental_law(self):
        data = good()
        data["chain"][0]["realizer_satisfies_developmental_law"] = False
        self.assertTrue(
            any(
                "realizer_satisfies_developmental_law" in e
                for e in validate_certificate(data)
            )
        )


if __name__ == "__main__":
    unittest.main()
