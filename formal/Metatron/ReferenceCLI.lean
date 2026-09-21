import Metatron.WarrantGraph

namespace Metatron

def renderNatList (xs : List Nat) : String :=
  String.intercalate "," (xs.map toString)

def referenceMain : IO Unit := do
  IO.println s!"WARRANT_BASELINE={renderNatList (warrantLive warrantBaseline)}"
  IO.println s!"WARRANT_REVOKED={renderNatList (warrantLive warrantRevokedFixture)}"

end Metatron

def main : IO Unit := Metatron.referenceMain
