from dataclasses import replace
from hashlib import sha256

from .model import (
    ID_TABLE,
    Capability,
    Certificate,
    LineageEvent,
    Relation,
    Residual,
    ResidualCertificate,
    Query,
    State,
    Table,
    compose,
    eval_query,
    table_digest,
)

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

class NonCongruentProjectionError(RuntimeError):
    pass

class UncertifiedResidualError(RuntimeError):
    pass

class UnverifiedCertificateError(RuntimeError):
    pass

class UnverifiedRelationError(RuntimeError):
    pass

class UnknownCapabilityError(KeyError):
    pass

def relation_digest(left, right, table) -> str:
    payload = repr((tuple(left), right, tuple(table))).encode()
    return sha256(payload).hexdigest()

def partition_for_queries(queries):
    groups = {}
    for state in State:
        signature = tuple(eval_query(query, state) for query in queries)
        groups.setdefault(signature, []).append(int(state))
    return tuple(tuple(block) for block in sorted(groups.values(), key=lambda xs: xs[0]))

def project_table(table, partition):
    class_of = {member: index for index, block in enumerate(partition) for member in block}
    projected = []
    for block in partition:
        targets = {class_of[table[source]] for source in block}
        if len(targets) != 1:
            raise NonCongruentProjectionError(f"table {table} splits active class {block}")
        projected.append(next(iter(targets)))
    return tuple(projected)

