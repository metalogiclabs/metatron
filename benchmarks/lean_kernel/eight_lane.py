from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runtime.metatron.nucleus import Node, append, dumps, live, loads


PROBLEMS = (
    "fib", "partition", "mertens", "primecount",
    "permanent", "ca-rule110", "sha256", "polydisc",
)


@dataclass(frozen=True)
class Lane:
    problem: str
    action: str
    reason: str
    priority: int


def _add(log, kind, payload, premises=()):
    node = Node(kind, payload, premises)
    return append(log, node), node.id


def build_log():
    log = ()
    log, root = _add(log, "programme", {
        "name": "SAIR Lean Kernel Challenge Stage 1",
        "objective": "lowest kernel instruction total on all eight independent leaderboards",
    })
    problems = {}
    for problem in PROBLEMS:
        log, problems[problem] = _add(log, "problem", {"problem": problem}, (root,))

    # Fibonacci: proven champion retained; shift transfer rejected.
    log, fib_v2 = _add(log, "candidate", {
        "problem": "fib", "name": "v2-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-fib-v2-frozen",
        "commit": "9f637e976b587a1623d83be12a82522a35a95b6c",
    }, (problems["fib"],))
    log, _ = _add(log, "verification", {
        "subject": "v2-frozen", "universal": True, "canonical": True,
    }, (fib_v2,))
    log, fib_v4 = _add(log, "candidate", {
        "problem": "fib", "name": "flash-v4-shift", "repo": "heathsanchez/test",
        "branch": "lkc-flash2-fib-v4-shift",
        "commit": "8f06a3fe81476fb8d2755e290d1deb8b14fb247c",
    }, (problems["fib"],))
    log, fib_m = _add(log, "measurement", {
        "subject": "flash-v4-shift", "metric": "wall_time_full_public",
        "run_id": 35422786945, "improvement_pct_vs_champion": -1.7309719455808725,
        "tier": "local_probe",
    }, (fib_v4,))
    log, _ = _add(log, "decision", {
        "problem": "fib", "action": "NEW_REPRESENTATION_FAMILY",
        "reason": "shift transfer regressed 1.73%; retain proven champion and search a different kernel reduction spine",
    }, (fib_m,))

    # Partition: external V5 remains warranted; V12 is best verified local contender.
    log, p5 = _add(log, "candidate", {
        "problem": "partition", "name": "v5-natfold", "repo": "heathsanchez/test",
        "branch": "lkc-partition-frontier-v5",
    }, (problems["partition"],))
    log, p5v = _add(log, "verification", {
        "subject": "v5-natfold", "universal": True, "canonical": True,
    }, (p5,))
    log, p5m = _add(log, "measurement", {
        "subject": "v5-natfold", "metric": "perf_instructions",
        "cohort": "sair-playground-grouped-practice-v1-partition-14-22-32",
        "values": [396369526, 1167256227, 2982486899],
        "total": 4546112652, "tier": "external", "run_id": 198,
    }, (p5, p5v))
    log, p13 = _add(log, "candidate", {
        "problem": "partition", "name": "v13-three-compiled", "repo": "heathsanchez/test",
        "branch": "lkc-partition-three-compiled-v13",
        "commit": "ebcc890db3098f1a238c6419fc1ed9eddfcaaf2d",
        "source_sha256": "bcb6325b9d0ca5c7259b0de76d903ba5cb20e05fdb60938b5201745d00491085",
    }, (problems["partition"],))
    log, p13v = _add(log, "verification", {
        "subject": "v13-three-compiled", "universal": True, "canonical": True,
        "axioms": ["propext", "Quot.sound"], "run_id": 35660577434,
    }, (p13,))
    log, p13m = _add(log, "measurement", {
        "subject": "v13-three-compiled", "metric": "wall_seconds",
        "cohort": "frozen-local-partition", "value": 0.182697394, "tier": "local",
    }, (p13, p13v))
    log, _ = _add(log, "decision", {
        "problem": "partition", "action": "CONTINUE_VERIFIED_COMPRESSION",
        "external_champion": "v5-natfold", "staged": "v13-three-compiled",
        "reason": "V13 is universally proved and reduces the local proxy again; continue compounding before spending the next external PMU run",
    }, (p5m, p13m))

    # Mertens: bitset family refuted.
    log, m6 = _add(log, "candidate", {
        "problem": "mertens", "name": "v6-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-mertens-v6-frozen",
        "commit": "df8824794cfb1cd2764fbde1ddfe54c07957b98e",
    }, (problems["mertens"],))
    log, _ = _add(log, "verification", {
        "subject": "v6-frozen", "universal": True, "canonical": True,
    }, (m6,))
    log, m9 = _add(log, "candidate", {
        "problem": "mertens", "name": "flash-v9-bitset", "repo": "heathsanchez/test",
        "branch": "lkc-flash2-mertens-v9-bitset",
        "commit": "0e90efe068bf3ab54c1c350a03f671b3578551a3",
    }, (problems["mertens"],))
    log, m9m = _add(log, "measurement", {
        "subject": "flash-v9-bitset", "metric": "wall_time_full_public",
        "run_id": 35423028612, "improvement_pct_vs_champion": -23.301916230627384,
        "tier": "local_probe",
    }, (m9,))
    log, _ = _add(log, "decision", {
        "problem": "mertens", "action": "NEW_REPRESENTATION_FAMILY",
        "reason": "bitset family regressed 23.30%; target a summatory/quotient-block recurrence",
    }, (m9m,))

    # Primecount: fastest current probe is unproved.
    log, q3 = _add(log, "candidate", {
        "problem": "primecount", "name": "v3-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-primecount-v3-frozen",
        "commit": "45b2caf3da75be177e9571b4deff118b34f24c46",
    }, (problems["primecount"],))
    log, _ = _add(log, "verification", {
        "subject": "v3-frozen", "universal": True, "canonical": True,
    }, (q3,))
    log, q5 = _add(log, "candidate", {
        "problem": "primecount", "name": "flash-v5-bitset-probe", "repo": "heathsanchez/test",
        "branch": "lkc-flash2-primecount-v5-bitset",
        "commit": "e0b506b2276b181890fb31912b391cb748fb196e",
    }, (problems["primecount"],))
    log, q5m = _add(log, "measurement", {
        "subject": "flash-v5-bitset-probe", "metric": "wall_time_full_public",
        "run_id": 35423022766, "improvement_pct_vs_champion": 11.171794277638526,
        "tier": "local_probe",
    }, (q5,))
    log, _ = _add(log, "decision", {
        "problem": "primecount", "action": "PROVE_PROMISING_PROBE",
        "reason": "bitset sieve is 11.17% faster locally but has no universal proof; proof is prerequisite to staging or PMU",
    }, (q5m,))

    # Permanent: reverse-row probe not yet warranted.
    log, r5 = _add(log, "candidate", {
        "problem": "permanent", "name": "v5-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-permanent-v5-frozen",
        "commit": "3573e2c75d79c69344e032f154683d5fe63fe47f",
    }, (problems["permanent"],))
    log, _ = _add(log, "verification", {
        "subject": "v5-frozen", "universal": True, "canonical": True,
    }, (r5,))
    log, r6 = _add(log, "candidate", {
        "problem": "permanent", "name": "flash-v6-reverse-probe", "repo": "heathsanchez/test",
        "branch": "lkc-flash2-permanent-v6",
        "commit": "62bbb6616e9a9f8473ca84865d2f5706deaa2811",
    }, (problems["permanent"],))
    log, _ = _add(log, "decision", {
        "problem": "permanent", "action": "FIND_CHEAP_PROOF_OR_NEW_FAMILY",
        "reason": "reverse-row DFS affects scored traversal but lacks a row-permutation proof and measured warranted result",
    }, (r6,))

    # Rule110: V64 only changes non-scored fallback.
    log, c60 = _add(log, "candidate", {
        "problem": "ca-rule110", "name": "v60-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-rule110-v60-frozen",
        "commit": "9ae9e5b1d0d77a04f8f31ef56a66934e3feeff68",
    }, (problems["ca-rule110"],))
    log, _ = _add(log, "verification", {
        "subject": "v60-frozen", "universal": True, "canonical": True,
    }, (c60,))
    log, c64 = _add(log, "candidate", {
        "problem": "ca-rule110", "name": "flash-v64-generic-fallback",
        "repo": "heathsanchez/test", "branch": "lkc-flash2-rule110-v64",
        "commit": "216c0e5973e8bd6a66c80e5aa86392a8c8e3bdc9",
    }, (problems["ca-rule110"],))
    log, _ = _add(log, "decision", {
        "problem": "ca-rule110", "action": "OPTIMIZE_SCORED_2_4_8_PATHS",
        "reason": "V64 changes only fallback outside scored 2/4/8 step counts; scored unrolled paths are unchanged from V60",
    }, (c64,))

    # SHA: V24 algebra probe needs proof before it becomes a candidate.
    log, h23 = _add(log, "candidate", {
        "problem": "sha256", "name": "v23-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-sha256-v23-frozen",
        "commit": "04f7a8042210b87ad360d29eba0248bfbaff1cf1",
    }, (problems["sha256"],))
    log, _ = _add(log, "verification", {
        "subject": "v23-frozen", "universal": True, "canonical": True,
    }, (h23,))
    log, h24 = _add(log, "candidate", {
        "problem": "sha256", "name": "flash-v24-deferred-mask-probe",
        "repo": "heathsanchez/test", "branch": "lkc-flash2-sha-v24",
        "commit": "f55bae277f4d0aa01718140e5b36bdacba06934a",
    }, (problems["sha256"],))
    log, _ = _add(log, "decision", {
        "problem": "sha256", "action": "PROVE_OR_REFUTE_ALGEBRA_PROBE",
        "reason": "V24 removes intermediate masks; modular transport proof is required before staging",
    }, (h24,))

    # Polydisc: V4 is flat and proof-red.
    log, d3 = _add(log, "candidate", {
        "problem": "polydisc", "name": "v3-frozen", "repo": "heathsanchez/test",
        "branch": "lkc-polydisc-v3-frozen",
        "commit": "3daeb833823d33febe379fca909c7363d8439331",
    }, (problems["polydisc"],))
    log, _ = _add(log, "verification", {
        "subject": "v3-frozen", "universal": True, "canonical": True,
    }, (d3,))
    log, d4 = _add(log, "candidate", {
        "problem": "polydisc", "name": "flash-v4-fixed-shape", "repo": "heathsanchez/test",
        "branch": "lkc-flash2-polydisc-v4",
        "commit": "5caaeb5f83044fcdd5d35068caeaf2b4290573d8",
    }, (problems["polydisc"],))
    log, d4m = _add(log, "measurement", {
        "subject": "flash-v4-fixed-shape", "metric": "callgrind",
        "run_id": 35423038757, "improvement_pct_vs_champion": 0.01065298045975771,
        "tier": "local_probe",
    }, (d4,))
    log, _ = _add(log, "decision", {
        "problem": "polydisc", "action": "NEW_REPRESENTATION_FAMILY",
        "reason": "V4 is only 0.01065% better by Callgrind and later proof runs remain red",
    }, (d4m,))

    # Current public Contributor Network census.
    log, snap = _add(log, "external_snapshot", {
        "source": "SAIR Contributor Network", "run_id": 35659790535,
        "artifact_id": 10667450755,
        "artifact_sha256": "427ba7744a938d0c884a4bc6f67102782c1353b0cd2c5b8bbae69901b6fe73c3",
        "total_items": 2,
    }, (root,))
    counts = {
        "fib": 2, "partition": 0, "mertens": 0, "primecount": 0,
        "permanent": 0, "ca-rule110": 0, "sha256": 0, "polydisc": 0,
    }
    for problem, count in counts.items():
        log, _ = _add(log, "public_package_count", {
            "problem": problem, "count": count,
        }, (snap, problems[problem]))

    return log


def lanes(log=None):
    if log is None:
        log = build_log()
    latest = {}
    for _, node in live(log, "decision"):
        payload = node.payload
        latest[payload["problem"]] = payload

    priorities = {
        "PROVE_PROMISING_PROBE": 100,
        "CONTINUE_VERIFIED_COMPRESSION": 95,
        "PROVE_OR_REFUTE_ALGEBRA_PROBE": 90,
        "FIND_CHEAP_PROOF_OR_NEW_FAMILY": 85,
        "OPTIMIZE_SCORED_2_4_8_PATHS": 85,
        "NEW_REPRESENTATION_FAMILY": 75,
    }
    result = []
    for problem in PROBLEMS:
        decision = latest[problem]
        action = decision["action"]
        result.append(Lane(
            problem=problem,
            action=action,
            reason=decision["reason"],
            priority=priorities[action],
        ))
    return tuple(sorted(result, key=lambda x: (-x.priority, x.problem)))


def write_log(path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(build_log()))
    return path
