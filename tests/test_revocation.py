import unittest

from runtime.metatron.model import STEP_TABLE, State
from runtime.metatron.machine import Machine, RevokedCapabilityError


class RevocationTests(unittest.TestCase):
    def test_revocation_disables_execution_but_preserves_history(self):
        machine = Machine.genesis()
        residual = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)
        relation, relation_cert = machine.verify_relation(("step", "step"), "step")
        machine.install_relation(relation, relation_cert)

        promotion = next(
            event for event in machine.lineage
            if event.kind == "PROMOTE"
        )
        relation_record = machine.relations()

        machine.revoke(cert.id)

        with self.assertRaises(RevokedCapabilityError):
            machine.execute("step", State.ZERO)

        self.assertNotIn("step", machine.active_capability_names())
        self.assertIn(promotion, machine.lineage)
        self.assertEqual(machine.relations(), relation_record)
        self.assertTrue(any(
            event.kind == "REVOKE"
            and event.payload["certificate"] == cert.id
            for event in machine.lineage
        ))


if __name__ == "__main__":
    unittest.main()
