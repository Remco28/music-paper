#!/usr/bin/env python3
"""Minimal non-interactive smoke checks for BTT."""

from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_imports() -> None:
    import app  # noqa: F401
    import config  # noqa: F401
    import pipeline  # noqa: F401
    import utils  # noqa: F401


def check_config_invariants() -> None:
    from config import DEFAULT_PROFILE, SIMPLIFY_ADVANCED_RANGES, SIMPLIFY_PROFILES

    _assert(DEFAULT_PROFILE in SIMPLIFY_PROFILES, "DEFAULT_PROFILE missing from SIMPLIFY_PROFILES")

    expected = {"quantize_grid", "min_note_duration_beats", "density_threshold"}
    for name, profile in SIMPLIFY_PROFILES.items():
        _assert(set(profile.keys()) == expected, f"Profile '{name}' keys mismatch")

        grid = profile["quantize_grid"]
        min_duration = float(profile["min_note_duration_beats"])
        density = int(profile["density_threshold"])

        _assert(grid in SIMPLIFY_ADVANCED_RANGES["quantize_grid"], f"Invalid grid in profile '{name}'")
        _assert(
            SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"][0]
            <= min_duration
            <= SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"][1],
            f"Invalid min duration in profile '{name}'",
        )
        _assert(
            SIMPLIFY_ADVANCED_RANGES["density_threshold"][0]
            <= density
            <= SIMPLIFY_ADVANCED_RANGES["density_threshold"][1],
            f"Invalid density in profile '{name}'",
        )


def check_manifest_roundtrip() -> None:
    from utils import MANIFEST_SCHEMA_VERSION, write_run_manifest

    with tempfile.TemporaryDirectory(prefix="btt-smoke-") as tmp:
        path = Path(tmp) / "manifest.json"
        write_run_manifest(
            manifest_path=path,
            run_id="smoke",
            source_type="local",
            source_value="sample.wav",
            options={
                "profile": "Easy Intermediate",
                "simplify_enabled": True,
                "quantize_grid": "1/8",
                "min_note_duration_beats": 0.25,
                "density_threshold": 6,
            },
            assignments={"bass": "Tuba"},
            part_report=[{"name": "Tuba", "status": "exported", "note_count": 12}],
            pipeline={"app_version": "smoke", "demucs_model": "htdemucs"},
            tool_versions={"python": sys.version.split()[0]},
            zip_filename="smoke_exports.zip",
            outcome_success=True,
        )
        data = json.loads(path.read_text())
        required = {
            "run_id",
            "timestamp",
            "input",
            "options",
            "pipeline",
            "outcome",
            "assignments",
            "parts",
            "tool_versions",
        }
        _assert(required.issubset(data.keys()), "Manifest missing required top-level keys")
        _assert(data.get("schema_version") == MANIFEST_SCHEMA_VERSION, "Manifest schema_version mismatch")
        _assert(isinstance(data["outcome"].get("success"), bool), "Manifest outcome.success missing/bad type")


def check_run_prune_helpers() -> None:
    from utils import prune_old_runs, run_storage_summary

    with tempfile.TemporaryDirectory(prefix="btt-prune-") as tmp:
        runs_dir = Path(tmp) / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        for run_id in ("20260219_100000_000001", "20260219_100000_000002", "20260219_100000_000003"):
            run_dir = runs_dir / run_id
            run_dir.mkdir()
            (run_dir / "artifact.txt").write_text(f"run={run_id}")

        before = run_storage_summary(runs_dir)
        _assert(before["count"] == 3, "Expected three run directories before prune")
        _assert(before["size_bytes"] > 0, "Expected non-zero size before prune")

        result = prune_old_runs(
            runs_dir=runs_dir,
            keep_latest_n=1,
            active_run_id="20260219_100000_000001",
        )
        _assert(result["deleted_count"] == 1, "Expected one deleted run after prune")
        _assert(result["reclaimed_bytes"] > 0, "Expected reclaimed bytes after prune")

        remaining = sorted(path.name for path in runs_dir.iterdir() if path.is_dir())
        _assert(
            remaining == ["20260219_100000_000001", "20260219_100000_000003"],
            "Prune did not keep expected run IDs",
        )


