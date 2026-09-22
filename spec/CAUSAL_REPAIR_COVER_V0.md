# Certified Causal Repair Cover V0

**Status:** replacement theorem experiment  
**Branch:** causal-repair-cover-v0

Residual Synergy V0 proved that ordinary singleton-generator cover is incomplete once lawful composition can generate consequences that no component generates alone.

This branch replaces the primitive repair unit. A certified causal repair C=(P,sigma,label) carries a finite port-aware causal event structure P, an executable event schedule sigma, generator labels, and a certification that the schedule contains every event exactly once and respects every causal edge.

Every ordinary generator embeds as a one-event certified causal repair. The theorem singleton_support_is_arity_one seals that embedding, so Blind V3 ordinary tau is retained as the one-event special case.

The general bridge is causalRepairCover_iff_targetSufficient: a family of certified causal repairs covers every future-demanded residual pair iff the refined relation is sufficient for the frozen target. minimumCausalRepair_minimalSufficient transfers exact minimum repair count to minimum target sufficiency.

The two-event fixture reuses the qualified synergy world: A copies source to hidden; B copies hidden to observed. A->B is represented by a two-event port-wired causal chain and resolves the witness. B->A uses the same reusable generators in the opposite causal order and does not.

Required results:

- ab_port_order
- ba_port_order
- ab_repair_separates_xy
- ba_repair_does_not_separate_xy
- ordinary_singletons_still_fail
- ab_causal_repair_covers
- ba_causal_repair_fails_cover
- ab_is_minimum_one_repair

Therefore the native unit is not merely a subset of generators. Causal structure is semantically relevant.

The refined discovery architecture is:

behavioral quotient -> consequential residual -> certified causal repair frontier -> independent warrant -> reclosure.

Ordinary tau is the arity-one projection.

Claim boundary: this finite result does not establish unrestricted synthesis of arbitrary event structures, a complete cost theory, equivalence under all linearizations of a partial order, conflict/synchronization/feedback search, tractable large-scale optimization, or any enlargement of Nucleus authority.
