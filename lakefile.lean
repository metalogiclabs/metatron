import Lake
open Lake DSL

package metatron where
  moreLeanArgs := #["-DautoImplicit=false"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @
  "44ba35c6daa9d69aff8fed9fff9bbde17ded774d"

@[default_target]
lean_lib Metatron where
  srcDir := "formal"
  roots := #[`Metatron.WarrantGraph]

lean_exe metatron_reference where
  srcDir := "formal"
  root := `Metatron.ReferenceCLI
