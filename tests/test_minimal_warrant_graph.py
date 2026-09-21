import ast
import unittest
from pathlib import Path

from runtime.metatron.nucleus import Node, WarrantGraph


class MinimalWarrantGraphTests(unittest.TestCase):
    def test_content_address_is_canonical(self):
        a = Node("fact", {"b": 2, "a": 1})
        b = Node("fact", {"a": 1, "b": 2})
        self.assertEqual(a.id, b.id)

    def test_unknown_premise_fails_closed(self):
        graph = WarrantGraph()
        with self.assertRaises(KeyError):
            graph.append(Node("claim", {"x": 1}, ("missing",)))

    def test_one_node_type_carries_complete_v0_lifecycle(self):
        graph = WarrantGraph()

        genesis = graph.append(Node(
            "capability",
            {"name": "id", "table": [0, 1, 2]},
        ))
        residual = graph.append(Node(
            "residual",
            {
                "target": [1, 1, 2],
                "closure_size": 1,
                "authority_digest": genesis,
            },
            (genesis,),
        ))
        verification = graph.append(Node(
            "verification",
            {"subject": "step", "verdict": "accept"},
            (residual,),
        ))
        step = graph.append(Node(
            "capability",
            {"name": "step", "table": [1, 1, 2]},
            (residual, verification),
        ))
        relation_verification = graph.append(Node(
            "verification",
            {
                "subject": "step;step=step",
                "verdict": "accept",
            },
            (step,),
        ))
        relation = graph.append(Node(
            "relation",
            {"left": ["step", "step"], "right": "step"},
            (step, relation_verification),
        ))

        self.assertEqual(
            {node.payload["name"] for _, node in graph.live("capability")},
            {"id", "step"},
        )
        self.assertIn(relation, graph.live_ids())

        revoke = graph.append(Node(
            "revoke",
            {"target": step, "reason": "qualification withdrawn"},
        ))

        self.assertIn(revoke, graph.ids)
        self.assertIn(step, graph.ids)
        self.assertNotIn(step, graph.live_ids())
        self.assertNotIn(relation, graph.live_ids())
        self.assertIn(genesis, graph.live_ids())

    def test_revocation_invalidates_only_dependency_cone(self):
        graph = WarrantGraph()
        a = graph.append(Node("fact", {"name": "a"}))
        b = graph.append(Node("fact", {"name": "b"}, (a,)))
        c = graph.append(Node("fact", {"name": "c"}, (b,)))
        independent = graph.append(Node("fact", {"name": "independent"}))

        self.assertEqual(graph.affected((a,)), (a, b, c))
        graph.append(Node("revoke", {"target": b}))

        self.assertIn(a, graph.live_ids())
        self.assertNotIn(b, graph.live_ids())
        self.assertNotIn(c, graph.live_ids())
        self.assertIn(independent, graph.live_ids())

    def test_jsonl_is_the_only_persisted_authority(self):
        graph = WarrantGraph()
        root = graph.append(Node("fact", {"name": "root"}))
        child = graph.append(Node("fact", {"name": "child"}, (root,)))
        graph.append(Node("measurement", {"metric": "cost", "value": 7}, (child,)))

        payload = graph.dumps()
        restored = WarrantGraph.loads(payload)

        self.assertEqual(restored.dumps(), payload)
        self.assertEqual(restored.ids, graph.ids)
        self.assertEqual(restored.live_ids(), graph.live_ids())
        self.assertEqual(restored.root_digest(), graph.root_digest())

    def test_tampered_history_is_rejected(self):
        graph = WarrantGraph()
        graph.append(Node("fact", {"value": 1}))
        payload = graph.dumps().replace('"value":1', '"value":2')

        with self.assertRaises(ValueError):
            WarrantGraph.loads(payload)

    def test_lkc_facts_need_no_kernel_specific_types(self):
        graph = WarrantGraph()

        v5 = graph.append(Node(
            "candidate",
            {"name": "v5-natfold", "family": "folded-multiplicity-sum"},
        ))
        graph.append(Node(
            "verification",
            {"subject": "v5-natfold", "universal": True, "canonical": True},
            (v5,),
        ))
        graph.append(Node(
            "measurement",
            {
                "subject": "v5-natfold",
                "metric": "perf_instructions",
                "cohort": "partition-14-22-32",
                "value": 4546112652,
                "tier": "external",
            },
            (v5,),
        ))

        locals_by_name = {}
        for name, value in (
            ("v8-shiftzip", 0.505994296),
            ("v9-directshift", 0.320588831),
            ("v10-seeded", 0.282958007),
        ):
            candidate = graph.append(Node(
                "candidate",
                {"name": name},
            ))
            graph.append(Node(
                "verification",
                {"subject": name, "universal": True, "canonical": True},
                (candidate,),
            ))
            graph.append(Node(
                "measurement",
                {
                    "subject": name,
                    "metric": "wall_seconds",
                    "cohort": "frozen-local-partition",
                    "value": value,
                    "tier": "local",
                },
                (candidate,),
            ))
            locals_by_name[name] = value

        # Policy remains outside the nucleus. It can derive the next contender
        # from warranted facts without introducing another authoritative store.
        self.assertEqual(min(locals_by_name, key=locals_by_name.get), "v10-seeded")
        self.assertEqual(len(graph.live("candidate")), 4)

    def test_nucleus_has_a_hard_size_and_dependency_budget(self):
        path = Path("runtime/metatron/nucleus.py")
        source = path.read_text()
        tree = ast.parse(source)

        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

        self.assertLessEqual(
            imported_roots,
            {"dataclasses", "hashlib", "json", "typing", "__future__"},
        )

        semantic_lines = [
            line for line in source.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertLessEqual(len(semantic_lines), 180)


if __name__ == "__main__":
    unittest.main()
