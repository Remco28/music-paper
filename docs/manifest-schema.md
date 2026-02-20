# Manifest Schema (MVP)

This document defines the JSON schema written to each run's `manifest.json`.

## Top-Level Fields

- `schema_version` (string): Manifest schema version for compatibility handling.
- `run_id` (string): Unique run identifier (timestamp-based).
- `timestamp` (string): ISO8601 timestamp when manifest was written.
- `status` (string, derived at read time): Normalized outcome status (`success`, `failed`, or `unknown`).
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
- `profile` (string): Selected simplification profile (for example `Easy Intermediate`).
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
- `success` (boolean): Whether export packaging completed successfully for this run.
- `integrity_warnings` (array of strings): Non-blocking export/package warning messages captured post-build.
- `failure_stage` (string): Failure stage identifier when `success=false` (for example `transcription`, `pdf_rendering`).
- `failure_summary` (string): Concise failure summary when `success=false`.

### Status Semantics
- `success`: `outcome.success == true`
- `failed`: `outcome.success == false`
- `unknown`: `outcome.success` missing/invalid (legacy or incomplete metadata)

### `parts[]`
Each entry includes:
- `name` (string)
- `status` (string): `exported` or `skipped`
- `note_count` (integer)
- `reason` (string, optional): usually present when skipped

## Example

```json
{
  "schema_version": "1",
  "run_id": "20260219_161500_123456",
  "timestamp": "2026-02-19T16:15:01.102938",
  "status": "success",
  "input": {
    "type": "local",
    "value": "song.mp3"
  },
  "options": {
    "profile": "Easy Intermediate",
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
    "zip_filename": "My_Song_20260219_161500_123456_exports.zip",
    "success": true,
    "integrity_warnings": [],
    "failure_stage": "",
    "failure_summary": ""
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

## Compatibility Notes

- Older manifests may be unversioned (`schema_version` absent). The app treats them as legacy and reads them with safe defaults.
- Unknown/future schema versions are read best-effort as long as JSON is valid.
