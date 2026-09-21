from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json


def _digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Distinction:
    pivot: int

    @property
    def name(self) -> str:
        return f"is_{self.pivot}"

    def observe(self, state: int) -> bool:
        return state == self.pivot


@dataclass(frozen=True)
class TerminalRequirement:
    kind: str = "singleton_partition"


@dataclass(frozen=True)
class Obstruction:
    id: str
    block: tuple[int, ...]
    partition_digest: str
    authority_digest: str
    potential: int


@dataclass(frozen=True)
class CandidateLift:
    distinction: Distinction
    obstruction_id: str
    before_potential: int
    after_potential: int


@dataclass(frozen=True)
class Warrant:
    id: str
    subject: str
    obstruction_id: str
    depends_on: tuple[str, ...]


@dataclass(frozen=True)
class Event:
    generation: int
    kind: str
    subject: str
    details: dict


class NebulaError(RuntimeError):
    pass


class NotDerivableError(NebulaError):
    pass


class UnknownChoiceError(NebulaError):
    pass


class InvalidWarrantError(NebulaError):
    pass


def unresolved_potential(partition: tuple[tuple[int, ...], ...]) -> int:
    return sum(max(0, len(block) - 1) for block in partition)


def select_unique_minimal(candidates: tuple[tuple[int, object], ...]):
    if not candidates:
        raise NebulaError("no admissible repair")
    best_cost = min(cost for cost, _ in candidates)
    best = tuple(item for cost, item in candidates if cost == best_cost)
    if len(best) != 1:
        raise UnknownChoiceError("minimal repair is not unique")
    return best[0]


