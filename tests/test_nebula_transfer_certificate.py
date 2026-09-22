import unittest

from scripts.check_nebula_transfer_certificate import validate_transfer_certificate


def cert():
    def row(force):
        return {"force_calls": force, "dominant_witness": "src/relevance.rs:82"}

    return {
        "schema_version": 1,
        "status": "BOUNDED_POSITIVE",
        "target_independent_of_source_lineage": True,
        "source": {
            "repo": "metalogiclabs/mathgraph-lean-kernel",
            "branch": "msi-nebula-transfer-v42",
            "commit": "a" * 40,
            "run_id": 1,
            "artifact_sha256": "b" * 64,
        },
        "inherited": {
            "ignition_source_sha": "c" * 40,
            "products": ["K1:sort", "K2:pi", "K3:pi_continuation"],
        },
        "metrics": {
            "acquisition": {
                "cold": row(1000),
                "warm12": row(900),
                "warm123": row(800),
                "sham123": row(850),
            },
            "heldout": {
                "cold": row(500),
                "warm12": row(490),
                "warm123": row(480),
                "sham123": row(495),
            },
        },
        "controls": {
            "acquisition_semantics": "IDENTICAL",
            "heldout_semantics": "IDENTICAL",
            "same_target_witness": "PASS",
            "causal_marginal": "PASS",
            "k3_real_vs_sham": "PASS",
            "heldout_nonreversal": "PASS",
        },
    }


class NebulaTransferCertificateTests(unittest.TestCase):
    def test_complete_transfer_certificate_is_valid(self):
        self.assertEqual(validate_transfer_certificate(cert()), [])

    def test_requires_independent_target(self):
        x = cert()
        x["target_independent_of_source_lineage"] = False
        self.assertTrue(any("target_independent" in e for e in validate_transfer_certificate(x)))

    def test_requires_strict_acquisition_gain(self):
        x = cert()
        x["metrics"]["acquisition"]["warm123"]["force_calls"] = 1000
        self.assertTrue(any("strictly beat cold" in e for e in validate_transfer_certificate(x)))

    def test_requires_causal_marginal(self):
        x = cert()
        x["metrics"]["acquisition"]["warm12"]["force_calls"] = 1000
        x["metrics"]["acquisition"]["warm123"]["force_calls"] = 1000
        self.assertTrue(any("causal marginal" in e for e in validate_transfer_certificate(x)))

    def test_requires_real_k3_to_beat_sham(self):
        x = cert()
        x["metrics"]["acquisition"]["sham123"]["force_calls"] = 800
        self.assertTrue(any("strictly beat sham" in e for e in validate_transfer_certificate(x)))

    def test_rejects_heldout_reversal(self):
        x = cert()
        x["metrics"]["heldout"]["warm123"]["force_calls"] = 501
        self.assertTrue(any("must not reverse" in e for e in validate_transfer_certificate(x)))

    def test_rejects_witness_drift(self):
        x = cert()
        x["metrics"]["acquisition"]["warm123"]["dominant_witness"] = "src/infer.rs:154"
        self.assertTrue(any("same dominant" in e for e in validate_transfer_certificate(x)))


if __name__ == "__main__":
    unittest.main()
