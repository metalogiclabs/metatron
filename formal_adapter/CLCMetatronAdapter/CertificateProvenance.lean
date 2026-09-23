import CLCMetatronAdapter.LiveWarrantCertificate

namespace CLCMetatronAdapter

universe u

structure CertificateProvenance
    (Cert : Type u)
    (L : List Metatron.WarrantEntry) where
  toLive : Cert → LiveWarrantCertificate L

def certificateProvenanceSupport
    {Cert : Type u} [DecidableEq Cert]
    (L : List Metatron.WarrantEntry)
    (π : CertificateProvenance Cert L)
    (Ωauth : CLC.AuthoritySnapshot Cert) :
    FrozenCertificateSupport Ωauth L where
  support := fun c => {(π.toLive c).1}
  live_support := by
    intro c _ i hi
    have hic : i = (π.toLive c).1 := by
      simpa using hi
    subst i
    exact (π.toLive c).2

theorem certificateProvenance_support_is_singleton
    {Cert : Type u} [DecidableEq Cert]
    {L : List Metatron.WarrantEntry}
    (π : CertificateProvenance Cert L)
    (Ωauth : CLC.AuthoritySnapshot Cert)
    (c : Cert) :
    (certificateProvenanceSupport L π Ωauth).support c =
      {(π.toLive c).1} := by
  rfl

theorem certificateProvenance_verifiedTransport_static_authority
    {Cert : Type u} [DecidableEq Cert]
    {L : List Metatron.WarrantEntry}
    {Ωauth : CLC.AuthoritySnapshot Cert}
    {A B : CLC.Form}
    (π : CertificateProvenance Cert L)
    (a : CLC.VerifiedTransport Ωauth A B) :
    Ωauth.accepts a.cert = true ∧
      (CLC.liveView (snapshotOf L)
        ({({(π.toLive a.cert).1} : CLC.Support Nat)} :
          CLC.SupportFamily Nat)).Nonempty := by
  simpa [certificateProvenanceSupport] using
    (verifiedTransport_static_authority
      (certificateProvenanceSupport L π Ωauth) a)

theorem certificateProvenance_verifiedTransport_decisive_preserved
    {Cert : Type u} [DecidableEq Cert]
    {L : List Metatron.WarrantEntry}
    {Ωauth : CLC.AuthoritySnapshot Cert}
    {A B : CLC.Form}
    (π : CertificateProvenance Cert L)
    (a : CLC.VerifiedTransport Ωauth A B)
    (x : A.State)
    (p : CLC.Protected A)
    (h : CLC.Decisive (A.eval x p.1)) :
    (CLC.liveView (snapshotOf L)
      ({({(π.toLive a.cert).1} : CLC.Support Nat)} :
        CLC.SupportFamily Nat)).Nonempty ∧
      B.eval (a.mapState x) (a.liftProtected p).1 = A.eval x p.1 := by
  simpa [certificateProvenanceSupport] using
    (verifiedTransport_decisive_preserved_with_live_support
      (certificateProvenanceSupport L π Ωauth) a x p h)

end CLCMetatronAdapter
