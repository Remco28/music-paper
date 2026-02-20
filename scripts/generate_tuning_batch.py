#!/usr/bin/env python3
"""Create a tuning round manifest from existing successful run manifests."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import APP_VERSION


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate tuning round manifest from run manifests.")
    parser.add_argument("--runs-dir", default="temp/runs", help="Path containing run folders.")
    parser.add_argument("--out-root", default="datasets/tuning_rounds", help="Round output root.")
    parser.add_argument("--round-id", default="", help="Optional explicit round id.")
    parser.add_argument(
        "--run-id",
        action="append",
        default=[],
        help="Run ID to include (can be repeated). If omitted, uses newest successful runs.",
    )
    parser.add_argument(
        "--limit-runs",
        type=int,
        default=2,
        help="When --run-id is omitted, include this many newest successful runs.",
    )
    return parser.parse_args()


def _load_manifest(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _collect_run_ids(runs_dir: Path, explicit_ids: list[str], limit_runs: int) -> list[str]:
    if explicit_ids:
        return explicit_ids
    candidates: list[str] = []
    for manifest_path in sorted(runs_dir.glob("*/manifest.json"), key=lambda p: p.parent.name, reverse=True):
        data = _load_manifest(manifest_path)
        if not data:
            continue
        outcome = data.get("outcome") or {}
        if outcome.get("success") is not True:
            continue
        candidates.append(str(data.get("run_id") or manifest_path.parent.name))
        if len(candidates) >= max(1, limit_runs):
            break
    return candidates


def main() -> int:
    args = _parse_args()
    runs_dir = Path(args.runs_dir)
    out_root = Path(args.out_root)

    run_ids = _collect_run_ids(runs_dir, list(args.run_id), int(args.limit_runs))
    if not run_ids:
        raise SystemExit("No candidate runs found. Provide --run-id or create successful runs first.")

    round_id = args.round_id.strip() or f"round_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    round_dir = out_root / round_id
    round_dir.mkdir(parents=True, exist_ok=True)

    samples: list[dict] = []
    sample_index = 1
    for run_id in run_ids:
        manifest_path = runs_dir / run_id / "manifest.json"
        data = _load_manifest(manifest_path)
        if not data:
            continue
        options = data.get("options") or {}
        for part in data.get("parts") or []:
            if not isinstance(part, dict):
                continue
            if str(part.get("status", "")) != "exported":
                continue
            pdf_path = str(part.get("path", ""))
            if not pdf_path or not Path(pdf_path).exists():
                continue
            sample_id = f"{round_id}_S{sample_index:03d}"
            sample_index += 1
            samples.append(
                {
                    "sample_id": sample_id,
                    "run_id": run_id,
                    "profile": str(options.get("profile", "")),
                    "part_name": str(part.get("name", "")),
                    "pdf_path": pdf_path,
                    "params": {
                        "profile": options.get("profile"),
                        "quantize_grid": options.get("quantize_grid"),
                        "min_note_duration_beats": options.get("min_note_duration_beats"),
                        "density_threshold": options.get("density_threshold"),
                        "fit_label": options.get("fit_label"),
                        "fit_score": options.get("fit_score"),
                    },
                }
            )

    if not samples:
        raise SystemExit("No exported part PDFs found for selected run(s).")

    manifest = {
        "round_id": round_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "app_version": APP_VERSION,
        "source_runs": run_ids,
        "rubric_fields": [
            "playable",
            "difficulty_fit",
            "readability",
            "melody_match",
            "accidentals_confusing",
            "comment",
        ],
        "samples": samples,
    }
    manifest_path = round_dir / "round_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    print(f"Created tuning round: {round_id}")
    print(f"- manifest: {manifest_path}")
    print(f"- sample count: {len(samples)}")
    print(f"- runs: {', '.join(run_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
