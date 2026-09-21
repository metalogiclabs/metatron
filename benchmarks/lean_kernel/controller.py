from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from .adapter import CandidateEvidence, Comparison, compare


Action = Literal[
    "PROMOTE",
    "REJECT_REGRESSION",
    "REJECT_UNVERIFIED",
    "REQUEST_EXTERNAL",
    "ESCALATE_SEARCH_POLICY",
]


@dataclass(frozen=True)
class FrontierCandidate:
    evidence: CandidateEvidence
    family: str


@dataclass(frozen=True)
class DecisionEvent:
    serial: int
    candidate: str
    family: str
    champion_before: str
    champion_after: str
    comparison_decision: str
    action: Action
    reason: str
    certified_insufficiency: bool


class FrontierController:
    """Append-only controller for externally calibrated development.

    Policy escalation is not an inadequacy theorem. This controller is therefore
    forbidden from issuing an insufficiency certificate: exact structural growth
    still requires a separate accepted no-resolution certificate.
    """

    def __init__(
        self,
        champion: FrontierCandidate,
        *,
        escalation_after_distinct_regressions: int = 2,
    ) -> None:
        if escalation_after_distinct_regressions < 1:
            raise ValueError("escalation threshold must be positive")
        self.champion = champion
        self.escalation_after_distinct_regressions = (
            escalation_after_distinct_regressions
        )
        self.failed_families_since_promotion: set[str] = set()
        self.lineage: list[DecisionEvent] = []
        self._next_serial = 1

    def _append(
        self,
        candidate: FrontierCandidate,
        comparison: Comparison,
        action: Action,
        reason: str,
        champion_before: str,
    ) -> DecisionEvent:
        event = DecisionEvent(
            serial=self._next_serial,
            candidate=candidate.evidence.name,
            family=candidate.family,
            champion_before=champion_before,
            champion_after=self.champion.evidence.name,
            comparison_decision=comparison.decision,
            action=action,
            reason=reason,
            certified_insufficiency=False,
        )
        self._next_serial += 1
        self.lineage.append(event)
        return event

    def observe(self, candidate: FrontierCandidate) -> DecisionEvent:
        before = self.champion.evidence.name
        result = compare(candidate.evidence, self.champion.evidence)

        if result.decision == "PROMOTE":
            self.champion = candidate
            self.failed_families_since_promotion.clear()
            return self._append(
                candidate,
                result,
                "PROMOTE",
                result.reason,
                before,
            )

        if result.decision == "REJECT_UNVERIFIED":
            return self._append(
                candidate,
                result,
                "REJECT_UNVERIFIED",
                result.reason,
                before,
            )

        if result.decision == "MEASURE_EXTERNAL":
            return self._append(
                candidate,
                result,
                "REQUEST_EXTERNAL",
                result.reason,
                before,
            )

        if result.decision == "REJECT_REGRESSION":
            self.failed_families_since_promotion.add(candidate.family)
            if (
                len(self.failed_families_since_promotion)
                >= self.escalation_after_distinct_regressions
            ):
                return self._append(
                    candidate,
                    result,
                    "ESCALATE_SEARCH_POLICY",
                    (
                        result.reason
                        + "; multiple distinct verified representation families "
                        "have regressed since the current promotion, so broaden "
                        "the search family without claiming certified inadequacy"
                    ),
                    before,
                )
            return self._append(
                candidate,
                result,
                "REJECT_REGRESSION",
                result.reason,
                before,
            )

        raise AssertionError(result.decision)

    def snapshot(self) -> dict[str, object]:
        return {
            "champion": self.champion.evidence.name,
            "failed_families_since_promotion": sorted(
                self.failed_families_since_promotion
            ),
            "lineage": [asdict(event) for event in self.lineage],
            "next_serial": self._next_serial,
            "certified_insufficiency": False,
        }
