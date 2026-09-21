from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .adapter import CandidateEvidence, Measurement


StageAction = Literal[
    "STAGE_FOR_EXTERNAL",
    "REPLACE_STAGED",
    "REJECT_LOCAL_REGRESSION",
    "REJECT_UNVERIFIED",
    "EXTERNAL_PROMOTE",
    "EXTERNAL_REJECT",
    "EXTERNAL_NOT_COMPARABLE",
]


@dataclass(frozen=True)
class StagedCandidate:
    evidence: CandidateEvidence
    family: str


@dataclass(frozen=True)
class StageEvent:
    serial: int
    candidate: str
    family: str
    action: StageAction
    external_champion_before: str
    external_champion_after: str
    staged_before: str | None
    staged_after: str | None
    reason: str


class TwoTierFrontier:
    """Keep externally warranted and locally promising champions separate.

    The external champion may change only on a comparable external measurement.
    Local proxy improvements may replace the staged contender, but never promote
    it into the externally warranted slot.
    """

    def __init__(self, external_champion: StagedCandidate) -> None:
        if external_champion.evidence.external is None:
            raise ValueError("external champion must carry external measurement")
        if not (
            external_champion.evidence.universal_proof
            and external_champion.evidence.canonical_accepted
        ):
            raise ValueError("external champion must be verified and accepted")
        self.external_champion = external_champion
        self.staged: StagedCandidate | None = None
        self.lineage: list[StageEvent] = []
        self._next_serial = 1

    def _append(
        self,
        candidate: StagedCandidate,
        action: StageAction,
        reason: str,
        external_before: str,
        staged_before: str | None,
    ) -> StageEvent:
        event = StageEvent(
            serial=self._next_serial,
            candidate=candidate.evidence.name,
            family=candidate.family,
            action=action,
            external_champion_before=external_before,
            external_champion_after=self.external_champion.evidence.name,
            staged_before=staged_before,
            staged_after=self.staged.evidence.name if self.staged else None,
            reason=reason,
        )
        self._next_serial += 1
        self.lineage.append(event)
        return event

    @staticmethod
    def _verified(candidate: StagedCandidate) -> bool:
        return (
            candidate.evidence.universal_proof
            and candidate.evidence.canonical_accepted
        )

    def observe_local(self, candidate: StagedCandidate) -> StageEvent:
        external_before = self.external_champion.evidence.name
        staged_before = self.staged.evidence.name if self.staged else None

        if not self._verified(candidate):
            return self._append(
                candidate,
                "REJECT_UNVERIFIED",
                "candidate has not passed universal proof and canonical acceptance",
                external_before,
                staged_before,
            )

        local = candidate.evidence.local_proxy_seconds
        if local is None:
            return self._append(
                candidate,
                "REJECT_LOCAL_REGRESSION",
                "candidate has no frozen local proxy measurement",
                external_before,
                staged_before,
            )

        if self.staged is None:
            champion_local = self.external_champion.evidence.local_proxy_seconds
            if champion_local is not None and local >= champion_local:
                return self._append(
                    candidate,
                    "REJECT_LOCAL_REGRESSION",
                    "candidate does not improve the frozen local proxy over the external champion",
                    external_before,
                    staged_before,
                )
            self.staged = candidate
            return self._append(
                candidate,
                "STAGE_FOR_EXTERNAL",
                "verified candidate improves the frozen local proxy and is now the sole external-measurement contender",
                external_before,
                staged_before,
            )

        staged_local = self.staged.evidence.local_proxy_seconds
        if staged_local is None or local < staged_local:
            self.staged = candidate
            return self._append(
                candidate,
                "REPLACE_STAGED",
                "verified candidate improves the frozen local proxy over the previously staged contender",
                external_before,
                staged_before,
            )

        return self._append(
            candidate,
            "REJECT_LOCAL_REGRESSION",
            "candidate does not improve the frozen local proxy over the staged contender",
            external_before,
            staged_before,
        )

    def observe_external(
        self,
        candidate: StagedCandidate,
        measurement: Measurement,
    ) -> StageEvent:
        external_before = self.external_champion.evidence.name
        staged_before = self.staged.evidence.name if self.staged else None

        if not self._verified(candidate):
            return self._append(
                candidate,
                "REJECT_UNVERIFIED",
                "candidate has not passed universal proof and canonical acceptance",
                external_before,
                staged_before,
            )

        incumbent_measurement = self.external_champion.evidence.external
        assert incumbent_measurement is not None
        if not measurement.comparable_with(incumbent_measurement):
            return self._append(
                candidate,
                "EXTERNAL_NOT_COMPARABLE",
                "external measurement is not from the frozen metric/cohort/case plan",
                external_before,
                staged_before,
            )

        measured_candidate = StagedCandidate(
            CandidateEvidence(
                name=candidate.evidence.name,
                universal_proof=True,
                canonical_accepted=True,
                external=measurement,
                local_proxy_seconds=candidate.evidence.local_proxy_seconds,
            ),
            candidate.family,
        )

        if measurement.total < incumbent_measurement.total:
            self.external_champion = measured_candidate
            if self.staged and self.staged.evidence.name == candidate.evidence.name:
                self.staged = None
            return self._append(
                candidate,
                "EXTERNAL_PROMOTE",
                "same-cohort external measurement strictly improves the external champion",
                external_before,
                staged_before,
            )

        if self.staged and self.staged.evidence.name == candidate.evidence.name:
            self.staged = None
        return self._append(
            candidate,
            "EXTERNAL_REJECT",
            "same-cohort external measurement does not improve the external champion",
            external_before,
            staged_before,
        )

    def next_external_candidate(self) -> StagedCandidate | None:
        return self.staged

    def snapshot(self) -> dict[str, object]:
        return {
            "external_champion": self.external_champion.evidence.name,
            "staged_candidate": self.staged.evidence.name if self.staged else None,
            "next_serial": self._next_serial,
            "lineage": [asdict(e) for e in self.lineage],
        }
