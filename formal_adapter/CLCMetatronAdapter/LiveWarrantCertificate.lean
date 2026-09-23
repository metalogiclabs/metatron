import CLCMetatronAdapter.VerifiedTransportSupport

namespace CLCMetatronAdapter

abbrev LiveWarrantCertificate (L : List Metatron.WarrantEntry) :=
  {i : Nat // i ∈ Metatron.warrantLive L}

theorem liveWarrantCertificate_exists_iff
    (L : List Metatron.WarrantEntry) (i : Nat) :
    (∃ c : LiveWarrantCertificate L, c.1 = i) ↔
      i ∈ Metatron.warrantLive L := by
  constructor
  · rintro ⟨c, rfl⟩
    exact c.2
  · intro h
    exact ⟨⟨i, h⟩, rfl⟩

def liveWarrantCertificateSupport
    (L : List Metatron.WarrantEntry)
    (Ωauth : CLC.AuthoritySnapshot (LiveWarrantCertificate L)) :
    FrozenCertificateSupport Ωauth L where
  support := fun c => {c.1}
  live_support := by
    intro c _ i hi
    have hic : i = c.1 := by
      simpa using hi
    subst i
    exact c.2

theorem liveWarrantCertificate_support_is_singleton
    {L : List Metatron.WarrantEntry}
    (Ωauth : CLC.AuthoritySnapshot (LiveWarrantCertificate L))
    (c : LiveWarrantCertificate L) :
    (liveWarrantCertificateSupport L Ωauth).support c = {c.1} := by
  rfl

theorem liveWarrantCertificate_verifiedTransport_static_authority
    {L : List Metatron.WarrantEntry}
    {Ωauth : CLC.AuthoritySnapshot (LiveWarrantCertificate L)}
    {A B : CLC.Form}
    (a : CLC.VerifiedTransport Ωauth A B) :
    Ωauth.accepts a.cert = true ∧
      (CLC.liveView (snapshotOf L)
        ({({a.cert.1} : CLC.Support Nat)} : CLC.SupportFamily Nat)).Nonempty := by
  simpa [liveWarrantCertificateSupport] using
    (verifiedTransport_static_authority
      (liveWarrantCertificateSupport L Ωauth) a)

theorem liveWarrantCertificate_verifiedTransport_decisive_preserved
    {L : List Metatron.WarrantEntry}
    {Ωauth : CLC.AuthoritySnapshot (LiveWarrantCertificate L)}
    {A B : CLC.Form}
    (a : CLC.VerifiedTransport Ωauth A B)
    (x : A.State)
    (p : CLC.Protected A)
    (h : CLC.Decisive (A.eval x p.1)) :
    (CLC.liveView (snapshotOf L)
      ({({a.cert.1} : CLC.Support Nat)} : CLC.SupportFamily Nat)).Nonempty ∧
      B.eval (a.mapState x) (a.liftProtected p).1 = A.eval x p.1 := by
  simpa [liveWarrantCertificateSupport] using
    (verifiedTransport_decisive_preserved_with_live_support
      (liveWarrantCertificateSupport L Ωauth) a x p h)

end CLCMetatronAdapter
