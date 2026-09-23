import CLCMetatronAdapter.CertificateProvenance

namespace CLCMetatronAdapter

def attestedUnitLiveWarrant :
    LiveWarrantCertificate Metatron.warrantBaseline :=
  ⟨0, by
    rw [Metatron.warrant_baseline_all_live]
    simp⟩

def attestedUnitCertificateProvenance :
    CertificateProvenance Unit Metatron.warrantBaseline where
  toLive := fun _ => attestedUnitLiveWarrant

theorem attestedUnitCertificateProvenance_index :
    (attestedUnitCertificateProvenance.toLive ()).1 = 0 := by
  rfl

theorem attestedUnitCertificateProvenance_is_live :
    0 ∈ Metatron.warrantLive Metatron.warrantBaseline := by
  exact (attestedUnitCertificateProvenance.toLive ()).2

theorem attestedUnitCertificateProvenance_support :
    (certificateProvenanceSupport
      Metatron.warrantBaseline
      attestedUnitCertificateProvenance
      unitAuthority).support () = ({0} : CLC.Support Nat) := by
  rfl

end CLCMetatronAdapter
