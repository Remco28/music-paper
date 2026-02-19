# Task Spec: BTT MVP Foundation (Phase 1)

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Deliver a working local-first MVP of the Band Transcription Tool (BTT) that supports both local audio uploads and YouTube URL ingestion, producing:
- 1 conductor score PDF (concert pitch)
- 0..N individual part PDFs for assigned, non-empty parts only

No authentication in this phase.

## User Stories
1. As a band teacher, I can submit either a local audio file or a YouTube URL from one UI.
2. As a band teacher, I can map detected stems to concert-band instruments.
3. As a band teacher, I can generate a full score and only useful part PDFs (assigned/non-empty).
4. As a band teacher, I can enable simplification mode and optionally reveal advanced fine-tuning controls.
5. As a band teacher, I see clear educational-use disclaimers on exported PDFs.

## Rationale
This is the minimal path that proves the core product value: conversion from real-world audio to rehearsal-ready band materials. We avoid non-essential complexity (accounts/auth/multi-user concerns) and focus effort on the highest-risk technical path: stem separation, transcription quality, instrument mapping, and export correctness.

## In Scope
- Streamlit local app flow for:
  - local file upload
  - YouTube URL input and audio extraction
  - stem-to-instrument assignment
  - transcription options
  - export/download
- Pipeline integration:
  - Demucs stem separation
  - Basic Pitch MIDI transcription per stem
  - music21 score construction and transposition
  - MuseScore CLI PDF rendering
- Simplification controls:
  - default preset behavior
  - hidden "Advanced" toggle for fine tuning
- Disclaimer stamping with school/teacher metadata

## Out of Scope (Phase 1)
- Authentication/login
- Cloud services or paid APIs
- Batch processing/library management
- Automatic part-writing for unassigned stems

## Required Files to Create
- `app.py`
- `pipeline.py`
- `config.py`
- `utils.py`
- `requirements.txt`
- `start.bat`
- `README_for_teacher.md`

## Required Functions / Interfaces
- `pipeline.py`
  - `download_or_convert_audio(source: str) -> str`
  - `separate_stems(wav_path: str) -> dict[str, str]`
  - `transcribe_to_midi(stems: dict[str, str]) -> dict[str, str]`
  - `build_score(midis: dict[str, str], assignment: dict[str, str], options: dict) -> str`
  - `render_pdfs(musicxml_path: str, assignment: dict[str, str]) -> list[str]`
- `utils.py`
  - `cleanup_temp(temp_dir: str) -> None`
  - `create_disclaimer_text(school_name: str) -> str`
  - `zip_outputs(paths: list[str], zip_path: str) -> str`

## Functional Constraints
1. Input supports both:
   - local audio files (MP3/AAC/WAV minimum)
   - YouTube single-video URLs only (audio-only extraction, no playlists)
2. Export only assigned and non-empty parts.
3. No auth gate in app startup flow.
4. Simplification must include:
   - one-click preset mode
   - optional advanced controls hidden behind a toggle
5. Generated score/parts include educational-use disclaimer text.
6. App runs fully locally after dependencies are installed.

## Expected Behavior
1. User provides input audio (file or URL).
2. App normalizes to WAV.
3. Demucs produces stems.
4. User assigns stems to target instruments.
5. Basic Pitch transcribes each assigned stem.
6. music21 builds a score with correct transpositions.
7. If simplification enabled, apply preset; if advanced enabled, apply user-tuned parameters.
8. MuseScore CLI renders full score and per-part PDFs.
9. App packages outputs into ZIP and offers download.

## Simplification Behavior (Phase 1 Defaults)
- Preset defaults:
  - quantize grid: eighth note
  - remove note events shorter than a configurable minimum duration
  - suppress tuplet-like dense fragments via thresholding
- Advanced controls (hidden unless toggled):
  - quantize grid selector
  - minimum note duration
  - rhythmic density threshold

### Recommended Default Values (Architect Judgment)
- preset quantize grid: `1/8`
- preset minimum note duration: `0.25 beats`
- preset rhythmic density threshold: `6 onset events per beat-window`
- advanced ranges:
  - quantize grid: `1/4`, `1/8`, `1/16`
  - minimum note duration: `0.125` to `0.5 beats`
  - rhythmic density threshold: `3` to `10 onset events per beat-window`

## Acceptance Criteria
1. Both input paths (local file and YouTube URL) complete end-to-end.
2. Output includes conductor score PDF and assigned/non-empty part PDFs only.
3. No auth prompts exist.
4. Simplification preset works and advanced settings can override preset thresholds.
5. Disclaimers appear in exported documents.
6. Teacher validates quality as acceptable on at least 3 representative songs.

## Pseudocode (High Level)
```text
if source is youtube_url:
    wav = download_audio_from_youtube(source)
else:
    wav = convert_local_audio_to_wav(source)

stems = demucs_separate(wav)
assignments = ui_capture_stem_assignments(stems, standard_instruments)
selected_stems = keep_only_assigned(stems, assignments)

midis = {}
for stem in selected_stems:
    midis[stem] = basic_pitch_transcribe(stem)

score_xml = build_music21_score(midis, assignments, options)
pdfs = render_full_and_non_empty_parts(score_xml, assignments)
zip_path = package_outputs(pdfs, score_xml, optional_mscz)
return zip_path
```

## Review Notes for Developer
- Prioritize correctness of transposition and part extraction over runtime.
- Keep external tool paths configurable (Demucs/Basic Pitch/MuseScore).
- Handle failures with clear UI messages at each pipeline stage.
