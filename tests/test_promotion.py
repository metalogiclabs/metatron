import unittest
from dataclasses import replace

from runtime.metatron.model import STEP_TABLE, ResidualCertificate, State
from runtime.metatron.machine import (
    Machine,
    UncertifiedResidualError,
    UnverifiedCertificateError,
    UnverifiedRelationError,
)

class PromotionTests(unittest.TestCase):
    def test_issued_residual_is_persisted_and_binds_candidate_verification(self):
        machine = Machine.genesis()
        residual_cert = machine.certify_target(STEP_TABLE)
        self.assertIsNotNone(residual_cert)
        self.assertEqual(machine.residual_certificates[residual_cert.id], residual_cert)
        candidate = machine.free_extend(residual_cert, "step")
        self.assertEqual(candidate.residual_certificate_id, residual_cert.id)
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)
        self.assertEqual(machine.execute("step", State.ZERO), State.ONE)
        self.assertEqual(machine.execute("step", State.TWO), State.TWO)

    def test_forged_or_stale_residual_cannot_force_growth(self):
        machine = Machine.genesis()
        issued = machine.certify_target(STEP_TABLE)
        forged = replace(issued, id="residual:forged")
        with self.assertRaises(UncertifiedResidualError):
            machine.free_extend(forged, "step")
        candidate = machine.free_extend(issued, "step")
        cert = machine.verify_candidate(candidate)
        machine.promote(candidate, cert)
        with self.assertRaises(UncertifiedResidualError):
            machine.free_extend(issued, "step-again")

    def test_forged_certificate_object_reusing_live_id_is_rejected(self):
        machine = Machine.genesis()
        residual_cert = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual_cert, "step")
        cert = machine.verify_candidate(candidate)
        forged = replace(cert, subject_digest="0" * 64)
        with self.assertRaises(UnverifiedCertificateError):
            machine.promote(candidate, forged)
        machine.promote(candidate, cert)
        relation, relation_cert = machine.verify_relation(("step", "step"), "step")
        forged_relation_cert = replace(relation_cert, kind="capability")
        with self.assertRaises(UnverifiedRelationError):
            machine.install_relation(relation, forged_relation_cert)

    def test_relation_requires_its_own_persisted_warrant(self):
        machine = Machine.genesis()
        residual_cert = machine.certify_target(STEP_TABLE)
        candidate = machine.free_extend(residual_cert, "step")
        capability_cert = machine.verify_candidate(candidate)
        machine.promote(candidate, capability_cert)
        proposal = machine.propose_relation(("step", "step"), "step")
        with self.assertRaises(UnverifiedRelationError):
            machine.install_relation(proposal, None)
        with self.assertRaises(UnverifiedRelationError):
            machine.install_relation(proposal, capability_cert)
        relation, relation_cert = machine.verify_relation(("step", "step"), "step")
        machine.install_relation(relation, relation_cert)
        self.assertEqual(machine.relations(), ((("step", "step"), "step"),))

if __name__ == "__main__":
    unittest.main()
