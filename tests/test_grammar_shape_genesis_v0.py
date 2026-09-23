import inspect
import unittest

from scripts.grammar_shape_genesis_v0 import (
    binary_grammar,
    report,
    run_once,
    synthesize_binary_shape,
    unary_grammar,
)


class GrammarShapeGenesisTests(unittest.TestCase):
    def test_shape_synthesizer_has_no_target(self):
        self.assertEqual(
            tuple(inspect.signature(synthesize_binary_shape).parameters),
            ("current_residual", "installed", "dim"),
        )

    def test_declared_grammars_are_extensional_not_named_operator_families(self):
        self.assertEqual(len(unary_grammar(5)), 10)
        self.assertEqual(len(binary_grammar(5)), 80)
        self.assertEqual(
            {p.table for p in binary_grammar(5)},
            {
                (0, 1, 0, 1),
                (0, 1, 1, 0),
                (1, 0, 0, 1),
                (1, 0, 1, 0),
            },
        )

    def test_unary_exhaustion_forces_binary_shape_then_constructor_reuse(self):
        r = run_once()
        self.assertEqual(r["residual_trace"], [240, 112, 48, 16, 0])
        self.assertEqual(r["generic_binary_synthesis_calls"], 2)
        self.assertEqual(r["induced_constructor_calls"], 2)
        self.assertEqual(
            [g["mode"] for g in r["generations"]],
            [
                "grammar_shape_genesis",
                "generic_binary_synthesis",
                "induced_binary_constructor",
                "induced_binary_constructor",
            ],
        )
        self.assertEqual(r["generations"][0]["unary_grammar_max_gain"], 0)
        self.assertEqual(r["generations"][0]["selected_program"]["arity"], 2)
        self.assertTrue(r["generations"][1]["constructor_promoted_now"])
        self.assertEqual(r["constructor_schema"]["arity"], 2)
        self.assertEqual(r["constructor_schema"]["table"], [0, 1, 1, 0])

    def test_controls(self):
        r = report()
        self.assertEqual(
            r["verdict"], "PASS_RESIDUAL_DRIVEN_GRAMMAR_SHAPE_GENESIS"
        )
        self.assertTrue(r["result"]["restart"]["same_interface"])
        self.assertTrue(r["result"]["restart"]["same_constructor"])
        self.assertTrue(r["result"]["semantic_sham"]["same_controls"])
        self.assertTrue(r["result"]["knockout"]["restores_seed_interface"])


if __name__ == "__main__":
    unittest.main()
