import unittest
from runtime.metatron.model import ID_TABLE, STEP_TABLE
from runtime.metatron.machine import authority_digest, closure, certify_no_resolution

class ObstructionTests(unittest.TestCase):
    def test_genesis_cannot_express_step(self):
        self.assertEqual(closure({ID_TABLE}), frozenset({ID_TABLE}))
        residual = certify_no_resolution({ID_TABLE}, STEP_TABLE)
        self.assertIsNotNone(residual)
        self.assertEqual(residual.closure_size, 1)
        self.assertEqual(residual.authority_digest, authority_digest({ID_TABLE}))

    def test_existing_target_emits_no_residual(self):
        self.assertIsNone(certify_no_resolution({ID_TABLE}, ID_TABLE))

if __name__ == "__main__":
    unittest.main()
