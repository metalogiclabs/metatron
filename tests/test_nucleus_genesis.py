import unittest
from dataclasses import replace

from runtime.metatron.genesis import (
    STEP_TABLE,
    Machine,
    Query,
    RevokedCapabilityError,
    State,
    UncertifiedResidualError,
    closure,
    qeval,
)


class NucleusGenesisTests(unittest.TestCase):
    def test_genesis_is_the_minimum_safe_quotient(self):
        machine = Machine.genesis()
        self.assertEqual(machine.partition, ((0,), (1, 2)))
        self.assertEqual(len(closure(machine.active().values())), 1)

    def test_obstruction_forces_one_generator_and_reclosure(self):
        machine = Machine.genesis()
        residual = machine.certify(STEP_TABLE)
        self.assertEqual(residual.size, 1)

        candidate = machine.lift(residual, "step")
        warrant = machine.verify(candidate)
        machine.promote(candidate, warrant)

        self.assertEqual(machine.execute("step", State.ZERO), State.ONE)
        self.assertEqual(machine.execute("step", State.TWO), State.TWO)
        self.assertIn((("step", "step"), "step"), machine.relations)
        self.assertEqual(machine.partition, ((0,), (1, 2)))

    def test_forged_and_stale_obstructions_fail_closed(self):
        machine = Machine.genesis()
        residual = machine.certify(STEP_TABLE)

        with self.assertRaises(UncertifiedResidualError):
            machine.lift(replace(residual, id="residual:forged"), "step")

        candidate = machine.lift(residual, "step")
        warrant = machine.verify(candidate)
        machine.promote(candidate, warrant)

        with self.assertRaises(UncertifiedResidualError):
            machine.lift(residual, "step-again")

    def test_new_future_forces_representation_lift(self):
        machine = Machine.genesis()
        residual = machine.certify(STEP_TABLE)
        candidate = machine.lift(residual, "step")
        machine.promote(candidate, machine.verify(candidate))

        machine.protect(Query.IS_ONE)
        self.assertEqual(machine.partition, ((0,), (1,), (2,)))

        lift = next(
            e for e in reversed(machine.lineage)
            if e.kind == "REPRESENTATION_LIFT"
        )
        self.assertEqual(lift.details["witness"], [1, 2])

        for block in machine.partition:
            for a in block:
                for b in block:
                    for table in closure(machine.active().values()):
                        for query in machine.queries:
                            self.assertEqual(
                                qeval(query, table[a]),
                                qeval(query, table[b]),
                            )

    def test_revocation_retracts_authority_not_history(self):
        machine = Machine.genesis()
        residual = machine.certify(STEP_TABLE)
        candidate = machine.lift(residual, "step")
        warrant = machine.verify(candidate)
        machine.promote(candidate, warrant)
        prefix = tuple(machine.lineage)

        machine.revoke(warrant.id)

        with self.assertRaises(RevokedCapabilityError):
            machine.execute("step", State.ZERO)

        self.assertEqual(tuple(machine.lineage[:len(prefix)]), prefix)
        self.assertNotIn((("step", "step"), "step"), machine.relations)
        regenerated = machine.certify(STEP_TABLE)
        self.assertIsNotNone(regenerated)
        self.assertEqual(regenerated.size, 1)


    def test_restart_uses_compiled_inheritance_without_replaying_discovery(self):
        machine = Machine.genesis()
        residual = machine.certify(STEP_TABLE)
        candidate = machine.lift(residual, "step")
        machine.promote(candidate, machine.verify(candidate))
        machine.protect(Query.IS_ONE)

        payload = machine.dump()
        restarted = Machine.load(payload)

        self.assertEqual(restarted.dump(), payload)
        self.assertEqual(restarted.execute("step", State.ZERO), State.ONE)
        self.assertEqual(restarted.partition, ((0,), (1,), (2,)))


if __name__ == "__main__":
    unittest.main()
