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
    print(f"→ Generating {config['site_name']} to {dist_path}")

    outcome = build(
        Path.cwd(),
        filename=args.filename,
        flush=args.flush,
        resources=args.resources,
    )

    if args.verbose and outcome["log"]:
        def _fmt_size(n):
            return f"{n / 1_000_000:.1f} MB" if n >= 1_000_000 else f"{round(n / 1_000)} KB"

        def _is_post_entry(entry):
            action, name = entry[0], entry[1]
            return action == "RESIZED" or (name.endswith(".html") and name[:-5].isdigit())

        post_log = [e for e in outcome["log"] if _is_post_entry(e)]
        site_log = [e for e in outcome["log"] if not _is_post_entry(e)]

        for entry in post_log:
            action, name = entry[0], entry[1]
            if action == "RESIZED" and len(entry) == 4:
                print(f"  RESIZED: {name} ({_fmt_size(entry[2])} → {_fmt_size(entry[3])})")
            elif action == "RESIZED":
                print(f"  RESIZED: {name}")
            elif len(entry) == 4:
                char_count, is_micro = entry[2], entry[3]
                suffix = f" - {char_count} characters"
                if is_micro:
                    suffix += " (micro)"
                print(f"{action}: {name}{suffix}")
            else:
                print(f"{action}: {name}")
        if post_log and site_log:
            print()
        for entry in site_log:
            print(f"{entry[0]}: {entry[1]}")

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
