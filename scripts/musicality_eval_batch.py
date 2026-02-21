#!/usr/bin/env python3
"""Evaluate multiple run variants with automatic musicality scoring."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from utils import sanitize_filename

from musicality_score import score_candidate_part


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run batch musicality scoring for run variants.")
    parser.add_argument("--run-id", action="append", required=True, help="Run ID to evaluate. Repeatable.")
    parser.add_argument("--runs-dir", default="temp/runs", help="Run manifest root.")
    parser.add_argument("--out-root", default="datasets/musicality_rounds", help="Output root directory.")
    parser.add_argument("--round-id", default="", help="Explicit round id; default timestamped.")
    parser.add_argument("--top-n", type=int, default=3, help="Top candidates to surface in summary.")
    return parser.parse_args()


def _safe_load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _normalize_part_name(part_name: str) -> str:
    value = str(part_name or "").strip()
    if value.endswith(")") and "(" in value:
        value = value.rsplit("(", 1)[0].strip()
    return value


def _find_stem_for_part(assignments: dict, part_name: str) -> str | None:
    normalized = _normalize_part_name(part_name)
    for stem, instrument in (assignments or {}).items():
        if str(instrument).strip() == normalized:
            return str(stem)
    return None


def _find_reference_midi(run_dir: Path, stem_name: str) -> Path | None:
    if not stem_name:
        return None
    stem_dir = run_dir / "midi" / sanitize_filename(stem_name)
    candidates = sorted(stem_dir.glob("*.mid")) + sorted(stem_dir.glob("*.midi"))
    return candidates[0] if candidates else None


def _candidate_payload(run_dir: Path, run_manifest: dict) -> dict:
    run_id = str(run_manifest.get("run_id") or run_dir.name)
    options = run_manifest.get("options") or {}
    assignments = run_manifest.get("assignments") or {}
    parts = run_manifest.get("parts") or []
    part_exports = run_dir / "part_exports"

    scored_parts: list[dict] = []
    for part in parts:
        if not isinstance(part, dict) or str(part.get("status", "")) != "exported":
            continue
        part_name = str(part.get("name", ""))
        xml_path = part_exports / f"{sanitize_filename(part_name)}.musicxml"
        if not xml_path.exists():
            continue
        stem_name = _find_stem_for_part(assignments, part_name)
        reference_midi = _find_reference_midi(run_dir, stem_name or "")
        if reference_midi is None or not reference_midi.exists():
            continue
        metrics = score_candidate_part(reference_midi, xml_path)
        scored_parts.append(
            {
                "part_name": part_name,
                "stem_name": stem_name,
                "reference_midi": str(reference_midi),
                "candidate_musicxml": str(xml_path),
                "metrics": metrics,
            }
        )

    if not scored_parts:
        return {
            "run_id": run_id,
            "variant_id": str(options.get("variant_id") or run_id),
            "profile": str(options.get("profile") or ""),
            "hard_gate_pass": False,
            "part_scores": [],
            "aggregate_score": 0.0,
            "reason": "no_scorable_parts",
        }

    aggregate = sum(float(item["metrics"]["part_score"]) for item in scored_parts) / len(scored_parts)
    hard_gate_pass = all(bool(item["metrics"]["hard_gate_pass"]) for item in scored_parts)
    return {
        "run_id": run_id,
        "variant_id": str(options.get("variant_id") or run_id),
        "profile": str(options.get("profile") or ""),
        "hard_gate_pass": hard_gate_pass,
        "part_scores": scored_parts,
        "aggregate_score": round(aggregate, 4),
        "reason": "",
    }


def main() -> int:
    args = _parse_args()
    runs_dir = Path(args.runs_dir)
    round_id = args.round_id.strip() or f"musicality_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    round_dir = Path(args.out_root) / round_id
    round_dir.mkdir(parents=True, exist_ok=True)

    candidates: list[dict] = []
    missing_runs: list[str] = []
    for run_id in args.run_id:
        manifest_path = runs_dir / run_id / "manifest.json"
        data = _safe_load_json(manifest_path)
        if not data:
            missing_runs.append(run_id)
            continue
        candidates.append(_candidate_payload(manifest_path.parent, data))

    if not candidates:
        raise SystemExit("No valid candidate runs were loaded.")

    candidates.sort(
        key=lambda item: (
            0 if item["hard_gate_pass"] else 1,
            -float(item.get("aggregate_score", 0.0)),
            str(item.get("run_id", "")),
        )
    )
    for idx, item in enumerate(candidates, start=1):
        item["rank"] = idx

    round_manifest = {
        "round_id": round_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runs_requested": list(args.run_id),
        "runs_missing": missing_runs,
        "candidate_count": len(candidates),
        "score_formula": "0.40*onset + 0.30*pitch + 0.20*rhythm - 0.10*fragmentation_penalty",
    }
    auto_scores = {
        "round_id": round_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "candidates": candidates,
    }
    promoted = [item for item in candidates if item.get("hard_gate_pass")][: max(1, int(args.top_n))]
    summary = {
        "round_id": round_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "winner": promoted[0] if promoted else candidates[0],
        "top_candidates": promoted if promoted else candidates[: max(1, int(args.top_n))],
        "hard_gate_pass_count": sum(1 for item in candidates if item.get("hard_gate_pass")),
        "candidate_count": len(candidates),
    }

    (round_dir / "round_manifest.json").write_text(json.dumps(round_manifest, indent=2))
    (round_dir / "auto_scores.json").write_text(json.dumps(auto_scores, indent=2))
    (round_dir / "summary.json").write_text(json.dumps(summary, indent=2))

    votes_path = round_dir / "ab_votes.csv"
    if not votes_path.exists():
        votes_path.write_text(
            "round_id,timestamp,reviewer_id,candidate_a,candidate_b,winner,confidence,notes\n"
        )

    print(f"Musicality round created: {round_id}")
    print(f"- manifest: {round_dir / 'round_manifest.json'}")
    print(f"- auto scores: {round_dir / 'auto_scores.json'}")
    print(f"- summary: {round_dir / 'summary.json'}")
    print(f"- candidates: {len(candidates)}")
    if missing_runs:
        print(f"- missing runs: {', '.join(missing_runs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
