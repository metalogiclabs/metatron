import CLCMetatronAdapter.LiveWarrantCertificate

namespace CLCMetatronAdapter

def singletonWarrantLog : List Metatron.WarrantEntry :=
  [⟨[], none⟩]

theorem singletonWarrantLog_live :
    Metatron.warrantLive singletonWarrantLog = [0] := by
  decide

def singletonLiveCert0 : LiveWarrantCertificate singletonWarrantLog :=
  ⟨0, by rw [singletonWarrantLog_live]; simp⟩

def singletonCertificateAuthority :
    CLC.AuthoritySnapshot (LiveWarrantCertificate singletonWarrantLog) where
  accepts := fun _ => true
  live := fun _ => true
  idCert := singletonLiveCert0
  compCert := fun _ _ => singletonLiveCert0
  accepts_id := rfl
  live_id := rfl
  accepts_comp := by intros; rfl
  live_comp := by intros; rfl
  certEq := fun _ _ => True
  certEq_refl := by intros; trivial
  certEq_symm := by intros; trivial
  certEq_trans := by intros; trivial
  accepts_congr := by intros; rfl
  live_congr := by intros; rfl
  comp_congr := by intros; trivial
  comp_assoc := by intros; trivial
  id_left := by intros; trivial
  id_right := by intros; trivial

def provenanceUnitForm : CLC.Form where
  State := Unit
  Test := Unit
  stateFinite := inferInstance
  testFinite := inferInstance
  decState := inferInstance
  decTest := inferInstance
  «protected» := fun _ => true
  eval := fun _ _ => CLC.Verdict.eq

theorem singleton_id_transport_has_earned_live_support :
    singletonCertificateAuthority.accepts
        (CLC.VerifiedTransport.id singletonCertificateAuthority
          provenanceUnitForm).cert = true ∧
      (CLC.liveView (snapshotOf singletonWarrantLog)
        ({({(CLC.VerifiedTransport.id singletonCertificateAuthority
          provenanceUnitForm).cert.1} : CLC.Support Nat)} :
          CLC.SupportFamily Nat)).Nonempty := by
  exact liveWarrantCertificate_verifiedTransport_static_authority
    (CLC.VerifiedTransport.id singletonCertificateAuthority provenanceUnitForm)

theorem singleton_id_transport_preserves_decisive_with_earned_support :
    (CLC.liveView (snapshotOf singletonWarrantLog)
      ({({(CLC.VerifiedTransport.id singletonCertificateAuthority
        provenanceUnitForm).cert.1} : CLC.Support Nat)} :
        CLC.SupportFamily Nat)).Nonempty ∧
      provenanceUnitForm.eval
          ((CLC.VerifiedTransport.id singletonCertificateAuthority
            provenanceUnitForm).mapState ())
          ((CLC.VerifiedTransport.id singletonCertificateAuthority
            provenanceUnitForm).liftProtected
              (⟨(), rfl⟩ : CLC.Protected provenanceUnitForm)).1 =
        provenanceUnitForm.eval () () := by
  exact liveWarrantCertificate_verifiedTransport_decisive_preserved
    (CLC.VerifiedTransport.id singletonCertificateAuthority provenanceUnitForm)
    ()
    (⟨(), rfl⟩ : CLC.Protected provenanceUnitForm)
    (Or.inl rfl)

theorem revoked_fixture_has_no_certificate_one :
    ¬ ∃ c : LiveWarrantCertificate Metatron.warrantRevokedFixture,
      c.1 = 1 := by
  intro h
  have hLive :
      1 ∈ Metatron.warrantLive Metatron.warrantRevokedFixture :=
    (liveWarrantCertificate_exists_iff
      Metatron.warrantRevokedFixture 1).1 h
  rw [Metatron.warrant_revocation_cuts_dependency_cone] at hLive
  simp at hLive

end CLCMetatronAdapter