class NebulaMachine:
    """
    Nebula Ignition V0.

    One external terminal requirement is supplied. Intermediate obstructions
    and representation lifts are generated only from the current active
    quotient. Every learned distinction is justified by an obstruction that
    did not exist as an active block before the previous reclosure.
    """

    def __init__(self, size: int = 5):
        if size < 3:
            raise ValueError("Nebula V0 needs at least three states")
        self.states = tuple(range(size))
        self.requirement: TerminalRequirement | None = None
        self.distinctions: dict[str, tuple[Distinction, str | None]] = {
            "is_0": (Distinction(0), None)
        }
        self.obstructions: dict[str, Obstruction] = {}
        self.warrants: dict[str, Warrant] = {}
        self.revoked: set[str] = set()
        self.lineage: list[Event] = []
        self.generation = 0
        self.partition = self._partition()
        self._append("GENESIS", "unperturbed")

    @classmethod
    def genesis(cls, size: int = 5) -> "NebulaMachine":
        return cls(size)

    def _append(self, kind: str, subject: str, **details) -> None:
        self.lineage.append(
            Event(self.generation, kind, subject, details)
        )

    def _active_items(self):
        return {
            name: (distinction, warrant_id)
            for name, (distinction, warrant_id) in self.distinctions.items()
            if warrant_id is None or warrant_id not in self.revoked
        }

    def authority_digest(self) -> str:
        return _digest([
            (name, distinction.pivot, warrant_id)
            for name, (distinction, warrant_id)
            in sorted(self._active_items().items())
        ])

    def _partition(self) -> tuple[tuple[int, ...], ...]:
        active = tuple(
            distinction
            for distinction, _ in self._active_items().values()
        )
        groups: dict[tuple[bool, ...], list[int]] = {}
        for state in self.states:
            signature = tuple(d.observe(state) for d in active)
            groups.setdefault(signature, []).append(state)
        return tuple(
            sorted(
                (tuple(block) for block in groups.values()),
                key=lambda block: block[0],
            )
        )

    def satisfied(self) -> bool:
        return self.requirement is not None and all(
            len(block) == 1 for block in self.partition
        )

    def active_obstruction_blocks(self) -> tuple[tuple[int, ...], ...]:
        return tuple(block for block in self.partition if len(block) > 1)

    def certify_current_obstruction(self) -> Obstruction | None:
        if self.requirement is None:
            raise NotDerivableError("no terminal requirement is active")
        blocks = self.active_obstruction_blocks()
        if not blocks:
            return None
        if len(blocks) != 1:
            raise UnknownChoiceError(
                "V0 ignition requires a unique active obstruction block"
            )
        block = blocks[0]
        pdigest = _digest([list(b) for b in self.partition])
        authority = self.authority_digest()
        potential = unresolved_potential(self.partition)
        ident = "obstruction:" + _digest([
            list(block), pdigest, authority, potential
        ])[:24]
        obstruction = Obstruction(
            ident, block, pdigest, authority, potential
        )
        self.obstructions[ident] = obstruction
        self._append(
            "OBSTRUCTION",
            ident,
            block=list(block),
            potential=potential,
        )
        return obstruction

    def certify_named_block(self, block: tuple[int, ...]) -> Obstruction:
        if block not in self.active_obstruction_blocks():
            raise NotDerivableError(
                "requested obstruction block does not exist in current quotient"
            )
        obstruction = self.certify_current_obstruction()
        if obstruction is None or obstruction.block != block:
            raise NotDerivableError("block is not the current obstruction")
        return obstruction

    def synthesize_minimal_lift(
        self, obstruction: Obstruction
    ) -> CandidateLift:
        stored = self.obstructions.get(obstruction.id)
        if stored != obstruction:
            raise NotDerivableError("obstruction was not issued")
        if obstruction.authority_digest != self.authority_digest():
            raise NotDerivableError("obstruction is stale")
        if obstruction.partition_digest != _digest(
            [list(b) for b in self.partition]
        ):
            raise NotDerivableError("representation changed")

        # Generic V0 developmental law: split the head from the exact
        # unresolved block. The law is block-relative; no intermediate
        # state/query names are preloaded.
        pivot = min(obstruction.block)
        distinction = Distinction(pivot)
        if distinction.name in self._active_items():
            raise NebulaError("head distinction is already active")

        before = unresolved_potential(self.partition)
        active = tuple(
            d for d, _ in self._active_items().values()
        ) + (distinction,)
        groups: dict[tuple[bool, ...], list[int]] = {}
        for state in self.states:
            sig = tuple(d.observe(state) for d in active)
            groups.setdefault(sig, []).append(state)
        after_partition = tuple(
            sorted(
                (tuple(block) for block in groups.values()),
                key=lambda block: block[0],
            )
        )
        after = unresolved_potential(after_partition)

        if after >= before:
            raise NebulaError("candidate does not strictly reduce obstruction")

        candidate = CandidateLift(
            distinction, obstruction.id, before, after
        )
        self._append(
            "SYNTHESIZE",
            distinction.name,
            obstruction=obstruction.id,
            before_potential=before,
            after_potential=after,
        )
        return candidate

    def verify(self, candidate: CandidateLift) -> Warrant:
        obstruction = self.obstructions.get(candidate.obstruction_id)
        if obstruction is None:
            raise NotDerivableError("candidate lacks issued obstruction")
        if candidate.before_potential != obstruction.potential:
            raise NebulaError("candidate was verified against wrong potential")
        if candidate.after_potential != candidate.before_potential - 1:
            raise NebulaError("V0 lift must remove exactly one unresolved degree")

        dependencies = tuple(
            sorted(
                warrant_id
                for _, warrant_id in self._active_items().values()
                if warrant_id is not None
            )
        )
        payload = _digest([
            candidate.distinction.pivot,
            candidate.obstruction_id,
            candidate.before_potential,
            candidate.after_potential,
            dependencies,
        ])
        warrant = Warrant(
            "warrant:" + payload[:24],
            candidate.distinction.name,
            candidate.obstruction_id,
            dependencies,
        )
        self.warrants[warrant.id] = warrant
        self._append(
            "VERIFY",
            candidate.distinction.name,
            warrant=warrant.id,
            depends_on=list(dependencies),
        )
        return warrant

    def promote(self, candidate: CandidateLift, warrant: Warrant) -> None:
        if self.warrants.get(warrant.id) != warrant:
            raise InvalidWarrantError("warrant was not issued")
        if warrant.subject != candidate.distinction.name:
            raise InvalidWarrantError("warrant subject mismatch")
        if warrant.obstruction_id != candidate.obstruction_id:
            raise InvalidWarrantError("warrant obstruction mismatch")

        self.distinctions[candidate.distinction.name] = (
            candidate.distinction,
            warrant.id,
        )
        self.generation += 1
        self._append(
            "PROMOTE",
            candidate.distinction.name,
            warrant=warrant.id,
        )
        before = self.partition
        self.partition = self._partition()
        self._append(
            "RECLOSE",
            candidate.distinction.name,
            before=[list(b) for b in before],
            after=[list(b) for b in self.partition],
            potential=unresolved_potential(self.partition),
        )

    def step(self) -> bool:
        if self.satisfied():
            return False
        obstruction = self.certify_current_obstruction()
        if obstruction is None:
            return False
        candidate = self.synthesize_minimal_lift(obstruction)
        warrant = self.verify(candidate)
        self.promote(candidate, warrant)
        return True

    def perturb(self, requirement: TerminalRequirement) -> None:
        if self.requirement is not None and self.requirement != requirement:
            raise NebulaError("a different terminal requirement is already active")
        if self.requirement is None:
            self.requirement = requirement
            self._append("PERTURB", requirement.kind)

    def ignite(
        self,
        requirement: TerminalRequirement | None = None,
        max_generations: int = 32,
    ) -> int:
        if requirement is not None:
            self.perturb(requirement)
        if self.requirement is None:
            raise NotDerivableError("no terminal requirement is active")
        start = self.generation
        while not self.satisfied():
            if self.generation - start >= max_generations:
                raise NebulaError("generation budget exhausted")
            self.step()
        self._append(
            "TERMINAL_REQUIREMENT_SATISFIED",
            self.requirement.kind,
            generations=self.generation - start,
        )
        return self.generation - start

    def revoke(self, warrant_id: str) -> tuple[str, ...]:
        if warrant_id not in self.warrants:
            raise KeyError(warrant_id)

        revoked_now = {warrant_id}
        changed = True
        while changed:
            changed = False
            for wid, warrant in self.warrants.items():
                if wid in revoked_now:
                    continue
                if any(dep in revoked_now for dep in warrant.depends_on):
                    revoked_now.add(wid)
                    changed = True

        self.revoked.update(revoked_now)
        self._append(
            "CAUSAL_KNOCKOUT",
            warrant_id,
            revoked=sorted(revoked_now),
        )
        self.partition = self._partition()
        self._append(
            "RECLOSE",
            "REVOCATION",
            after=[list(b) for b in self.partition],
            potential=unresolved_potential(self.partition),
        )
        return tuple(sorted(revoked_now))

    def dump(self) -> str:
        return json.dumps(
            {
                "states": list(self.states),
                "generation": self.generation,
                "partition": [list(b) for b in self.partition],
                "distinctions": {
                    name: [distinction.pivot, warrant_id]
                    for name, (distinction, warrant_id)
                    in sorted(self.distinctions.items())
                },
                "obstructions": {
                    ident: {
                        **asdict(obstruction),
                        "block": list(obstruction.block),
                    }
                    for ident, obstruction in sorted(self.obstructions.items())
                },
                "warrants": {
                    ident: {
                        **asdict(warrant),
                        "depends_on": list(warrant.depends_on),
                    }
                    for ident, warrant in sorted(self.warrants.items())
                },
                "revoked": sorted(self.revoked),
                "lineage": [asdict(event) for event in self.lineage],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
