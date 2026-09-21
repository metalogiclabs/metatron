import itertools
import unittest

from runtime.metatron.nucleus import Node, WarrantGraph


def all_parent_patterns(n):
    edges = [(child, parent) for child in range(n) for parent in range(child)]
    for bits in itertools.product((False, True), repeat=len(edges)):
        parents = [[] for _ in range(n)]
        for enabled, (child, parent) in zip(bits, edges):
            if enabled:
                parents[child].append(parent)
        yield tuple(tuple(ps) for ps in parents)


def build_graph(parents):
    graph = WarrantGraph()
    ids = []
    for i, ps in enumerate(parents):
        node_id = graph.append(Node(
            "fact",
            {"index": i},
            tuple(ids[p] for p in ps),
        ))
        ids.append(node_id)
    return graph, tuple(ids)


def expected_live_indices(parents, revoked):
    live = []
    live_set = set()
    for i, ps in enumerate(parents):
        if i in revoked:
            continue
        if all(p in live_set for p in ps):
            live.append(i)
            live_set.add(i)
    return tuple(live)


class ExhaustiveSmallDagTests(unittest.TestCase):
    def test_all_five_node_dags_under_every_single_revocation(self):
        n = 5
        dag_count = 0
        revocation_cases = 0

        for parents in all_parent_patterns(n):
            dag_count += 1
            base, ids = build_graph(parents)
            self.assertEqual(base.live_ids(), ids)

            for target in range(n):
                revocation_cases += 1
                graph = WarrantGraph.loads(base.dumps())
                graph.append(Node("revoke", {"target": ids[target]}))

                expected_indices = expected_live_indices(parents, {target})
                expected_ids = tuple(ids[i] for i in expected_indices)

                self.assertEqual(graph.live_ids(), expected_ids)
                self.assertTrue(set(graph.live_ids()).issubset(set(base.live_ids())))

                # Replay is exact: persistence is not a second semantics.
                restored = WarrantGraph.loads(graph.dumps())
                self.assertEqual(restored.dumps(), graph.dumps())
                self.assertEqual(restored.live_ids(), expected_ids)

        self.assertEqual(dag_count, 1024)
        self.assertEqual(revocation_cases, 5120)


if __name__ == "__main__":
    unittest.main()
