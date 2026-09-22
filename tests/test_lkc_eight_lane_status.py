import json
import unittest
from pathlib import Path

class EightLaneStatusTests(unittest.TestCase):
    def test_status_file_has_all_eight_lanes_and_clean_boundaries(self):
        d=json.loads(Path("benchmarks/lean_kernel/records/eight-lane-status-v1.json").read_text())
        expected={"partition","primecount","mertens","fib","polydisc","ca-rule110","permanent","sha256"}
        self.assertEqual(set(d["lanes"]),expected)
        self.assertTrue(d["lanes"]["partition"]["best_local"]["universal_proof"])
        self.assertEqual(d["lanes"]["partition"]["status"],"EXTERNAL_PROMOTE_PRACTICE")
        self.assertFalse(d["lanes"]["primecount"]["screen_candidate"]["universal_proof"])
        self.assertEqual(d["lanes"]["mertens"]["status"],"REFUTED_RESOURCE")
        self.assertEqual(d["lanes"]["permanent"]["status"],"EXTERNAL_PROMOTE_PRACTICE")
        self.assertTrue(d["lanes"]["permanent"]["champion"]["universal_proof"])
        self.assertEqual(d["lanes"]["permanent"]["external_champion"]["external_run_id"],213)
        self.assertEqual(d["lanes"]["sha256"]["status"],"EXTERNAL_PROMOTE_PRACTICE")
        self.assertTrue(d["lanes"]["sha256"]["champion"]["universal_proof"])
        self.assertEqual(d["lanes"]["sha256"]["external_champion"]["external_run_id"],215)

if __name__=="__main__":
    unittest.main()
