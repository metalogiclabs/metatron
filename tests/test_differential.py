import subprocess
import unittest

from runtime.metatron.machine import partition_for_queries, project_table
from runtime.metatron.model import Query, STEP_TABLE, State, eval_query
from runtime.metatron.nucleus import Node, WarrantGraph


def reference():
    proc = subprocess.run(
        ["lake", "exe", "metatron_reference"],
        check=True,
        capture_output=True,
        text=True,
    )
    out = {}
    for line in proc.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            out[key] = tuple(int(x) for x in value.split(",") if x)
    return out


def warrant_fixture():
    graph = WarrantGraph()
    a = graph.append(Node("fact", {"name": "a"}))
    b = graph.append(Node("fact", {"name": "b"}, (a,)))
    graph.append(Node("fact", {"name": "c"}, (b,)))
    graph.append(Node("fact", {"name": "independent"}))
    return graph, b


def live_positions(graph):
    positions = {node_id: i for i, node_id in enumerate(graph.ids)}
    return tuple(positions[node_id] for node_id in graph.live_ids())


class DifferentialTests(unittest.TestCase):
    def test_python_matches_lean(self):
        ref = reference()
        self.assertEqual(ref["STEP"], STEP_TABLE)
        self.assertEqual(
            ref["Q0"],
            tuple(int(eval_query(Query.IS_ZERO, s)) for s in State),
        )
        self.assertEqual(
            ref["Q1"],
            tuple(int(eval_query(Query.IS_ONE, s)) for s in State),
        )
        self.assertEqual(ref["Q0_PROJECT"], (0, 1, 1))
        self.assertEqual(
            ref["Q0_STEP"],
            project_table(STEP_TABLE, partition_for_queries([Query.IS_ZERO])),
        )
        self.assertEqual(ref["IDEMPOTENT"], (1,))
        self.assertEqual(ref["COMPILED_EXACT"], (1,))

        graph, b = warrant_fixture()
        self.assertEqual(
            ref["WARRANT_BASELINE"],
            live_positions(graph),
        )
        graph.append(Node("revoke", {"target": b}))
        self.assertEqual(
            ref["WARRANT_REVOKED"],
            live_positions(graph),
        )


if __name__ == "__main__":
    unittest.main()
