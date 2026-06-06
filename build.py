#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from magnetizer.builder import build
from magnetizer.config import load_config
from magnetizer.publisher import publish


def main():
    parser = argparse.ArgumentParser(
        prog="build.py",
        description="Generate static web pages from the content in ./content.",
    )
    parser.add_argument("filename", nargs="?", metavar="FILENAME")
    parser.add_argument("--flush", action="store_true")
    parser.add_argument("--resources", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.filename and any([args.flush, args.resources, args.push]):
        print("Error: FILENAME cannot be used together with other options.", file=sys.stderr)
        sys.exit(1)

    config = load_config(Path.cwd() / "config.yaml")
    dist_path = (Path.cwd() / "dist").resolve()
    print(f"Generating {config['site_title']} to {dist_path}")

    outcome = build(
        Path.cwd(),
        filename=args.filename,
        flush=args.flush,
        resources=args.resources,
    )

    if args.verbose:
        for action, name in outcome["log"]:
            print(f"{action}: {name}")

    if outcome["log"]:
        print(
            f"{outcome['created']} post(s) created, "
            f"{outcome['updated']} post(s) updated, "
            f"{outcome['deleted']} post(s) deleted"
        )
    else:
        print("No changes detected.")

    if args.push:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        publish(Path.cwd() / "dist", timestamp)


if __name__ == "__main__":
    main()
