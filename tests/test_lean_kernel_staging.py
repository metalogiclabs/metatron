import json
import unittest
from pathlib import Path

from benchmarks.lean_kernel.adapter import CandidateEvidence, Measurement
from benchmarks.lean_kernel.staging import StagedCandidate, TwoTierFrontier


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


def candidate(name, family, local, external=None):
    return StagedCandidate(
        CandidateEvidence(name, True, True, external, local),
        family,
    )


class TwoTierFrontierTests(unittest.TestCase):
    def setUp(self):
        self.v5 = candidate(
            "v5-natfold",
            "folded-multiplicity-sum",
            1.311141315,
            pmu("SAIR playground run 198", (396369526, 1167256227, 2982486899)),
        )
        self.v8 = candidate("v8-shiftzip", "sequential-shift-zip", 0.505994296)
        self.v9 = candidate("v9-directshift", "allocation-free-sequential-shift", 0.320588831)
        self.v10 = candidate("v10-seeded", "seeded-allocation-free-sequential-shift", 0.282958007)

    def test_v8_v9_v10_collapse_to_one_external_request(self):
        ctl = TwoTierFrontier(self.v5)
        self.assertEqual(ctl.observe_local(self.v8).action, "STAGE_FOR_EXTERNAL")
        self.assertEqual(ctl.observe_local(self.v9).action, "REPLACE_STAGED")
        self.assertEqual(ctl.observe_local(self.v10).action, "REPLACE_STAGED")
        self.assertEqual(ctl.external_champion.evidence.name, "v5-natfold")
        self.assertEqual(ctl.next_external_candidate().evidence.name, "v10-seeded")

    def test_local_evidence_never_promotes_external_champion(self):
        ctl = TwoTierFrontier(self.v5)
        for c in (self.v8, self.v9, self.v10):
            ctl.observe_local(c)
        self.assertEqual(ctl.external_champion.evidence.name, "v5-natfold")
        self.assertEqual(
            [e.action for e in ctl.lineage],
            ["STAGE_FOR_EXTERNAL", "REPLACE_STAGED", "REPLACE_STAGED"],
        )

    def test_slower_local_candidate_is_rejected_without_spending_external(self):
        ctl = TwoTierFrontier(self.v5)
        ctl.observe_local(self.v10)
        slower = candidate("slower", "another-family", 0.4)
        event = ctl.observe_local(slower)
        self.assertEqual(event.action, "REJECT_LOCAL_REGRESSION")
        self.assertEqual(ctl.next_external_candidate().evidence.name, "v10-seeded")

    def test_comparable_external_measurement_is_only_promotion_path(self):
        ctl = TwoTierFrontier(self.v5)
        ctl.observe_local(self.v10)
        better = pmu("new run", (100000000, 200000000, 300000000))
        event = ctl.observe_external(self.v10, better)
        self.assertEqual(event.action, "EXTERNAL_PROMOTE")
        self.assertEqual(ctl.external_champion.evidence.name, "v10-seeded")
        self.assertIsNone(ctl.next_external_candidate())

    def test_noncomparable_external_measurement_cannot_promote(self):
        ctl = TwoTierFrontier(self.v5)
        ctl.observe_local(self.v10)
        other = Measurement(
            metric="perf_instructions",
            cohort_id="different-cohort",
            case_ids=("x",),
            values=(1,),
            official=False,
            scoreable=False,
            source="other",
        )
        event = ctl.observe_external(self.v10, other)
        self.assertEqual(event.action, "EXTERNAL_NOT_COMPARABLE")
        self.assertEqual(ctl.external_champion.evidence.name, "v5-natfold")

    def test_record_points_only_to_v10_for_next_measurement(self):
        data = json.loads(Path(
            "benchmarks/lean_kernel/records/partition-v8-v10.json"
        ).read_text())
        self.assertEqual(data["result"]["external_champion"], "v5-natfold")
        self.assertEqual(data["result"]["staged_candidate"], "v10-seeded")
        self.assertFalse(data["result"]["v8_v9_external_measurement_needed"])


if __name__ == "__main__":
    unittest.main()
