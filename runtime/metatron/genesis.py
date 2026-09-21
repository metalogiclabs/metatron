from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import IntEnum, StrEnum
from hashlib import sha256
import json

class State(IntEnum):
    ZERO=0; ONE=1; TWO=2

class Query(StrEnum):
    IS_ZERO="is_zero"; IS_ONE="is_one"

ID_TABLE=(0,1,2)
STEP_TABLE=(1,1,2)

def qeval(q, s):
    return s == (0 if q is Query.IS_ZERO else 1)

def compose(a,b):
    return tuple(b[a[i]] for i in range(3))

def closure(tables):
    k=set(tables)
    while True:
        n=k|{compose(a,b) for a in k for b in k}
        if n==k: return frozenset(k)
        k=n

def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

@dataclass(frozen=True)
class Residual:
    id:str; target:tuple; authority:str; closure:str; size:int

@dataclass(frozen=True)
class Warrant:
    id:str; subject:str; payload:str

@dataclass(frozen=True)
class Event:
    kind:str; subject:str; details:dict

class GenesisError(RuntimeError): pass
class UncertifiedResidualError(GenesisError): pass
class RevokedCapabilityError(GenesisError): pass

class Machine:
    def __init__(self):
        self.capabilities={"id":(ID_TABLE,None)}
        self.residuals={}
        self.warrants={}
        self.revoked=set()
        self.queries=[Query.IS_ZERO]
        self.relations=set()
        self.lineage=[]
        self.partition=()
        self.reclose("GENESIS")

    @classmethod
    def genesis(cls): return cls()

    def active(self):
        return {n:t for n,(t,w) in self.capabilities.items() if w is None or w not in self.revoked}

    def authority(self):
        return digest([(n,list(t),self.capabilities[n][1]) for n,t in sorted(self.active().items())])

    def certify(self,target):
        c=closure(self.active().values())
        if target in c: return None
        cd=digest([list(t) for t in sorted(c)])
        rid="residual:"+digest([list(target),self.authority(),cd])[:24]
        r=Residual(rid,target,self.authority(),cd,len(c))
        self.residuals[rid]=r
        self.lineage.append(Event("OBSTRUCTION",rid,{"target":list(target),"closure_size":len(c)}))
        return r

    def lift(self,r,name):
        if self.residuals.get(r.id)!=r or r.authority!=self.authority():
            raise UncertifiedResidualError("unissued or stale obstruction")
        c=closure(self.active().values())
        if r.target in c or r.closure!=digest([list(t) for t in sorted(c)]):
            raise UncertifiedResidualError("obstruction no longer current")
        self.lineage.append(Event("LIFT",name,{"residual":r.id,"added_generators":1}))
        return (name,r.target,r.id)

    def verify(self,candidate):
        name,table,rid=candidate
        if self.residuals.get(rid) is None or self.residuals[rid].target!=table:
            raise UncertifiedResidualError("candidate is not obstruction-bound")
        payload=digest([name,list(table),rid])
        w=Warrant("warrant:"+payload[:24],name,payload)
        self.warrants[w.id]=w
        self.lineage.append(Event("VERIFY",name,{"warrant":w.id}))
        return w

    def promote(self,candidate,w):
        name,table,rid=candidate
        if self.warrants.get(w.id)!=w or w.payload!=digest([name,list(table),rid]):
            raise GenesisError("invalid warrant")
        self.capabilities[name]=(table,w.id)
        self.lineage.append(Event("PROMOTE",name,{"warrant":w.id}))
        self.reclose("PROMOTION")

    def execute(self,name,state):
        table,w=self.capabilities[name]
        if w in self.revoked: raise RevokedCapabilityError(name)
        return State(table[int(state)])

    def behavior_partition(self):
        cont=sorted(closure(self.active().values()))
        groups={}
        for s in State:
            sig=tuple(qeval(q,t[int(s)]) for q in self.queries for t in cont)
            groups.setdefault(sig,[]).append(int(s))
        return tuple(sorted((tuple(v) for v in groups.values()),key=lambda b:b[0]))

    def reclose(self,reason):
        self.relations=set()
        a=self.active()
        if "step" in a and compose(a["step"],a["step"])==a["step"]:
            self.relations.add((("step","step"),"step"))
        self.partition=self.behavior_partition()
        self.lineage.append(Event("RECLOSE",reason,{"partition":[list(b) for b in self.partition]}))

    def protect(self,q):
        if q in self.queries: return
        before=self.partition
        witness=None
        for block in before:
            for i,a in enumerate(block):
                for b in block[i+1:]:
                    if any(qeval(q,t[a])!=qeval(q,t[b]) for t in closure(self.active().values())):
                        witness=(a,b); break
                if witness: break
            if witness: break
        self.queries.append(q)
        self.reclose("QUERY_CHANGE")
        if len(self.partition)>len(before):
            self.lineage.append(Event("REPRESENTATION_LIFT",q.value,{"witness":list(witness),"before":[list(b) for b in before],"after":[list(b) for b in self.partition]}))

    def revoke(self,wid):
        if wid not in self.warrants: raise KeyError(wid)
        self.revoked.add(wid)
        self.lineage.append(Event("REVOKE",self.warrants[wid].subject,{"warrant":wid}))
        self.reclose("REVOCATION")

    def dump(self):
        return json.dumps({
            "capabilities":{n:[list(t),w] for n,(t,w) in sorted(self.capabilities.items())},
            "residuals":{k:{**asdict(v),"target":list(v.target)} for k,v in sorted(self.residuals.items())},
            "warrants":{k:asdict(v) for k,v in sorted(self.warrants.items())},
            "revoked":sorted(self.revoked),
            "queries":[q.value for q in self.queries],
            "lineage":[asdict(e) for e in self.lineage],
            "partition":[list(b) for b in self.partition],
        },sort_keys=True,separators=(",",":"))


    @classmethod
    def load(cls, payload):
        data=json.loads(payload)
        machine=cls.__new__(cls)
        machine.capabilities={
            name:(tuple(item[0]),item[1])
            for name,item in data["capabilities"].items()
        }
        machine.residuals={
            ident:Residual(
                item["id"],tuple(item["target"]),item["authority"],
                item["closure"],item["size"]
            )
            for ident,item in data["residuals"].items()
        }
        machine.warrants={
            ident:Warrant(item["id"],item["subject"],item["payload"])
            for ident,item in data["warrants"].items()
        }
        machine.revoked=set(data["revoked"])
        machine.queries=[Query(value) for value in data["queries"]]
        machine.lineage=[
            Event(item["kind"],item["subject"],item["details"])
            for item in data["lineage"]
        ]
        machine.partition=tuple(tuple(block) for block in data["partition"])
        machine.relations=set()
        active=machine.active()
        if "step" in active and compose(active["step"],active["step"])==active["step"]:
            machine.relations.add((("step","step"),"step"))
        if machine.behavior_partition()!=machine.partition:
            raise GenesisError("serialized live view is semantically invalid")
        return machine
