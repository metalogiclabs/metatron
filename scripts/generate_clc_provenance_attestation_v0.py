#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence/integration/clc-provenance-attestation-v0.json"
OUT = ROOT / "formal_adapter/CLCMetatronAdapter/ProvenanceAttestationGenerated.lean"

EXPECTED = {
    "schema": "metatron.clc-provenance-attestation-v0",
    "certificate_repo": "heathsanchez/Minimal-Sufficient-Interface",
    "certificate_head": "900a73c1d386ee0eee1205a1cf31d270f3311ef7",
    "certificate_path": "qcklean/CLC/Fixtures.lean",
    "certificate_blob": "ead1d6f1da004770f93539f589acd83a35578a15",
    "certificate_type": "Unit",
    "authority_name": "CLC.Fixtures.positiveAuthority",
    "warrant_blob": "d2affc0a57a1815f303f6f1859941465c69e7d32",
    "log_name": "Metatron.warrantBaseline",
    "warrant_index": 0,
    "certificate_value": "()",
}

def load():
    return json.loads(MANIFEST.read_text())

def validate(d):
    assert d["schema"] == EXPECTED["schema"]
    cs = d["certificate_source"]
    ws = d["warrant_source"]
    bd = d["binding"]
    assert cs["repo"] == EXPECTED["certificate_repo"]
    assert cs["head"] == EXPECTED["certificate_head"]
    assert cs["path"] == EXPECTED["certificate_path"]
    assert cs["blob"] == EXPECTED["certificate_blob"]
    assert cs["certificate_type"] == EXPECTED["certificate_type"]
    assert cs["authority_name"] == EXPECTED["authority_name"]
    assert ws["blob"] == EXPECTED["warrant_blob"]
    assert ws["log_name"] == EXPECTED["log_name"]
    assert ws["warrant_index"] == EXPECTED["warrant_index"]
    assert bd["certificate_value"] == EXPECTED["certificate_value"]
    assert bd["warrant_index"] == EXPECTED["warrant_index"]

def render(d):
    idx = d["binding"]["warrant_index"]
    return f'''import CLCMetatronAdapter.CertificateProvenance

namespace CLCMetatronAdapter

def attestedUnitLiveWarrant :
    LiveWarrantCertificate Metatron.warrantBaseline :=
  ⟨{idx}, by
    rw [Metatron.warrant_baseline_all_live]
    simp⟩

def attestedUnitCertificateProvenance :
    CertificateProvenance Unit Metatron.warrantBaseline where
  toLive := fun _ => attestedUnitLiveWarrant

theorem attestedUnitCertificateProvenance_index :
    (attestedUnitCertificateProvenance.toLive ()).1 = {idx} := by
  rfl

theorem attestedUnitCertificateProvenance_is_live :
    {idx} ∈ Metatron.warrantLive Metatron.warrantBaseline := by
  exact (attestedUnitCertificateProvenance.toLive ()).2

theorem attestedUnitCertificateProvenance_support :
    (certificateProvenanceSupport
      Metatron.warrantBaseline
      attestedUnitCertificateProvenance
      unitAuthority).support () = ({{{idx}}} : CLC.Support Nat) := by
  rfl

end CLCMetatronAdapter
'''

def main():
    d=load()
    validate(d)
    OUT.write_text(render(d))
    print(f"WROTE {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
