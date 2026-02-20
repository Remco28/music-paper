#!/usr/bin/env python3
"""Generate a kid-friendly playability labeling pack from existing run artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class LabelRow:
    item_id: str
    run_id: str
    part_name: str
    profile: str
    source: str
    pdf_path: str


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a labeling CSV and markdown checklist for student reviewers."
    )
    parser.add_argument(
        "--runs-dir",
        default="temp/runs",
        help="Directory containing run folders with manifest.json files.",
    )
    parser.add_argument(
        "--out-dir",
        default="datasets/labeling",
        help="Directory where labeling pack files should be written.",
    )
    parser.add_argument(
        "--limit-runs",
        type=int,
        default=0,
        help="Limit number of newest runs included (0 = all).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Shuffle seed so review order is stable/reproducible.",
    )
    return parser.parse_args()


def _iter_manifests(runs_dir: Path, limit_runs: int) -> list[Path]:
    if not runs_dir.exists():
        return []
    manifests = sorted(runs_dir.glob("*/manifest.json"), key=lambda p: p.parent.name, reverse=True)
    if limit_runs > 0:
        manifests = manifests[:limit_runs]
    return manifests


def _build_rows(manifest_paths: list[Path], seed: int) -> list[LabelRow]:
    rows: list[LabelRow] = []
    for manifest_path in manifest_paths:
        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception:
            continue
        run_id = str(manifest.get("run_id") or manifest_path.parent.name)
        options = manifest.get("options") or {}
        profile = str(options.get("profile", ""))
        source = str((manifest.get("input") or {}).get("value", ""))
        for part in manifest.get("parts") or []:
            if not isinstance(part, dict):
                continue
            if str(part.get("status", "")) != "exported":
                continue
            path = str(part.get("path", ""))
            if not path:
                continue
            pdf_path = Path(path)
            if not pdf_path.exists():
                continue
            part_name = str(part.get("name", ""))
            item_id = f"{run_id}:{part_name}"
            rows.append(
                LabelRow(
                    item_id=item_id,
                    run_id=run_id,
                    part_name=part_name,
                    profile=profile,
                    source=source,
                    pdf_path=str(pdf_path),
                )
            )

    rng = random.Random(seed)
    rng.shuffle(rows)
    return rows


def _write_csv(rows: list[LabelRow], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "item_id",
                "run_id",
                "part_name",
                "profile",
                "source",
                "pdf_path",
                "student_name",
                "playable_yes_no",
                "resembles_song_1_to_5",
                "difficulty_1_to_5",
                "confidence_1_to_5",
                "notes",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "item_id": row.item_id,
                    "run_id": row.run_id,
                    "part_name": row.part_name,
                    "profile": row.profile,
                    "source": row.source,
                    "pdf_path": row.pdf_path,
                    "student_name": "",
                    "playable_yes_no": "",
                    "resembles_song_1_to_5": "",
                    "difficulty_1_to_5": "",
                    "confidence_1_to_5": "",
                    "notes": "",
                }
            )


def _write_markdown(rows: list[LabelRow], out_path: Path, csv_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# Student Labeling Packet")
    lines.append("")
    lines.append("Use this packet to quickly rate whether generated parts are usable.")
    lines.append("")
    lines.append("## Quick Rubric")
    lines.append("1. `playable_yes_no`: `yes` if a middle-schooler can read and play it after light practice.")
    lines.append("2. `resembles_song_1_to_5`: 1 = not recognizable, 5 = clearly sounds like the song.")
    lines.append("3. `difficulty_1_to_5`: 1 = very easy, 5 = too hard for class.")
    lines.append("4. `confidence_1_to_5`: 1 = guessing, 5 = very sure.")
    lines.append("")
    lines.append("Keep each rating under 30 seconds. Short notes in `notes` are enough.")
    lines.append("")
    lines.append("## Files")
    lines.append(f"- Label CSV: `{csv_path}`")
    lines.append("")
    lines.append("## Review Order")
    lines.append("")
    lines.append("| # | Item ID | Profile | Part | PDF |")
    lines.append("|---|---|---|---|---|")
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | `{row.item_id}` | `{row.profile}` | `{row.part_name}` | `{row.pdf_path}` |"
        )
    out_path.write_text("\n".join(lines) + "\n")


def main() -> int:
    args = _parse_args()
    runs_dir = Path(args.runs_dir)
    out_dir = Path(args.out_dir)
    manifest_paths = _iter_manifests(runs_dir, int(args.limit_runs))
    rows = _build_rows(manifest_paths, int(args.seed))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = out_dir / f"playability_labels_{timestamp}.csv"
    md_path = out_dir / f"labeling_packet_{timestamp}.md"
    latest_csv = out_dir / "playability_labels_latest.csv"
    latest_md = out_dir / "labeling_packet_latest.md"

    _write_csv(rows, csv_path)
    _write_markdown(rows, md_path, csv_path)
    latest_csv.write_text(csv_path.read_text())
    latest_md.write_text(md_path.read_text())

    print(f"Wrote {len(rows)} review rows")
    print(f"- {csv_path}")
    print(f"- {md_path}")
    print(f"- {latest_csv}")
    print(f"- {latest_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
