import copy
import unittest

from scripts.check_g14_replication import validate


def valid_record():
    return {
        "version": "g14-pprod-replication-v0",
        "experiment": "G14-001",
        "predecessor": {
            "g13_head": "6b50ae9d3a5543528ca815b69b423978dee0ab08",
            "external_seal": {
                "run": 35668452215,
                "job": 106559301866,
                "artifact": 10670935477,
                "digest": "sha256:fe0207e05ffb8564ce7ff076250f482b69a58bd4928fe436204c2d62c038f556",
            },
        },
        "residual": {
            "tutorial": 41,
            "pre_verdict": "UNKNOWN",
            "fixture_sha256": "a" * 64,
        },
        "hypothesis": {
            "proposed_delta": ["sort_polymorphic_parameter_and_result_levels"],
        },
        "result": {
            "g14_head": "b" * 40,
            "exact_pprod": "ACCEPT",
            "malformed_recognized": "REJECT",
            "unsupported_neighbors": "UNKNOWN",
            "existing_handlers_unchanged": True,
            "shared_abstraction_promoted": False,
            "forbidden_authority_added": False,
            "observed_delta": ["sort_polymorphic_parameter_and_result_levels"],
            "replicated": True,
            "differential": {
                "identical": 40,
                "earned_delta": 1,
                "mismatches": 0,
            },
        },
        "formal": {
            "semantic_warrant": True,
            "rust_refinement": False,
            "whole_checker_verification": False,
        },
        "performance": {
            "status": "UNKNOWN_NO_SAME_COHORT_HARDWARE_COUNTERS",
            "promotion": False,
        },
        "evidence": {
            "run": 1,
            "job": 2,
            "artifact": 3,
            "digest": "sha256:" + "c" * 64,
        },
    }


class G14ReplicationContractTests(unittest.TestCase):
    def test_valid_replication_record(self):
        self.assertEqual(validate(valid_record()), [])

    def test_valid_falsification_record_does_not_force_replication(self):
        record = valid_record()
        record["result"]["replicated"] = False
        record["result"]["observed_delta"] = [
            "sort_polymorphic_parameter_and_result_levels",
            "unexpected_extra_degree_of_freedom",
        ]
        self.assertEqual(validate(record), [])

    def test_wrong_predecessor_fails(self):
        record = valid_record()
        record["predecessor"]["g13_head"] = "0" * 40
        self.assertTrue(any("sealed G13" in e for e in validate(record)))

    def test_premature_abstraction_promotion_fails(self):
        record = valid_record()
        record["result"]["shared_abstraction_promoted"] = True
        self.assertTrue(any("cannot promote abstraction" in e for e in validate(record)))

    def test_broader_neighbor_acceptance_fails(self):
        record = valid_record()
        record["result"]["unsupported_neighbors"] = "ACCEPT"
        self.assertTrue(any("must be UNKNOWN" in e for e in validate(record)))

    def test_differential_regression_fails(self):
        record = valid_record()
        record["result"]["differential"]["mismatches"] = 1
        self.assertTrue(any("40 identical" in e for e in validate(record)))

    def test_performance_promotion_fails(self):
        record = valid_record()
        record["performance"]["promotion"] = True
        self.assertTrue(any("must be false" in e for e in validate(record)))


if __name__ == "__main__":
    unittest.main()
