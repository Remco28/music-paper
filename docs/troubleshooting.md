# Troubleshooting (MVP)

## Missing Executables

### Symptoms
- Preflight shows `FAIL` for `demucs`, `basic-pitch`, `mscore`, or `ffmpeg`.
- A stage fails quickly with command-not-found style errors.

### Actions
1. Run: `python scripts/validate_setup.py`
2. Install missing tools and ensure they are on `PATH`.
3. Re-run preflight in the app.
4. Open `Diagnostics` and copy the `Copyable Diagnostics Summary` for support handoff.
5. Use the preflight change indicator:
   - `No change since last preflight` means tool status/path is stable.
   - `Changed since last preflight: ...` lists tools whose status/path changed.
6. Check preflight freshness:
   - `Preflight freshness` shows last run time and age.
   - If stale reminder appears (30m+), rerun preflight before retrying export.

## YouTube URL Issues

### Symptoms
- Input stage fails for YouTube links.
- Error mentions playlists or no extracted audio file.

### Actions
1. Use a single-video URL only (no `list=` playlist parameter).
2. Use `http://` or `https://` and a recognized YouTube host (`youtube.com`, `www.youtube.com`, `youtu.be`).
3. Confirm the link is public and valid.
4. Retry input preparation.
5. If issue persists, share the `Copyable Diagnostics Summary` from `Diagnostics`.

## Local File Validation Issues

### Symptoms
- Input stage reports unsupported file type.
- Input stage reports file is empty (`0 bytes`).

### Actions
1. Use supported audio types only: `.wav`, `.mp3`, `.aac`, `.m4a`, `.flac`.
2. Confirm the selected file is not empty/corrupt.
3. Retry upload and input preparation.

## Empty or Sparse Parts

### Symptoms
- Part summary shows skipped parts with `no_notes`.
- Exported parts contain very few notes.

### Actions
1. Use a less aggressive profile (`Easy Intermediate` or `Intermediate`).
2. In advanced settings, reduce minimum duration and/or increase density threshold.
3. Run `Quick Rerun` to test without re-separating stems.

## Unassigned Stems

### Symptoms
- Part summary shows skipped parts with `unassigned`.
- Assignment stage warns that most stems are unassigned.
- Export blocks with "Assign at least one stem..." message.

### Actions
1. Assign each relevant stem to a target instrument.
2. Re-run export.

## Assignment Guard Warnings

### Symptoms
- Warning: most stems are unassigned.
- Warning: all assigned stems map to one instrument.

### Actions
1. Treat these as quality warnings (not hard errors) unless export is blocked for zero assignments.
2. Assign additional stems if you need fuller instrumentation.
3. Split assignments across multiple instruments when musically appropriate.

## MusicXML Missing During Part Rendering

### Symptoms
- Part summary shows skipped parts with `missing_musicxml`.

### Actions
1. Re-run export to regenerate part files.
2. If repeated, reset workspace and run again from input.

## Sharing Environment Context

When reporting an issue, include:
1. Relevant stage/error shown in app.
2. The in-app `Copyable Diagnostics Summary`.
3. If applicable, the `Copyable Summary` from `Recent Runs`.
4. If run failed, include selected-run failure context (`failure_stage`, `failure_summary`) from Recent Runs details.

## Reset Workspace Clarification

- `Reset Temp Workspace` clears temp working files and current in-session pointers/state.
- It requires explicit confirmation and shows a compact impact preview before running.
- It does not remove ZIP files already written to `downloads/`.
