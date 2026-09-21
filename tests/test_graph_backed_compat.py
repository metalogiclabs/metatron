import unittest

from runtime.metatron.machine import Machine, RevokedCapabilityError
from runtime.metatron.model import Query, STEP_TABLE, State
from runtime.metatron.serialization import dump_machine, load_machine
from runtime.metatron.views import affected


class GraphBackedCompatibilityTests(unittest.TestCase):
    def test_legacy_v0_trace_is_preserved_by_one_authoritative_graph(self):
        machine = Machine.genesis()
        self.assertEqual(set(machine.__dict__), {"graph"})
        self.assertEqual(machine.active_capability_names(), ("id",))

        residual = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)

        self.assertEqual(machine.active_capability_names(), ("id", "step"))
        self.assertEqual(machine.execute("step", State.ZERO), State.ONE)

        relation, relation_cert = machine.verify_relation(
            ("step", "step"),
            "step",
        )
        machine.install_relation(relation, relation_cert)
        self.assertEqual(machine.relations(), ((("step", "step"), "step"),))
        self.assertEqual(len(machine.graph.live("relation")), 1)

        machine.set_queries([Query.IS_ZERO])
        machine.project()
        self.assertEqual(machine.active_partition, ((0,), (1, 2)))

        payload = dump_machine(machine)
        self.assertEqual(payload, machine.graph.dumps())

        restarted = load_machine(payload)
        self.assertEqual(set(restarted.__dict__), {"graph"})
        self.assertEqual(dump_machine(restarted), payload)
        self.assertEqual(restarted.active_capability_names(), ("id", "step"))
        self.assertEqual(restarted.execute("step", State.ZERO), State.ONE)
        self.assertEqual(restarted.active_partition, ((0,), (1, 2)))

        restarted.revoke(cert.id)
        with self.assertRaises(RevokedCapabilityError):
            restarted.execute("step", State.ZERO)

        # Old public behavior retained: the installed relation remains historical.
        self.assertEqual(restarted.relations(), ((("step", "step"), "step"),))
        # New live-view law: revoking its dependency removes it from active closure.
        self.assertEqual(restarted.graph.live("relation"), ())

        restarted.set_queries([Query.IS_ZERO, Query.IS_ONE])
        restarted.project()
        self.assertEqual(restarted.active_partition, ((0,), (1,), (2,)))

        self.assertEqual(
            [event.kind for event in restarted.lineage],
            [
                "GENESIS",
                "RESIDUAL",
                "CANDIDATE",
                "VERIFY",
                "PROMOTE",
                "VERIFY_RELATION",
                "INSTALL_RELATION",
                "SET_QUERIES",
                "PROJECT",
                "REVOKE",
                "SET_QUERIES",
                "REGROW",
            ],
        )

    def test_legacy_stores_are_disposable_views_not_authority(self):
        machine = Machine.genesis()
        residual = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)

        certificates = machine.certificates
        residuals = machine.residual_certificates
        capabilities = machine.capabilities
        live = machine.live_certificates

        certificates.clear()
        residuals.clear()
        capabilities.clear()
        live.clear()

        self.assertIn(cert.id, machine.certificates)
        self.assertIn(residual.id, machine.residual_certificates)
        self.assertIn("step", machine.capabilities)
        self.assertIn(cert.id, machine.live_certificates)

    def test_revocation_cone_is_derived_not_stored(self):
        machine = Machine.genesis()
        residual = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)
        relation, relation_cert = machine.verify_relation(
            ("step", "step"),
            "step",
        )
        machine.install_relation(relation, relation_cert)

        certificate_node = machine._find_by_legacy_id(
            "verification",
            cert.id,
            live=True,
        )[0]
        cone = affected(machine.graph, (certificate_node,))

        self.assertGreaterEqual(len(cone), 3)
        self.assertTrue(any(
            machine.graph[node_id].kind == "capability"
            for node_id in cone
        ))
        self.assertTrue(any(
            machine.graph[node_id].kind == "relation"
            for node_id in cone
        ))


if __name__ == "__main__":
    unittest.main()
