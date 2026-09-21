from hashlib import sha256

from .model import Residual, Table, compose

def closure(tables) -> frozenset[Table]:
    known = set(tables)
    changed = True
    while changed:
        changed = False
        snapshot = tuple(known)
        for first in snapshot:
            for second in snapshot:
                candidate = compose(first, second)
                if candidate not in known:
                    known.add(candidate)
                    changed = True
    return frozenset(known)

def _tables_digest(tables) -> str:
    payload = b"|".join(bytes(table) for table in sorted(tables))
    return sha256(payload).hexdigest()

def authority_digest(active_tables) -> str:
    return _tables_digest(frozenset(active_tables))

def certify_no_resolution(active_tables, target):
    active = frozenset(active_tables)
    reachable = closure(active)
    if target in reachable:
        return None
    return Residual(
        target=target,
        closure_size=len(reachable),
        closure_digest=_tables_digest(reachable),
        authority_digest=authority_digest(active),
    )
