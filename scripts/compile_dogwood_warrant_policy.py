#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from runtime.metatron.dogwood import write_bundle
from runtime.metatron.nucleus import loads


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile a canonical Metatron warrant log to Dogwood Use policies."
    )
    parser.add_argument("log", type=Path, help="canonical Metatron JSONL warrant log")
    parser.add_argument("--out", type=Path, required=True, help="output bundle directory")
    parser.add_argument(
        "--window",
        default="3650d",
        help="Dogwood bounded history window (default: 3650d)",
    )
    args = parser.parse_args()

    log = loads(args.log.read_text())
    manifest = write_bundle(log, args.out, window=args.window)
    print(args.out / "policy.dw")
    print(f"nodes={len(manifest['node_ids'])}")
    print(f"live={len(manifest['current_live_ids'])}")
    print(f"policy_sha256={manifest['policy_sha256']}")


if __name__ == "__main__":
    main()
