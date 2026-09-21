from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Decision = Literal[
    "PROMOTE",
    "REJECT_REGRESSION",
    "MEASURE_EXTERNAL",
    "REJECT_UNVERIFIED",
]


@dataclass(frozen=True)
class Measurement:
    metric: str
    cohort_id: str
    case_ids: tuple[str, ...]
    values: tuple[int, ...]
    official: bool
    scoreable: bool
    source: str

    @property
    def total(self) -> int:
        return sum(self.values)

    def comparable_with(self, other: "Measurement") -> bool:
        return (
            self.metric == other.metric
            and self.cohort_id == other.cohort_id
            and self.case_ids == other.case_ids
        )


@dataclass(frozen=True)
class CandidateEvidence:
    name: str
    universal_proof: bool
    canonical_accepted: bool
    external: Measurement | None = None
    local_proxy_seconds: float | None = None


@dataclass(frozen=True)
class Comparison:
    decision: Decision
    reason: str
    improvement_fraction: float | None
    candidate_total: int | None
    incumbent_total: int | None


def compare(candidate: CandidateEvidence, incumbent: CandidateEvidence) -> Comparison:
    if not candidate.universal_proof or not candidate.canonical_accepted:
        return Comparison(
            "REJECT_UNVERIFIED",
            "candidate has not passed the universal proof and canonical acceptance gates",
            None,
            None,
            None,
        )

    if candidate.external is not None and incumbent.external is not None:
        if not candidate.external.comparable_with(incumbent.external):
            return Comparison(
                "MEASURE_EXTERNAL",
                "external measurements exist but are not from the same frozen metric/cohort/case plan",
                None,
                candidate.external.total,
                incumbent.external.total,
            )
        c = candidate.external.total
        i = incumbent.external.total
        improvement = (i - c) / i
        if c < i:
            return Comparison(
                "PROMOTE",
                "verified candidate strictly improves the frozen external consequence",
                improvement,
                c,
                i,
            )
        return Comparison(
            "REJECT_REGRESSION",
            "verified candidate does not improve the frozen external consequence",
            improvement,
            c,
            i,
        )

    if (
        candidate.local_proxy_seconds is not None
        and incumbent.local_proxy_seconds is not None
        and candidate.local_proxy_seconds >= incumbent.local_proxy_seconds
    ):
        return Comparison(
            "REJECT_REGRESSION",
            "candidate regresses on the frozen local proxy before external measurement",
            (incumbent.local_proxy_seconds - candidate.local_proxy_seconds)
            / incumbent.local_proxy_seconds,
            None,
            None,
        )

    return Comparison(
        "MEASURE_EXTERNAL",
        "candidate may be locally promising but lacks a comparable frozen external measurement",
        None,
        candidate.external.total if candidate.external else None,
        incumbent.external.total if incumbent.external else None,
    )
