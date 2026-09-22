import inspect
import unittest

from scripts.language_genesis_v0 import (
    choose_schema,
    report,
    run_once,
    schema_family,
)


class LanguageGenesisTests(unittest.TestCase):
    def test_schema_selector_has_no_target_argument(self):
        self.assertEqual(
            tuple(inspect.signature(choose_schema).parameters),
            ("residual", "installed", "schemas", "dim"),
        )

    def test_language_must_be_stuck_before_every_genesis(self):
        r = run_once(False)
        self.assertEqual(r["residual_trace"], [56, 24, 8, 0])
        self.assertEqual(r["generation_count"], 3)
        self.assertTrue(
            all(g["current_language_max_gain"] == 0 for g in r["generations"])
        )

    def test_meta_language_is_generic_transposition_family(self):
        schemas = schema_family(4)
        self.assertEqual(len(schemas), 6)
        self.assertEqual(
            {s.swap for s in schemas},
            {(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)},
        )

    def test_controls_and_schema_name_invariance(self):
        r = report()
        self.assertEqual(
            r["verdict"], "PASS_RESIDUAL_DRIVEN_LANGUAGE_GENESIS"
        )
        self.assertTrue(all(r["schema_rename_control"]["invariants"].values()))
        self.assertTrue(r["primary"]["restart"]["same_observations"])
        self.assertTrue(r["primary"]["semantic_sham"]["same_observations"])
        self.assertTrue(r["primary"]["knockout"]["restores_seed_interface"])


if __name__ == "__main__":
    unittest.main()
