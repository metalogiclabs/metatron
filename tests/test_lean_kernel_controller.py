import json
import unittest
from pathlib import Path

from benchmarks.lean_kernel.adapter import CandidateEvidence, Measurement
from benchmarks.lean_kernel.controller import FrontierCandidate, FrontierController


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


def partition_trace():
    v4 = FrontierCandidate(
        CandidateEvidence(
            "v4-rowdp",
            True,
            True,
            pmu("SAIR playground run 191", (487757592, 1395165807, 3470753040)),
            1.877882057,
        ),
        "row-dp",
    )
    v5 = FrontierCandidate(
        CandidateEvidence(
            "v5-natfold",
            True,
            True,
            pmu("SAIR playground run 198", (396369526, 1167256227, 2982486899)),
            1.311141315,
        ),
        "folded-multiplicity-sum",
    )
    v6 = FrontierCandidate(
        CandidateEvidence("v6-streaming-list", True, True, None, 1.455617047),
        "streaming-list-sharing",
    )
    v7 = FrontierCandidate(
        CandidateEvidence("v7-array-streaming", True, True, None, 4.648955425),
        "persistent-array-sharing",
    )
    return v4, v5, v6, v7


class FrontierControllerTests(unittest.TestCase):
    def test_partition_trace_promotes_then_rejects_then_escalates_policy(self):
        v4, v5, v6, v7 = partition_trace()
        ctl = FrontierController(v4, escalation_after_distinct_regressions=2)

        e1 = ctl.observe(v5)
        self.assertEqual(e1.action, "PROMOTE")
        self.assertEqual(ctl.champion.evidence.name, "v5-natfold")

        e2 = ctl.observe(v6)
        self.assertEqual(e2.action, "REJECT_REGRESSION")
        self.assertEqual(ctl.champion.evidence.name, "v5-natfold")

        e3 = ctl.observe(v7)
        self.assertEqual(e3.action, "ESCALATE_SEARCH_POLICY")
        self.assertEqual(ctl.champion.evidence.name, "v5-natfold")
        self.assertFalse(e3.certified_insufficiency)

    def test_lineage_is_append_only_and_serial(self):
        v4, v5, v6, v7 = partition_trace()
        ctl = FrontierController(v4)
        ctl.observe(v5)
        prefix = tuple(ctl.lineage)
        ctl.observe(v6)
        ctl.observe(v7)
        self.assertEqual(tuple(ctl.lineage[: len(prefix)]), prefix)
        self.assertEqual([e.serial for e in ctl.lineage], [1, 2, 3])

    def test_policy_escalation_never_mints_insufficiency(self):
        v4, v5, v6, v7 = partition_trace()
        ctl = FrontierController(v4)
        for candidate in (v5, v6, v7):
            ctl.observe(candidate)
        self.assertFalse(ctl.snapshot()["certified_insufficiency"])
        self.assertTrue(all(not e.certified_insufficiency for e in ctl.lineage))

    def test_declared_controller_record_matches_policy_boundary(self):
        data = json.loads(Path(
            "benchmarks/lean_kernel/records/partition-controller-v1.json"
        ).read_text())
        self.assertFalse(data["result"]["certified_insufficiency"])
        self.assertTrue(
            data["controller_policy"][
                "policy_escalation_is_not_certified_insufficiency"
            ]
        )


if __name__ == "__main__":
    unittest.main()
