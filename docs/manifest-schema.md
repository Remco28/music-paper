# Manifest Schema (MVP)

This document defines the JSON schema written to each run's `manifest.json`.

## Top-Level Fields

- `run_id` (string): Unique run identifier (timestamp-based).
- `timestamp` (string): ISO8601 timestamp when manifest was written.
- `input` (object): Input source details.
- `options` (object): Effective score/simplification options used for this run.
- `pipeline` (object): Pipeline metadata for traceability.
- `outcome` (object): Compact result summary for quick run comparison.
- `assignments` (object): Stem to instrument map as selected in UI.
- `parts` (array): Part export outcomes including skipped reasons.
- `tool_versions` (object): Best-effort tool version strings.

## Field Details

### `input`
- `type` (string): `local` or `youtube`.
- `value` (string): Uploaded filename or URL.

### `options`
- `profile` (string): Selected simplification profile (for example `Balanced`).
- `simplify_enabled` (boolean): Whether simplification logic was enabled.
- `quantize_grid` (string): Quantize grid (one of `1/4`, `1/8`, `1/16`).
- `min_note_duration_beats` (number): Minimum note length retained.
- `density_threshold` (integer): Max note density threshold.

### `pipeline`
- `app_version` (string): App version from `config.py`.
- `demucs_model` (string): Active Demucs model name.

### `outcome`
- `exported_part_count` (integer): Number of exported non-empty parts.
- `skipped_part_count` (integer): Number of skipped parts.
- `zip_filename` (string): ZIP artifact filename for this run, typically `<song_title>_<run_id>_exports.zip`.

### `parts[]`
Each entry includes:
- `name` (string)
- `status` (string): `exported` or `skipped`
- `note_count` (integer)
- `reason` (string, optional): usually present when skipped

## Example

```json
{
  "run_id": "20260219_161500_123456",
  "timestamp": "2026-02-19T16:15:01.102938",
  "input": {
    "type": "local",
    "value": "song.mp3"
  },
  "options": {
    "profile": "Balanced",
    "simplify_enabled": true,
    "quantize_grid": "1/8",
    "min_note_duration_beats": 0.25,
    "density_threshold": 6
  },
  "pipeline": {
    "app_version": "0.4.0",
    "demucs_model": "htdemucs"
  },
  "outcome": {
    "exported_part_count": 1,
    "skipped_part_count": 0,
    "zip_filename": "My_Song_exports.zip"
  },
  "assignments": {
    "bass": "Tuba"
  },
  "parts": [
    {
      "name": "Tuba",
      "status": "exported",
      "note_count": 42
    }
  ],
  "tool_versions": {
    "python": "3.11.11"
  }
}
```
