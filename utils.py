"""General utility helpers for BTT MVP."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

MANIFEST_SCHEMA_VERSION = "1"


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


def _host_matches_allowed_domain(host: str, allowed_domains: tuple[str, ...]) -> bool:
    normalized = (host or "").strip().lower().split(":", 1)[0]
    return any(
        normalized == domain or normalized.endswith(f".{domain}")
        for domain in allowed_domains
    )


def classify_audio_source(source: str, youtube_domains: tuple[str, ...]) -> str:
    """Classify source text as local path, YouTube URL, or other remote URL."""
    value = (source or "").strip()
    if not value:
        return "empty"
    try:
        parsed = urlparse(value)
    except ValueError:
        return "local_path"
    scheme = (parsed.scheme or "").lower()
    if scheme in ("http", "https"):
        if _host_matches_allowed_domain(parsed.netloc, youtube_domains):
            return "youtube_url"
        return "remote_url"
    return "local_path"


def validate_single_video_youtube_url(url: str, youtube_domains: tuple[str, ...]) -> str:
    """Return validation error text for single-video YouTube URLs, else empty string."""
    value = (url or "").strip()
    if not value:
        return "Please enter a URL first."
    try:
        parsed = urlparse(value)
    except ValueError:
        return "URL format appears invalid."
    scheme = (parsed.scheme or "").lower()
    if scheme not in ("http", "https"):
        return "URL must start with http:// or https://."
    if not _host_matches_allowed_domain(parsed.netloc, youtube_domains):
        return "Use a recognized YouTube URL host (youtube.com or youtu.be)."
    query = parse_qs(parsed.query)
    if "list" in query:
        return "Playlist URLs are not supported. Use a single-video URL."
    return ""


def zip_outputs(paths: list[str], zip_path: str) -> str:
    zip_file = Path(zip_path)
    zip_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                bundle.write(path, arcname=path.name)
    return str(zip_file)


def inspect_export_zip(
    zip_path: str | Path,
    expected_musicxml_filename: str,
    expected_exported_part_count: int,
    expected_part_pdf_filenames: list[str] | None = None,
) -> list[str]:
    """Return non-blocking warnings for export ZIP consistency checks."""
    zip_file = Path(zip_path)
    warnings: list[str] = []
    if not zip_file.exists():
        return ["ZIP consistency warning: ZIP file was not found after packaging."]

    try:
        with zipfile.ZipFile(zip_file, "r") as bundle:
            names = [Path(name).name for name in bundle.namelist()]
    except Exception:
        return ["ZIP consistency warning: unable to inspect ZIP contents."]

    name_set = set(names)
    if "manifest.json" not in name_set:
        warnings.append("ZIP consistency warning: missing manifest.json in package.")
    if expected_musicxml_filename not in name_set:
        warnings.append(
            f"ZIP consistency warning: missing full score MusicXML `{expected_musicxml_filename}`."
        )

    part_pdf_count = sum(
        1
        for name in names
        if name.lower().endswith(".pdf") and not name.lower().endswith("_full_score.pdf")
    )
    if part_pdf_count != int(expected_exported_part_count):
        warnings.append(
            "ZIP consistency warning: part PDF count mismatch "
            f"(expected {expected_exported_part_count}, found {part_pdf_count})."
        )

    expected_pdf_names = expected_part_pdf_filenames or []
    if expected_pdf_names:
        missing_parts = [name for name in expected_pdf_names if name not in name_set]
        if missing_parts:
            sample = ", ".join(missing_parts[:3])
            warnings.append(
                "ZIP consistency warning: expected exported part PDFs missing "
                f"(sample: {sample})."
            )
    return warnings


def part_report_counts(part_report: list[dict]) -> tuple[int, int]:
    """Return exported/skipped counts from a part report list."""
    exported = sum(1 for part in part_report if part.get("status") == "exported")
    skipped = sum(1 for part in part_report if part.get("status") != "exported")
    return exported, skipped


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
    zip_filename: str,
    outcome_success: bool = False,
) -> str:
    """Write a JSON manifest summarizing a pipeline run."""
    exported_count, skipped_count = part_report_counts(part_report)
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "input": {"type": source_type, "value": source_value},
        "options": {
            "profile": options.get("profile"),
            "variant_id": options.get("variant_id"),
            "simplify_enabled": bool(options.get("simplify_enabled", False)),
            "quantize_grid": options.get("quantize_grid"),
            "min_note_duration_beats": options.get("min_note_duration_beats"),
            "density_threshold": options.get("density_threshold"),
            "fit_score": options.get("fit_score"),
            "fit_label": options.get("fit_label"),
            "recommended_profile": options.get("recommended_profile"),
        },
        "pipeline": pipeline,
        "outcome": {
            "exported_part_count": exported_count,
            "skipped_part_count": skipped_count,
            "zip_filename": zip_filename,
            "success": bool(outcome_success),
            "integrity_warnings": [],
            "failure_stage": "",
            "failure_summary": "",
        },
        "assignments": assignments,
        "parts": part_report,
        "tool_versions": tool_versions,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return str(manifest_path)


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def derive_outcome_status(success_value: object) -> str:
    """Map outcome.success value to normalized status label."""
    if success_value is True:
        return "success"
    if success_value is False:
        return "failed"
    return "unknown"


def normalize_manifest_data(data: object) -> dict:
    """Normalize manifest content for compatibility across schema revisions."""
    if not isinstance(data, dict):
        data = {}

    raw_schema = data.get("schema_version")
    schema_version = str(raw_schema) if raw_schema is not None else None
    legacy_schema = schema_version is None

    input_block = data.get("input")
    if not isinstance(input_block, dict):
        input_block = {}

    options = data.get("options")
    if not isinstance(options, dict):
        options = {}

    outcome = data.get("outcome")
    if not isinstance(outcome, dict):
        outcome = {}

    pipeline = data.get("pipeline")
    if not isinstance(pipeline, dict):
        pipeline = {}

    parts = data.get("parts")
    if not isinstance(parts, list):
        parts = []
    normalized_parts = [entry for entry in parts if isinstance(entry, dict)]

    assignments = data.get("assignments")
    if not isinstance(assignments, dict):
        assignments = {}

    tool_versions = data.get("tool_versions")
    if not isinstance(tool_versions, dict):
        tool_versions = {}

    success_raw = outcome.get("success")
    success_value = success_raw if isinstance(success_raw, bool) else None
    outcome_status = derive_outcome_status(success_value)
    integrity_warnings_raw = outcome.get("integrity_warnings")
    integrity_warnings = []
    if isinstance(integrity_warnings_raw, list):
        integrity_warnings = [str(item) for item in integrity_warnings_raw if str(item).strip()]
    failure_stage = str(outcome.get("failure_stage", "") or "")
    failure_summary = str(outcome.get("failure_summary", "") or "")

    return {
        "schema_version": schema_version,
        "legacy_schema": legacy_schema,
        "run_id": data.get("run_id", ""),
        "timestamp": data.get("timestamp", ""),
        "input": {
            "type": input_block.get("type", ""),
            "value": input_block.get("value", ""),
        },
        "options": {
            "profile": options.get("profile", ""),
            "simplify_enabled": (
                options.get("simplify_enabled")
                if isinstance(options.get("simplify_enabled"), bool)
                else None
            ),
            "quantize_grid": options.get("quantize_grid"),
            "min_note_duration_beats": options.get("min_note_duration_beats"),
            "density_threshold": options.get("density_threshold"),
            "fit_score": options.get("fit_score"),
            "fit_label": options.get("fit_label", ""),
            "recommended_profile": options.get("recommended_profile", ""),
        },
        "outcome": {
            "exported_part_count": _safe_int(outcome.get("exported_part_count"), 0),
            "skipped_part_count": _safe_int(outcome.get("skipped_part_count"), 0),
            "zip_filename": outcome.get("zip_filename", ""),
            "success": success_value,
            "integrity_warnings": integrity_warnings,
            "failure_stage": failure_stage,
            "failure_summary": failure_summary,
        },
        "status": outcome_status,
        "pipeline": {
            "app_version": pipeline.get("app_version", ""),
            "demucs_model": pipeline.get("demucs_model", ""),
        },
        "parts": normalized_parts,
        "assignments": assignments,
        "tool_versions": tool_versions,
    }


def set_manifest_outcome_success(manifest_path: Path, success: bool) -> None:
    """Update manifest outcome success flag, best-effort."""
    data = json.loads(manifest_path.read_text())
    outcome = data.get("outcome")
    if not isinstance(outcome, dict):
        outcome = {}
    outcome["success"] = bool(success)
    data["outcome"] = outcome
    manifest_path.write_text(json.dumps(data, indent=2))


def set_manifest_outcome_integrity_warnings(manifest_path: Path, warnings: list[str]) -> None:
    """Update manifest outcome integrity warnings list, best-effort."""
    data = json.loads(manifest_path.read_text())
    outcome = data.get("outcome")
    if not isinstance(outcome, dict):
        outcome = {}
    outcome["integrity_warnings"] = [str(item) for item in warnings if str(item).strip()]
    data["outcome"] = outcome
    manifest_path.write_text(json.dumps(data, indent=2))


def set_manifest_outcome_failure_context(manifest_path: Path, stage: str, summary: str) -> None:
    """Update manifest failure context for failed outcomes, best-effort."""
    data = json.loads(manifest_path.read_text())
    outcome = data.get("outcome")
    if not isinstance(outcome, dict):
        outcome = {}
    outcome["failure_stage"] = str(stage or "").strip()
    outcome["failure_summary"] = str(summary or "").strip()
    data["outcome"] = outcome
    manifest_path.write_text(json.dumps(data, indent=2))


def list_recent_run_summaries(runs_dir: Path, limit: int = 5) -> list[dict]:
    """Return recent manifest summaries (newest-first), skipping unreadable/corrupt files."""
    if limit <= 0 or not runs_dir.exists():
        return []

    summaries: list[dict] = []
    run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    run_dirs.sort(key=lambda path: path.name, reverse=True)

    for run_dir in run_dirs:
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        try:
            raw_data = json.loads(manifest_path.read_text())
        except Exception:
            continue
        data = normalize_manifest_data(raw_data)

        input_block = data["input"]
        options = data["options"]
        outcome = data["outcome"]
        summaries.append(
            {
                "run_id": data.get("run_id") or run_dir.name,
                "timestamp": data.get("timestamp", ""),
                "input_type": input_block.get("type", ""),
                "input_value": input_block.get("value", ""),
                "profile": options.get("profile", ""),
                "simplify_enabled": bool(options.get("simplify_enabled", False)),
                "exported_parts": _safe_int(outcome.get("exported_part_count", 0)),
                "skipped_parts": _safe_int(outcome.get("skipped_part_count", 0)),
                "zip_filename": outcome.get("zip_filename", ""),
                "status": data.get("status", "unknown"),
                "fit_label": options.get("fit_label", ""),
                "recommended_profile": options.get("recommended_profile", ""),
            }
        )
        if len(summaries) >= limit:
            break
    return summaries


def _dir_size_bytes(path: Path) -> int:
    """Return recursive directory size in bytes (best-effort)."""
    total = 0
    if not path.exists():
        return total
    for entry in path.rglob("*"):
        if not entry.is_file():
            continue
        try:
            total += entry.stat().st_size
        except OSError:
            continue
    return total


def run_storage_summary(runs_dir: Path) -> dict[str, int]:
    """Return run directory count and aggregate size."""
    if not runs_dir.exists():
        return {"count": 0, "size_bytes": 0}
    run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    return {
        "count": len(run_dirs),
        "size_bytes": sum(_dir_size_bytes(path) for path in run_dirs),
    }


def prune_old_runs(runs_dir: Path, keep_latest_n: int, active_run_id: str = "") -> dict[str, int]:
    """Prune old run directories while keeping latest N and current active run."""
    if keep_latest_n < 0:
        keep_latest_n = 0
    if not runs_dir.exists():
        return {"deleted_count": 0, "reclaimed_bytes": 0}

    run_dirs = [path for path in runs_dir.iterdir() if path.is_dir()]
    run_dirs.sort(key=lambda path: path.name, reverse=True)

    keep_ids: set[str] = set()
    if active_run_id:
        keep_ids.add(active_run_id)

    kept_non_active = 0
    for run_dir in run_dirs:
        run_id = run_dir.name
        if run_id in keep_ids:
            continue
        if kept_non_active < keep_latest_n:
            keep_ids.add(run_id)
            kept_non_active += 1

    deleted_count = 0
    reclaimed_bytes = 0
    for run_dir in run_dirs:
        if run_dir.name in keep_ids:
            continue
        size_bytes = _dir_size_bytes(run_dir)
        try:
            shutil.rmtree(run_dir)
        except OSError:
            continue
        deleted_count += 1
        reclaimed_bytes += size_bytes

    return {"deleted_count": deleted_count, "reclaimed_bytes": reclaimed_bytes}


def load_run_manifest(runs_dir: Path, run_id: str) -> dict:
    """Load a run manifest by run_id with explicit status."""
    if not run_id:
        return {"status": "missing", "manifest_path": None, "data": None}

    manifest_path = runs_dir / run_id / "manifest.json"
    if not manifest_path.exists():
        return {"status": "missing", "manifest_path": str(manifest_path), "data": None}

    try:
        raw_data = json.loads(manifest_path.read_text())
    except Exception:
        return {"status": "corrupt", "manifest_path": str(manifest_path), "data": None}

    return {
        "status": "ok",
        "manifest_path": str(manifest_path),
        "data": normalize_manifest_data(raw_data),
    }
