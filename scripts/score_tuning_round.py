#!/usr/bin/env python3
"""Aggregate round ratings and produce ranking summary."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a tuning round from ratings.csv.")
    parser.add_argument("--round-dir", required=True, help="Round directory under datasets/tuning_rounds.")
    return parser.parse_args()


def _norm_1_to_5(value: str) -> float:
    try:
        v = int(value)
    except ValueError:
        return 0.0
    return max(0.0, min(1.0, (v - 1) / 4.0))


def _difficulty_score(value: str) -> float:
    mapping = {"right": 1.0, "too_easy": 0.6, "too_hard": 0.2}
    return mapping.get(str(value).strip(), 0.0)


def _playable_score(value: str) -> float:
    return 1.0 if str(value).strip() == "yes" else 0.0


def _accidental_penalty(value: str) -> float:
    return 0.15 if str(value).strip() == "yes" else 0.0


def _row_score(row: dict) -> float:
    score = 0.0
    score += 0.30 * _playable_score(row.get("playable", ""))
    score += 0.20 * _difficulty_score(row.get("difficulty_fit", ""))
    score += 0.25 * _norm_1_to_5(row.get("readability", ""))
    score += 0.25 * _norm_1_to_5(row.get("melody_match", ""))
    score -= _accidental_penalty(row.get("accidentals_confusing", ""))
    return max(0.0, min(1.0, score))


def main() -> int:
    args = _parse_args()
    round_dir = Path(args.round_dir)
    manifest_path = round_dir / "round_manifest.json"
    ratings_path = round_dir / "ratings.csv"
    if not manifest_path.exists():
        raise SystemExit(f"Missing {manifest_path}")
    if not ratings_path.exists():
        raise SystemExit(f"Missing {ratings_path}")

    manifest = json.loads(manifest_path.read_text())
    sample_map = {str(s.get("sample_id")): s for s in manifest.get("samples", [])}

    by_sample: dict[str, list[dict]] = defaultdict(list)
    with ratings_path.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sample_id = str(row.get("sample_id", "")).strip()
            if sample_id in sample_map:
                by_sample[sample_id].append(row)

    sample_summaries: list[dict] = []
    profile_totals: dict[str, list[float]] = defaultdict(list)
    param_impact: dict[str, list[float]] = defaultdict(list)

    for sample_id, rows in by_sample.items():
        if not rows:
            continue
        scores = [_row_score(r) for r in rows]
        mean_score = sum(scores) / len(scores)
        sample = sample_map[sample_id]
        profile = str(sample.get("profile", ""))
        profile_totals[profile].append(mean_score)

        params = sample.get("params") or {}
        for key in ("quantize_grid", "min_note_duration_beats", "density_threshold", "fit_label"):
            value = params.get(key)
            token = f"{key}={value}"
            param_impact[token].append(mean_score)

        sample_summaries.append(
            {
                "sample_id": sample_id,
                "profile": profile,
                "part_name": sample.get("part_name", ""),
                "run_id": sample.get("run_id", ""),
                "ratings_count": len(rows),
                "mean_score": round(mean_score, 4),
            }
        )

    sample_summaries.sort(key=lambda row: row["mean_score"], reverse=True)
    profile_summary = {
        profile: round(sum(values) / len(values), 4)
        for profile, values in profile_totals.items() if values
    }
    param_summary = {
        token: round(sum(values) / len(values), 4)
        for token, values in param_impact.items() if values
    }

    summary = {
        "round_id": manifest.get("round_id", round_dir.name),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "rated_sample_count": len(sample_summaries),
        "profile_summary": profile_summary,
        "parameter_impact_summary": dict(sorted(param_summary.items(), key=lambda kv: kv[0])),
        "sample_ranking": sample_summaries,
    }
    out_path = round_dir / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2))

    print(f"Scored round: {summary['round_id']}")
    print(f"- rated samples: {summary['rated_sample_count']}")
    print(f"- summary: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
