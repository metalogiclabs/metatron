import ast
import unittest
from pathlib import Path

from runtime.metatron.nucleus import (
    Node,
    append,
    dumps,
    ids,
    live,
    live_ids,
    loads,
)


def add(log, kind, payload=None, premises=()):
    node = Node(kind, payload, premises)
    return append(log, node), node.id


class MinimalWarrantGraphTests(unittest.TestCase):
    def test_content_address_is_canonical_and_payload_is_frozen(self):
        payload = {"b": [2], "a": 1}
        a = Node("fact", payload)
        b = Node("fact", {"a": 1, "b": [2]})
        self.assertEqual(a.id, b.id)

        frozen_id = a.id
        payload["b"].append(3)
        self.assertEqual(a.id, frozen_id)
        self.assertEqual(a.payload, {"a": 1, "b": [2]})

    def test_unknown_premise_fails_closed(self):
        with self.assertRaises(KeyError):
            append((), Node("claim", {"x": 1}, ("missing",)))

    def test_one_node_type_carries_complete_v0_lifecycle(self):
        log = ()
        log, genesis = add(log, "capability", {"name": "id", "table": [0, 1, 2]})
        log, residual = add(
            log,
            "residual",
            {
                "target": [1, 1, 2],
                "closure_size": 1,
                "authority_digest": genesis,
            },
            (genesis,),
        )
        log, verification = add(
            log,
            "verification",
            {"subject": "step", "verdict": "accept"},
            (residual,),
        )
        log, step = add(
            log,
            "capability",
            {"name": "step", "table": [1, 1, 2]},
            (residual, verification),
        )
        log, relation_verification = add(
            log,
            "verification",
            {"subject": "step;step=step", "verdict": "accept"},
            (step,),
        )
        log, relation = add(
            log,
            "relation",
            {"left": ["step", "step"], "right": "step"},
            (step, relation_verification),
        )

        self.assertEqual(
            {node.payload["name"] for _, node in live(log, "capability")},
            {"id", "step"},
        )
        self.assertIn(relation, live_ids(log))

        log, revoke = add(
            log,
            "revoke",
            {"target": step, "reason": "qualification withdrawn"},
        )

        self.assertIn(revoke, ids(log))
        self.assertIn(step, ids(log))
        self.assertNotIn(step, live_ids(log))
        self.assertNotIn(relation, live_ids(log))
        self.assertIn(genesis, live_ids(log))

    def test_revocation_invalidates_dependency_cone_not_independent_history(self):
        log = ()
        log, a = add(log, "fact", {"name": "a"})
        log, b = add(log, "fact", {"name": "b"}, (a,))
        log, c = add(log, "fact", {"name": "c"}, (b,))
        log, independent = add(log, "fact", {"name": "independent"})

        log, _ = add(log, "revoke", {"target": b})

        self.assertIn(a, live_ids(log))
        self.assertNotIn(b, live_ids(log))
        self.assertNotIn(c, live_ids(log))
        self.assertIn(independent, live_ids(log))

    def test_jsonl_is_the_only_persisted_authority(self):
        log = ()
        log, root = add(log, "fact", {"name": "root"})
        log, child = add(log, "fact", {"name": "child"}, (root,))
        log, _ = add(log, "measurement", {"metric": "cost", "value": 7}, (child,))

        payload = dumps(log)
        restored = loads(payload)

        self.assertEqual(dumps(restored), payload)
        self.assertEqual(ids(restored), ids(log))
        self.assertEqual(live_ids(restored), live_ids(log))

    def test_tampered_history_is_rejected(self):
        log, _ = add((), "fact", {"value": 1})
        payload = dumps(log).replace('"value":1', '"value":2')

        with self.assertRaises(ValueError):
            loads(payload)

    def test_lkc_facts_need_no_kernel_specific_types(self):
        log = ()
        log, v5 = add(
            log,
            "candidate",
            {"name": "v5-natfold", "family": "folded-multiplicity-sum"},
        )
        log, _ = add(
            log,
            "verification",
            {"subject": "v5-natfold", "universal": True, "canonical": True},
            (v5,),
        )
        log, _ = add(
            log,
            "measurement",
            {
                "subject": "v5-natfold",
                "metric": "perf_instructions",
                "cohort": "partition-14-22-32",
                "value": 4546112652,
                "tier": "external",
            },
            (v5,),
        )

        locals_by_name = {}
        for name, value in (
            ("v8-shiftzip", 0.505994296),
            ("v9-directshift", 0.320588831),
            ("v10-seeded", 0.282958007),
        ):
            log, candidate = add(log, "candidate", {"name": name})
            log, _ = add(
                log,
                "verification",
                {"subject": name, "universal": True, "canonical": True},
                (candidate,),
            )
            log, _ = add(
                log,
                "measurement",
                {
                    "subject": name,
                    "metric": "wall_seconds",
                    "cohort": "frozen-local-partition",
                    "value": value,
                    "tier": "local",
                },
                (candidate,),
            )
            locals_by_name[name] = value

        self.assertEqual(min(locals_by_name, key=locals_by_name.get), "v10-seeded")
        self.assertEqual(len(live(log, "candidate")), 4)

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
            {"dataclasses", "hashlib", "json", "__future__"},
        )

        semantic_lines = [
            line for line in source.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertLessEqual(len(semantic_lines), 120)


if __name__ == "__main__":
    unittest.main()
