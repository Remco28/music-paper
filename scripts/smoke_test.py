#!/usr/bin/env python3
"""Minimal non-interactive smoke checks for BTT."""

from __future__ import annotations

import json
import sys
import tempfile
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
    from utils import write_run_manifest

    with tempfile.TemporaryDirectory(prefix="btt-smoke-") as tmp:
        path = Path(tmp) / "manifest.json"
        write_run_manifest(
            manifest_path=path,
            run_id="smoke",
            source_type="local",
            source_value="sample.wav",
            options={
                "profile": "Balanced",
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


def main() -> int:
    checks = [
        ("imports", check_imports),
        ("config invariants", check_config_invariants),
        ("manifest roundtrip", check_manifest_roundtrip),
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
