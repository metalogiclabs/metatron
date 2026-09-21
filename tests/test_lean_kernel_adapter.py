import json
import unittest
from pathlib import Path

from benchmarks.lean_kernel.adapter import CandidateEvidence, Measurement, compare


CASES = ("P1:0@n=14", "P2:0@n=22", "P3:0@n=32")
COHORT = "sair-playground-grouped-practice-v1-partition-14-22-32"


def pmu(source, values):
    return Measurement(
        metric="perf_instructions",
        cohort_id=COHORT,
        case_ids=CASES,
        values=tuple(values),
        official=False,
        scoreable=False,
        source=source,
    )


class LeanKernelAdapterTests(unittest.TestCase):
    def test_partition_v5_promotes_on_same_plan_external_pmu(self):
        v4 = CandidateEvidence(
            "v4-rowdp", True, True,
            pmu("SAIR playground run 191", (487757592, 1395165807, 3470753040)),
            1.877882057,
        )
        v5 = CandidateEvidence(
            "v5-natfold", True, True,
            pmu("SAIR playground run 198", (396369526, 1167256227, 2982486899)),
            1.311141315,
        )
        result = compare(v5, v4)
        self.assertEqual(result.decision, "PROMOTE")
        self.assertEqual(result.incumbent_total, 5353676439)
        self.assertEqual(result.candidate_total, 4546112652)
        self.assertAlmostEqual(result.improvement_fraction, 0.15084284532347322)

    def test_v6_and_v7_are_rejected_by_frozen_local_proxy_before_spending_pmu(self):
        v5 = CandidateEvidence("v5", True, True, None, 1.311141315)
        v6 = CandidateEvidence("v6", True, True, None, 1.455617047)
        v7 = CandidateEvidence("v7", True, True, None, 4.648955425)
        self.assertEqual(compare(v6, v5).decision, "REJECT_REGRESSION")
        self.assertEqual(compare(v7, v5).decision, "REJECT_REGRESSION")

    def test_different_cohorts_are_not_compared_as_scores(self):
        a = CandidateEvidence("a", True, True, pmu("a", (10, 20, 30)), 1.0)
        other = Measurement(
            metric="perf_instructions",
            cohort_id="official-hidden-plan",
            case_ids=("hidden:1",),
            values=(1,),
            official=True,
            scoreable=True,
            source="leaderboard",
        )
        b = CandidateEvidence("b", True, True, other, 1.0)
        self.assertEqual(compare(a, b).decision, "MEASURE_EXTERNAL")

    def test_record_reconciles_exact_totals_and_preserves_frontier_boundary(self):
        record = json.loads(Path(
            "benchmarks/lean_kernel/records/partition-v4-v7.json"
        ).read_text())
        self.assertEqual(
            sum(record["candidates"]["v4-rowdp"]["external"]["values"]),
            record["candidates"]["v4-rowdp"]["external"]["total"],
        )
        self.assertEqual(
            sum(record["candidates"]["v5-natfold"]["external"]["values"]),
            record["candidates"]["v5-natfold"]["external"]["total"],
        )
        self.assertFalse(record["frontier_reference"]["same_cohort_as_practice"])


if __name__ == "__main__":
    unittest.main()
