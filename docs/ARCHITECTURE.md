# Architecture Overview: Band Transcription Tool (BTT)

This document is the short system map for the MVP. It describes component boundaries and data flow for a local-only deployment.

## System Components

### Core Services
- **Streamlit App** (`app.py`) - Local browser UI for input, options, assignment, progress, and download.
- **Pipeline Engine** (`pipeline.py`) - Orchestrates audio normalization, stem separation, transcription, score build, and export.
- **Config Layer** (`config.py`) - Central constants for paths, instrument catalog, and tool settings.
- **Utility Layer** (`utils.py`) - Shared helpers for cleanup, disclaimers, and output packaging.

### External Tooling (Local Process Calls)
- **FFmpeg / pydub** - Audio conversion and normalization.
- **yt-dlp** - YouTube single-video audio extraction (no playlists in MVP).
- **Demucs** - Stem separation.
- **Basic Pitch** - Audio-to-MIDI transcription per assigned stem.
- **music21** - Score assembly and transposition.
- **MuseScore CLI** - PDF rendering from MusicXML.

### Storage / Runtime Directories
- **Temporary working files**: `temp/`
- **Exported artifacts**: `outputs/` (optional persisted copies)
- **No remote data store** and **no cloud services** in MVP.

## Process Architecture
```text
Teacher (Browser @ localhost:8501)
  -> Streamlit UI (app.py)
  -> Pipeline Orchestrator (pipeline.py)
      -> Audio Normalize (ffmpeg/pydub or yt-dlp + ffmpeg)
      -> Stem Separation (demucs)
      -> MIDI Transcription (basic-pitch)
      -> Score Build + Transposition (music21)
      -> PDF Rendering (MuseScore CLI)
  -> ZIP Output (score + assigned/non-empty part PDFs)
```

All processing runs on the local machine after installation.

## Data Flow Examples

### Example: Local File to Score Package
```text
Teacher uploads MP3/AAC/WAV
-> convert to WAV
-> separate stems
-> teacher assigns stems to instruments
-> transcribe assigned stems to MIDI
-> build concert score + transposed parts
-> render conductor PDF + assigned/non-empty part PDFs
-> package ZIP for download
```

### Example: YouTube URL to Score Package
```text
Teacher submits single-video URL
-> yt-dlp extracts audio
-> convert to WAV
-> same downstream pipeline as local file path
```

## Key Abstractions
- **Input Source**: local file path or YouTube URL.
- **Stem Assignment Map**: `stem_name -> target_instrument`.
- **Transcription Options**:
  - Simplification preset (enabled/disabled)
  - Advanced simplification overrides (hidden toggle)
  - Metadata fields (title/composer/school)
- **Output Contract**:
  - 1 conductor score PDF (concert pitch)
  - N part PDFs where parts are both assigned and non-empty
  - Packaged ZIP for download

## Authentication & Authorization
- Not included in MVP by design.
- App is intended for trusted local usage by one teacher.

## Configuration
- Centralized in `config.py`.
- Expected config domains:
  - tool executable paths (MuseScore/ffmpeg if needed)
  - model choices (`htdemucs`/`htdemucs_6s`)
  - instrument definitions and transpositions
  - runtime directories (`temp/`, `outputs/`)
  - simplification defaults and advanced ranges

## Integration Points
- **CLI integrations** via subprocess calls:
  - `yt-dlp`
  - `demucs`
  - `MuseScore` executable
- **Python library integrations**:
  - `pydub`
  - `basic_pitch`
  - `music21`

Each integration must surface actionable errors to the UI stage where it fails.

## Runtime & Operations Notes
- Target runtime: local Windows machine (teacher), offline after dependency install.
- Dev environment: WSL/Linux is acceptable, but deployment behavior is validated on Windows.
- Priority order: transcription correctness and transposition accuracy over speed.
- Cleanup policy: clear temporary artifacts after run/session completion.

## Development Guidelines
- Keep orchestration in `pipeline.py`; keep UI concerns in `app.py`.
- Keep external command paths/config values out of business logic.
- Prefer additive, testable functions for each pipeline stage.
- Preserve deterministic behavior for simplification defaults.

## Related Docs
- Plan: `docs/plan.md`
- Manifest: `project-manifest.md`
- Active spec: `comms/tasks/2026-02-19-mvp-foundation-spec.md`
- Activity log: `comms/log.md`
