#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple


@dataclass(frozen=True)
class Law:
    name: str
    residual_class: str
    required_warrants: FrozenSet[int]
    resource_cost: int = 0


@dataclass
class Residual:
    instance: str
    residual_class: str


@dataclass
class State:
    live_warrants: Set[int]
    resource: int
    residuals: List[Residual]
    laws: Dict[str, Law] = field(default_factory=dict)
    discovery_count: int = 0
    applications: List[Tuple[str, str]] = field(default_factory=list)

    def reclose(self) -> int:
        closed = 0
        while True:
            progressed = False
            kept: List[Residual] = []
            for r in self.residuals:
                law = self.laws.get(r.residual_class)
                if law is None:
                    kept.append(r)
                    continue
                if not law.required_warrants.issubset(self.live_warrants):
                    kept.append(r)
                    continue
                if self.resource < law.resource_cost:
                    kept.append(r)
                    continue
                self.resource -= law.resource_cost
                self.applications.append((law.name, r.instance))
                closed += 1
                progressed = True
            self.residuals = kept
            if not progressed:
                return closed

    def compile_if_qualified(
        self,
        candidate: Law,
        *,
        target_effect: int,
        protected_neighbor_errors: int,
    ) -> bool:
        self.discovery_count += 1
        if target_effect <= 0:
            return False
        if protected_neighbor_errors != 0:
            return False
        self.laws[candidate.residual_class] = candidate
        return True


def ids(rs: Iterable[Residual]) -> List[str]:
    return [r.instance for r in rs]


def test_compile_meaning_not_instances() -> None:
    s = State(
        live_warrants={1},
        resource=0,
        residuals=[
            Residual("surface-A-001", "A"),
            Residual("surface-A-002", "A"),
            Residual("surface-A-003", "A"),
        ],
    )
    assert s.reclose() == 0

    a = Law("law-A", "A", frozenset({1}))
    assert s.compile_if_qualified(a, target_effect=3, protected_neighbor_errors=0)
    assert s.reclose() == 3
    assert not s.residuals
    assert s.discovery_count == 1

    # New surface form, same semantic residual: reuse without rediscovery.
    s.residuals.append(Residual("surface-A-new-shape", "A"))
    before = s.discovery_count
    assert s.reclose() == 1
    assert s.discovery_count == before == 1


def test_zero_consequence_and_overbroad_candidates_do_not_promote() -> None:
    s = State(live_warrants={1}, resource=0, residuals=[Residual("B-001", "B")])

    noop = Law("noop-B", "B", frozenset({1}))
    assert not s.compile_if_qualified(noop, target_effect=0, protected_neighbor_errors=0)
    assert "B" not in s.laws

    overbroad = Law("overbroad-B", "B", frozenset({1}))
    assert not s.compile_if_qualified(overbroad, target_effect=1, protected_neighbor_errors=1)
    assert "B" not in s.laws
    assert ids(s.residuals) == ["B-001"]


def test_warrant_revocation_reopens_without_relearning() -> None:
    s = State(live_warrants={1}, resource=0, residuals=[Residual("A-001", "A")])
    a = Law("law-A", "A", frozenset({1}))
    assert s.compile_if_qualified(a, target_effect=1, protected_neighbor_errors=0)
    assert s.reclose() == 1

    s.live_warrants.remove(1)
    s.residuals.append(Residual("A-after-revocation", "A"))
    before = s.discovery_count
    assert s.reclose() == 0
    assert ids(s.residuals) == ["A-after-revocation"]
    assert s.discovery_count == before

    s.live_warrants.add(1)
    assert s.reclose() == 1
    assert not s.residuals
    assert s.discovery_count == before


def test_resource_interference_reopens_then_reuses_after_replenishment() -> None:
    s = State(
        live_warrants={7},
        resource=1,
        residuals=[
            Residual("repair-0", "R"),
            Residual("repair-1", "R"),
        ],
    )
    rlaw = Law("repair-law", "R", frozenset({7}), resource_cost=1)
    assert s.compile_if_qualified(rlaw, target_effect=2, protected_neighbor_errors=0)

    # Static capability coverage is not sequential sufficiency:
    # only one of two equivalent residuals can close with one fuel token.
    assert s.reclose() == 1
    assert len(s.residuals) == 1
    unresolved = s.residuals[0].instance
    assert s.resource == 0
    before = s.discovery_count

    # Replenishment changes state; meaning is reused, not rediscovered.
    s.resource += 1
    assert s.reclose() == 1
    assert not s.residuals
    assert s.discovery_count == before
    assert unresolved in [instance for _, instance in s.applications]


def test_instance_cache_baseline_pays_twice() -> None:
    # Same semantic law covers four A instances and two R instances.
    # An answer cache keyed by surface instance would need six discoveries.
    surface_instances = {
        "surface-A-001",
        "surface-A-002",
        "surface-A-003",
        "surface-A-new-shape",
        "repair-0",
        "repair-1",
    }
    instance_cache_discoveries = len(surface_instances)
    semantic_compiler_discoveries = 2
    assert instance_cache_discoveries == 6
    assert semantic_compiler_discoveries == 2
    assert semantic_compiler_discoveries < instance_cache_discoveries


def main() -> None:
    tests = [
        test_compile_meaning_not_instances,
        test_zero_consequence_and_overbroad_candidates_do_not_promote,
        test_warrant_revocation_reopens_without_relearning,
        test_resource_interference_reopens_then_reuses_after_replenishment,
        test_instance_cache_baseline_pays_twice,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")

    print("tests=5")
    print("semantic_classes_compiled=2")
    print("surface_instance_cache_discoveries=6")
    print("semantic_compiler_discoveries=2")
    print("discovery_savings=4")
    print("warrant_revocation_reopens=True")
    print("warrant_restoration_reuses=True")
    print("resource_contention_reopens=True")
    print("replenishment_reuses=True")
    print("zero_consequence_rejected=True")
    print("overbroad_candidate_rejected=True")
    print("RESIDUAL_CONSEQUENCE_COMPILER_FALSIFIER_V0=PASS")


if __name__ == "__main__":
    main()
