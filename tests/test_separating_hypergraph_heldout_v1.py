import unittest

from scripts.separating_hypergraph_heldout_v1 import build_report


class SeparatingHypergraphHeldoutV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report()

    def test_future_equivalence_stage1_hits_historical_family(self):
        stage = self.report["future_equivalence_v1"]["stage1"]
        self.assertEqual(stage["residual_pairs"], 32)
        self.assertEqual(stage["coverage"]["c1"], 32)
        self.assertIn("c1", stage["top_equivalence_class"])
        self.assertTrue(stage["historical_hit"])
        self.assertEqual(len(stage["minimum_basis"]), 1)

    def test_future_equivalence_stage2_hits_historical_family(self):
        stage = self.report["future_equivalence_v1"]["stage2"]
        self.assertEqual(stage["residual_pairs"], 16)
        self.assertEqual(stage["coverage"]["d0"], 16)
        self.assertEqual(stage["coverage"]["h0"], 0)
        self.assertIn("d0", stage["top_equivalence_class"])
        self.assertTrue(stage["historical_hit"])
        self.assertEqual(len(stage["minimum_basis"]), 1)

    def test_v14_exact_cover_beats_historical_search(self):
        result = self.report["induced_residual_history_v14"]
        self.assertEqual(result["heldout_nonpermanent_residuals"], 6)
        self.assertEqual(result["candidate_queries"], 256)
        self.assertEqual(result["maximum_single_query_coverage"], 4)
        self.assertEqual(result["maximum_coverage_queries"], [15, 240])
        self.assertEqual(result["greedy_basis"], [15, 105])
        self.assertEqual(result["exact_minimum_basis"], [15, 105])
        self.assertEqual(result["exact_minimum_basis_size"], 2)
        self.assertEqual(result["historical_total_queries"], 10)
        self.assertEqual(result["historical_successful_queries"], [12, 85, 105])
        self.assertTrue(result["no_false_split_on_permanent_controls"])

    def test_all_promotion_findings_hold(self):
        self.assertEqual(
            self.report["status"],
            "POSITIVE_RETROSPECTIVE_HELDOUT_SIGNAL",
        )
        self.assertTrue(all(self.report["findings"].values()))


if __name__ == "__main__":
    unittest.main()
