import subprocess
import unittest

from runtime.metatron.nucleus import Node, append, ids, live_ids


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


def fixture():
    log = ()
    node_ids = []

    for name, premise_positions in (
        ("a", ()),
        ("b", (0,)),
        ("c", (1,)),
        ("independent", ()),
    ):
        node = Node(
            "fact",
            {"name": name},
            tuple(node_ids[i] for i in premise_positions),
        )
        log = append(log, node)
        node_ids.append(node.id)

    return log, tuple(node_ids)


def live_positions(log):
    positions = {node_id: i for i, node_id in enumerate(ids(log))}
    return tuple(positions[node_id] for node_id in live_ids(log))


class DifferentialTests(unittest.TestCase):
    def test_python_matches_lean_warrant_semantics(self):
        ref = reference()
        log, node_ids = fixture()
        self.assertEqual(ref["WARRANT_BASELINE"], live_positions(log))

        log = append(log, Node("revoke", {"target": node_ids[1]}))
        self.assertEqual(ref["WARRANT_REVOKED"], live_positions(log))


if __name__ == "__main__":
    unittest.main()