def check_load_run_manifest() -> None:
    from utils import (
        derive_outcome_status,
        load_run_manifest,
        normalize_manifest_data,
        set_manifest_outcome_failure_context,
        set_manifest_outcome_integrity_warnings,
    )

    with tempfile.TemporaryDirectory(prefix="btt-manifest-load-") as tmp:
        runs_dir = Path(tmp) / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        ok_dir = runs_dir / "20260219_110000_000001"
        ok_dir.mkdir()
        (ok_dir / "manifest.json").write_text(json.dumps({"run_id": "20260219_110000_000001"}))

        corrupt_dir = runs_dir / "20260219_110000_000002"
        corrupt_dir.mkdir()
        (corrupt_dir / "manifest.json").write_text("{bad json")

        ok_result = load_run_manifest(runs_dir, "20260219_110000_000001")
        _assert(ok_result["status"] == "ok", "Expected ok status for valid manifest")
        _assert(ok_result["data"]["run_id"] == "20260219_110000_000001", "Valid manifest data mismatch")
        _assert(ok_result["data"]["legacy_schema"] is True, "Expected legacy flag for unversioned manifest")

        missing_result = load_run_manifest(runs_dir, "20260219_110000_000003")
        _assert(missing_result["status"] == "missing", "Expected missing status for absent manifest")

        corrupt_result = load_run_manifest(runs_dir, "20260219_110000_000002")
        _assert(corrupt_result["status"] == "corrupt", "Expected corrupt status for invalid manifest")

        normalized = normalize_manifest_data(
            {
                "schema_version": "1",
                "run_id": "v1",
                "outcome": {"exported_part_count": "2", "success": True},
            }
        )
        _assert(normalized["legacy_schema"] is False, "Expected non-legacy flag for versioned manifest")
        _assert(normalized["outcome"]["exported_part_count"] == 2, "Expected normalized int outcome count")
        _assert(normalized["status"] == "success", "Expected success status derivation")
        _assert(
            normalized["outcome"]["integrity_warnings"] == [],
            "Expected default empty integrity_warnings for manifests without the field",
        )
        _assert(
            normalized["outcome"]["failure_stage"] == "",
            "Expected default empty failure_stage for manifests without the field",
        )
        _assert(
            normalized["outcome"]["failure_summary"] == "",
            "Expected default empty failure_summary for manifests without the field",
        )

        failed_normalized = normalize_manifest_data(
            {"schema_version": "1", "run_id": "v2", "outcome": {"success": False}}
        )
        _assert(failed_normalized["status"] == "failed", "Expected failed status derivation")
        _assert(derive_outcome_status(None) == "unknown", "Expected unknown derivation for missing success")

        warning_manifest = ok_dir / "manifest.json"
        set_manifest_outcome_integrity_warnings(
            warning_manifest,
            ["warning-1", "warning-2"],
        )
        warning_data = json.loads(warning_manifest.read_text())
        warning_list = (warning_data.get("outcome") or {}).get("integrity_warnings")
        _assert(
            warning_list == ["warning-1", "warning-2"],
            "Expected manifest integrity warnings to persist via helper",
        )
        set_manifest_outcome_failure_context(
            warning_manifest,
            "pdf_rendering",
            "MuseScore command failed",
        )
        failure_data = json.loads(warning_manifest.read_text())
        failure_outcome = failure_data.get("outcome") or {}
        _assert(
            failure_outcome.get("failure_stage") == "pdf_rendering",
            "Expected failure_stage to persist via helper",
        )
        _assert(
            failure_outcome.get("failure_summary") == "MuseScore command failed",
            "Expected failure_summary to persist via helper",
        )


def check_outcome_status_contract() -> None:
    from utils import derive_outcome_status

    _assert(derive_outcome_status(True) == "success", "Expected success for True")
    _assert(derive_outcome_status(False) == "failed", "Expected failed for False")
    _assert(derive_outcome_status(None) == "unknown", "Expected unknown for None")
    _assert(derive_outcome_status("true") == "unknown", "Expected unknown for non-bool success value")


def check_source_validation_helpers() -> None:
    from config import YOUTUBE_DOMAINS
    from utils import classify_audio_source, validate_single_video_youtube_url

    _assert(
        classify_audio_source("https://www.youtube.com/watch?v=abc123", YOUTUBE_DOMAINS) == "youtube_url",
        "Expected youtube_url classification for youtube.com video URL",
    )
    _assert(
        classify_audio_source("https://m.youtube.com/watch?v=abc123", YOUTUBE_DOMAINS) == "youtube_url",
        "Expected youtube_url classification for mobile youtube URL",
    )
    _assert(
        classify_audio_source("https://vimeo.com/12345", YOUTUBE_DOMAINS) == "remote_url",
        "Expected remote_url classification for non-YouTube remote URL",
    )
    _assert(
        classify_audio_source("/tmp/input.wav", YOUTUBE_DOMAINS) == "local_path",
        "Expected local_path classification for filesystem path",
    )
    _assert(
        classify_audio_source("", YOUTUBE_DOMAINS) == "empty",
        "Expected empty classification for blank source",
    )

    _assert(
        validate_single_video_youtube_url("https://www.youtube.com/watch?v=abc123", YOUTUBE_DOMAINS) == "",
        "Expected no validation error for single-video YouTube URL",
    )
    _assert(
        "Playlist URLs are not supported"
        in validate_single_video_youtube_url(
            "https://www.youtube.com/watch?v=abc123&list=PLxyz",
            YOUTUBE_DOMAINS,
        ),
        "Expected playlist rejection message",
    )
    _assert(
        "recognized YouTube URL host"
        in validate_single_video_youtube_url("https://vimeo.com/12345", YOUTUBE_DOMAINS),
        "Expected host rejection message for non-YouTube URL",
    )


