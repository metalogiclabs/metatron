import unittest

from runtime.metatron.model import Query, STEP_TABLE
from runtime.metatron.machine import (
    Machine,
    NonCongruentProjectionError,
    partition_for_queries,
    project_table,
)


class ProjectionTests(unittest.TestCase):
    def test_is_zero_compresses_then_is_one_regrows(self):
        machine = Machine.genesis()
        machine.set_queries([Query.IS_ZERO])
        machine.project()
        self.assertEqual(machine.active_partition, ((0,), (1, 2)))

        prefix = tuple(machine.lineage)
        machine.set_queries([Query.IS_ZERO, Query.IS_ONE])
        machine.project()
        self.assertEqual(machine.active_partition, ((0,), (1,), (2,)))
        self.assertEqual(tuple(machine.lineage[:len(prefix)]), prefix)

    def test_non_congruent_projection_fails_closed(self):
        with self.assertRaises(NonCongruentProjectionError):
            project_table((0, 2, 2), ((0, 1), (2,)))

    def test_step_descends_to_is_zero_quotient(self):
        partition = partition_for_queries([Query.IS_ZERO])
        self.assertEqual(project_table(STEP_TABLE, partition), (1, 1))


if __name__ == "__main__":
    unittest.main()
