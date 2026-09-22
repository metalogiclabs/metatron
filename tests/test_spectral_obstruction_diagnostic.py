import unittest

from scripts.spectral_obstruction_diagnostic import (
    authority_signature,
    build_report,
    spectral_metrics,
    warrant_lifecycle,
    _edge_graph_from_live_warrants,
    _equivalence_graph,
)


class SpectralObstructionDiagnosticTests(unittest.TestCase):
    def test_behavioral_equivalence_graph_is_cluster_tautology(self):
        old = spectral_metrics(*_equivalence_graph(((0,), (1, 2))))
        new = spectral_metrics(*_equivalence_graph(((0,), (1,), (2,))))

        self.assertTrue(old["cluster_graph"])
        self.assertTrue(new["cluster_graph"])
        self.assertAlmostEqual(old["lambda_min"], -1.0, places=9)
        self.assertAlmostEqual(new["lambda_min"], 0.0, places=9)

    def test_successful_capability_moves_negative_mode_wrong_way(self):
        stages = warrant_lifecycle()
        verification = spectral_metrics(
            *_edge_graph_from_live_warrants(stages["verification"])
        )
        capability = spectral_metrics(
            *_edge_graph_from_live_warrants(stages["capability"])
        )

        self.assertLess(capability["lambda_min"], verification["lambda_min"])

    def test_successful_relation_moves_negative_mode_wrong_way(self):
        stages = warrant_lifecycle()
        before = spectral_metrics(
            *_edge_graph_from_live_warrants(stages["relation_verification"])
        )
        after = spectral_metrics(
            *_edge_graph_from_live_warrants(stages["relation"])
        )

        self.assertLess(after["lambda_min"], before["lambda_min"])

    def test_inert_measurement_changes_spectrum_not_authority(self):
        stages = warrant_lifecycle()
        base = stages["relation"]
        measured = stages["measurement"]
        base_metric = spectral_metrics(*_edge_graph_from_live_warrants(base))
        measured_metric = spectral_metrics(*_edge_graph_from_live_warrants(measured))

        self.assertEqual(authority_signature(base), authority_signature(measured))
        self.assertGreater(
            abs(base_metric["lambda_min"] - measured_metric["lambda_min"]),
            1e-6,
        )

    def test_report_rejects_core_promotion(self):
        report = build_report()
        self.assertEqual(report["status"], "FALSIFIED_FOR_CORE_PROMOTION")
        self.assertTrue(all(report["findings"].values()))


if __name__ == "__main__":
    unittest.main()
