#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_SCHEMA = "metatron.clc-certificate-provenance-manifest-v0"
EXPECTED_PARENT = "8d2323da735720478c50eab068f844d9a3c0948d"
EXPECTED_CLC_HEAD = "900a73c1d386ee0eee1205a1cf31d270f3311ef7"
EXPECTED_FIXTURE_BLOB = "ead1d6f1da004770f93539f589acd83a35578a15"


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text())
    assert data["schema"] == EXPECTED_SCHEMA
    assert data["parent_a9d_head"] == EXPECTED_PARENT
    assert data["clc_source_head"] == EXPECTED_CLC_HEAD
    assert data["clc_fixture_blob"] == EXPECTED_FIXTURE_BLOB
    assert data["certificate_type"] == "Unit"
    assert data["certificate_authority"] == "CLC.Fixtures.positiveAuthority"
    assert data["certificate_literal"] == "()"
    assert data["metatron_log"] == "Metatron.warrantBaseline"
    idx = data["warrant_index"]
    assert isinstance(idx, int) and idx >= 0
    return data


def render(data: dict, manifest_sha256: str) -> str:
    idx = data["warrant_index"]
    return f'''import CLCMetatronAdapter.CertificateProvenance

namespace CLCMetatronAdapter

-- Generated from source-pinned provenance manifest.
-- manifest_sha256: {manifest_sha256}
-- clc_source_head: {data["clc_source_head"]}
-- clc_fixture_blob: {data["clc_fixture_blob"]}
-- certificate_authority: {data["certificate_authority"]}
-- metatron_log: {data["metatron_log"]}
-- warrant_index: {idx}

def manifestCertificateProvenance :
    CertificateProvenance Unit Metatron.warrantBaseline where
  toLive := fun _ =>
    ⟨{idx}, by
      rw [Metatron.warrant_baseline_all_live]
      decide⟩

theorem manifest_binding_exact :
    (manifestCertificateProvenance.toLive ()).1 = {idx} := by
  rfl

theorem manifest_binding_live :
    {idx} ∈ Metatron.warrantLive Metatron.warrantBaseline := by
  exact (manifestCertificateProvenance.toLive ()).2

theorem manifest_verifiedTransport_static_authority
    {{Ωauth : CLC.AuthoritySnapshot Unit}}
    {{A B : CLC.Form}}
    (a : CLC.VerifiedTransport Ωauth A B) :
    Ωauth.accepts a.cert = true ∧
      (CLC.liveView (snapshotOf Metatron.warrantBaseline)
        ({{({{(manifestCertificateProvenance.toLive a.cert).1}} :
          CLC.Support Nat)}} : CLC.SupportFamily Nat)).Nonempty := by
  exact certificateProvenance_verifiedTransport_static_authority
    manifestCertificateProvenance a

theorem manifest_verifiedTransport_decisive_preserved
    {{Ωauth : CLC.AuthoritySnapshot Unit}}
    {{A B : CLC.Form}}
    (a : CLC.VerifiedTransport Ωauth A B)
    (x : A.State)
    (p : CLC.Protected A)
    (h : CLC.Decisive (A.eval x p.1)) :
    (CLC.liveView (snapshotOf Metatron.warrantBaseline)
      ({{({{(manifestCertificateProvenance.toLive a.cert).1}} :
        CLC.Support Nat)}} : CLC.SupportFamily Nat)).Nonempty ∧
      B.eval (a.mapState x) (a.liftProtected p).1 = A.eval x p.1 := by
  exact certificateProvenance_verifiedTransport_decisive_preserved
    manifestCertificateProvenance a x p h

#print axioms CLCMetatronAdapter.manifest_binding_live
#print axioms CLCMetatronAdapter.manifest_verifiedTransport_static_authority
#print axioms CLCMetatronAdapter.manifest_verifiedTransport_decisive_preserved

end CLCMetatronAdapter
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    data = load_manifest(manifest_path)
    digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(data, digest))
    print(f"MANIFEST_SHA256={digest}")
    print(f"WARRANT_INDEX={data['warrant_index']}")
    print(f"OUTPUT={output}")


if __name__ == "__main__":
    main()
