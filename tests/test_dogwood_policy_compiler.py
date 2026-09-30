import unittest

from runtime.metatron.dogwood import compile_bundle, dependency_cone
from runtime.metatron.nucleus import Node, append, live_ids


def add(log, kind, payload=None, premises=()):
    node = Node(kind, payload, premises)
    return append(log, node), node.id


class DogwoodPolicyCompilerTests(unittest.TestCase):
    def fixture(self):
        log = ()
        log, root = add(log, "fact", {"name": "root"})
        log, middle = add(log, "fact", {"name": "middle"}, (root,))
        log, dependent = add(log, "capability", {"name": "dependent"}, (middle,))
        log, independent = add(log, "fact", {"name": "independent"})
        log, _ = add(log, "revoke", {"target": middle})
        return log, root, middle, dependent, independent

    def test_dependency_cone_is_transitive_and_log_ordered(self):
        log, root, middle, dependent, _ = self.fixture()
        self.assertEqual(
            dependency_cone(log, dependent),
            (root, middle, dependent),
        )

    def test_manifest_uses_canonical_live_view(self):
        log, root, _, _, independent = self.fixture()
        bundle = compile_bundle(log)
        self.assertEqual(bundle["manifest"]["current_live_ids"], list(live_ids(log)))
        self.assertEqual(set(live_ids(log)), {root, independent})

    def test_dependent_use_rule_mentions_entire_cone(self):
        log, root, middle, dependent, _ = self.fixture()
        policy = compile_bundle(log)["policy"]
        marker = f'@id("use_{dependent[:16]}")'
        block = policy.split(marker, 1)[1].split("@id(", 1)[0]
        for node_id in (root, middle, dependent):
            self.assertIn(f'input.node: "{node_id}"', block)
        self.assertIn('Action::"Revoke"::response', block)
        self.assertIn('Action::"Admit"::response', block)

    def test_compiler_is_not_nucleus_authority(self):
        log, *_ = self.fixture()
        bundle = compile_bundle(log)
        self.assertIn(
            "Metatron canonical log remains sole warrant authority",
            bundle["manifest"]["boundary"],
        )


if __name__ == "__main__":
    unittest.main()
