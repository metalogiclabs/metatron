import unittest

from runtime.metatron.nebula import (
    NebulaMachine,
    NotDerivableError,
    UnknownChoiceError,
    select_unique_minimal,
    unresolved_potential,
)


class NebulaIgnitionTests(unittest.TestCase):
    def test_one_terminal_requirement_drives_three_generations(self):
        machine = NebulaMachine.genesis(size=5)

        self.assertEqual(machine.partition, ((0,), (1, 2, 3, 4)))
        self.assertEqual(unresolved_potential(machine.partition), 3)

        generations = machine.ignite()

        self.assertEqual(generations, 3)
        self.assertTrue(machine.satisfied())
        self.assertEqual(
            machine.partition,
            ((0,), (1,), (2,), (3,), (4,)),
        )

        promoted = [
            event.subject
            for event in machine.lineage
            if event.kind == "PROMOTE"
        ]
        self.assertEqual(promoted, ["is_1", "is_2", "is_3"])

    def test_next_obstruction_does_not_exist_before_parent_lift(self):
        machine = NebulaMachine.genesis(size=5)

        # The future block is not a current object in the quotient.
        with self.assertRaises(NotDerivableError):
            machine.certify_named_block((2, 3, 4))

        first = machine.certify_current_obstruction()
        candidate = machine.synthesize_minimal_lift(first)
        machine.promote(candidate, machine.verify(candidate))

        # G1 created the quotient block from which o2 can now be issued.
        self.assertEqual(machine.partition, ((0,), (1,), (2, 3, 4)))
        second = machine.certify_named_block((2, 3, 4))
        self.assertEqual(second.block, (2, 3, 4))

        with self.assertRaises(NotDerivableError):
            machine.certify_named_block((3, 4))

        candidate2 = machine.synthesize_minimal_lift(second)
        machine.promote(candidate2, machine.verify(candidate2))

        # Only after G2 does the third obstruction become derivable.
        third = machine.certify_named_block((3, 4))
        self.assertEqual(third.block, (3, 4))

    def test_each_generation_strictly_reduces_exact_residual(self):
        machine = NebulaMachine.genesis(size=5)
        potentials = [unresolved_potential(machine.partition)]

        while not machine.satisfied():
            machine.step()
            potentials.append(unresolved_potential(machine.partition))

        self.assertEqual(potentials, [3, 2, 1, 0])

    def test_causal_knockout_of_g1_retracts_all_descendants(self):
        machine = NebulaMachine.genesis(size=5)
        machine.ignite()

        learned = [
            (name, warrant_id)
            for name, (_, warrant_id) in sorted(machine.distinctions.items())
            if warrant_id is not None
        ]
        self.assertEqual([name for name, _ in learned], ["is_1", "is_2", "is_3"])

        g1_warrant = learned[0][1]
        revoked = machine.revoke(g1_warrant)

        self.assertEqual(set(revoked), {wid for _, wid in learned})
        self.assertEqual(machine.partition, ((0,), (1, 2, 3, 4)))
        self.assertFalse(machine.satisfied())

        # The terminal pressure is still present, so development can begin
        # again from the restored coarse quotient.
        obstruction = machine.certify_current_obstruction()
        self.assertEqual(obstruction.block, (1, 2, 3, 4))

    def test_descendant_warrants_record_causal_parentage(self):
        machine = NebulaMachine.genesis(size=5)
        machine.ignite()

        learned = [
            (name, warrant_id)
            for name, (_, warrant_id) in sorted(machine.distinctions.items())
            if warrant_id is not None
        ]
        g1 = machine.warrants[learned[0][1]]
        g2 = machine.warrants[learned[1][1]]
        g3 = machine.warrants[learned[2][1]]

        self.assertEqual(g1.depends_on, ())
        self.assertEqual(g2.depends_on, (g1.id,))
        self.assertEqual(g3.depends_on, tuple(sorted((g1.id, g2.id))))

    def test_ambiguous_minimal_repair_fails_closed(self):
        with self.assertRaises(UnknownChoiceError):
            select_unique_minimal(((1, "left"), (1, "right")))

        self.assertEqual(
            select_unique_minimal(((2, "larger"), (1, "unique"))),
            "unique",
        )


if __name__ == "__main__":
    unittest.main()
