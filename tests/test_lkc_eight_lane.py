import unittest
from pathlib import Path

from benchmarks.lean_kernel.eight_lane import PROBLEMS, build_log, lanes, write_log
from runtime.metatron.nucleus import live, live_ids, loads


class EightLaneTests(unittest.TestCase):
    def test_all_eight_problem_nodes_are_live(self):
        log = build_log()
        names = {node.payload["problem"] for _, node in live(log, "problem")}
        self.assertEqual(names, set(PROBLEMS))

    def test_one_live_decision_per_problem(self):
        log = build_log()
        decisions = [node.payload for _, node in live(log, "decision")]
        self.assertEqual(len(decisions), 8)
        self.assertEqual({d["problem"] for d in decisions}, set(PROBLEMS))

    def test_priority_puts_primecount_proof_first(self):
        schedule = lanes()
        self.assertEqual(schedule[0].problem, "primecount")
        self.assertEqual(schedule[0].action, "PROVE_PROMISING_PROBE")
        self.assertIn("partition", [lane.problem for lane in schedule[:2]])

    def test_unproved_primecount_probe_has_no_verification_node(self):
        log = build_log()
        verifications = [node.payload for _, node in live(log, "verification")]
        subjects = {v["subject"] for v in verifications}
        self.assertNotIn("flash-v5-bitset-probe", subjects)

    def test_rule110_v64_is_not_staged(self):
        lane = next(x for x in lanes() if x.problem == "ca-rule110")
        self.assertEqual(lane.action, "OPTIMIZE_SCORED_2_4_8_PATHS")

    def test_public_package_census_is_warranted_data(self):
        log = build_log()
        counts = {
            node.payload["problem"]: node.payload["count"]
            for _, node in live(log, "public_package_count")
        }
        self.assertEqual(counts["fib"], 2)
        self.assertEqual(sum(counts.values()), 2)

    def test_jsonl_replay_is_exact(self):
        path = Path("/tmp/metatron-lkc8-events.jsonl")
        write_log(path)
        restored = loads(path.read_text())
        self.assertEqual(live_ids(restored), live_ids(build_log()))


if __name__ == "__main__":
    unittest.main()
