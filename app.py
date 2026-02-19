from __future__ import annotations

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
)
from pipeline import (
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
    list_recent_run_summaries,
    part_report_counts,
    run_preflight_checks,
    sanitize_filename,
    write_run_manifest,
    zip_outputs,
)


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
        "opt_title": "Untitled",
        "opt_composer": "",
        "opt_school": "",
        "opt_simplify_enabled": SIMPLIFY_PRESET["enabled"],
        "opt_profile": DEFAULT_PROFILE,
        "opt_profile_applied": DEFAULT_PROFILE,
        "opt_quantize_grid": SIMPLIFY_PRESET["quantize_grid"],
        "opt_min_duration": float(SIMPLIFY_PRESET["min_note_duration_beats"]),
        "opt_density_threshold": int(SIMPLIFY_PRESET["density_threshold"]),
        "export_last_ok": False,
        "export_integrity_warning": "",
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


def _clear_export_outputs() -> None:
    """Invalidate last export artifacts before a new export attempt."""
    st.session_state.musicxml_path = ""
    st.session_state.pdf_paths = []
    st.session_state.part_report = []
    st.session_state.zip_path = ""
    st.session_state.export_last_ok = False
    st.session_state.export_integrity_warning = ""


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


def _render_preflight() -> None:
    st.subheader("Environment Check")
    if st.button("Run Preflight Checks", use_container_width=True):
        st.session_state.preflight = run_preflight_checks(REQUIRED_TOOLS)

    if not st.session_state.preflight:
        st.info("Click above to verify required tools before running the pipeline.")
        return

    for check in st.session_state.preflight:
        icon = "+" if check["status"] == "pass" else "-"
        st.markdown(f"- [{icon}] **{check['name']}**: {check['message']}")

    if _preflight_ok():
        st.success("All required tools found.")
    else:
        st.error("Some required tools are missing. Install them before running the pipeline.")


def _render_input_stage() -> None:
    st.subheader("1) Input")
    source_mode = st.radio("Choose input source", ["Local audio file", "YouTube URL"], horizontal=True)

    if source_mode == "Local audio file":
        uploaded = st.file_uploader(
            "Upload MP3, AAC, WAV, M4A, or FLAC",
            type=[ext.replace(".", "") for ext in SUPPORTED_AUDIO_EXTENSIONS],
        )
        if st.button("Use Uploaded Audio", type="primary", use_container_width=True):
            if not uploaded:
                st.error("Please upload a file first.")
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
        if st.button("Use YouTube Audio", type="primary", use_container_width=True):
            if not youtube_url.strip():
                st.error("Please enter a URL first.")
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

    if st.button("Separate Stems with Demucs", use_container_width=True):
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


def _render_options_stage() -> dict:
    st.subheader("3) Score Options")
    title = st.text_input("Song Title", key="opt_title")
    composer = st.text_input("Composer", key="opt_composer")
    school = st.text_input("School / Teacher Name", key="opt_school")

    simplify_enabled = st.checkbox("Student Simplification Mode", key="opt_simplify_enabled")

    profile_names = list(SIMPLIFY_PROFILES.keys())
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
            "Aggressive simplification selected: quarter-note grid + long minimum duration can remove many notes."
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
    if not st.session_state.run_id or not st.session_state.part_report:
        return
    exported = sum(1 for item in st.session_state.part_report if item.get("status") == "exported")
    skipped = sum(1 for item in st.session_state.part_report if item.get("status") != "exported")
    st.info(f"Run `{st.session_state.run_id}` complete: {exported} parts exported, {skipped} skipped.")


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
        tool_versions = get_tool_versions()
        tool_paths = get_tool_paths(REQUIRED_TOOLS)
        status_map = {item["name"]: ("pass" if item["path"] else "fail") for item in tool_paths}
        for item in st.session_state.preflight:
            status_map[item["name"]] = item["status"]

        st.markdown(f"- Python: `{tool_versions.get('python', 'unknown')}`")
        st.markdown(f"- App Version: `{APP_VERSION}`")
        st.markdown(f"- Demucs Model: `{DEMUCS_MODEL}`")
        st.markdown(f"- Latest Run ID: `{st.session_state.run_id or 'n/a'}`")
        st.markdown(f"- Latest ZIP: `{st.session_state.zip_path or 'n/a'}`")
        st.markdown("**Tool Availability**")
        for name, status in status_map.items():
            icon = "PASS" if status == "pass" else "FAIL"
            st.markdown(f"- `{name}`: `{icon}`")
        st.markdown("**Executable Paths**")
        for item in tool_paths:
            st.markdown(f"- `{item['name']}`: `{item['path'] or 'not found'}`")
        if st.session_state.export_integrity_warning:
            st.warning(st.session_state.export_integrity_warning)