def check_export_zip_inspection_helper() -> None:
    from utils import inspect_export_zip

    with tempfile.TemporaryDirectory(prefix="btt-zip-check-") as tmp:
        tmp_path = Path(tmp)
        zip_path = tmp_path / "bundle.zip"

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            bundle.writestr("manifest.json", "{}")
            bundle.writestr("song.musicxml", "<score/>")
            bundle.writestr("song_full_score.pdf", "pdf")
            bundle.writestr("Bb_Clarinet_1.pdf", "pdf")

        warnings = inspect_export_zip(
            zip_path=zip_path,
            expected_musicxml_filename="song.musicxml",
            expected_exported_part_count=1,
            expected_part_pdf_filenames=["Bb_Clarinet_1.pdf"],
        )
        _assert(not warnings, f"Expected no warnings for consistent zip, got: {warnings}")

        mismatch = inspect_export_zip(
            zip_path=zip_path,
            expected_musicxml_filename="missing.musicxml",
            expected_exported_part_count=2,
            expected_part_pdf_filenames=["Bb_Clarinet_1.pdf", "Flute.pdf"],
        )
        _assert(
            any("missing full score MusicXML" in message for message in mismatch),
            "Expected missing musicxml warning",
        )
        _assert(
            any("part PDF count mismatch" in message for message in mismatch),
            "Expected part count mismatch warning",
        )
        _assert(
            any("expected exported part PDFs missing" in message for message in mismatch),
            "Expected missing part PDF warning",
        )


def check_simplify_part_effectiveness() -> None:
    from music21 import chord, note, stream

    from pipeline import _simplify_part

    part = stream.Part()
    # Dense/tuplet-heavy synthetic content to verify simplification is active.
    part.insert(0.0, note.Note("C4", quarterLength=1 / 3))
    part.insert(1 / 3, note.Note("D4", quarterLength=1 / 3))
    part.insert(2 / 3, note.Note("E4", quarterLength=1 / 3))
    for idx in range(12):
        off = 4.0 + (idx * 0.25)
        part.insert(off, chord.Chord(["C4", "E4"], quarterLength=0.125))

    before_notes = list(part.recurse().notes)
    before_tuplets = sum(1 for n in before_notes if n.duration.tuplets)
    _assert(before_tuplets > 0, "Expected tuplets in synthetic source part")

    _simplify_part(
        part,
        {
            "quantize_grid": "1/8",
            "min_note_duration_beats": 0.25,
            "density_threshold": 3,
        },
    )

    after_notes = list(part.recurse().notes)
    min_duration = min(float(n.duration.quarterLength) for n in after_notes)

    _assert(min_duration >= 0.25, "Expected simplification to enforce minimum duration")
    _assert(
        len(after_notes) < len(before_notes),
        "Expected simplification to reduce dense note count on synthetic content",
    )


def main() -> int:
    checks = [
        ("imports", check_imports),
        ("config invariants", check_config_invariants),
        ("manifest roundtrip", check_manifest_roundtrip),
        ("run prune helpers", check_run_prune_helpers),
        ("manifest loader", check_load_run_manifest),
        ("outcome status contract", check_outcome_status_contract),
        ("source validation helpers", check_source_validation_helpers),
        ("export zip inspection helper", check_export_zip_inspection_helper),
        ("simplify part effectiveness", check_simplify_part_effectiveness),
    ]

    failed = False
    print("=== BTT Smoke Test ===")
    for label, fn in checks:
        try:
            fn()
            print(f"PASS: {label}")
        except Exception as exc:  # pragma: no cover
            failed = True
            print(f"FAIL: {label}: {exc}")

    if failed:
        print("Smoke test failed.")
        return 1

    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
