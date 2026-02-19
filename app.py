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
                st.error(str(exc))
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
                st.error(str(exc))

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
            st.error(str(exc))
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

    return {
        "title": title,
        "composer": composer,
        "school": school,
        "simplify_enabled": simplify_enabled,
        "profile": selected_profile,
        "quantize_grid": quantize_grid,
        "min_note_duration_beats": min_duration,
        "density_threshold": density_threshold,
    }


def _render_run_summary() -> None:
    """Show a compact summary of the most recent export."""
    if not st.session_state.run_id or not st.session_state.part_report:
        return
    exported = sum(1 for item in st.session_state.part_report if item.get("status") == "exported")
    skipped = sum(1 for item in st.session_state.part_report if item.get("status") != "exported")
    st.info(f"Run `{st.session_state.run_id}` complete: {exported} parts exported, {skipped} skipped.")


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
            st.warning(f"**{name}**: skipped ({reason})")
            has_skips = True

    if has_skips:
        st.caption("Skipped parts were either unassigned or contained no notes after processing.")


def _run_export(options: dict, assigned_stems: dict[str, str], run_dir: Path, run_id: str) -> None:
    """Execute the transcribe -> score -> PDF -> manifest -> ZIP pipeline."""
    with st.spinner("Transcribing stems with Basic Pitch..."):
        st.session_state.midi_map = transcribe_to_midi(assigned_stems, run_dir=run_dir)
    with st.spinner("Building score..."):
        st.session_state.score_data = build_score(
            st.session_state.midi_map,
            st.session_state.assignments,
            options,
            run_dir=run_dir,
        )
        st.session_state.musicxml_path = st.session_state.score_data["full_score"]
    with st.spinner("Rendering PDFs with MuseScore..."):
        render_result = render_pdfs(st.session_state.score_data)
        st.session_state.pdf_paths = render_result["paths"]
        st.session_state.part_report = render_result["part_report"]

    # Build unassigned-stem entries for manifest
    all_part_report = list(st.session_state.part_report)
    for stem_name in st.session_state.stems:
        if not st.session_state.assignments.get(stem_name, "").strip():
            all_part_report.append({
                "name": stem_name, "status": "skipped",
                "reason": "unassigned", "note_count": 0,
            })

    # Write manifest
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
    )
    # Package ZIP (PDFs + MusicXML + manifest)
    zip_name = f"{sanitize_filename(options['title'])}_exports.zip"
    st.session_state.zip_path = zip_outputs(
        st.session_state.pdf_paths + [st.session_state.musicxml_path, manifest_path],
        str(DOWNLOADS_DIR / zip_name),
    )
    st.success(f"Export complete (run {run_id}).")


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
            run_dir = _current_run_dir()
            if not run_dir:
                st.error("No active run. Prepare audio input first.")
                return
            _run_export(options, assigned_stems, run_dir, st.session_state.run_id)
        except Exception as exc:
            st.error(str(exc))
            return

    # Quick Rerun — reuse stems + assignments with new run ID and current settings
    if st.session_state.midi_map and assigned_stems:
        if st.button("Quick Rerun (new settings, same stems)", use_container_width=True):
            try:
                new_run_dir = _new_run()  # updates session_state.run_id
                _run_export(options, assigned_stems, new_run_dir, st.session_state.run_id)
            except Exception as exc:
                st.error(str(exc))
                return

    # QC surface
    _render_run_summary()
    _render_part_report()

    if st.session_state.pdf_paths:
        st.write("Generated PDFs:")
        for path in st.session_state.pdf_paths:
            st.write(f"- {Path(path).name}")

    if st.session_state.zip_path and Path(st.session_state.zip_path).exists():
        zip_bytes = Path(st.session_state.zip_path).read_bytes()
        st.download_button(
            "Download ZIP",
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
            ):
                if key in ("stems", "assignments", "midi_map", "score_data"):
                    st.session_state[key] = {}
                elif key in ("pdf_paths", "part_report"):
                    st.session_state[key] = []
                else:
                    st.session_state[key] = ""
            st.success("Workspace reset.")

    _render_preflight()
    _render_diagnostics_panel()
    _render_input_stage()
    _render_stem_stage()
    options = _render_options_stage()
    _render_export_stage(options)


if __name__ == "__main__":
    main()
