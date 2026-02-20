from __future__ import annotations

import csv
import io
import warnings
from datetime import datetime
from pathlib import Path

import streamlit as st

from config import (
    APP_VERSION,
    DEFAULT_PROFILE,
    DOWNLOADS_DIR,
    DEMUCS_MODEL,
    REQUIRED_TOOLS,
    RUNS_DIR,
    SIMPLIFY_ADVANCED_RANGES,
    SIMPLIFY_PRESET,
    SIMPLIFY_PROFILES,
    STANDARD_INSTRUMENTS,
    SUPPORTED_AUDIO_EXTENSIONS,
    TEMP_DIR,
    TEACHER_VISIBLE_PROFILES,
    YOUTUBE_DOMAINS,
)
from pipeline import (
    assess_song_fit,
    build_score,
    download_or_convert_audio,
    render_pdfs,
    separate_stems,
    transcribe_to_midi,
)
from utils import (
    cleanup_temp,
    create_run_dir,
    create_run_id,
    get_tool_paths,
    get_tool_versions,
    load_run_manifest,
    part_report_counts,
    prune_old_runs,
    inspect_export_zip,
    run_preflight_checks,
    run_storage_summary,
    sanitize_filename,
    set_manifest_outcome_failure_context,
    set_manifest_outcome_integrity_warnings,
    set_manifest_outcome_success,
    validate_single_video_youtube_url,
    write_run_manifest,
    zip_outputs,
)

LEGACY_PROFILE_ALIASES = {
    "Conservative": "Intermediate",
    "Balanced": "Easy Intermediate",
    "Aggressive": "Beginner",
}


def _normalize_profile_name(profile_name: object) -> str:
    """Map legacy profile labels to current names."""
    value = str(profile_name or "").strip()
    return LEGACY_PROFILE_ALIASES.get(value, value)


def _init_state() -> None:
    defaults = {
        "wav_path": "",
        "source_type": "",
        "source_value": "",
        "stems": {},
        "assignments": {},
        "midi_map": {},
        "score_data": {},
        "musicxml_path": "",
        "pdf_paths": [],
        "part_report": [],
        "zip_path": "",
        "run_id": "",
        "run_dir": "",
        "preflight": [],
        "preflight_snapshot": {},
        "preflight_change_indicator": "",
        "preflight_last_run_ts": "",
        "opt_title": "Untitled",
        "opt_composer": "",
        "opt_school": "",
        "opt_simplify_enabled": SIMPLIFY_PRESET["enabled"],
        "opt_profile": DEFAULT_PROFILE,
        "opt_profile_applied": DEFAULT_PROFILE,
        "opt_quantize_grid": SIMPLIFY_PRESET["quantize_grid"],
        "opt_min_duration": float(SIMPLIFY_PRESET["min_note_duration_beats"]),
        "opt_density_threshold": int(SIMPLIFY_PRESET["density_threshold"]),
        "opt_auto_apply_recommendation": True,
        "opt_two_pass_export": False,
        "export_last_ok": False,
        "export_integrity_warning": "",
        "export_complexity_rows": [],
        "export_complexity_summary": "",
        "fit_analysis": {},
        "fit_analysis_signature": "",
        "fit_analysis_profile_used": "",
        "multi_pass_exports": [],
        "history_input_filter": "all",
        "history_status_filter": "all",
        "history_warning_filter": "all",
        "history_warning_category_query": "",
        "history_sort_mode": "newest_first",
        "history_run_id_query": "",
        "history_limit": 5,
        "history_selected_run_id": "",
        "history_session_note": "",
        "history_copy_summary": "",
        "history_warning_digest": "",
        "history_manifest_cache": [],
        "history_manifest_cache_signature": "",
        "history_manifest_cache_last_refresh": "",
        "history_cache_auto_refresh": True,
        "diagnostics_copy_summary": "",
        "diagnostics_probe_cache": {},
        "diagnostics_probe_last_run_ts": "",
        "maintenance_keep_latest_n": 5,
        "maintenance_confirm_prune": False,
        "reset_confirm_temp_workspace": False,
        "reset_workspace_notice": "",
        "reset_workspace_clear_confirm_pending": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _save_uploaded_file(uploaded_file, run_dir: Path) -> str:
    uploads_dir = run_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    destination = uploads_dir / sanitize_filename(uploaded_file.name)
    destination.write_bytes(uploaded_file.getbuffer())
    return str(destination)


def _new_run() -> Path:
    """Create a fresh run_id and run_dir, store in session state, return run_dir."""
    run_id = create_run_id()
    run_dir = create_run_dir(RUNS_DIR, run_id)
    st.session_state.run_id = run_id
    st.session_state.run_dir = str(run_dir)
    return run_dir


def _current_run_dir() -> Path | None:
    """Return the current run_dir Path if one exists."""
    val = st.session_state.get("run_dir", "")
    return Path(val) if val else None


def _preflight_ok() -> bool:
    """Return True if all required tools passed preflight."""
    return all(r["status"] == "pass" for r in st.session_state.preflight)


def _show_stage_error(stage: str, exc: Exception, hint: str) -> None:
    """Render concise stage failure context without verbose traceback."""
    summary = str(exc).strip().split("\n")[0] or exc.__class__.__name__
    st.error(f"{stage} failed: {summary}")
    st.caption(f"Next step: {hint}")


def _validate_local_upload(uploaded_file) -> str:
    """Return validation error text for uploaded local file, else empty string."""
    if uploaded_file is None:
        return "Please upload a file first."
    suffix = Path(uploaded_file.name or "").suffix.lower()
    if suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(SUPPORTED_AUDIO_EXTENSIONS))
        return f"Unsupported file type `{suffix or 'unknown'}`. Use one of: {allowed}."
    size_bytes = len(uploaded_file.getbuffer())
    if size_bytes <= 0:
        return "Uploaded file is empty (0 bytes). Choose a valid audio file and retry."
    return ""


def _validate_youtube_url(url: str) -> str:
    """Return validation error text for YouTube URL, else empty string."""
    return validate_single_video_youtube_url(url, YOUTUBE_DOMAINS)


def _clear_export_outputs() -> None:
    """Invalidate last export artifacts before a new export attempt."""
    st.session_state.musicxml_path = ""
    st.session_state.pdf_paths = []
    st.session_state.part_report = []
    st.session_state.zip_path = ""
    st.session_state.export_last_ok = False
    st.session_state.export_integrity_warning = ""
    st.session_state.export_complexity_rows = []
    st.session_state.export_complexity_summary = ""
    st.session_state.multi_pass_exports = []


def _assigned_stems_signature(assigned_stems: dict[str, str]) -> str:
    """Build deterministic signature for assigned stem set."""
    pairs = [f"{name}:{path}" for name, path in sorted(assigned_stems.items())]
    return "|".join(pairs)


def _apply_profile_defaults(profile_name: str) -> None:
    """Apply simplification defaults for the given profile to session options."""
    defaults = SIMPLIFY_PROFILES.get(profile_name)
    if not defaults:
        return
    st.session_state.opt_profile = profile_name
    st.session_state.opt_profile_applied = profile_name
    st.session_state.opt_quantize_grid = defaults["quantize_grid"]
    st.session_state.opt_min_duration = float(defaults["min_note_duration_beats"])
    st.session_state.opt_density_threshold = int(defaults["density_threshold"])


def _assignment_guard_state(stems: dict, assignments: dict[str, str]) -> dict:
    """Return assignment quality guard metrics and warning messages."""
    stem_count = len(stems)
    assigned_names = [assignments.get(stem, "").strip() for stem in stems if assignments.get(stem, "").strip()]
    assigned_count = len(assigned_names)
    unassigned_count = max(stem_count - assigned_count, 0)
    unassigned_ratio = (unassigned_count / stem_count) if stem_count else 0.0

    warnings: list[str] = []
    if stem_count >= 3 and unassigned_ratio >= 0.6:
        warnings.append(
            "Most stems are unassigned. Assign more stems if the export seems too sparse."
        )
    unique_instruments = sorted(set(assigned_names))
    if assigned_count >= 2 and len(unique_instruments) == 1:
        warnings.append(
            "All assigned stems map to one instrument. This can produce a narrow arrangement."
        )

    return {
        "stem_count": stem_count,
        "assigned_count": assigned_count,
        "unassigned_count": unassigned_count,
        "warnings": warnings,
    }


def _format_size(num_bytes: int) -> str:
    """Render byte size as a short human-readable string."""
    units = ("B", "KB", "MB", "GB")
    value = float(num_bytes)
    unit = units[0]
    for candidate in units:
        unit = candidate
        if value < 1024.0 or candidate == units[-1]:
            break
        value /= 1024.0
    if unit == "B":
        return f"{int(value)} {unit}"
    return f"{value:.1f} {unit}"


