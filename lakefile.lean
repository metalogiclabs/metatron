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
    `Metatron.MonoidalDeepPresent,
    `Metatron.WiredPomset,
    `Metatron.PortEventStructure,
    `Metatron.ResidualBasis,
    `Metatron.ResidualSynergy,
    `Metatron.CausalRepairCover,
    `Metatron.CausalLinearization,
    `Metatron.CausalTraceQuotient,
    `Metatron.FinitePosetConnectivity,
    `Metatron.EarnedCommutation,
    `Metatron.BehavioralCommutation,
    `Metatron.EmbeddedObserverOntology,
    `Metatron.NovelCapabilityGenesis,
    `Metatron.ResidualGeneratedCapability,
    `Metatron.WarrantedContinuationViability,
    `Metatron.WarrantedContinuationViabilityV1,
    `Metatron.WarrantedContinuationViabilityV2,
    `Metatron.WarrantedContinuationViabilityV3,
    `Metatron.WarrantedContinuationViabilityV4,
    `Metatron.WarrantedContinuationViabilityV5,
    `Metatron.WarrantedContinuationViabilityV6
  ]

lean_exe metatron_reference where
  srcDir := "formal"
  root := `Metatron.ReferenceCLI
