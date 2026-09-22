import Lake
open Lake DSL

package metatron where
  moreLeanArgs := #["-DautoImplicit=false"]

@[default_target]
lean_lib Metatron where
  srcDir := "formal"
  roots := #[
    `Metatron.WarrantGraph,
    `Metatron.FutureObservations,
    `Metatron.FixedPointReflection,
    `Metatron.DevelopmentalRelation,
    `Metatron.ProofRelevantOplax,
    `Metatron.MonoidalDeepPresent
  ]

lean_exe metatron_reference where
  srcDir := "formal"
  root := `Metatron.ReferenceCLI