def _format_elapsed_since(iso_timestamp: str) -> str:
    """Return short elapsed text from an ISO timestamp."""
    if not iso_timestamp:
        return "n/a"
    try:
        then = datetime.fromisoformat(iso_timestamp)
    except ValueError:
        return "n/a"
    delta = datetime.now() - then
    seconds = int(max(delta.total_seconds(), 0))
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def _render_preflight() -> None:
    st.subheader("Environment Check")
    if st.button("Run Preflight Checks", use_container_width=True):
        previous_snapshot = st.session_state.preflight_snapshot or {}
        st.session_state.preflight = run_preflight_checks(REQUIRED_TOOLS)
        st.session_state.preflight_last_run_ts = datetime.now().isoformat(timespec="seconds")
        tool_paths = get_tool_paths(REQUIRED_TOOLS)
        path_by_name = {item["name"]: item.get("path") for item in tool_paths}
        current_snapshot = {
            check["name"]: {
                "status": check["status"],
                "path": path_by_name.get(check["name"]),
            }
            for check in st.session_state.preflight
        }
        st.session_state.preflight_snapshot = current_snapshot

        if previous_snapshot:
            changed_tools: list[str] = []
            all_names = sorted(set(previous_snapshot.keys()) | set(current_snapshot.keys()))
            for name in all_names:
                if previous_snapshot.get(name) != current_snapshot.get(name):
                    changed_tools.append(name)
            if changed_tools:
                st.session_state.preflight_change_indicator = (
                    f"Changed since last preflight: {', '.join(changed_tools)}"
                )
            else:
                st.session_state.preflight_change_indicator = "No change since last preflight."
        else:
            st.session_state.preflight_change_indicator = "Baseline preflight captured."

    if not st.session_state.preflight:
        st.info("Click above to verify required tools before running the pipeline.")
        return

    for check in st.session_state.preflight:
        icon = "+" if check["status"] == "pass" else "-"
        st.markdown(f"- [{icon}] **{check['name']}**: {check['message']}")

    preflight_ts = st.session_state.get("preflight_last_run_ts", "")
    preflight_age = _format_elapsed_since(preflight_ts)
    if preflight_ts:
        st.caption(f"Preflight freshness: last run `{preflight_ts}` ({preflight_age})")
        try:
            age_minutes = (datetime.now() - datetime.fromisoformat(preflight_ts)).total_seconds() / 60.0
        except ValueError:
            age_minutes = 0.0
        if age_minutes >= 30:
            st.info("Preflight result may be stale (30m+). Consider rerunning checks.")

    change_indicator = st.session_state.preflight_change_indicator
    if change_indicator:
        if change_indicator.startswith("Changed since last preflight:"):
            st.warning(change_indicator)
            st.caption("Environment appears to have changed. Re-run preflight after setup/path updates.")
        else:
            st.caption(change_indicator)

    if _preflight_ok():
        st.success("All required tools found.")
    else:
        st.error("Some required tools are missing. Install them before running the pipeline.")


