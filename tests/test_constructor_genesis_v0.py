import inspect
import unittest

from scripts.constructor_genesis_v0 import (
    concrete_grammar,
    report,
    run_once,
    synthesize_concrete,
)


class ConstructorGenesisTests(unittest.TestCase):
    def test_generic_synthesizer_has_no_target_argument(self):
        self.assertEqual(
            tuple(inspect.signature(synthesize_concrete).parameters),
            ("current_residual", "dim", "installed_local"),
        )

    def test_generic_grammar_has_no_predeclared_toggle_schema(self):
        grammar = concrete_grammar(5)
        self.assertEqual(len(grammar), 10)
        self.assertTrue(all(w.op == "LocalRewrite" for w in grammar))
        self.assertEqual(
            {w.table for w in grammar},
            {(0, 1), (1, 0)},
        )

    def test_constructor_is_induced_then_reused_on_heldout_parameters(self):
        r = run_once()
        self.assertEqual(r["residual_trace"], [110, 54, 24, 8, 0])
        self.assertEqual(r["generic_synthesis_calls"], 2)
        self.assertEqual(r["induced_instantiation_calls"], 2)
        self.assertEqual(
            [g["mode"] for g in r["generations"]],
            [
                "generic_concrete_synthesis",
                "generic_concrete_synthesis",
                "induced_schema_instantiation",
                "induced_schema_instantiation",
            ],
        )
        self.assertTrue(r["generations"][1]["schema_promoted_now"])
        self.assertEqual(r["schema"]["coord"], "$i")
        self.assertEqual(r["schema"]["table"], [1, 0])

    def test_controls(self):
        r = report()
        self.assertEqual(
            r["verdict"], "PASS_RESIDUAL_DRIVEN_CONSTRUCTOR_GENESIS"
        )
        self.assertTrue(r["result"]["restart"]["same_coords"])
        self.assertTrue(r["result"]["restart"]["same_schema"])
        self.assertTrue(r["result"]["semantic_sham"]["same_coords"])
        self.assertTrue(r["result"]["knockout"]["restores_seed_interface"])


if __name__ == "__main__":
    unittest.main()
