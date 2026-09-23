import CLCMetatronAdapter.VerifiedTransportSupport

namespace CLCMetatronAdapter

def unitAuthority : CLC.AuthoritySnapshot Unit where
  accepts := fun _ => true
  live := fun _ => true
  idCert := ()
  compCert := fun _ _ => ()
  accepts_id := rfl
  live_id := rfl
  accepts_comp := by intros; rfl
  live_comp := by intros; rfl
  certEq := Eq
  certEq_refl := fun _ => rfl
  certEq_symm := Eq.symm
  certEq_trans := Eq.trans
  accepts_congr := by intros; rfl
  live_congr := by intros; rfl
  comp_congr := by intros; rfl
  comp_assoc := by intros; rfl
  id_left := by intros; rfl
  id_right := by intros; rfl

def unitForm : CLC.Form where
  State := Unit
  Test := Unit
  stateFinite := inferInstance
  testFinite := inferInstance
  decState := inferInstance
  decTest := inferInstance
  «protected» := fun _ => true
  eval := fun _ _ => CLC.Verdict.eq

def baselineCertificateSupport :
    FrozenCertificateSupport unitAuthority Metatron.warrantBaseline where
  support := fun _ => {0}
  live_support := by
    intro _ _ i hi
    have hi0 : i = 0 := by simpa using hi
    subst i
    rw [Metatron.warrant_baseline_all_live]
    simp

theorem baseline_id_transport_static_authority :
    unitAuthority.accepts
        (CLC.VerifiedTransport.id unitAuthority unitForm).cert = true ∧
      (CLC.liveView (snapshotOf Metatron.warrantBaseline)
        ({baselineCertificateSupport.support
            (CLC.VerifiedTransport.id unitAuthority unitForm).cert} :
          CLC.SupportFamily Nat)).Nonempty := by
  exact verifiedTransport_static_authority baselineCertificateSupport
    (CLC.VerifiedTransport.id unitAuthority unitForm)

theorem baseline_id_decisive_preserved_with_live_support :
    (CLC.liveView (snapshotOf Metatron.warrantBaseline)
      ({baselineCertificateSupport.support
          (CLC.VerifiedTransport.id unitAuthority unitForm).cert} :
        CLC.SupportFamily Nat)).Nonempty ∧
      unitForm.eval
          ((CLC.VerifiedTransport.id unitAuthority unitForm).mapState ())
          ((CLC.VerifiedTransport.id unitAuthority unitForm).liftProtected
            (⟨(), rfl⟩ : CLC.Protected unitForm)).1 =
        unitForm.eval () () := by
  exact verifiedTransport_decisive_preserved_with_live_support
    baselineCertificateSupport
    (CLC.VerifiedTransport.id unitAuthority unitForm)
    ()
    (⟨(), rfl⟩ : CLC.Protected unitForm)
    (Or.inl rfl)

theorem revoked_one_support_cannot_be_live :
    ¬ ∃ β : FrozenCertificateSupport unitAuthority
          Metatron.warrantRevokedFixture,
        β.support () = ({1} : CLC.Support Nat) := by
  rintro ⟨β, hβ⟩
  have hmem : 1 ∈ β.support () := by
    rw [hβ]
    simp
  have hlive := β.live_support () rfl 1 hmem
  rw [Metatron.warrant_revocation_cuts_dependency_cone] at hlive
  simp at hlive

end CLCMetatronAdapter
