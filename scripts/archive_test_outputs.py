#!/usr/bin/env python3
"""Move test run artifacts into dedicated testing folders."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_PREFIXES = [
    "cheers_",
    "laufey_recheck_",
    "manual_recheck_",
    "quality_compare_",
    "relabel_check_",
    "simplify_profile_test_",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive test outputs into outputs/testing and temp/runs/testing."
    )
    parser.add_argument(
        "--prefix",
        action="append",
        dest="prefixes",
        default=[],
        help="Run-id prefix to archive (can be repeated).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually move folders. Without this flag, only prints planned moves.",
    )
    return parser.parse_args()


def list_matching_dirs(root: Path, prefixes: list[str]) -> list[Path]:
    if not root.exists():
        return []
    matches: list[Path] = []
    for entry in sorted(root.iterdir(), key=lambda p: p.name):
        if not entry.is_dir():
            continue
        if entry.name == "testing":
            continue
        if any(entry.name.startswith(prefix) for prefix in prefixes):
            matches.append(entry)
    return matches


def move_dirs(items: list[Path], dest_root: Path, apply: bool) -> list[str]:
    actions: list[str] = []
    dest_root.mkdir(parents=True, exist_ok=True)
    for source in items:
        target = dest_root / source.name
        if target.exists():
            actions.append(f"SKIP exists: {source} -> {target}")
            continue
        actions.append(f"MOVE: {source} -> {target}")
        if apply:
            shutil.move(str(source), str(target))
    return actions


def main() -> int:
    args = parse_args()
    prefixes = args.prefixes or DEFAULT_PREFIXES

    output_root = Path("outputs")
    output_testing = output_root / "testing"
    runs_root = Path("temp/runs")
    runs_testing = runs_root / "testing"

    output_matches = list_matching_dirs(output_root, prefixes)
    run_matches = list_matching_dirs(runs_root, prefixes)

    output_actions = move_dirs(output_matches, output_testing, args.apply)
    run_actions = move_dirs(run_matches, runs_testing, args.apply)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{mode}] prefixes={prefixes}")
    print("Outputs:")
    for line in output_actions:
        print(f"  {line}")
    if not output_actions:
        print("  (no matches)")
    print("Temp runs:")
    for line in run_actions:
        print(f"  {line}")
    if not run_actions:
        print("  (no matches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
