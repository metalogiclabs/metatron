from __future__ import annotations

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
from .nucleus import Node, WarrantGraph


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


class RevokedCapabilityError(RuntimeError):
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
    class_of = {
        member: index
        for index, block in enumerate(partition)
        for member in block
    }
    projected = []
    for block in partition:
        targets = {class_of[table[source]] for source in block}
        if len(targets) != 1:
            raise NonCongruentProjectionError(
                f"table {table} splits active class {block}"
            )
        projected.append(next(iter(targets)))
    return tuple(projected)


class Machine:
    """Compatibility facade over the minimal append-only warrant graph.

    The graph is the only authoritative mutable state. Legacy dictionaries,
    certificate sets, lineage, relations, queries and projection state are
    derived views retained only so the qualified V0 API keeps working.
    """

    def __init__(self, graph: WarrantGraph | None = None) -> None:
        self.graph = graph if graph is not None else WarrantGraph()

    @classmethod
    def genesis(cls):
        machine = cls()
        cert = Certificate("genesis:id", "capability", table_digest(ID_TABLE))
        cert_node = machine._append_certificate(cert)
        machine.graph.append(Node(
            "capability",
            {
                "name": "id",
                "table": list(ID_TABLE),
                "certificate_id": cert.id,
                "residual_certificate_id": None,
                "origin": "genesis",
            },
            (cert_node,),
        ))
        return machine

    def _nodes(self, kind: str | None = None, *, live: bool = False):
        if live:
            return self.graph.live(kind)
        out = []
        for node_id in self.graph.ids:
            node = self.graph[node_id]
            if kind is None or node.kind == kind:
                out.append((node_id, node))
        return tuple(out)

    def _find_by_legacy_id(self, kind: str, legacy_id: str, *, live=False):
        for node_id, node in self._nodes(kind, live=live):
            if node.payload.get("legacy_id") == legacy_id:
                return node_id, node
        return None

    def _append_certificate(self, cert: Certificate, premises=()):
        return self.graph.append(Node(
            "verification",
            {
                "legacy_id": cert.id,
                "verification_kind": cert.kind,
                "subject_digest": cert.subject_digest,
            },
            tuple(premises),
        ))

    def _capability_node(self, name: str, *, live=False):
        found = None
        for item in self._nodes("capability", live=live):
            if item[1].payload["name"] == name:
                found = item
        return found

    @property
    def capabilities(self):
        result = {}
        for _, node in self._nodes("capability"):
            payload = node.payload
            name = str(payload["name"])
            result[name] = Capability(
                name=name,
                table=tuple(payload["table"]),
                residual_certificate_id=payload.get("residual_certificate_id"),
                certificate_id=payload.get("certificate_id"),
            )
        return result

    @property
    def certificates(self):
        result = {}
        for _, node in self._nodes("verification"):
            payload = node.payload
            ident = str(payload["legacy_id"])
            result[ident] = Certificate(
                ident,
                str(payload["verification_kind"]),
                str(payload["subject_digest"]),
            )
        return result

    @property
    def residual_certificates(self):
        result = {}
        for _, node in self._nodes("residual"):
            payload = node.payload
            ident = str(payload["legacy_id"])
            result[ident] = ResidualCertificate(
                id=ident,
                target=tuple(payload["target"]),
                target_digest=str(payload["target_digest"]),
                closure_size=int(payload["closure_size"]),
                closure_digest=str(payload["closure_digest"]),
                authority_digest=str(payload["authority_digest"]),
            )
        return result

    @property
    def live_certificates(self):
        return {
            str(node.payload["legacy_id"])
            for _, node in self._nodes("verification", live=True)
        }

    @property
    def revoked_certificates(self):
        revoked = set()
        for _, node in self._nodes("revoke"):
            target = str(node.payload["target"])
            if target not in self.graph:
                continue
            target_node = self.graph[target]
            if target_node.kind == "verification":
                revoked.add(str(target_node.payload["legacy_id"]))
        return revoked

    @property
    def _next_residual_serial(self):
        return 1 + len(self._nodes("residual"))

    @property
    def queries(self):
        latest = []
        for _, node in self._nodes("query-set"):
            latest = [Query(value) for value in node.payload["queries"]]
        return latest

    @property
    def active_partition(self):
        latest = ((0,), (1,), (2,))
        for _, node in self._nodes("projection"):
            latest = tuple(tuple(block) for block in node.payload["partition"])
        return latest

    @property
    def lineage(self):
        events = []
        for _, node in self._nodes():
            p = node.payload
            if node.kind == "capability":
                if p.get("origin") == "genesis":
                    events.append(LineageEvent("GENESIS", {"capability": p["name"]}))
                elif p.get("origin") == "promotion":
                    events.append(LineageEvent(
                        "PROMOTE",
                        {
                            "capability": p["name"],
                            "certificate": p["certificate_id"],
                        },
                    ))
            elif node.kind == "residual":
                events.append(LineageEvent(
                    "RESIDUAL",
                    {
                        "certificate": p["legacy_id"],
                        "target": list(p["target"]),
                        "closure_size": p["closure_size"],
                        "closure_digest": p["closure_digest"],
                        "authority_digest": p["authority_digest"],
                    },
                ))
            elif node.kind == "candidate":
                events.append(LineageEvent(
                    "CANDIDATE",
                    {
                        "name": p["name"],
                        "residual_certificate": p["residual_certificate_id"],
                    },
                ))
            elif node.kind == "verification":
                scope = p.get("scope")
                if scope == "candidate":
                    events.append(LineageEvent(
                        "VERIFY",
                        {
                            "certificate": p["legacy_id"],
                            "capability": p["capability"],
                            "residual_certificate": p["residual_certificate_id"],
                        },
                    ))
                elif scope == "relation":
                    events.append(LineageEvent(
                        "VERIFY_RELATION",
                        {
                            "left": list(p["left"]),
                            "right": p["right"],
                            "certificate": p["legacy_id"],
                        },
                    ))
            elif node.kind == "relation":
                events.append(LineageEvent(
                    "INSTALL_RELATION",
                    {
                        "left": list(p["left"]),
                        "right": p["right"],
                        "certificate": p["certificate_id"],
                    },
                ))
            elif node.kind == "query-set":
                events.append(LineageEvent(
                    "SET_QUERIES",
                    {"queries": list(p["queries"])},
                ))
            elif node.kind == "projection":
                events.append(LineageEvent(
                    str(p["mode"]),
                    {"partition": [list(block) for block in p["partition"]]},
                ))
            elif node.kind == "revoke":
                events.append(LineageEvent(
                    "REVOKE",
                    {"certificate": p["legacy_certificate_id"]},
                ))
        return events

    def active_capability_names(self):
        return tuple(sorted(
            str(node.payload["name"])
            for _, node in self._nodes("capability", live=True)
        ))

    def active_tables(self):
        return {
            tuple(node.payload["table"])
            for _, node in self._nodes("capability", live=True)
        }

    def certify_target(self, target):
        residual = certify_no_resolution(self.active_tables(), target)
        if residual is None:
            return None

        serial = self._next_residual_serial
        ident = f"residual:{serial}:{table_digest(target)[:16]}"
        cert = ResidualCertificate(
            ident,
            target,
            table_digest(target),
            residual.closure_size,
            residual.closure_digest,
            residual.authority_digest,
        )
        premises = tuple(node_id for node_id, _ in self._nodes("capability", live=True))
        self.graph.append(Node(
            "residual",
            {
                "legacy_id": cert.id,
                "target": list(cert.target),
                "target_digest": cert.target_digest,
                "closure_size": cert.closure_size,
                "closure_digest": cert.closure_digest,
                "authority_digest": cert.authority_digest,
            },
            premises,
        ))
        return cert

    def free_extend(self, residual_cert, name):
        found = self._find_by_legacy_id("residual", residual_cert.id, live=True)
        if found is None:
            raise UncertifiedResidualError(
                "residual certificate was not issued by this machine"
            )
        residual_node_id, residual_node = found
        p = residual_node.payload
        stored = self.residual_certificates[residual_cert.id]
        if stored != residual_cert:
            raise UncertifiedResidualError(
                "residual certificate was not issued by this machine"
            )

        current = certify_no_resolution(self.active_tables(), stored.target)
        if current is None:
            raise UncertifiedResidualError("residual is no longer obstructed")
        if (
            current.closure_digest != stored.closure_digest
            or current.authority_digest != stored.authority_digest
            or table_digest(stored.target) != stored.target_digest
        ):
            raise UncertifiedResidualError("residual certificate is stale")

        candidate = Capability(name, stored.target, stored.id, None)
        self.graph.append(Node(
            "candidate",
            {
                "name": name,
                "table": list(candidate.table),
                "residual_certificate_id": stored.id,
            },
            (residual_node_id,),
        ))
        return candidate

    def verify_candidate(self, candidate):
        found = self._find_by_legacy_id(
            "residual",
            candidate.residual_certificate_id,
            live=True,
        )
        if found is None:
            raise UncertifiedResidualError("candidate lacks an issued residual")
        residual_node_id, _ = found
        stored_residual = self.residual_certificates[candidate.residual_certificate_id]
        if table_digest(candidate.table) != stored_residual.target_digest:
            raise UnverifiedCertificateError(
                "candidate does not match frozen residual target"
            )

        candidate_node = None
        for node_id, node in self._nodes("candidate", live=True):
            if (
                node.payload["name"] == candidate.name
                and tuple(node.payload["table"]) == candidate.table
                and node.payload["residual_certificate_id"]
                == candidate.residual_certificate_id
            ):
                candidate_node = node_id
        if candidate_node is None:
            raise UncertifiedResidualError("candidate was not derived by free extension")

        cert = Certificate(
            f"cert:{candidate.name}:{table_digest(candidate.table)[:16]}",
            "capability",
            table_digest(candidate.table),
        )
        self.graph.append(Node(
            "verification",
            {
                "legacy_id": cert.id,
                "verification_kind": cert.kind,
                "subject_digest": cert.subject_digest,
                "scope": "candidate",
                "capability": candidate.name,
                "residual_certificate_id": stored_residual.id,
            },
            (residual_node_id, candidate_node),
        ))
        return cert

    def _require_stored_certificate(self, certificate, *, live=True):
        found = self._find_by_legacy_id("verification", certificate.id, live=live)
        if found is None:
            raise UnverifiedCertificateError(
                "certificate object does not match persisted warrant"
            )
        _, node = found
        stored = Certificate(
            str(node.payload["legacy_id"]),
            str(node.payload["verification_kind"]),
            str(node.payload["subject_digest"]),
        )
        if stored != certificate:
            raise UnverifiedCertificateError(
                "certificate object does not match persisted warrant"
            )
        return found, stored

    def promote(self, candidate, certificate):
        (cert_node_id, _), stored = self._require_stored_certificate(certificate)
        if stored.kind != "capability":
            raise UnverifiedCertificateError(
                "certificate is not a capability warrant"
            )
        if stored.subject_digest != table_digest(candidate.table):
            raise UnverifiedCertificateError("certificate does not warrant candidate")

        candidate_node = None
        for node_id, node in self._nodes("candidate", live=True):
            if (
                node.payload["name"] == candidate.name
                and tuple(node.payload["table"]) == candidate.table
                and node.payload["residual_certificate_id"]
                == candidate.residual_certificate_id
            ):
                candidate_node = node_id
        if candidate_node is None:
            raise UnverifiedCertificateError("candidate is not live")

        self.graph.append(Node(
            "capability",
            {
                "name": candidate.name,
                "table": list(candidate.table),
                "residual_certificate_id": candidate.residual_certificate_id,
                "certificate_id": stored.id,
                "origin": "promotion",
            },
            (candidate_node, cert_node_id),
        ))

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

        capability_nodes = []
        for name in (*relation.left, relation.right):
            found = self._capability_node(name, live=True)
            if found is None:
                raise UnknownCapabilityError(name)
            if found[0] not in capability_nodes:
                capability_nodes.append(found[0])

        digest = relation_digest(relation.left, relation.right, left_table)
        cert = Certificate(
            f"cert:relation:{digest[:16]}",
            "relation",
            digest,
        )
        self.graph.append(Node(
            "verification",
            {
                "legacy_id": cert.id,
                "verification_kind": cert.kind,
                "subject_digest": cert.subject_digest,
                "scope": "relation",
                "left": list(relation.left),
                "right": relation.right,
            },
            tuple(capability_nodes),
        ))
        return relation, cert

    def install_relation(self, relation, certificate):
        if certificate is None:
            raise UnverifiedRelationError("relation lacks warrant")
        try:
            (cert_node_id, _), stored = self._require_stored_certificate(certificate)
        except UnverifiedCertificateError as exc:
            raise UnverifiedRelationError(str(exc)) from exc

        left_table = self._compose_names(relation.left)
        expected = relation_digest(relation.left, relation.right, left_table)
        if stored.kind != "relation" or stored.subject_digest != expected:
            raise UnverifiedRelationError(
                "certificate does not warrant this relation"
            )

        self.graph.append(Node(
            "relation",
            {
                "left": list(relation.left),
                "right": relation.right,
                "certificate_id": stored.id,
            },
            (cert_node_id,),
        ))

    def relations(self):
        return tuple(
            (tuple(node.payload["left"]), str(node.payload["right"]))
            for _, node in self._nodes("relation")
        )

    def set_queries(self, queries):
        values = [q.value for q in dict.fromkeys(queries)]
        self.graph.append(Node("query-set", {"queries": values}))

    def project(self):
        old = self.active_partition
        new = partition_for_queries(self.queries)
        for name in self.active_capability_names():
            project_table(self.capabilities[name].table, new)

        query_nodes = self._nodes("query-set")
        premises = (query_nodes[-1][0],) if query_nodes else ()
        mode = "REGROW" if len(new) > len(old) else "PROJECT"
        self.graph.append(Node(
            "projection",
            {
                "mode": mode,
                "partition": [list(block) for block in new],
            },
            premises,
        ))

    def revoke(self, certificate_id):
        found = self._find_by_legacy_id("verification", certificate_id, live=True)
        if found is None:
            raise ValueError("cannot revoke unknown certificate")
        target_node_id, _ = found
        self.graph.append(Node(
            "revoke",
            {
                "target": target_node_id,
                "legacy_certificate_id": certificate_id,
            },
        ))

    def execute(self, name, state):
        historical = self._capability_node(name)
        if historical is None:
            raise UnknownCapabilityError(name)
        live = self._capability_node(name, live=True)
        if live is None:
            certificate_id = historical[1].payload.get("certificate_id")
            if certificate_id in self.revoked_certificates:
                raise RevokedCapabilityError(name)
            raise UnverifiedCertificateError(
                "capability certificate is not live"
            )
        return State(int(live[1].payload["table"][int(state)]))
