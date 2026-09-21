import unittest

from runtime.metatron.model import Query, STEP_TABLE, State
from runtime.metatron.machine import Machine
from runtime.metatron.serialization import dump_machine, load_machine


class SerializationTests(unittest.TestCase):
    def test_restart_preserves_active_historical_and_warrant_state(self):
        machine = Machine.genesis()
        residual = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)
        relation, rel_cert = machine.verify_relation(("step", "step"), "step")
        machine.install_relation(relation, rel_cert)
        machine.set_queries([Query.IS_ZERO])
        machine.project()

        payload = dump_machine(machine)
        restarted = load_machine(payload)

        self.assertEqual(dump_machine(restarted), payload)
        self.assertEqual(restarted.execute("step", State.ZERO), State.ONE)
        self.assertEqual(restarted.active_partition, ((0,), (1, 2)))
        self.assertEqual(restarted.relations(), ((("step", "step"), "step"),))
        self.assertEqual(restarted.lineage, machine.lineage)
        self.assertEqual(restarted.certificates, machine.certificates)
        self.assertEqual(restarted.residual_certificates, machine.residual_certificates)
        self.assertEqual(restarted._next_residual_serial, machine._next_residual_serial)
        self.assertEqual(restarted.live_certificates, machine.live_certificates)
        self.assertEqual(restarted.revoked_certificates, machine.revoked_certificates)


if __name__ == "__main__":
    unittest.main()
