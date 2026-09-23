import CLC.Transport
import CLCMetatronAdapter.Adapter

namespace CLCMetatronAdapter

universe u

structure FrozenCertificateSupport {Cert : Type u} [DecidableEq Cert]
    (Ωauth : CLC.AuthoritySnapshot Cert)
    (L : List Metatron.WarrantEntry) where
  support : Cert → CLC.Support Nat
  live_support : ∀ c, Ωauth.live c = true →
    ∀ i ∈ support c, i ∈ Metatron.warrantLive L

theorem verifiedTransport_support_live
    {Cert : Type u} [DecidableEq Cert]
    {Ωauth : CLC.AuthoritySnapshot Cert}
    {A B : CLC.Form}
    {L : List Metatron.WarrantEntry}
    (β : FrozenCertificateSupport Ωauth L)
    (a : CLC.VerifiedTransport Ωauth A B) :
    (CLC.liveView (snapshotOf L)
      ({β.support a.cert} : CLC.SupportFamily Nat)).Nonempty := by
  apply (warrant_support_iff L
    ({β.support a.cert} : CLC.SupportFamily Nat)).2
  refine ⟨β.support a.cert, by simp, ?_⟩
  exact β.live_support a.cert a.liveAt

theorem verifiedTransport_static_authority
    {Cert : Type u} [DecidableEq Cert]
    {Ωauth : CLC.AuthoritySnapshot Cert}
    {A B : CLC.Form}
    {L : List Metatron.WarrantEntry}
    (β : FrozenCertificateSupport Ωauth L)
    (a : CLC.VerifiedTransport Ωauth A B) :
    Ωauth.accepts a.cert = true ∧
      (CLC.liveView (snapshotOf L)
        ({β.support a.cert} : CLC.SupportFamily Nat)).Nonempty := by
  exact ⟨a.checked, verifiedTransport_support_live β a⟩

theorem verifiedTransport_decisive_preserved_with_live_support
    {Cert : Type u} [DecidableEq Cert]
    {Ωauth : CLC.AuthoritySnapshot Cert}
    {A B : CLC.Form}
    {L : List Metatron.WarrantEntry}
    (β : FrozenCertificateSupport Ωauth L)
    (a : CLC.VerifiedTransport Ωauth A B)
    (x : A.State)
    (p : CLC.Protected A)
    (h : CLC.Decisive (A.eval x p.1)) :
    (CLC.liveView (snapshotOf L)
      ({β.support a.cert} : CLC.SupportFamily Nat)).Nonempty ∧
      B.eval (a.mapState x) (a.liftProtected p).1 = A.eval x p.1 := by
  exact ⟨verifiedTransport_support_live β a,
    CLC.decisive_preserved a x p h⟩

end CLCMetatronAdapter
