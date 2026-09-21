from dataclasses import dataclass
from enum import IntEnum, StrEnum
from hashlib import sha256
from typing import TypeAlias


class State(IntEnum):
    ZERO = 0
    ONE = 1
    TWO = 2


class Query(StrEnum):
    IS_ZERO = "is_zero"
    IS_ONE = "is_one"


Table: TypeAlias = tuple[int, int, int]
ID_TABLE: Table = (0, 1, 2)
STEP_TABLE: Table = (1, 1, 2)


def compose(first: Table, second: Table) -> Table:
    return tuple(second[first[i]] for i in range(3))


def table_digest(table: Table) -> str:
    return sha256(bytes(table)).hexdigest()


@dataclass(frozen=True)
class Residual:
    target: Table
    closure_size: int
    closure_digest: str
    authority_digest: str


@dataclass(frozen=True)
class ResidualCertificate:
    id: str
    target: Table
    target_digest: str
    closure_size: int
    closure_digest: str
    authority_digest: str


@dataclass(frozen=True)
class Capability:
    name: str
    table: Table
    residual_certificate_id: str | None = None
    certificate_id: str | None = None


@dataclass(frozen=True)
class Certificate:
    id: str
    kind: str
    subject_digest: str


@dataclass(frozen=True)
class Relation:
    left: tuple[str, ...]
    right: str


@dataclass(frozen=True)
class LineageEvent:
    kind: str
    payload: dict[str, object]