def _render_input_stage() -> None:
    st.subheader("1) Input")
    st.caption("Preparing audio starts a new run ID and run workspace.")
    source_mode = st.radio("Choose input source", ["Local audio file", "YouTube URL"], horizontal=True)

    if source_mode == "Local audio file":
        uploaded = st.file_uploader(
            "Upload MP3, AAC, WAV, M4A, or FLAC",
            type=[ext.replace(".", "") for ext in SUPPORTED_AUDIO_EXTENSIONS],
        )
        if st.button("Prepare Uploaded Audio (Start Run)", type="primary", use_container_width=True):
            local_error = _validate_local_upload(uploaded)
            if local_error:
                st.error(local_error)
                return
            try:
                run_dir = _new_run()
                source_path = _save_uploaded_file(uploaded, run_dir)
                st.session_state.wav_path = download_or_convert_audio(source_path, run_dir=run_dir)
                st.session_state.source_type = "local"
                st.session_state.source_value = uploaded.name
                st.success("Audio prepared.")
            except Exception as exc:
                _show_stage_error(
                    "Input preparation",
                    exc,
                    "Confirm the file is readable and supported (MP3/AAC/WAV/M4A/FLAC), then retry.",
                )
    else:
        youtube_url = st.text_input("Single-video YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        if st.button("Prepare YouTube Audio (Start Run)", type="primary", use_container_width=True):
            youtube_error = _validate_youtube_url(youtube_url)
            if youtube_error:
                st.error(youtube_error)
                return
            try:
                run_dir = _new_run()
                st.session_state.wav_path = download_or_convert_audio(youtube_url.strip(), run_dir=run_dir)
                st.session_state.source_type = "youtube"
                st.session_state.source_value = youtube_url.strip()
                st.success("Audio downloaded and prepared.")
            except Exception as exc:
                _show_stage_error(
                    "YouTube audio preparation",
                    exc,
                    "Use a single-video URL (not playlist) and verify network access/URL validity.",
                )

    if st.session_state.wav_path:
        st.caption(f"Prepared WAV: {st.session_state.wav_path}")


def _render_stem_stage() -> None:
    st.subheader("2) Stem Separation + Instrument Assignment")
    if not st.session_state.wav_path:
        st.info("Complete step 1 first.")
        return

    if st.button("Separate Stems", use_container_width=True):
        try:
            with st.spinner("Running Demucs..."):
                st.session_state.stems = separate_stems(
                    st.session_state.wav_path, run_dir=_current_run_dir(),
                )
            st.success("Stems generated.")
        except Exception as exc:
            _show_stage_error(
                "Stem separation",
                exc,
                "Verify `demucs` is installed and rerun preflight checks.",
            )
            return

    stems = st.session_state.stems
    if not stems:
        st.caption("No stems yet.")
        return

    st.write("Assign each stem to a target instrument:")
    for stem_name in sorted(stems.keys()):
        key = f"assignment_{stem_name}"
        default_value = st.session_state.assignments.get(stem_name, "Unassigned")
        options = ["Unassigned"] + STANDARD_INSTRUMENTS
        if default_value not in options:
            default_value = "Unassigned"
        selected = st.selectbox(
            f"{stem_name}",
            options=options,
            index=options.index(default_value),
            key=key,
        )
        st.session_state.assignments[stem_name] = "" if selected == "Unassigned" else selected

    guard = _assignment_guard_state(stems, st.session_state.assignments)
    st.caption(
        f"Assignment coverage: {guard['assigned_count']} assigned / "
        f"{guard['unassigned_count']} unassigned stem(s)."
    )
    for message in guard["warnings"]:
        st.warning(message)


def _render_options_stage() -> dict:
    st.subheader("3) Score Options")
    title = st.text_input("Song Title", key="opt_title")
    composer = st.text_input("Composer", key="opt_composer")
    school = st.text_input("School / Teacher Name", key="opt_school")

    simplify_enabled = st.checkbox("Student Simplification Mode", key="opt_simplify_enabled")

    profile_names = [name for name in TEACHER_VISIBLE_PROFILES if name in SIMPLIFY_PROFILES]
    if not profile_names:
        profile_names = [DEFAULT_PROFILE]
    st.session_state.opt_profile = _normalize_profile_name(st.session_state.opt_profile)
    st.session_state.opt_profile_applied = _normalize_profile_name(st.session_state.opt_profile_applied)
    if st.session_state.opt_profile not in profile_names:
        st.session_state.opt_profile = DEFAULT_PROFILE

    selected_profile = st.selectbox(
        "Simplification Profile",
        options=profile_names,
        index=profile_names.index(st.session_state.opt_profile),
        key="opt_profile",
    )
    profile_defaults = SIMPLIFY_PROFILES[selected_profile]
    if st.session_state.opt_profile_applied != selected_profile:
        st.session_state.opt_quantize_grid = profile_defaults["quantize_grid"]
        st.session_state.opt_min_duration = float(profile_defaults["min_note_duration_beats"])
        st.session_state.opt_density_threshold = int(profile_defaults["density_threshold"])
        st.session_state.opt_profile_applied = selected_profile

    default_quantize = profile_defaults["quantize_grid"]
    default_min_duration = float(profile_defaults["min_note_duration_beats"])
    default_density = int(profile_defaults["density_threshold"])

    with st.expander("Advanced Simplification Settings (overrides profile)"):
        quantize_grid = st.selectbox(
            "Quantize Grid",
            options=list(SIMPLIFY_ADVANCED_RANGES["quantize_grid"]),
            index=list(SIMPLIFY_ADVANCED_RANGES["quantize_grid"]).index(
                st.session_state.opt_quantize_grid
                if st.session_state.opt_quantize_grid in SIMPLIFY_ADVANCED_RANGES["quantize_grid"]
                else default_quantize
            ),
            key="opt_quantize_grid",
        )
        min_duration = st.slider(
            "Minimum Note Duration (beats)",
            min_value=float(SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"][0]),
            max_value=float(SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"][1]),
            value=(
                float(st.session_state.opt_min_duration)
                if float(SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"][0])
                <= float(st.session_state.opt_min_duration)
                <= float(SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"][1])
                else default_min_duration
            ),
            step=0.125,
            key="opt_min_duration",
        )
        density_threshold = st.slider(
            "Rhythmic Density Threshold (onsets per beat window)",
            min_value=int(SIMPLIFY_ADVANCED_RANGES["density_threshold"][0]),
            max_value=int(SIMPLIFY_ADVANCED_RANGES["density_threshold"][1]),
            value=(
                int(st.session_state.opt_density_threshold)
                if int(SIMPLIFY_ADVANCED_RANGES["density_threshold"][0])
                <= int(st.session_state.opt_density_threshold)
                <= int(SIMPLIFY_ADVANCED_RANGES["density_threshold"][1])
                else default_density
            ),
            step=1,
            key="opt_density_threshold",
        )
        if st.button("Reset Advanced to Selected Profile", use_container_width=True):
            st.session_state.opt_quantize_grid = profile_defaults["quantize_grid"]
            st.session_state.opt_min_duration = float(profile_defaults["min_note_duration_beats"])
            st.session_state.opt_density_threshold = int(profile_defaults["density_threshold"])
            st.rerun()

    options = {
        "title": title,
        "composer": composer,
        "school": school,
        "simplify_enabled": simplify_enabled,
        "profile": selected_profile,
        "quantize_grid": quantize_grid,
        "min_note_duration_beats": min_duration,
        "density_threshold": density_threshold,
    }
    _render_simplification_guardrails(options)
    return options


def _render_simplification_guardrails(options: dict) -> None:
    """Show non-blocking warnings for unusually risky simplification settings."""
    if not options.get("simplify_enabled", False):
        return

    grid = options.get("quantize_grid")
    min_duration = float(options.get("min_note_duration_beats", 0.25))
    density = int(options.get("density_threshold", 6))

    if grid == "1/4" and min_duration >= 0.5:
        st.warning(
            "Beginner-level simplification selected: quarter-note grid + long minimum duration can remove many notes."
        )
    if density <= 4:
        st.warning(
            "Low density threshold may prune busy passages heavily. Increase threshold if parts become too sparse."
        )
    if grid == "1/16" and min_duration <= 0.125 and density >= 9:
        st.info(
            "Very light simplification selected: output may remain rhythmically dense for younger players."
        )


def _render_run_summary() -> None:
    """Show a compact summary of the most recent export."""
    if st.session_state.get("multi_pass_exports"):
        count = len(st.session_state.multi_pass_exports)
        st.info(f"Two-pass export complete: {count} profile package(s) generated.")
        return
    if not st.session_state.run_id or not st.session_state.part_report:
        return
    exported = sum(1 for item in st.session_state.part_report if item.get("status") == "exported")
    skipped = sum(1 for item in st.session_state.part_report if item.get("status") != "exported")
    st.info(f"Run `{st.session_state.run_id}` complete: {exported} parts exported, {skipped} skipped.")


def _render_workflow_snapshot() -> None:
    """Show a compact read-only stage snapshot for quick orientation."""
    preflight_ready = bool(st.session_state.preflight) and _preflight_ok()
    input_ready = bool(st.session_state.wav_path)
    stems_ready = bool(st.session_state.stems)
    assigned_count = sum(
        1
        for stem in st.session_state.stems
        if st.session_state.assignments.get(stem, "").strip()
    )
    assignment_ready = assigned_count > 0
    export_ready = bool(st.session_state.export_last_ok and st.session_state.zip_path)
    fit_ready = bool(st.session_state.get("fit_analysis")) and bool(
        st.session_state.get("fit_analysis_signature")
    )
    fit_label = ""
    if fit_ready:
        fit_label = str((st.session_state.get("fit_analysis") or {}).get("fit_label", ""))

    def mark(ok: bool) -> str:
        return "[x]" if ok else "[ ]"

    st.caption(
        "Workflow snapshot: "
        f"{mark(preflight_ready)} preflight | "
        f"{mark(input_ready)} input | "
        f"{mark(stems_ready)} stems | "
        f"{mark(assignment_ready)} assignments | "
        f"{mark(fit_ready)} fit{f'({fit_label})' if fit_label else ''} | "
        f"{mark(export_ready)} export"
    )


def _render_export_artifact_summary() -> None:
    """Show ZIP artifact details for the successful run."""
    zip_path_val = st.session_state.zip_path
    if not zip_path_val:
        return
    zip_path = Path(zip_path_val)
    if not zip_path.exists():
        return
    size = _format_size(zip_path.stat().st_size)
    st.caption(f"Export artifact: `{zip_path.name}` | {size} | run `{st.session_state.run_id}`")


def _render_diagnostics_panel() -> None:
    """Read-only diagnostics for environment and latest run pointers."""
    with st.expander("Diagnostics", expanded=False):
        now_stamp = datetime.now().isoformat(timespec="seconds")
        if not st.session_state.get("diagnostics_probe_last_run_ts"):
            st.session_state.diagnostics_probe_cache = {
                "tool_versions": get_tool_versions(),
                "tool_paths": get_tool_paths(REQUIRED_TOOLS),
            }
            st.session_state.diagnostics_probe_last_run_ts = now_stamp

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Refresh Diagnostics Probe", use_container_width=True):
                refreshed_at = datetime.now().isoformat(timespec="seconds")
                st.session_state.diagnostics_probe_cache = {
                    "tool_versions": get_tool_versions(),
                    "tool_paths": get_tool_paths(REQUIRED_TOOLS),
                }
                st.session_state.diagnostics_probe_last_run_ts = refreshed_at
        with col2:
            last_probe = st.session_state.get("diagnostics_probe_last_run_ts", "")
            st.caption(f"Probe last refreshed: `{last_probe or 'n/a'}`")

        probe_cache = st.session_state.get("diagnostics_probe_cache") or {}
        tool_versions = probe_cache.get("tool_versions") or {}
        tool_paths = probe_cache.get("tool_paths") or []
        status_map = {item["name"]: ("pass" if item["path"] else "fail") for item in tool_paths}
        for item in st.session_state.preflight:
            status_map[item["name"]] = item["status"]

        st.markdown(f"- Python: `{tool_versions.get('python', 'unknown')}`")
        st.markdown(f"- App Version: `{APP_VERSION}`")
        st.markdown(f"- Demucs Model: `{DEMUCS_MODEL}`")
        st.markdown(f"- Latest Run ID: `{st.session_state.run_id or 'n/a'}`")
        st.markdown(f"- Latest ZIP: `{st.session_state.zip_path or 'n/a'}`")
        preflight_ts = st.session_state.get("preflight_last_run_ts", "")
        preflight_age = _format_elapsed_since(preflight_ts)
        st.markdown(f"- Preflight Last Run: `{preflight_ts or 'n/a'}`")
        st.markdown(f"- Preflight Age: `{preflight_age}`")
        st.markdown("**Tool Availability**")
        for name, status in status_map.items():
            icon = "PASS" if status == "pass" else "FAIL"
            st.markdown(f"- `{name}`: `{icon}`")
        st.markdown("**Executable Paths**")
        for item in tool_paths:
            st.markdown(f"- `{item['name']}`: `{item['path'] or 'not found'}`")
        if st.session_state.export_integrity_warning:
            st.warning(st.session_state.export_integrity_warning)

        summary_lines = [
            "BTT Diagnostics Snapshot",
            f"Generated: {now_stamp}",
            f"Python: {tool_versions.get('python', 'unknown')}",
            f"App Version: {APP_VERSION}",
            f"Demucs Model: {DEMUCS_MODEL}",
            f"Latest Run ID: {st.session_state.run_id or 'n/a'}",
            f"Latest ZIP: {st.session_state.zip_path or 'n/a'}",
            f"Preflight Last Run: {preflight_ts or 'n/a'}",
            f"Preflight Age: {preflight_age}",
            "Tool Availability:",
        ]
        for name, status in status_map.items():
            summary_lines.append(f"- {name}: {status}")
        summary_lines.append("Executable Paths:")
        for item in tool_paths:
            summary_lines.append(f"- {item['name']}: {item['path'] or 'not found'}")
        if st.session_state.export_integrity_warning:
            summary_lines.append(f"Export Integrity Warning: {st.session_state.export_integrity_warning}")
        st.session_state.diagnostics_copy_summary = "\n".join(summary_lines)
        st.text_area(
            "Copyable Diagnostics Summary",
            key="diagnostics_copy_summary",
            height=200,
            help="Copy this snapshot when reporting setup or environment issues.",
        )


def _shorten(value: str, max_len: int = 48) -> str:
    if len(value) <= max_len:
        return value
    return f"{value[:max_len - 3]}..."


def _format_selected_run_part_summary(parts_block: object) -> str:
    """Build a concise part-level summary from manifest parts."""
    if not isinstance(parts_block, list):
        return "Part details unavailable."

    exported = 0
    skipped = 0
    reason_counts: dict[str, int] = {}
    for item in parts_block:
        if not isinstance(item, dict):
            continue
        if item.get("status") == "exported":
            exported += 1
            continue
        skipped += 1
        reason = str(item.get("reason", "unknown"))
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    if not reason_counts:
        reasons_text = "none"
    else:
        sorted_reasons = sorted(reason_counts.items(), key=lambda pair: pair[0])
        reasons_text = ", ".join(f"{name} ({count})" for name, count in sorted_reasons[:3])

    return f"{exported} exported / {skipped} skipped | reasons: {reasons_text}"


def _apply_selected_run_options(options_block: object) -> tuple[list[str], list[str]]:
    """Apply valid manifest options to current session option keys."""
    if not isinstance(options_block, dict):
        return [], ["options block missing/invalid"]

    applied: list[str] = []
    invalid: list[str] = []

    profile = _normalize_profile_name(options_block.get("profile"))
    if isinstance(profile, str) and profile in SIMPLIFY_PROFILES:
        st.session_state.opt_profile = profile
        st.session_state.opt_profile_applied = profile
        applied.append("profile")
    elif profile is not None:
        invalid.append("profile")

    simplify_enabled = options_block.get("simplify_enabled")
    if isinstance(simplify_enabled, bool):
        st.session_state.opt_simplify_enabled = simplify_enabled
        applied.append("simplify_enabled")
    elif simplify_enabled is not None:
        invalid.append("simplify_enabled")

    grid = options_block.get("quantize_grid")
    valid_grids = set(SIMPLIFY_ADVANCED_RANGES["quantize_grid"])
    if isinstance(grid, str) and grid in valid_grids:
        st.session_state.opt_quantize_grid = grid
        applied.append("quantize_grid")
    elif grid is not None:
        invalid.append("quantize_grid")

    min_duration = options_block.get("min_note_duration_beats")
    try:
        min_duration_float = float(min_duration) if min_duration is not None else None
    except (TypeError, ValueError):
        min_duration_float = None
    min_low, min_high = SIMPLIFY_ADVANCED_RANGES["min_note_duration_beats"]
    if min_duration_float is not None and min_low <= min_duration_float <= min_high:
        st.session_state.opt_min_duration = min_duration_float
        applied.append("min_note_duration_beats")
    elif min_duration is not None:
        invalid.append("min_note_duration_beats")

    density = options_block.get("density_threshold")
    try:
        density_int = int(density) if density is not None else None
    except (TypeError, ValueError):
        density_int = None
    den_low, den_high = SIMPLIFY_ADVANCED_RANGES["density_threshold"]
    if density_int is not None and den_low <= density_int <= den_high:
        st.session_state.opt_density_threshold = density_int
        applied.append("density_threshold")
    elif density is not None:
        invalid.append("density_threshold")

    return applied, invalid


def _build_recent_runs_csv(records: list[dict]) -> str:
    """Build deterministic CSV text for recent-run records."""
    output = io.StringIO()
    fieldnames = [
        "run_id",
        "timestamp",
        "input_type",
        "input_value",
        "fit_label",
        "recommended_profile",
        "status",
        "exported_parts",
        "skipped_parts",
        "zip_filename",
        "zip_present",
        "manifest_status",
        "warning_count",
        "has_warnings",
        "warning_preview",
        "warning_categories",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for record in records:
        writer.writerow(
            {
                "run_id": str(record.get("run_id", "")),
                "timestamp": str(record.get("timestamp", "")),
                "input_type": str(record.get("input_type", "")),
                "input_value": str(record.get("input_value", "")),
                "fit_label": str(record.get("fit_label", "")),
                "recommended_profile": str(record.get("recommended_profile", "")),
                "status": str(record.get("status", "")),
                "exported_parts": int(record.get("exported_parts", 0)),
                "skipped_parts": int(record.get("skipped_parts", 0)),
                "zip_filename": str(record.get("zip_filename", "")),
                "zip_present": bool(record.get("zip_present", False)),
                "manifest_status": str(record.get("manifest_status", "")),
                "warning_count": int(record.get("warning_count", 0)),
                "has_warnings": bool(record.get("has_warnings", False)),
                "warning_preview": str(record.get("warning_preview", "")),
                "warning_categories": str(record.get("warning_categories", "")),
            }
        )
    return output.getvalue()


def _warning_category_from_message(message: str) -> str:
    text = (message or "").strip()
    if not text:
        return "unknown"
    head = text.split(":", 1)[0].strip().lower()
    if not head:
        return "unknown"
    return "_".join(head.split())


def _compute_run_manifest_signature(run_dirs: list[Path]) -> str:
    """Build a lightweight signature for run/manifest set change detection."""
    signature_parts: list[str] = []
    for run_dir in run_dirs:
        manifest_path = run_dir / "manifest.json"
        if manifest_path.exists():
            mtime = manifest_path.stat().st_mtime_ns
        else:
            mtime = -1
        signature_parts.append(f"{run_dir.name}:{mtime}")
    return "|".join(signature_parts)


def _render_recent_runs_panel() -> None:
    """Read-only summary of recent run manifests."""
    with st.expander("Recent Runs", expanded=False):
        run_dirs: list[Path] = []
        if RUNS_DIR.exists():
            run_dirs = [path for path in RUNS_DIR.iterdir() if path.is_dir()]
            run_dirs.sort(key=lambda path: path.name, reverse=True)
        if not run_dirs:
            st.caption("No recent run directories found.")
            return

        current_signature = _compute_run_manifest_signature(run_dirs)
        refresh_col, toggle_col, stamp_col = st.columns([1, 1, 2])
        force_refresh = False
        with refresh_col:
            if st.button("Refresh Run Cache", use_container_width=True):
                force_refresh = True
        with toggle_col:
            st.checkbox("Auto Refresh Run Cache", key="history_cache_auto_refresh")
        with stamp_col:
            last_refresh = st.session_state.get("history_manifest_cache_last_refresh", "")
            refresh_age = _format_elapsed_since(last_refresh) if last_refresh else "n/a"
            st.caption(
                f"Run cache last refreshed: `{last_refresh or 'n/a'}` ({refresh_age})"
            )

        signature_changed = st.session_state.get("history_manifest_cache_signature", "") != current_signature
        auto_refresh_enabled = bool(st.session_state.get("history_cache_auto_refresh", True))

        if (
            force_refresh
            or not st.session_state.get("history_manifest_cache")
            or (auto_refresh_enabled and signature_changed)
        ):
            cached_records: list[dict] = []
            for run_dir in run_dirs:
                loaded = load_run_manifest(RUNS_DIR, run_dir.name)
                record = {
                    "run_id": run_dir.name,
                    "timestamp": "",
                    "input_type": "",
                    "input_value": "",
                    "fit_label": "",
                    "recommended_profile": "",
                    "profile": "",
                    "simplify_enabled": False,
                    "exported_parts": 0,
                    "skipped_parts": 0,
                    "zip_filename": "",
                    "status": "unknown",
                    "manifest_status": loaded["status"],
                    "zip_present": False,
                    "warning_count": 0,
                    "has_warnings": False,
                    "warning_preview": "",
                    "warning_categories": "",
                }
                if loaded["status"] == "ok":
                    data = loaded["data"] or {}
                    outcome = data.get("outcome") or {}
                    zip_filename = str(outcome.get("zip_filename", "") or "")
                    zip_present = bool(zip_filename and (DOWNLOADS_DIR / zip_filename).exists())
                    integrity_warnings = outcome.get("integrity_warnings") or []
                    if not isinstance(integrity_warnings, list):
                        integrity_warnings = []
                    normalized_warnings = [str(item).strip() for item in integrity_warnings if str(item).strip()]
                    warning_count = len(normalized_warnings)
                    warning_preview = _shorten(normalized_warnings[0], 64) if normalized_warnings else ""
                    warning_category_tokens = sorted(
                        {_warning_category_from_message(msg) for msg in normalized_warnings}
                    )
                    record.update(
                        {
                            "run_id": str(data.get("run_id") or run_dir.name),
                            "timestamp": str(data.get("timestamp", "")),
                            "input_type": str((data.get("input") or {}).get("type", "")),
                            "input_value": str((data.get("input") or {}).get("value", "")),
                            "fit_label": str((data.get("options") or {}).get("fit_label", "")),
                            "recommended_profile": str((data.get("options") or {}).get("recommended_profile", "")),
                            "profile": str((data.get("options") or {}).get("profile", "")),
                            "simplify_enabled": bool((data.get("options") or {}).get("simplify_enabled", False)),
                            "exported_parts": int(outcome.get("exported_part_count", 0)),
                            "skipped_parts": int(outcome.get("skipped_part_count", 0)),
                            "zip_filename": zip_filename,
                            "status": str(data.get("status", "unknown")),
                            "zip_present": zip_present,
                            "warning_count": warning_count,
                            "has_warnings": warning_count > 0,
                            "warning_preview": warning_preview,
                            "warning_categories": ",".join(warning_category_tokens),
                        }
                    )
                cached_records.append(record)

            st.session_state.history_manifest_cache = cached_records
            st.session_state.history_manifest_cache_signature = current_signature
            st.session_state.history_manifest_cache_last_refresh = datetime.now().isoformat(timespec="seconds")
            signature_changed = False

        base_records = list(st.session_state.get("history_manifest_cache") or [])

        last_refresh = st.session_state.get("history_manifest_cache_last_refresh", "")
        if last_refresh:
            try:
                age_minutes = (
                    datetime.now() - datetime.fromisoformat(last_refresh)
                ).total_seconds() / 60.0
            except ValueError:
                age_minutes = 0.0
            if age_minutes >= 15:
                st.info("Run cache may be stale (15m+). Consider refreshing before review/export checks.")
        if signature_changed and not auto_refresh_enabled:
            st.info(
                "Run cache differs from on-disk manifests. Auto refresh is off; click 'Refresh Run Cache' to sync."
            )

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            input_filter = st.selectbox(
                "Input Type",
                options=("all", "local", "youtube"),
                key="history_input_filter",
            )
        with col2:
            status_filter = st.selectbox(
                "Status",
                options=("all", "success", "failed", "unknown"),
                key="history_status_filter",
            )
        with col3:
            warning_filter = st.selectbox(
                "Warning State",
                options=("all", "with_warnings", "no_warnings"),
                key="history_warning_filter",
            )
        with col4:
            sort_mode = st.selectbox(
                "Sort",
                options=("newest_first", "warning_count_desc", "warning_count_asc"),
                key="history_sort_mode",
            )
        with col5:
            st.selectbox(
                "History Limit",
                options=(5, 10, 20),
                key="history_limit",
            )
        run_id_query = st.text_input(
            "Run ID Search",
            key="history_run_id_query",
            placeholder="Filter by run ID (partial match)",
        ).strip().lower()
        warning_category_query = st.text_input(
            "Warning Category Filter",
            key="history_warning_category_query",
            placeholder="Filter warning categories (for example: zip_consistency_warning)",
        ).strip().lower()
        filtered_records: list[dict] = []
        for record in base_records:
            if input_filter != "all" and record["input_type"] != input_filter:
                continue
            if status_filter != "all" and record["status"] != status_filter:
                continue
            if warning_filter == "with_warnings" and not record["has_warnings"]:
                continue
            if warning_filter == "no_warnings" and record["has_warnings"]:
                continue
            if warning_category_query:
                categories_text = str(record.get("warning_categories", "")).lower()
                if warning_category_query not in categories_text:
                    continue
            if run_id_query and run_id_query not in record["run_id"].lower():
                continue
            filtered_records.append(record)

        if not filtered_records:
            st.caption("No runs match the current filters.")
            return

        if sort_mode == "warning_count_desc":
            filtered_records.sort(
                key=lambda row: (-int(row.get("warning_count", 0)), str(row.get("run_id", ""))),
                reverse=False,
            )
        elif sort_mode == "warning_count_asc":
            filtered_records.sort(
                key=lambda row: (int(row.get("warning_count", 0)), str(row.get("run_id", ""))),
                reverse=False,
            )
        else:
            filtered_records.sort(key=lambda row: str(row.get("run_id", "")), reverse=True)

        matched_count = len(filtered_records)
        displayed_records = filtered_records[: int(st.session_state.history_limit)]

        runs_loaded = len(displayed_records)
        readable_count = sum(1 for item in displayed_records if item["manifest_status"] == "ok")
        unreadable_count = runs_loaded - readable_count
        zip_present_count = sum(1 for item in displayed_records if item["zip_present"])
        zip_missing_count = runs_loaded - zip_present_count
        warning_run_count = sum(1 for item in displayed_records if item["has_warnings"])
        warning_category_totals: dict[str, int] = {}
        for item in displayed_records:
            categories = str(item.get("warning_categories", "")).split(",")
            for category in categories:
                token = category.strip()
                if not token:
                    continue
                warning_category_totals[token] = warning_category_totals.get(token, 0) + 1
        rollup_pairs = sorted(warning_category_totals.items(), key=lambda pair: pair[0])
        rollup_text = ", ".join(f"{name}={count}" for name, count in rollup_pairs) if rollup_pairs else "none"
        st.caption(
            "Health (current filtered set): "
            f"{matched_count} matched / {runs_loaded} shown | "
            f"{readable_count} readable manifest(s) | "
            f"{unreadable_count} missing/corrupt manifest(s) | "
            f"{zip_present_count} ZIP present | "
            f"{zip_missing_count} ZIP missing | "
            f"{warning_run_count} run(s) with warnings"
        )
        st.caption(f"Warning category rollup: {rollup_text}")
        st.text_input(
            "Session Note (optional)",
            key="history_session_note",
            placeholder="Optional note for copyable run summary",
        )

        summary_lines = [
            "BTT Recent Runs Summary",
            f"Generated: {datetime.now().isoformat(timespec='seconds')}",
            (
                "Filters: "
                f"input={input_filter}, status={status_filter}, "
                f"warnings={warning_filter}, warning_category='{warning_category_query or '-'}', "
                f"sort={sort_mode}, "
                f"search='{run_id_query or '-'}', "
                f"limit={int(st.session_state.history_limit)}"
            ),
            (
                "Health: "
                f"matched={matched_count}, shown={runs_loaded}, "
                f"readable={readable_count}, unreadable={unreadable_count}, "
                f"zip_present={zip_present_count}, zip_missing={zip_missing_count}, "
                f"with_warnings={warning_run_count}"
            ),
            f"Warning Categories: {rollup_text}",
            "Runs:",
        ]
        for row in displayed_records[:5]:
            summary_lines.append(
                f"- {row['run_id']} | status={row['status']} | "
                f"fit={row.get('fit_label') or '-'} | rec={row.get('recommended_profile') or '-'} | "
                f"parts={row['exported_parts']}/{row['skipped_parts']} | "
                f"warnings={row['warning_count']} | "
                f"warning_preview='{row['warning_preview'] or '-'}' | "
                f"zip={'present' if row['zip_present'] else 'missing'} | "
                f"manifest={row['manifest_status']}"
            )
        note = st.session_state.history_session_note.strip()
        if note:
            summary_lines.append(f"Note: {note}")
        st.session_state.history_copy_summary = "\n".join(summary_lines)
        st.text_area(
            "Copyable Summary",
            key="history_copy_summary",
            height=180,
            help="Copy this block to share a concise current run-history snapshot.",
        )
        csv_payload = _build_recent_runs_csv(displayed_records)
        csv_name = f"recent_runs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.caption("CSV export is scoped to current filters/sort/limit (displayed set).")
        st.download_button(
            "Download CSV (Current Filtered Set)",
            data=csv_payload.encode("utf-8"),
            file_name=csv_name,
            mime="text/csv",
            use_container_width=True,
        )

        filtered = [item for item in displayed_records if item["manifest_status"] == "ok"]
        if not filtered:
            st.caption("No readable manifests match the current filters.")
            return

        table_rows = []
        status_labels = {"success": "Success", "unknown": "Unknown"}
        status_labels["failed"] = "Failed"
        manifest_labels = {"ok": "Readable", "missing": "Missing", "corrupt": "Corrupt"}
        for row in filtered:
            table_rows.append(
                {
                    "Run ID": _shorten(str(row["run_id"]), 32),
                    "Time": _shorten(str(row["timestamp"]), 24),
                    "Input Source": f"{row['input_type']}: {_shorten(str(row['input_value']), 40)}",
                    "Fit": _shorten(str(row.get("fit_label", "")) or "-", 14),
                    "Recommended": _shorten(str(row.get("recommended_profile", "")) or "-", 18),
                    "Simplification": f"{_shorten(str(row['profile']), 16)} ({'on' if row['simplify_enabled'] else 'off'})",
                    "Run Outcome": status_labels.get(str(row.get("status", "unknown")), "Unknown"),
                    "Parts": f"{row['exported_parts']} exported / {row['skipped_parts']} skipped",
                    "Warnings": ("None" if int(row.get("warning_count", 0)) == 0 else str(row["warning_count"])),
                    "Warning Categories": _shorten(str(row.get("warning_categories", "")) or "-", 36),
                    "Warning Preview": _shorten(str(row.get("warning_preview", "")) or "-", 40),
                    "Manifest": manifest_labels.get(str(row.get("manifest_status", "")), "Unknown"),
                    "ZIP": "Present" if row.get("zip_present") else "Missing",
                }
            )
        st.table(table_rows)
        run_ids = [row["run_id"] for row in filtered]
        if st.session_state.history_selected_run_id not in run_ids:
            st.session_state.history_selected_run_id = run_ids[0]

        selected_run_id = st.selectbox(
            "Inspect run",
            options=run_ids,
            key="history_selected_run_id",
        )
        _render_selected_run_details(selected_run_id)


def _render_selected_run_details(run_id: str) -> None:
    """Show detailed information for a selected run manifest and reopen ZIP if available."""
    loaded = load_run_manifest(RUNS_DIR, run_id)
    status = loaded["status"]

    st.markdown("**Selected Run Details**")
    if status == "missing":
        st.caption("Manifest not found for this run. It may have been pruned.")
        return
    if status == "corrupt":
        st.caption("Manifest could not be parsed for this run.")
        return

    manifest = loaded["data"] or {}
    input_block = manifest.get("input") or {}
    options = manifest.get("options") or {}
    outcome = manifest.get("outcome") or {}
    pipeline = manifest.get("pipeline") or {}

    st.markdown(f"- Run ID: `{manifest.get('run_id', run_id)}`")
    schema_version = manifest.get("schema_version")
    if manifest.get("legacy_schema", False):
        st.markdown("- Manifest Schema: `legacy (unversioned)`")
    else:
        st.markdown(f"- Manifest Schema: `{schema_version or 'n/a'}`")
    st.markdown(f"- Timestamp: `{manifest.get('timestamp', 'n/a')}`")
    st.markdown(f"- Input: `{input_block.get('type', 'n/a')}: {_shorten(str(input_block.get('value', 'n/a')), 96)}`")
    st.markdown(
        f"- Simplification: `{options.get('profile', 'n/a')}` "
        f"(`{'on' if options.get('simplify_enabled', False) else 'off'}`)"
    )
    fit_label = str(options.get("fit_label", "") or "")
    fit_score = options.get("fit_score")
    recommended_profile = str(options.get("recommended_profile", "") or "")
    if fit_label:
        st.markdown(
            f"- Song Fit: `{fit_label}`"
            f"{f' ({fit_score}/100)' if isinstance(fit_score, (int, float)) else ''}"
            f"{f' | recommended `{recommended_profile}`' if recommended_profile else ''}"
        )
    st.markdown(
        f"- Settings: grid `{options.get('quantize_grid', 'n/a')}`, "
        f"min duration `{options.get('min_note_duration_beats', 'n/a')}`, "
        f"density `{options.get('density_threshold', 'n/a')}`"
    )
    st.markdown(
        f"- Outcome: `{outcome.get('exported_part_count', 0)}` exported / "
        f"`{outcome.get('skipped_part_count', 0)}` skipped, "
        f"status `{manifest.get('status', 'unknown')}`"
    )
    failure_stage = str(outcome.get("failure_stage", "") or "")
    failure_summary = str(outcome.get("failure_summary", "") or "")
    if failure_stage or failure_summary:
        st.caption(
            f"Failure context: stage `{failure_stage or 'n/a'}` | "
            f"summary `{_shorten(failure_summary or 'n/a', 120)}`"
        )
    integrity_warnings = outcome.get("integrity_warnings") or []
    if integrity_warnings:
        st.warning(
            f"Manifest recorded {len(integrity_warnings)} export integrity warning(s) for this run."
        )
        for warning_text in integrity_warnings[:3]:
            st.caption(f"- {warning_text}")
        digest_lines = [
            f"BTT Warning Digest | run={manifest.get('run_id', run_id)}",
            f"Generated: {datetime.now().isoformat(timespec='seconds')}",
            f"Warning Count: {len(integrity_warnings)}",
            "Warnings:",
        ]
        for warning_text in integrity_warnings:
            digest_lines.append(f"- {warning_text}")
        st.session_state.history_warning_digest = "\n".join(digest_lines)
        st.text_area(
            "Copyable Warning Digest",
            key="history_warning_digest",
            height=140,
            help="Copy warning details for this selected run.",
        )
    else:
        st.session_state.history_warning_digest = ""
        st.caption("No manifest-recorded export integrity warnings.")
    st.markdown(
        f"- Pipeline: app `{pipeline.get('app_version', 'n/a')}`, "
        f"demucs `{pipeline.get('demucs_model', 'n/a')}`"
    )
    st.markdown(f"- Part Summary: `{_format_selected_run_part_summary(manifest.get('parts'))}`")

    if st.button(
        "Apply Settings to Current Options",
        use_container_width=True,
        key=f"apply_options_{run_id}",
    ):
        applied, invalid = _apply_selected_run_options(options)
        if applied:
            st.success(f"Applied settings: {', '.join(applied)}")
        else:
            st.info("No valid settings were found to apply from this run.")
        if invalid:
            st.caption(f"Ignored invalid fields: {', '.join(invalid)}")

    zip_filename = outcome.get("zip_filename", "")
    if not zip_filename:
        st.caption("No ZIP filename in manifest for this run.")
        return
    zip_path = DOWNLOADS_DIR / zip_filename
    if not zip_path.exists():
        st.caption("ZIP artifact not found in downloads folder for this run.")
        return
    zip_size = _format_size(zip_path.stat().st_size)
    st.caption(f"Found artifact: `{zip_path.name}` ({zip_size})")
    st.download_button(
        f"Re-download ZIP ({zip_path.name})",
        data=zip_path.read_bytes(),
        file_name=zip_path.name,
        mime="application/zip",
        use_container_width=True,
        key=f"reopen_zip_{run_id}",
    )


def _render_maintenance_panel() -> None:
    """Minimal local controls for pruning old run artifacts."""
    with st.expander("Run Artifact Maintenance", expanded=False):
        summary = run_storage_summary(RUNS_DIR)
        st.markdown(f"- Run directories: `{summary['count']}`")
        st.markdown(f"- Approx storage used: `{_format_size(summary['size_bytes'])}`")

        keep_latest_n = st.number_input(
            "Keep latest N runs",
            min_value=0,
            step=1,
            key="maintenance_keep_latest_n",
            help="Keeps newest run folders by run ID timestamp. Active run is always preserved.",
        )
        st.checkbox(
            "I understand pruning permanently deletes old run folders.",
            key="maintenance_confirm_prune",
        )
        if st.button("Prune Old Runs", use_container_width=True):
            if not st.session_state.maintenance_confirm_prune:
                st.error("Confirm deletion with the checkbox before pruning.")
                return
            result = prune_old_runs(
                runs_dir=RUNS_DIR,
                keep_latest_n=int(keep_latest_n),
                active_run_id=st.session_state.run_id,
            )
            deleted_count = result["deleted_count"]
            reclaimed_bytes = result["reclaimed_bytes"]
            if deleted_count:
                st.success(
                    f"Pruned {deleted_count} run(s), reclaimed {_format_size(reclaimed_bytes)}."
                )
            else:
                st.info("No runs were pruned with the current keep setting.")
            st.session_state.maintenance_confirm_prune = False
            st.rerun()


def _render_part_report() -> None:
    """Show QC summary table for generated parts."""
    report = st.session_state.part_report
    if not report:
        return

    st.markdown("**Part Summary**")
    has_skips = False
    for entry in report:
        name = entry["name"]
        status = entry["status"]
        notes = entry["note_count"]
        if status == "exported":
            st.markdown(f"- **{name}**: {notes} notes — exported")
        else:
            reason = entry.get("reason", "unknown")
            suggestion = "Review assignments and rerun."
            if reason == "unassigned":
                suggestion = "Assign this stem to an instrument, then rerun export."
            elif reason == "no_notes":
                suggestion = (
                    "Try a less aggressive profile (or relax advanced settings), then rerun."
                )
            elif reason == "missing_musicxml":
                suggestion = "Re-run export to regenerate part files."
            elif reason == "unplayable_beginner":
                suggestion = (
                    "Beginner gate blocked this part as not classroom-playable. "
                    "Try a different stem assignment or use Easy Intermediate."
                )
            st.warning(f"**{name}**: skipped ({reason}). {suggestion}")
            has_skips = True

    if has_skips:
        st.caption("Skipped parts were either unassigned or contained no notes after processing.")


def _compute_export_complexity_rows() -> list[dict]:
    """Build per-part complexity metrics from exported part MusicXML/PDF artifacts."""
    score_data = st.session_state.score_data if isinstance(st.session_state.score_data, dict) else {}
    part_xml_map = score_data.get("parts", {}) if isinstance(score_data.get("parts"), dict) else {}
    exported_parts = [
        item for item in st.session_state.part_report
        if isinstance(item, dict) and item.get("status") == "exported"
    ]
    if not exported_parts:
        return []

    from music21 import converter
    try:
        from music21 import beam

        beam.environLocal["warnings"] = 0
    except Exception:
        pass

    pdf_pages_by_name: dict[str, int] = {}
    try:
        from pypdf import PdfReader

        for item in exported_parts:
            pdf_path = Path(str(item.get("path", "")))
            if not pdf_path.exists():
                continue
            reader = PdfReader(str(pdf_path))
            pdf_pages_by_name[str(item.get("name", ""))] = len(reader.pages)
    except Exception:
        pass

    rows: list[dict] = []
    for item in exported_parts:
        part_name = str(item.get("name", ""))
        part_xml_path = Path(str(part_xml_map.get(part_name, "")))
        if not part_name or not part_xml_path.exists():
            continue
        is_percussion = any(token in part_name for token in ("Snare", "Bass Drum", "Percussion"))

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"Cannot put in an element with a missing voice tag .*",
                category=UserWarning,
            )
            parsed = converter.parse(str(part_xml_path))
        notes = list(parsed.recurse().notes)
        note_count = len(notes)
        fast_notes = sum(1 for note in notes if float(note.duration.quarterLength) <= 0.5)
        tuplet_notes = sum(1 for note in notes if note.duration.tuplets)
        accidental_notes = 0
        midi_line: list[int] = []
        for note in notes:
            if getattr(note, "isChord", False):
                pitches = list(getattr(note, "pitches", []) or [])
                accidental_notes += sum(1 for p in pitches if p.accidental is not None)
                if pitches:
                    midi_line.append(int(min(p.midi for p in pitches)))
            elif getattr(note, "isNote", False):
                pitch_obj = getattr(note, "pitch", None)
                if pitch_obj is not None and pitch_obj.accidental is not None:
                    accidental_notes += 1
                if pitch_obj is not None:
                    midi_line.append(int(pitch_obj.midi))
        avg_duration = (
            sum(float(note.duration.quarterLength) for note in notes) / note_count
            if note_count
            else 0.0
        )
        fast_ratio = (fast_notes / note_count) if note_count else 0.0
        tuplet_ratio = (tuplet_notes / note_count) if note_count else 0.0
        if is_percussion:
            accidental_density = 0.0
            large_leap_rate = 0.0
        else:
            accidental_density = (accidental_notes / note_count) if note_count else 0.0
            leaps = [abs(curr - prev) for prev, curr in zip(midi_line, midi_line[1:])]
            large_leap_rate = (
                sum(1 for value in leaps if value >= 8) / len(leaps)
                if leaps
                else 0.0
            )

        difficulty_score = (fast_ratio * 0.65) + (tuplet_ratio * 0.35)
        if difficulty_score >= 0.55:
            difficulty = "Hard"
        elif difficulty_score >= 0.30:
            difficulty = "Medium"
        else:
            difficulty = "Easy"

        rows.append(
            {
                "part": part_name,
                "notes": note_count,
                "fast_notes": fast_notes,
                "tuplets": tuplet_notes,
                "avg_duration": round(avg_duration, 2),
                "pages": pdf_pages_by_name.get(part_name, 0),
                "difficulty": difficulty,
                "difficulty_score": difficulty_score,
                "accidental_density": accidental_density,
                "large_leap_rate": large_leap_rate,
            }
        )

    rows.sort(key=lambda row: row["part"])
    return rows


def _summarize_export_complexity(rows: list[dict]) -> str:
    if not rows:
        return ""
    avg_score = sum(float(row["difficulty_score"]) for row in rows) / len(rows)
    if avg_score >= 0.55:
        overall = "Hard overall"
    elif avg_score >= 0.30:
        overall = "Medium overall"
    else:
        overall = "Easy overall"
    return (
        f"{overall} | avg complexity score {avg_score:.2f} | "
        "score blends fast-note density and tuplet density."
    )


def _render_complexity_summary() -> None:
    """Show teacher-facing complexity digest for exported parts."""
    rows = st.session_state.export_complexity_rows
    if not rows:
        return

    st.markdown("**Complexity Summary**")
    st.caption(st.session_state.export_complexity_summary)
    table_rows = []
    for row in rows:
        table_rows.append(
            {
                "Part": row["part"],
                "Difficulty": row["difficulty"],
                "Notes": row["notes"],
                "Fast Notes (<=1/8)": row["fast_notes"],
                "Tuplet Notes": row["tuplets"],
                "Accidental Density": round(float(row["accidental_density"]), 2),
                "Large Leap Rate (>=m6)": round(float(row["large_leap_rate"]), 2),
                "Avg Duration (beats)": row["avg_duration"],
                "Pages": row["pages"],
            }
        )
    st.table(table_rows)


def _render_song_fit_panel(assigned_stems: dict[str, str]) -> None:
    """Show pre-export transcription-feasibility analysis and recommendation controls."""
    signature = _assigned_stems_signature(assigned_stems)

    if st.button("Analyze Song Fit", use_container_width=True):
        try:
            cached_signature = st.session_state.get("fit_analysis_signature", "")
            if not st.session_state.get("midi_map") or cached_signature != signature:
                with st.spinner("Analyzing song fit (transcribing assigned stems)..."):
                    st.session_state.midi_map = transcribe_to_midi(assigned_stems, run_dir=_current_run_dir())
            fit_analysis = assess_song_fit(st.session_state.midi_map, st.session_state.assignments)
            st.session_state.fit_analysis = fit_analysis
            st.session_state.fit_analysis_signature = signature
            st.session_state.fit_analysis_profile_used = str(fit_analysis.get("recommended_profile", ""))
        except Exception as exc:
            _show_stage_error(
                "Song fit analysis",
                exc,
                "Verify assignments and tool setup, then retry.",
            )
            return

    cached_signature = st.session_state.get("fit_analysis_signature", "")
    cached = st.session_state.get("fit_analysis") if isinstance(st.session_state.get("fit_analysis"), dict) else {}
    if not cached or cached_signature != signature:
        st.caption("Run `Analyze Song Fit` for a pre-export transcription-feasibility recommendation.")
        return

    label = str(cached.get("fit_label", ""))
    score = int(cached.get("fit_score", 0))
    recommendation = str(cached.get("recommended_profile", "") or "")
    if label == "Good Fit":
        st.success(f"Song Fit: {label} ({score}/100)")
    elif label == "Borderline":
        st.warning(f"Song Fit: {label} ({score}/100)")
    else:
        st.error(f"Song Fit: {label} ({score}/100)")
        st.caption("Suggested next step: try different stem assignments or a cleaner source file.")

    if recommendation:
        st.info(f"Recommended profile: {recommendation}")
    reasons = cached.get("reasons") or []
    if isinstance(reasons, list):
        for reason in reasons[:4]:
            st.markdown(f"- {reason}")

    st.checkbox(
        "Auto-apply recommended profile at export",
        key="opt_auto_apply_recommendation",
        help="If enabled, export will use the recommendation from this fit analysis.",
    )


def _merge_fit_metadata(run_options: dict, assigned_stems: dict[str, str]) -> dict:
    """Attach cached fit metadata when it matches current assigned stems."""
    merged = dict(run_options)
    signature = _assigned_stems_signature(assigned_stems)
    fit = st.session_state.get("fit_analysis") if isinstance(st.session_state.get("fit_analysis"), dict) else {}
    fit_signature = st.session_state.get("fit_analysis_signature", "")
    if fit and fit_signature == signature:
        merged["fit_score"] = fit.get("fit_score")
        merged["fit_label"] = fit.get("fit_label")
        merged["recommended_profile"] = fit.get("recommended_profile")
    return merged


def _record_failed_run_manifest(
    run_dir: Path,
    run_id: str,
    options: dict,
    stage: str,
    exc: Exception,
) -> None:
    """Best-effort failed-run manifest write/update for early-stage failures."""
    failure_summary = str(exc).strip().split("\n")[0] or exc.__class__.__name__
    manifest_path = run_dir / "manifest.json"
    part_report: list[dict] = []
    for stem_name in st.session_state.stems:
        if not st.session_state.assignments.get(stem_name, "").strip():
            part_report.append(
                {"name": stem_name, "status": "skipped", "reason": "unassigned", "note_count": 0}
            )

    if not manifest_path.exists():
        write_run_manifest(
            manifest_path=manifest_path,
            run_id=run_id,
            source_type=st.session_state.source_type,
            source_value=st.session_state.source_value,
            options=options,
            assignments=st.session_state.assignments,
            part_report=part_report,
            pipeline={"app_version": APP_VERSION, "demucs_model": DEMUCS_MODEL},
            tool_versions=get_tool_versions(),
            zip_filename="",
            outcome_success=False,
        )
    set_manifest_outcome_success(manifest_path, False)
    set_manifest_outcome_failure_context(manifest_path, stage, failure_summary)


def _run_export(options: dict, assigned_stems: dict[str, str], run_dir: Path, run_id: str) -> bool:
    """Execute the transcribe -> score -> PDF -> manifest -> ZIP pipeline."""
    try:
        midi_map = st.session_state.get("midi_map")
        can_reuse = (
            isinstance(midi_map, dict)
            and set(midi_map.keys()) == set(assigned_stems.keys())
            and all(Path(str(path)).exists() for path in midi_map.values())
        )
        if can_reuse:
            st.caption("Reusing recent transcription output from fit analysis.")
        else:
            with st.spinner("Transcribing stems with Basic Pitch..."):
                st.session_state.midi_map = transcribe_to_midi(assigned_stems, run_dir=run_dir)
    except Exception as exc:
        try:
            _record_failed_run_manifest(run_dir, run_id, options, "transcription", exc)
        except Exception:
            pass
        _show_stage_error(
            "Transcription",
            exc,
            "Verify `basic-pitch` is installed and stems are valid WAV files, then retry.",
        )
        return False
    try:
        with st.spinner("Building score..."):
            st.session_state.score_data = build_score(
                st.session_state.midi_map,
                st.session_state.assignments,
                options,
                run_dir=run_dir,
            )
            st.session_state.musicxml_path = st.session_state.score_data["full_score"]
    except Exception as exc:
        try:
            _record_failed_run_manifest(run_dir, run_id, options, "score_build", exc)
        except Exception:
            pass
        _show_stage_error(
            "Score build",
            exc,
            "Check assignments and simplification settings, then rerun.",
        )
        return False
    try:
        with st.spinner("Rendering PDFs with MuseScore..."):
            render_result = render_pdfs(st.session_state.score_data, run_id=run_id)
            st.session_state.pdf_paths = render_result["paths"]
            st.session_state.part_report = render_result["part_report"]
            complexity_rows = _compute_export_complexity_rows()
            st.session_state.export_complexity_rows = complexity_rows
            st.session_state.export_complexity_summary = _summarize_export_complexity(complexity_rows)
    except Exception as exc:
        try:
            _record_failed_run_manifest(run_dir, run_id, options, "pdf_rendering", exc)
        except Exception:
            pass
        _show_stage_error(
            "PDF rendering",
            exc,
            "Verify `mscore` is available and exported parts contain notes.",
        )
        return False

    # Build unassigned-stem entries for manifest
    all_part_report = list(st.session_state.part_report)
    for stem_name in st.session_state.stems:
        if not st.session_state.assignments.get(stem_name, "").strip():
            all_part_report.append({
                "name": stem_name, "status": "skipped",
                "reason": "unassigned", "note_count": 0,
            })

    try:
        # Write manifest
        zip_name = f"{sanitize_filename(options['title'])}_{run_id}_exports.zip"
        manifest_path = write_run_manifest(
            manifest_path=run_dir / "manifest.json",
            run_id=run_id,
            source_type=st.session_state.source_type,
            source_value=st.session_state.source_value,
            options=options,
            assignments=st.session_state.assignments,
            part_report=all_part_report,
            pipeline={"app_version": APP_VERSION, "demucs_model": DEMUCS_MODEL},
            tool_versions=get_tool_versions(),
            zip_filename=zip_name,
            outcome_success=True,
        )
    except Exception as exc:
        try:
            _record_failed_run_manifest(run_dir, run_id, options, "manifest_write", exc)
        except Exception:
            pass
        _show_stage_error(
            "Manifest write",
            exc,
            "Check write permissions for the run directory and retry export.",
        )
        return False

    try:
        # Package ZIP (PDFs + MusicXML + manifest)
        st.session_state.zip_path = zip_outputs(
            st.session_state.pdf_paths + [st.session_state.musicxml_path, manifest_path],
            str(DOWNLOADS_DIR / zip_name),
        )
    except Exception as exc:
        try:
            set_manifest_outcome_success(Path(manifest_path), False)
            failure_summary = str(exc).strip().split("\n")[0] or exc.__class__.__name__
            set_manifest_outcome_failure_context(
                Path(manifest_path), "zip_packaging", failure_summary
            )
        except Exception:
            pass
        _show_stage_error(
            "ZIP packaging",
            exc,
            "Check output directory permissions and available disk space, then retry.",
        )
        return False

    # Non-blocking integrity warning: verify manifest outcome vs in-memory counts.
    warning_messages: list[str] = []
    try:
        import json

        manifest_data = json.loads(Path(manifest_path).read_text())
        outcome = manifest_data.get("outcome") or {}
        mem_exported, mem_skipped = part_report_counts(all_part_report)
        if (
            int(outcome.get("exported_part_count", -1)) != mem_exported
            or int(outcome.get("skipped_part_count", -1)) != mem_skipped
        ):
            warning_messages.append(
                "Export integrity warning: manifest outcome counts do not match the current part report."
            )
    except Exception:
        warning_messages.append(
            "Export integrity warning: could not validate manifest outcome consistency."
        )

    try:
        expected_part_pdfs = [
            Path(str(item.get("path", ""))).name
            for item in st.session_state.part_report
            if item.get("status") == "exported" and item.get("path")
        ]
        warning_messages.extend(
            inspect_export_zip(
                zip_path=st.session_state.zip_path,
                expected_musicxml_filename=Path(st.session_state.musicxml_path).name,
                expected_exported_part_count=sum(
                    1 for item in st.session_state.part_report if item.get("status") == "exported"
                ),
                expected_part_pdf_filenames=expected_part_pdfs,
            )
        )
    except Exception:
        warning_messages.append(
            "ZIP consistency warning: export completed but post-package consistency checks could not run."
        )

    try:
        set_manifest_outcome_integrity_warnings(Path(manifest_path), warning_messages)
    except Exception:
        warning_messages.append(
            "Manifest warning persistence note: export warnings could not be written to manifest."
        )

    st.session_state.export_integrity_warning = "\n".join(warning_messages)

    st.success(f"Export complete (run {run_id}).")
    return True


def _render_export_stage(options: dict) -> None:
    st.subheader("4) Transcribe + Export")
    st.caption("Exports a ZIP with score PDFs, full-score MusicXML, and manifest.")
    if not st.session_state.stems:
        st.info("Complete stem generation and assignments first.")
        return

    # Mandatory preflight gate
    if not st.session_state.preflight:
        st.warning("Run preflight checks above before transcribing.")
        return
    if not _preflight_ok():
        st.error("Cannot run: preflight checks have failures. Fix them and re-check above.")
        return

    assigned_stems = {
        stem: path
        for stem, path in st.session_state.stems.items()
        if st.session_state.assignments.get(stem, "").strip()
    }
    guard = _assignment_guard_state(st.session_state.stems, st.session_state.assignments)
    for message in guard["warnings"]:
        st.warning(message)

    _render_song_fit_panel(assigned_stems)
    two_pass_enabled = bool(options.get("simplify_enabled", False)) and bool(
        st.checkbox(
            "Two-pass export (generate Beginner and Easy Intermediate packages)",
            key="opt_two_pass_export",
            help="Runs both levels automatically and gives two ZIP downloads for side-by-side review.",
        )
    )

    if st.button("Transcribe + Export ZIP", type="primary", use_container_width=True):
        if guard["assigned_count"] <= 0 or not assigned_stems:
            st.error("Assign at least one stem to an instrument before exporting.")
            return
        try:
            _clear_export_outputs()
            if two_pass_enabled:
                pass_results: list[dict] = []
                for pass_profile in ("Beginner", "Easy Intermediate"):
                    run_dir = _new_run()
                    pass_options = dict(options)
                    _apply_profile_defaults(pass_profile)
                    pass_options["profile"] = pass_profile
                    pass_options["quantize_grid"] = st.session_state.opt_quantize_grid
                    pass_options["min_note_duration_beats"] = st.session_state.opt_min_duration
                    pass_options["density_threshold"] = st.session_state.opt_density_threshold
                    pass_options = _merge_fit_metadata(pass_options, assigned_stems)
                    ok = _run_export(pass_options, assigned_stems, run_dir, st.session_state.run_id)
                    result_entry = {
                        "profile": pass_profile,
                        "run_id": st.session_state.run_id,
                        "zip_path": st.session_state.zip_path if ok else "",
                        "ok": ok,
                    }
                    pass_results.append(result_entry)
                st.session_state.multi_pass_exports = pass_results
                st.session_state.export_last_ok = any(item.get("ok") for item in pass_results)
            else:
                run_options = _merge_fit_metadata(dict(options), assigned_stems)
                recommended_profile = str(run_options.get("recommended_profile", "") or "")
                if (
                    bool(st.session_state.get("opt_auto_apply_recommendation", True))
                    and bool(run_options.get("simplify_enabled", False))
                    and recommended_profile in TEACHER_VISIBLE_PROFILES
                    and run_options.get("profile") != recommended_profile
                ):
                    _apply_profile_defaults(recommended_profile)
                    run_options["profile"] = recommended_profile
                    run_options["quantize_grid"] = st.session_state.opt_quantize_grid
                    run_options["min_note_duration_beats"] = st.session_state.opt_min_duration
                    run_options["density_threshold"] = st.session_state.opt_density_threshold
                    st.info(f"Auto-applied recommended profile: {recommended_profile}")
                run_dir = _current_run_dir()
                if not run_dir:
                    st.error("No active run. Prepare audio input first.")
                    return
                st.session_state.export_last_ok = _run_export(
                    run_options, assigned_stems, run_dir, st.session_state.run_id
                )
        except Exception as exc:
            _show_stage_error(
                "Export pipeline",
                exc,
                "Retry export; if it persists, run preflight checks and review Diagnostics.",
            )
            st.session_state.export_last_ok = False
            return

    # Quick Rerun — reuse stems + assignments with new run ID and current settings
    if st.session_state.midi_map and assigned_stems:
        if st.button("Quick Rerun (same stems, new settings)", use_container_width=True):
            try:
                _clear_export_outputs()
                new_run_dir = _new_run()  # updates session_state.run_id
                rerun_options = _merge_fit_metadata(dict(options), assigned_stems)
                st.session_state.export_last_ok = _run_export(
                    rerun_options, assigned_stems, new_run_dir, st.session_state.run_id
                )
            except Exception as exc:
                _show_stage_error(
                    "Quick rerun",
                    exc,
                    "Retry with current stems/assignments or restart from input if needed.",
                )
                st.session_state.export_last_ok = False
                return

    # QC surface
    if st.session_state.export_last_ok:
        _render_run_summary()
        _render_export_artifact_summary()
        if st.session_state.export_integrity_warning:
            st.warning(st.session_state.export_integrity_warning)
        _render_part_report()
        _render_complexity_summary()

        if st.session_state.pdf_paths:
            st.write("Generated PDFs:")
            for path in st.session_state.pdf_paths:
                st.write(f"- {Path(path).name}")

        if st.session_state.zip_path and Path(st.session_state.zip_path).exists():
            zip_bytes = Path(st.session_state.zip_path).read_bytes()
            st.download_button(
                f"Download ZIP ({Path(st.session_state.zip_path).name})",
                data=zip_bytes,
                file_name=Path(st.session_state.zip_path).name,
                mime="application/zip",
                use_container_width=True,
            )
        multi_pass = st.session_state.get("multi_pass_exports") or []
        if isinstance(multi_pass, list) and multi_pass:
            st.markdown("**Two-Pass Packages**")
            for entry in multi_pass:
                profile_name = str(entry.get("profile", "Profile"))
                run_id = str(entry.get("run_id", ""))
                zip_path = Path(str(entry.get("zip_path", "")))
                if not zip_path.exists():
                    st.warning(f"{profile_name}: export failed or ZIP missing (run {run_id}).")
                    continue
                st.download_button(
                    f"Download {profile_name} ZIP ({zip_path.name})",
                    data=zip_path.read_bytes(),
                    file_name=zip_path.name,
                    mime="application/zip",
                    use_container_width=True,
                )


def main() -> None:
    st.set_page_config(page_title="Band Transcription Tool", layout="wide")
    st.title("Band Transcription Tool (MVP)")
    st.caption("Local-only assistant for middle school concert band transcription.")

    _init_state()
    if st.session_state.get("reset_workspace_clear_confirm_pending", False):
        # Must run before rendering the checkbox widget for this key.
        st.session_state.reset_confirm_temp_workspace = False
        st.session_state.reset_workspace_clear_confirm_pending = False
    _render_workflow_snapshot()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state.reset_workspace_notice:
            st.success(st.session_state.reset_workspace_notice)
            st.session_state.reset_workspace_notice = ""
        has_stems = bool(st.session_state.stems)
        has_outputs = bool(st.session_state.musicxml_path or st.session_state.pdf_paths or st.session_state.zip_path)
        st.caption(
            "Reset impact preview: "
            f"run `{st.session_state.run_id or 'n/a'}` | "
            f"stems {'yes' if has_stems else 'no'} | "
            f"outputs {'yes' if has_outputs else 'no'}"
        )
        st.checkbox(
            "I understand this clears temp workspace and current session pointers.",
            key="reset_confirm_temp_workspace",
        )
        if st.button("Reset Temp Workspace"):
            if not st.session_state.reset_confirm_temp_workspace:
                st.warning("Confirm reset with the checkbox before clearing workspace.")
                return
            cleanup_temp(str(TEMP_DIR))
            for key in (
                "wav_path",
                "source_type",
                "source_value",
                "stems",
                "assignments",
                "midi_map",
                "score_data",
                "musicxml_path",
                "pdf_paths",
                "part_report",
                "zip_path",
                "run_id",
                "run_dir",
                "export_last_ok",
                "export_integrity_warning",
                "export_complexity_rows",
                "export_complexity_summary",
                "fit_analysis",
                "fit_analysis_signature",
                "fit_analysis_profile_used",
                "multi_pass_exports",
            ):
                if key in ("stems", "assignments", "midi_map", "score_data", "fit_analysis"):
                    st.session_state[key] = {}
                elif key in ("pdf_paths", "part_report", "export_complexity_rows", "multi_pass_exports"):
                    st.session_state[key] = []
                elif key == "export_last_ok":
                    st.session_state[key] = False
                elif key in ("export_integrity_warning", "export_complexity_summary", "fit_analysis_signature", "fit_analysis_profile_used"):
                    st.session_state[key] = ""
                else:
                    st.session_state[key] = ""
            st.session_state.reset_workspace_notice = "Workspace reset."
            st.session_state.reset_workspace_clear_confirm_pending = True
            st.rerun()

    _render_preflight()
    _render_diagnostics_panel()
    _render_recent_runs_panel()
    _render_maintenance_panel()
    _render_input_stage()
    _render_stem_stage()
    options = _render_options_stage()
    _render_export_stage(options)


if __name__ == "__main__":
    main()
