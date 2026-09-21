import json

from runtime.metatron.nebula import (
    NebulaMachine,
    TerminalRequirement,
    unresolved_potential,
)


def main() -> None:
    machine = NebulaMachine.genesis(size=5)
    initial = machine.partition
    potentials = [unresolved_potential(initial)]

    machine.perturb(TerminalRequirement())
    while not machine.satisfied():
        machine.step()
        potentials.append(unresolved_potential(machine.partition))

    promotions = [
        event.subject for event in machine.lineage if event.kind == "PROMOTE"
    ]
    obstructions = [
        event.details["block"]
        for event in machine.lineage
        if event.kind == "OBSTRUCTION"
    ]

    learned = [
        (name, warrant_id)
        for name, (_, warrant_id) in sorted(machine.distinctions.items())
        if warrant_id is not None
    ]
    first_warrant = learned[0][1]
    revoked = machine.revoke(first_warrant)

    report = {
        "name": "Nebula Ignition V0",
        "external_perturbations": 1,
        "initial_partition": [list(block) for block in initial],
        "obstruction_blocks": obstructions,
        "promotions": promotions,
        "generations": len(promotions),
        "potential": potentials,
        "terminal_partition_before_knockout": [
            [0], [1], [2], [3], [4]
        ],
        "g1_knockout_revoked_warrants": list(revoked),
        "partition_after_g1_knockout": [
            list(block) for block in machine.partition
        ],
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
