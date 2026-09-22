import unittest
from scripts.separating_hypergraph_prospective_v2 import build_report

class ProspectiveV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=build_report()

    def test_preregistration(self):
        self.assertEqual(self.r["preregistration_commit"],
          "6288e8aaa87b40f56bd0bc4adfa2c1f0c1bef5ac")

    def test_v12(self):
        x=self.r["targets"]["predictive_causal_state_genesis_v12"]
        self.assertEqual(x["history_count"],364)
        self.assertEqual(x["candidate_count"],6)
        self.assertEqual(x["full_predictive_classes"],5)
        self.assertEqual(x["residual_pair_count"],44189)
        self.assertEqual(x["maximum_coverage"],44189)
        self.assertEqual(x["maximum_coverage_class"],[4,5])
        self.assertEqual(x["independently_complete_singletons"],[4,5])
        self.assertEqual(x["exact_minimum_cover"],[4])
        self.assertEqual(x["greedy_cover"],[4])
        self.assertTrue(x["historical_selected_in_top_class"])

    def test_v21(self):
        x=self.r["targets"]["residual_generated_transformation_language_v21"]
        self.assertEqual(x["cell_count"],25)
        self.assertEqual(x["l0_candidate_transform_count"],14400)
        self.assertEqual(x["l0_symmetry_count"],10)
        self.assertEqual(x["initial_orbit_count"],3)
        self.assertEqual(x["initial_orbit_sizes"],[5,10,10])
        self.assertEqual(x["residual_pair_count"],50)
        self.assertEqual(x["candidate_generated_swaps"],50)
        self.assertEqual(x["maximum_coverage"],50)
        self.assertEqual(x["exact_minimum_cover_size"],1)
        self.assertEqual(x["greedy_cover_size"],1)
        self.assertFalse(x["wrong_control_replay"])

    def test_overall(self):
        self.assertEqual(self.r["status"],"POSITIVE_PROSPECTIVE_SIGNAL")
        for x in self.r["targets"].values():
            self.assertTrue(x["gates"]["G1_exact_cover_resolves_all"])
            self.assertTrue(x["gates"]["G2_no_false_control"])
            self.assertTrue(x["gates"]["G3_greedy_reported_exactly"])
            self.assertTrue(x["gates"]["G4_top_class_contains_independently_accepted"])

if __name__=="__main__":unittest.main()
