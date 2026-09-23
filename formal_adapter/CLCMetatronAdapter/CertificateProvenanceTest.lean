import CLCMetatronAdapter.CertificateProvenance
import CLCMetatronAdapter.VerifiedTransportSupportTest

namespace CLCMetatronAdapter

def baselineLiveWarrant0 :
    LiveWarrantCertificate Metatron.warrantBaseline :=
  ⟨0, by rw [Metatron.warrant_baseline_all_live]; simp⟩

def baselineLiveWarrant3 :
    LiveWarrantCertificate Metatron.warrantBaseline :=
  ⟨3, by rw [Metatron.warrant_baseline_all_live]; simp⟩

def unitProvenance0 :
    CertificateProvenance Unit Metatron.warrantBaseline where
  toLive := fun _ => baselineLiveWarrant0

def unitProvenance3 :
    CertificateProvenance Unit Metatron.warrantBaseline where
  toLive := fun _ => baselineLiveWarrant3

theorem unit_certificate_provenance_not_unique :
    unitProvenance0.toLive ≠ unitProvenance3.toLive := by
  intro h
  have hc := congrFun h ()
  have hv := congrArg
    (fun c : LiveWarrantCertificate Metatron.warrantBaseline => c.1) hc
  omega

theorem unit_certificate_identity_does_not_determine_warrant :
    ∃ p q : CertificateProvenance Unit Metatron.warrantBaseline,
      p.toLive ≠ q.toLive := by
  exact ⟨unitProvenance0, unitProvenance3,
    unit_certificate_provenance_not_unique⟩

theorem unit_identity_transport_preserved_with_bound_provenance :
    (CLC.liveView (snapshotOf Metatron.warrantBaseline)
      ({({(unitProvenance0.toLive
          (CLC.VerifiedTransport.id unitAuthority unitForm).cert).1} :
        CLC.Support Nat)} : CLC.SupportFamily Nat)).Nonempty ∧
      unitForm.eval
          ((CLC.VerifiedTransport.id unitAuthority unitForm).mapState ())
          ((CLC.VerifiedTransport.id unitAuthority unitForm).liftProtected
            (⟨(), rfl⟩ : CLC.Protected unitForm)).1 =
        unitForm.eval () () := by
  exact certificateProvenance_verifiedTransport_decisive_preserved
    unitProvenance0
    (CLC.VerifiedTransport.id unitAuthority unitForm)
    ()
    (⟨(), rfl⟩ : CLC.Protected unitForm)
    (Or.inl rfl)

end CLCMetatronAdapter
