# Export Verification (MVP)

## ZIP Naming Convention

Each successful export uses:

- `<song_title>_<run_id>_exports.zip`

This avoids ambiguity between multiple runs of the same song.

## PDF Output Isolation

Rendered PDFs are written to:

- `outputs/<run_id>/`

This prevents cross-run PDF overwrites when titles/instrument names repeat across runs.

## Quick Verification Steps

1. Confirm the app summary shows:
   - run ID
   - ZIP filename
   - ZIP size
2. Confirm ZIP filename includes the same run ID shown in the summary.
3. Open ZIP and verify it contains:
   - conductor score PDF
   - assigned/non-empty part PDFs
   - full-score MusicXML
   - `manifest.json`
4. In `manifest.json`, verify `outcome` includes:
   - `exported_part_count`
   - `skipped_part_count`
   - `zip_filename`

## Built-In Consistency Checks

After ZIP packaging, the app runs lightweight checks and surfaces non-blocking warnings if needed:

- `manifest.json` exists inside ZIP
- full-score MusicXML exists inside ZIP
- packaged part-PDF count matches exported-part count
- expected exported part PDF filenames are present

Warnings are also persisted to `manifest.json` under `outcome.integrity_warnings` for later run-detail review.

## Notes

- If the app shows an export integrity warning, treat the run as suspect and rerun export.
- Integrity warnings are non-blocking and intended as an audit aid.
