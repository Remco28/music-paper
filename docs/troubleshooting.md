# Troubleshooting (MVP)

## Missing Executables

### Symptoms
- Preflight shows `FAIL` for `demucs`, `basic-pitch`, `mscore`, or `ffmpeg`.
- A stage fails quickly with command-not-found style errors.

### Actions
1. Run: `python scripts/validate_setup.py`
2. Install missing tools and ensure they are on `PATH`.
3. Re-run preflight in the app.

## YouTube URL Issues

### Symptoms
- Input stage fails for YouTube links.
- Error mentions playlists or no extracted audio file.

### Actions
1. Use a single-video URL only (no `list=` playlist parameter).
2. Confirm the link is public and valid.
3. Retry input preparation.

## Empty or Sparse Parts

### Symptoms
- Part summary shows skipped parts with `no_notes`.
- Exported parts contain very few notes.

### Actions
1. Use a less aggressive profile (`Balanced` or `Conservative`).
2. In advanced settings, reduce minimum duration and/or increase density threshold.
3. Run `Quick Rerun` to test without re-separating stems.

## Unassigned Stems

### Symptoms
- Part summary shows skipped parts with `unassigned`.

### Actions
1. Assign each relevant stem to a target instrument.
2. Re-run export.

## MusicXML Missing During Part Rendering

### Symptoms
- Part summary shows skipped parts with `missing_musicxml`.

### Actions
1. Re-run export to regenerate part files.
2. If repeated, reset workspace and run again from input.
