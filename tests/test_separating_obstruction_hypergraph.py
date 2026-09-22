import itertools
import unittest

from scripts.separating_obstruction_hypergraph import (
    build_report,
    future_signatures,
    generator_edges,
    minimum_separating_basis,
    greedy_separating_basis,
    nucleus_genesis_fixture,
    relabel_world,
    unresolved_pairs,
)


class SeparatingObstructionHypergraphTests(unittest.TestCase):
    def setUp(self):
        self.states, self.actions, self.tests = nucleus_genesis_fixture()

    def test_retained_future_observation_partitions_are_reproduced(self):
        zero = unresolved_pairs(
            self.states,
            self.actions,
            self.tests,
            protected=("IS_ZERO",),
        )
        full = unresolved_pairs(
            self.states,
            self.actions,
            self.tests,
            protected=("IS_ZERO", "IS_ONE"),
        )

        self.assertEqual(zero, frozenset({(1, 2)}))
        self.assertEqual(full, frozenset())

    def test_future_closure_makes_is_one_a_complete_separator_from_empty(self):
        unresolved, edges = generator_edges(
            self.states,
            self.actions,
            self.tests,
            protected=(),
            candidates=("IS_ZERO", "IS_ONE"),
        )

        self.assertEqual(len(unresolved), 3)
        self.assertEqual(edges["IS_ZERO"], frozenset({(0, 1), (0, 2)}))
        self.assertEqual(edges["IS_ONE"], unresolved)
        self.assertEqual(
            future_signatures(
                self.states, self.actions, self.tests["IS_ONE"]
            ),
            ((False, True, False), (True, True, False)),
        )

    def test_exact_basis_compresses_three_pair_residual_to_one_generator(self):
        unresolved, edges = generator_edges(
            self.states,
            self.actions,
            self.tests,
            protected=(),
            candidates=("IS_ZERO", "IS_ONE"),
        )

        self.assertEqual(minimum_separating_basis(unresolved, edges), ("IS_ONE",))
        self.assertEqual(greedy_separating_basis(unresolved, edges), ("IS_ONE",))

    def test_current_residual_has_exactly_one_missing_generator(self):
        unresolved, edges = generator_edges(
            self.states,
            self.actions,
            self.tests,
            protected=("IS_ZERO",),
            candidates=("IS_ONE",),
        )

        self.assertEqual(unresolved, frozenset({(1, 2)}))
        self.assertEqual(edges["IS_ONE"], unresolved)
        self.assertEqual(minimum_separating_basis(unresolved, edges), ("IS_ONE",))

    def test_defect_strictly_descends_on_retained_history(self):
        d0 = len(unresolved_pairs(
            self.states, self.actions, self.tests, protected=()
        ))
        d1 = len(unresolved_pairs(
            self.states, self.actions, self.tests, protected=("IS_ZERO",)
        ))
        d2 = len(unresolved_pairs(
            self.states,
            self.actions,
            self.tests,
            protected=("IS_ZERO", "IS_ONE"),
        ))

        self.assertEqual((d0, d1, d2), (3, 1, 0))

    def test_metrics_are_invariant_under_all_state_relabelings(self):
        baseline_unresolved, baseline_edges = generator_edges(
            self.states,
            self.actions,
            self.tests,
            protected=("IS_ZERO",),
            candidates=("IS_ONE",),
        )
        baseline = (
            len(baseline_unresolved),
            len(minimum_separating_basis(baseline_unresolved, baseline_edges)),
            sorted(len(edge) for edge in baseline_edges.values()),
        )

        for permutation in itertools.permutations(self.states):
            rs, ra, rt = relabel_world(
                self.states, self.actions, self.tests, permutation
            )
            unresolved, edges = generator_edges(
                rs,
                ra,
                rt,
                protected=("IS_ZERO",),
                candidates=("IS_ONE",),
            )
            observed = (
                len(unresolved),
                len(minimum_separating_basis(unresolved, edges)),
                sorted(len(edge) for edge in edges.values()),
            )
            self.assertEqual(observed, baseline)

    def test_report_keeps_claim_boundary(self):
        report = build_report()
        self.assertEqual(
            report["status"],
            "POSITIVE_FINITE_SIGNAL_NOT_CORE_AUTHORITY",
        )
        self.assertTrue(all(report["findings"].values()))
        self.assertIn("held-out predictive value", report["verdict"])


if __name__ == "__main__":
    unittest.main()
