import Lake
open Lake DSL

package clcMetatronAdapter where
  moreLeanArgs := #["-DautoImplicit=false"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @
  "44ba35c6daa9d69aff8fed9fff9bbde17ded774d"

@[default_target]
lean_lib CLCMetatronAdapter where
  srcDir := "."
  roots := #[
    `CLC.Support,
    `Metatron.WarrantGraph,
    `CLCMetatronAdapter.Adapter,
    `CLCMetatronAdapter.Regression
  ]