class Machine:
    def __init__(self) -> None:
        self.lineage = []
        self.capabilities = {}
        self.certificates = {}
        self.residual_certificates = {}
        self.live_certificates = set()
        self.revoked_certificates = set()
        self._relations = []
        self._next_residual_serial = 1
        self.queries: list[Query] = []
        self.active_partition: tuple[tuple[int, ...], ...] = ((0,), (1,), (2,))
        self.queries = []
        self.active_partition = ((0,), (1,), (2,))

    @classmethod
    def genesis(cls):
        machine = cls()
        cert = Certificate("genesis:id", "capability", table_digest(ID_TABLE))
        machine.certificates[cert.id] = cert
        machine.live_certificates.add(cert.id)
        machine.capabilities["id"] = Capability("id", ID_TABLE, None, cert.id)
        machine.lineage.append(LineageEvent("GENESIS", {"capability": "id"}))
        return machine

    def active_capability_names(self):
        return tuple(sorted(name for name, cap in self.capabilities.items()
            if cap.certificate_id in self.live_certificates
            and cap.certificate_id not in self.revoked_certificates))

    def active_tables(self):
        return {self.capabilities[name].table for name in self.active_capability_names()}

    def certify_target(self, target):
        residual = certify_no_resolution(self.active_tables(), target)
        if residual is None:
            return None
        serial = self._next_residual_serial
        self._next_residual_serial += 1
        cert = ResidualCertificate(
            f"residual:{serial}:{table_digest(target)[:16]}",
            target, table_digest(target), residual.closure_size,
            residual.closure_digest, residual.authority_digest,
        )
        self.residual_certificates[cert.id] = cert
        self.lineage.append(LineageEvent("RESIDUAL", {
            "certificate": cert.id, "target": list(target),
            "closure_size": cert.closure_size,
            "closure_digest": cert.closure_digest,
            "authority_digest": cert.authority_digest,
        }))
        return cert

    def free_extend(self, residual_cert, name):
        stored = self.residual_certificates.get(residual_cert.id)
        if stored is None or stored != residual_cert:
            raise UncertifiedResidualError("residual certificate was not issued by this machine")
        current = certify_no_resolution(self.active_tables(), stored.target)
        if current is None:
            raise UncertifiedResidualError("residual is no longer obstructed")
        if (current.closure_digest != stored.closure_digest
            or current.authority_digest != stored.authority_digest
            or table_digest(stored.target) != stored.target_digest):
            raise UncertifiedResidualError("residual certificate is stale")
        candidate = Capability(name, stored.target, stored.id, None)
        self.lineage.append(LineageEvent("CANDIDATE", {"name": name, "residual_certificate": stored.id}))
        return candidate

    def verify_candidate(self, candidate):
        stored_residual = self.residual_certificates.get(candidate.residual_certificate_id)
        if stored_residual is None:
            raise UncertifiedResidualError("candidate lacks an issued residual")
        if table_digest(candidate.table) != stored_residual.target_digest:
            raise UnverifiedCertificateError("candidate does not match frozen residual target")
        cert = Certificate(
            f"cert:{candidate.name}:{table_digest(candidate.table)[:16]}",
            "capability", table_digest(candidate.table),
        )
        self.certificates[cert.id] = cert
        self.live_certificates.add(cert.id)
        self.lineage.append(LineageEvent("VERIFY", {
            "certificate": cert.id, "capability": candidate.name,
            "residual_certificate": stored_residual.id,
        }))
        return cert

    def _require_stored_certificate(self, certificate):
        stored = self.certificates.get(certificate.id)
        if stored is None or stored != certificate:
            raise UnverifiedCertificateError("certificate object does not match persisted warrant")
        return stored

    def promote(self, candidate, certificate):
        stored = self._require_stored_certificate(certificate)
        if stored.id not in self.live_certificates:
            raise UnverifiedCertificateError("certificate is not live")
        if stored.kind != "capability":
            raise UnverifiedCertificateError("certificate is not a capability warrant")
        if stored.subject_digest != table_digest(candidate.table):
            raise UnverifiedCertificateError("certificate does not warrant candidate")
        self.capabilities[candidate.name] = replace(candidate, certificate_id=stored.id)
        self.lineage.append(LineageEvent("PROMOTE", {"capability": candidate.name, "certificate": stored.id}))

    def _compose_names(self, names):
        table = ID_TABLE
        for name in names:
            try:
                capability = self.capabilities[name]
            except KeyError as exc:
                raise UnknownCapabilityError(name) from exc
            table = compose(table, capability.table)
        return table

    def propose_relation(self, left, right):
        return Relation(tuple(left), right)

    def verify_relation(self, left, right):
        relation = Relation(tuple(left), right)
        left_table = self._compose_names(relation.left)
        right_table = self._compose_names((right,))
        if left_table != right_table:
            raise ValueError("relation is not extensionally valid")
        digest = relation_digest(relation.left, relation.right, left_table)
        cert = Certificate(f"cert:relation:{digest[:16]}", "relation", digest)
        self.certificates[cert.id] = cert
        self.live_certificates.add(cert.id)
        self.lineage.append(LineageEvent("VERIFY_RELATION", {
            "left": list(relation.left), "right": right, "certificate": cert.id,
        }))
        return relation, cert

    def install_relation(self, relation, certificate):
        if certificate is None:
            raise UnverifiedRelationError("relation lacks warrant")
        try:
            stored = self._require_stored_certificate(certificate)
        except UnverifiedCertificateError as exc:
            raise UnverifiedRelationError(str(exc)) from exc
        left_table = self._compose_names(relation.left)
        expected = relation_digest(relation.left, relation.right, left_table)
        if (stored.id not in self.live_certificates
            or stored.kind != "relation"
            or stored.subject_digest != expected):
            raise UnverifiedRelationError("certificate does not warrant this relation")
        self._relations.append((relation, stored.id))
        self.lineage.append(LineageEvent("INSTALL_RELATION", {
            "left": list(relation.left), "right": relation.right, "certificate": stored.id,
        }))

    def relations(self):
        return tuple((relation.left, relation.right) for relation, _ in self._relations)

    def set_queries(self, queries):
        self.queries = list(dict.fromkeys(queries))
        self.lineage.append(LineageEvent("SET_QUERIES", {"queries": [q.value for q in self.queries]}))

    def project(self):
        old = self.active_partition
        new = partition_for_queries(self.queries)
        for name in self.active_capability_names():
            project_table(self.capabilities[name].table, new)
        self.active_partition = new
        kind = "REGROW" if len(new) > len(old) else "PROJECT"
        self.lineage.append(LineageEvent(kind, {"partition": [list(block) for block in new]}))

    def execute(self, name, state):
        try:
            capability = self.capabilities[name]
        except KeyError as exc:
            raise UnknownCapabilityError(name) from exc
        if capability.certificate_id not in self.live_certificates:
            raise UnverifiedCertificateError("capability certificate is not live")
        if capability.certificate_id in self.revoked_certificates:
            raise ValueError("capability certificate is revoked")
        return State(capability.table[int(state)])
