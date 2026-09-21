import json

from .machine import Machine
from .model import (
    Capability,
    Certificate,
    LineageEvent,
    Query,
    Relation,
    ResidualCertificate,
)


def dump_machine(machine: Machine) -> str:
    data = {
        "schema_version": 1,
        "active_partition": [list(block) for block in machine.active_partition],
        "capabilities": {
            name: {
                "table": list(cap.table),
                "residual_certificate_id": cap.residual_certificate_id,
                "certificate_id": cap.certificate_id,
            }
            for name, cap in sorted(machine.capabilities.items())
        },
        "certificates": {
            ident: {
                "kind": cert.kind,
                "subject_digest": cert.subject_digest,
            }
            for ident, cert in sorted(machine.certificates.items())
        },
        "residual_certificates": {
            ident: {
                "target": list(cert.target),
                "target_digest": cert.target_digest,
                "closure_size": cert.closure_size,
                "closure_digest": cert.closure_digest,
                "authority_digest": cert.authority_digest,
            }
            for ident, cert in sorted(machine.residual_certificates.items())
        },
        "next_residual_serial": machine._next_residual_serial,
        "lineage": [
            {"kind": event.kind, "payload": event.payload}
            for event in machine.lineage
        ],
        "live_certificates": sorted(machine.live_certificates),
        "revoked_certificates": sorted(machine.revoked_certificates),
        "queries": [query.value for query in machine.queries],
        "relations": [
            {
                "left": list(relation.left),
                "right": relation.right,
                "certificate_id": cert_id,
            }
            for relation, cert_id in machine._relations
        ],
    }
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def load_machine(payload: str) -> Machine:
    data = json.loads(payload)
    if data.get("schema_version") != 1:
        raise ValueError("unsupported machine schema")

    machine = Machine()
    machine.active_partition = tuple(tuple(block) for block in data["active_partition"])
    machine.capabilities = {
        name: Capability(
            name=name,
            table=tuple(item["table"]),
            residual_certificate_id=item["residual_certificate_id"],
            certificate_id=item["certificate_id"],
        )
        for name, item in data["capabilities"].items()
    }
    machine.certificates = {
        ident: Certificate(
            id=ident,
            kind=item["kind"],
            subject_digest=item["subject_digest"],
        )
        for ident, item in data["certificates"].items()
    }
    machine.residual_certificates = {
        ident: ResidualCertificate(
            id=ident,
            target=tuple(item["target"]),
            target_digest=item["target_digest"],
            closure_size=item["closure_size"],
            closure_digest=item["closure_digest"],
            authority_digest=item["authority_digest"],
        )
        for ident, item in data["residual_certificates"].items()
    }
    machine._next_residual_serial = data["next_residual_serial"]
    machine.lineage = [
        LineageEvent(item["kind"], item["payload"])
        for item in data["lineage"]
    ]
    machine.live_certificates = set(data["live_certificates"])
    machine.revoked_certificates = set(data["revoked_certificates"])
    machine.queries = [Query(value) for value in data["queries"]]
    machine._relations = [
        (
            Relation(tuple(item["left"]), item["right"]),
            item["certificate_id"],
        )
        for item in data["relations"]
    ]
    return machine