def _shorten(value: str, max_len: int = 48) -> str:
    if len(value) <= max_len:
        return value
    return f"{value[:max_len - 3]}..."


def _render_recent_runs_panel() -> None:
    """Read-only summary of recent run manifests."""
    with st.expander("Recent Runs", expanded=False):
        rows = list_recent_run_summaries(RUNS_DIR, limit=5)
        if not rows:
            st.caption("No recent run manifests found.")
            return

        table_rows = []
        for row in rows:
            table_rows.append(
                {
                    "run_id": row["run_id"],
                    "timestamp": row["timestamp"],
                    "input": f"{row['input_type']}: {_shorten(str(row['input_value']))}",
                    "simplify": f"{row['profile']} ({'on' if row['simplify_enabled'] else 'off'})",
                    "parts": f"{row['exported_parts']} exported / {row['skipped_parts']} skipped",
                    "zip": row["zip_filename"] or "n/a",
                }
            )
        st.table(table_rows)


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
            st.warning(f"**{name}**: skipped ({reason}). {suggestion}")
            has_skips = True

    if has_skips:
        st.caption("Skipped parts were either unassigned or contained no notes after processing.")


def _run_export(options: dict, assigned_stems: dict[str, str], run_dir: Path, run_id: str) -> bool:
    """Execute the transcribe -> score -> PDF -> manifest -> ZIP pipeline."""
    try:
        with st.spinner("Transcribing stems with Basic Pitch..."):
            st.session_state.midi_map = transcribe_to_midi(assigned_stems, run_dir=run_dir)
    except Exception as exc:
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
        _show_stage_error(
            "Score build",
            exc,
            "Check assignments and simplification settings, then rerun.",
        )
        return False
    try:
        with st.spinner("Rendering PDFs with MuseScore..."):
            render_result = render_pdfs(st.session_state.score_data)
            st.session_state.pdf_paths = render_result["paths"]
            st.session_state.part_report = render_result["part_report"]
    except Exception as exc:
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
        )
    except Exception as exc:
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
        _show_stage_error(
            "ZIP packaging",
            exc,
            "Check output directory permissions and available disk space, then retry.",
        )
        return False

    # Non-blocking integrity warning: verify manifest outcome vs in-memory counts.
    try:
        import json

        manifest_data = json.loads(Path(manifest_path).read_text())
        outcome = manifest_data.get("outcome") or {}
        mem_exported, mem_skipped = part_report_counts(all_part_report)
        if (
            int(outcome.get("exported_part_count", -1)) != mem_exported
            or int(outcome.get("skipped_part_count", -1)) != mem_skipped
        ):
            st.session_state.export_integrity_warning = (
                "Export integrity warning: manifest outcome counts do not match the current part report."
            )
    except Exception:
        st.session_state.export_integrity_warning = (
            "Export integrity warning: could not validate manifest outcome consistency."
        )

    st.success(f"Export complete (run {run_id}).")
    return True


def _render_export_stage(options: dict) -> None:
    st.subheader("4) Transcribe + Export")
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

    if st.button("Transcribe for Concert Band", type="primary", use_container_width=True):
        if not assigned_stems:
            st.error("Assign at least one stem to an instrument.")
            return
        try:
            _clear_export_outputs()
            run_dir = _current_run_dir()
            if not run_dir:
                st.error("No active run. Prepare audio input first.")
                return
            st.session_state.export_last_ok = _run_export(
                options, assigned_stems, run_dir, st.session_state.run_id
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
        if st.button("Quick Rerun (new settings, same stems)", use_container_width=True):
            try:
                _clear_export_outputs()
                new_run_dir = _new_run()  # updates session_state.run_id
                st.session_state.export_last_ok = _run_export(
                    options, assigned_stems, new_run_dir, st.session_state.run_id
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


def main() -> None:
    st.set_page_config(page_title="Band Transcription Tool", layout="wide")
    st.title("Band Transcription Tool (MVP)")
    st.caption("Local-only assistant for middle school concert band transcription.")

    _init_state()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Reset Temp Workspace"):
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
            ):
                if key in ("stems", "assignments", "midi_map", "score_data"):
                    st.session_state[key] = {}
                elif key in ("pdf_paths", "part_report"):
                    st.session_state[key] = []
                elif key == "export_last_ok":
                    st.session_state[key] = False
                elif key == "export_integrity_warning":
                    st.session_state[key] = ""
                else:
                    st.session_state[key] = ""
            st.success("Workspace reset.")

    _render_preflight()
    _render_diagnostics_panel()
    _render_recent_runs_panel()
    _render_input_stage()
    _render_stem_stage()
    options = _render_options_stage()
    _render_export_stage(options)


if __name__ == "__main__":
    main()
