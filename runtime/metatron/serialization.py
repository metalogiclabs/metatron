from .machine import Machine
from .nucleus import WarrantGraph


def dump_machine(machine: Machine) -> str:
    """Serialize only the authoritative append-only warrant log."""
    return machine.graph.dumps()


def load_machine(payload: str) -> Machine:
    """Replay the authoritative warrant log; all legacy views are derived."""
    return Machine(WarrantGraph.loads(payload))
