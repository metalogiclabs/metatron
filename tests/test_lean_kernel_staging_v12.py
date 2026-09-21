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


class PartitionV12StagingTests(unittest.TestCase):
    def test_v12_replaces_v11_without_external_promotion(self):
        v5 = candidate(
            "v5-natfold",
            "folded-multiplicity-sum",
            1.311141315,
            pmu("SAIR playground run 198", (396369526, 1167256227, 2982486899)),
        )
        v11 = candidate("v11-one-seed", "closed-form-part-size-1-seed", 0.249743756)
        v12 = candidate("v12-two-seed", "closed-form-part-size-2-seed", 0.2066626)

        ctl = TwoTierFrontier(v5)
        self.assertEqual(ctl.observe_local(v11).action, "STAGE_FOR_EXTERNAL")
        self.assertEqual(ctl.observe_local(v12).action, "REPLACE_STAGED")
        self.assertEqual(ctl.external_champion.evidence.name, "v5-natfold")
        self.assertEqual(ctl.next_external_candidate().evidence.name, "v12-two-seed")

    def test_record_preserves_external_local_boundary(self):
        data = json.loads(Path(
            "benchmarks/lean_kernel/records/partition-v11-v12.json"
        ).read_text())
        self.assertEqual(data["result"]["external_champion"], "v5-natfold")
        self.assertEqual(data["result"]["staged_candidate"], "v12-two-seed")
        self.assertFalse(data["result"]["v8_v9_v10_v11_external_measurement_needed"])
        self.assertEqual(
            data["staging_trace"][-1]["source_sha256"],
            "e2e234dea49ad7a4876676fa0894c70704c5a597ae584f358df63d4afe56690b",
        )


if __name__ == "__main__":
    unittest.main()
