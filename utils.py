"""General utility helpers for BTT MVP."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path


def cleanup_temp(temp_dir: str) -> None:
    """Delete and recreate the temp directory."""
    temp_path = Path(temp_dir)
    if temp_path.exists():
        shutil.rmtree(temp_path)
    temp_path.mkdir(parents=True, exist_ok=True)


def create_disclaimer_text(school_name: str) -> str:
    label = school_name.strip() or "School Name"
    return f"Educational Use Only - Generated for {label}"


def sanitize_filename(value: str) -> str:
    text = re.sub(r"[^\w\s.-]", "", value or "").strip()
    return re.sub(r"\s+", "_", text) or "untitled"


def zip_outputs(paths: list[str], zip_path: str) -> str:
    zip_file = Path(zip_path)
    zip_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                bundle.write(path, arcname=path.name)
    return str(zip_file)


# --- Phase 2 additions ---


def create_run_id() -> str:
    """Generate a timestamp-based run identifier (microsecond precision)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def create_run_dir(runs_dir: Path, run_id: str) -> Path:
    """Create and return a run-scoped working directory.

    Raises FileExistsError if the directory already exists (collision guard).
    """
    run_dir = runs_dir / run_id
    runs_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir()  # no exist_ok — collision must raise
    return run_dir


def run_preflight_checks(tool_specs: list[dict]) -> list[dict]:
    """Check each required tool for availability.

    Returns list of dicts: {"name", "status" (pass/fail), "message"}.
    """
    results = []
    for spec in tool_specs:
        name = spec["name"]

        # pydub-based ffmpeg check
        if spec.get("check") == "pydub":
            try:
                from pydub.utils import which
                if which("ffmpeg"):
                    results.append({"name": name, "status": "pass", "message": "Found (pydub path)"})
                else:
                    results.append({"name": name, "status": "fail", "message": "ffmpeg not found via pydub"})
            except Exception as exc:
                results.append({"name": name, "status": "fail", "message": str(exc)})
            continue

        # Standard executable check
        try:
            subprocess.run(
                [spec["cmd"]] + spec["args"],
                capture_output=True,
                timeout=10,
            )
            results.append({"name": name, "status": "pass", "message": "Found"})
        except FileNotFoundError:
            results.append({
                "name": name,
                "status": "fail",
                "message": f"'{spec['cmd']}' not found on PATH",
            })
        except subprocess.TimeoutExpired:
            results.append({"name": name, "status": "pass", "message": "Found (slow response)"})
        except Exception as exc:
            results.append({"name": name, "status": "fail", "message": str(exc)})
    return results


def get_tool_paths(tool_specs: list[dict]) -> list[dict]:
    """Resolve executable paths for configured tools (best-effort)."""
    resolved: list[dict] = []
    for spec in tool_specs:
        name = spec["name"]
        if spec.get("check") == "pydub":
            try:
                from pydub.utils import which

                resolved.append({"name": name, "path": which("ffmpeg")})
            except Exception:
                resolved.append({"name": name, "path": None})
            continue
        resolved.append({"name": name, "path": shutil.which(spec["cmd"])})
    return resolved


def get_tool_versions() -> dict[str, str]:
    """Collect version strings for core tools (best-effort)."""
    import sys

    versions: dict[str, str] = {"python": sys.version.split()[0]}
    version_cmds = {
        "streamlit": ["streamlit", "--version"],
        "demucs": ["demucs", "--help"],
        "basic-pitch": ["basic-pitch", "--help"],
        "ffmpeg": ["ffmpeg", "-version"],
    }
    for tool, cmd in version_cmds.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            first_line = (result.stdout or result.stderr or "").strip().split("\n")[0]
            versions[tool] = first_line
        except Exception:
            versions[tool] = "unavailable"
    return versions


def write_run_manifest(
    manifest_path: Path,
    run_id: str,
    source_type: str,
    source_value: str,
    options: dict,
    assignments: dict[str, str],
    part_report: list[dict],
    pipeline: dict[str, str],
    tool_versions: dict[str, str],
) -> str:
    """Write a JSON manifest summarizing a pipeline run."""
    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "input": {"type": source_type, "value": source_value},
        "options": {
            "profile": options.get("profile"),
            "simplify_enabled": bool(options.get("simplify_enabled", False)),
            "quantize_grid": options.get("quantize_grid"),
            "min_note_duration_beats": options.get("min_note_duration_beats"),
            "density_threshold": options.get("density_threshold"),
        },
        "pipeline": pipeline,
        "assignments": assignments,
        "parts": part_report,
        "tool_versions": tool_versions,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return str(manifest_path)
