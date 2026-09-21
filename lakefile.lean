import Lake
open Lake DSL

package metatron where
  moreLeanArgs := #["-DautoImplicit=false"]

@[default_target]
lean_lib Metatron where
  srcDir := "formal"
  roots := #[`Metatron.WarrantGraph]

lean_exe metatron_reference where
  srcDir := "formal"
  root := `Metatron.ReferenceCLI
