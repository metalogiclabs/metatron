import inspect
import unittest

from scripts.residual_driven_interface_v0 import (
    canonical_semantics,
    choose_next_process,
    observations,
    report,
    residual_from_target,
    run_once,
)


class ResidualDrivenInterfaceTests(unittest.TestCase):
    def test_selector_api_has_no_target(self):
        params = tuple(inspect.signature(choose_next_process).parameters)
        self.assertEqual(params, ("residual", "installed", "semantics"))
        self.assertFalse(any("target" in p for p in params))

    def test_three_generations_are_derived_from_one_loop(self):
        result = run_once(canonical_semantics())
        self.assertEqual(result["residual_counts"], [56, 24, 8, 0])
        self.assertEqual(result["process_sizes"], [2, 2, 2])
        self.assertEqual(result["generation_count"], 3)

    def test_no_singleton_can_ignite_first_generation(self):
        sem = canonical_semantics()
        residual = residual_from_target(tuple(range(16)), frozenset(), sem)
        selected, covered = choose_next_process(residual, frozenset(), sem)
        self.assertEqual(len(selected), 2)
        self.assertEqual(len(covered), 32)
        for atom in sem.atoms:
            self.assertEqual(observations(frozenset((atom,)), sem), (0,))

    def test_full_controls_and_rename_invariance(self):
        r = report()
        self.assertEqual(r["verdict"], "PASS_RESIDUAL_ONLY_NEXT_INTERFACE")
        self.assertTrue(all(r["rename_control"]["invariants"].values()))
        self.assertTrue(r["primary"]["restart"]["installed_equal"])
        self.assertTrue(r["primary"]["semantic_sham"]["installed_equal"])
        self.assertTrue(r["primary"]["knockout"]["restores_seed_interface"])


if __name__ == "__main__":
    unittest.main()
