import itertools
import unittest

from runtime.metatron.nucleus import Node, append, dumps, live_ids, loads


def all_parent_patterns(n):
    edges = [(child, parent) for child in range(n) for parent in range(child)]
    for bits in itertools.product((False, True), repeat=len(edges)):
        parents = [[] for _ in range(n)]
        for enabled, (child, parent) in zip(bits, edges):
            if enabled:
                parents[child].append(parent)
        yield tuple(tuple(ps) for ps in parents)


def build_log(parents):
    log = ()
    node_ids = []
    for i, ps in enumerate(parents):
        node = Node(
            "fact",
            {"index": i},
            tuple(node_ids[p] for p in ps),
        )
        log = append(log, node)
        node_ids.append(node.id)
    return log, tuple(node_ids)


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
            base, node_ids = build_log(parents)
            self.assertEqual(live_ids(base), node_ids)

            for target in range(n):
                revocation_cases += 1
                log = loads(dumps(base))
                revoke = Node("revoke", {"target": node_ids[target]})
                log = append(log, revoke)

                expected_indices = expected_live_indices(parents, {target})
                expected_ids = tuple(node_ids[i] for i in expected_indices)

                self.assertEqual(live_ids(log), expected_ids)
                self.assertTrue(set(live_ids(log)).issubset(set(live_ids(base))))

                restored = loads(dumps(log))
                self.assertEqual(dumps(restored), dumps(log))
                self.assertEqual(live_ids(restored), expected_ids)

        self.assertEqual(dag_count, 1024)
        self.assertEqual(revocation_cases, 5120)


if __name__ == "__main__":
    unittest.main()
