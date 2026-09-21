import unittest

from runtime.metatron.model import Query, STEP_TABLE, State, eval_query
from runtime.metatron.machine import Machine, RevokedCapabilityError
from runtime.metatron.serialization import dump_machine, load_machine


class CapstoneTests(unittest.TestCase):
    def test_complete_loop(self):
        machine = Machine.genesis()

        residual = machine.certify_target(STEP_TABLE)
        self.assertIsNotNone(residual)
        self.assertEqual(residual.closure_size, 1)

        candidate = machine.free_extend(residual, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)
        self.assertEqual(machine.execute("step", State.ZERO), State.ONE)

        relation, rel_cert = machine.verify_relation(("step", "step"), "step")
        machine.install_relation(relation, rel_cert)
        self.assertEqual(machine.relations(), ((("step", "step"), "step"),))

        machine.set_queries([Query.IS_ZERO])
        machine.project()
        self.assertEqual(machine.active_partition, ((0,), (1, 2)))

        for state in State:
            full = eval_query(Query.IS_ZERO, machine.execute("step", state))
            source_class = next(
                i for i, block in enumerate(machine.active_partition)
                if int(state) in block
            )
            quotient_target = (1, 1)[source_class]
            self.assertEqual(full, quotient_target == 0)

        payload = dump_machine(machine)
        restarted = load_machine(payload)
        self.assertEqual(dump_machine(restarted), payload)
        self.assertEqual(restarted.execute("step", State.ZERO), State.ONE)

        promotion = next(e for e in restarted.lineage if e.kind == "PROMOTE")
        restarted.revoke(cert.id)
        with self.assertRaises(RevokedCapabilityError):
            restarted.execute("step", State.ZERO)
        self.assertIn(promotion, restarted.lineage)

        prefix = tuple(restarted.lineage)
        restarted.set_queries([Query.IS_ZERO, Query.IS_ONE])
        restarted.project()
        self.assertEqual(restarted.active_partition, ((0,), (1,), (2,)))
        self.assertEqual(tuple(restarted.lineage[:len(prefix)]), prefix)


if __name__ == "__main__":
    unittest.main()
