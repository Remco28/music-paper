#!/usr/bin/env python3
"""Stage a Gemini screenshot-review pack from existing run artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare datasets/Gemini review pack.")
    parser.add_argument(
        "--round-id",
        default="",
        help="Optional folder name under datasets/Gemini (default: gemini_YYYYMMDD_HHMMSS).",
    )
    parser.add_argument(
        "--run-id",
        action="append",
        required=True,
        help="Run ID to include (repeat for multiple runs).",
    )
    parser.add_argument(
        "--include-part-keyword",
        action="append",
        default=["clarinet", "sax"],
        help="Only include part PDFs whose names contain these tokens (case-insensitive).",
    )
    parser.add_argument(
        "--include-full-score",
        action="store_true",
        help="Include full-score PDF from each run.",
    )
    parser.add_argument(
        "--runs-dir",
        default="temp/runs",
        help="Run root with per-run manifest.json files.",
    )
    parser.add_argument(
        "--gemini-root",
        default="datasets/Gemini",
        help="Output root for Gemini review packs.",
    )
    return parser.parse_args()


def _safe_read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> int:
    args = _parse_args()
    runs_dir = Path(args.runs_dir)
    gemini_root = Path(args.gemini_root)
    gemini_root.mkdir(parents=True, exist_ok=True)

    round_id = args.round_id.strip() or f"gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pack_dir = gemini_root / round_id
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    artifacts_dir = pack_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    keywords = [token.strip().lower() for token in args.include_part_keyword if token.strip()]
    included: list[dict] = []
    missing_runs: list[str] = []

    for run_id in args.run_id:
        manifest_path = runs_dir / run_id / "manifest.json"
        manifest = _safe_read_json(manifest_path)
        if not manifest:
            missing_runs.append(run_id)
            continue
        options = manifest.get("options") or {}
        profile = str(options.get("profile", ""))
        run_artifacts = artifacts_dir / run_id
        run_artifacts.mkdir(parents=True, exist_ok=True)

        # Part PDFs
        for part in manifest.get("parts") or []:
            if not isinstance(part, dict):
                continue
            if str(part.get("status", "")) != "exported":
                continue
            part_name = str(part.get("name", ""))
            if keywords and not any(token in part_name.lower() for token in keywords):
                continue
            src = Path(str(part.get("path", "")))
            if not src.exists():
                continue
            dst = run_artifacts / src.name
            _copy_file(src, dst)
            included.append(
                {
                    "run_id": run_id,
                    "profile": profile,
                    "type": "part",
                    "part_name": part_name,
                    "source_pdf": str(src),
                    "staged_pdf": str(dst),
                }
            )

        # Full score PDF
        if args.include_full_score:
            output_dir = Path("outputs") / run_id
            if output_dir.exists():
                score_candidates = sorted(output_dir.glob("*_full_score.pdf"))
                if score_candidates:
                    src = score_candidates[0]
                    dst = run_artifacts / src.name
                    _copy_file(src, dst)
                    included.append(
                        {
                            "run_id": run_id,
                            "profile": profile,
                            "type": "full_score",
                            "part_name": "",
                            "source_pdf": str(src),
                            "staged_pdf": str(dst),
                        }
                    )

    summary = {
        "round_id": round_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runs_requested": args.run_id,
        "runs_missing": missing_runs,
        "filters": {
            "include_part_keyword": keywords,
            "include_full_score": bool(args.include_full_score),
        },
        "included": included,
    }
    (pack_dir / "pack_manifest.json").write_text(json.dumps(summary, indent=2))

    prompt_lines = [
        "# Gemini Review Prompt",
        "",
        "You are reviewing screenshot images of generated sheet music for middle-school playability.",
        "",
        "## Pipeline Context (for diagnosis quality)",
        "- Stem separation: Demucs (`htdemucs` model)",
        "- Audio-to-MIDI transcription: Basic Pitch",
        "- Score build and simplification: music21",
        "- PDF engraving: MuseScore CLI",
        "",
        "Use this context when suggesting fixes. Keep advice practical for this stack.",
        "",
        "For each screenshot, score these fields:",
        "- `ledger_line_sanity` (1-5): 1 = impossible ranges, 5 = normal playable range",
        "- `measure_math` (1-5): 1 = many broken bars, 5 = rhythm math consistent",
        "- `symbol_clarity` (1-5): 1 = glitched notation, 5 = clean notation",
        "- `accidental_clutter` (1-5): 1 = excessive/confusing, 5 = manageable",
        "- `overall_readability` (1-5): 1 = unusable, 5 = classroom-ready",
        "",
        "Also provide:",
        "- `major_issues` (short bullet list)",
        "- `quick_fix_hint` (one short suggestion)",
        "- `likely_pipeline_stage`: one of `separation`, `transcription`, `simplification`, `engraving`",
        "- `pass_fail` (`pass` only if classroom-usable now)",
        "",
        "Do not grade based on song preference. Focus on notation validity and playability.",
        "",
        "## Files staged for this round",
    ]
    for idx, item in enumerate(included, start=1):
        label = item["part_name"] if item["part_name"] else "Full Score"
        prompt_lines.append(
            f"{idx}. `{Path(item['staged_pdf']).name}` | profile `{item['profile']}` | run `{item['run_id']}` | {label}"
        )
    (pack_dir / "gemini_prompt.md").write_text("\n".join(prompt_lines) + "\n")

    print(f"Gemini pack ready: {pack_dir}")
    print(f"- manifest: {pack_dir / 'pack_manifest.json'}")
    print(f"- prompt: {pack_dir / 'gemini_prompt.md'}")
    print(f"- staged files: {len(included)}")
    if missing_runs:
        print(f"- missing runs: {', '.join(missing_runs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
