# Export Verification (MVP)

## ZIP Naming Convention

Each successful export uses:

- `<song_title>_<run_id>_exports.zip`

This avoids ambiguity between multiple runs of the same song.

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

## Notes

- If the app shows an export integrity warning, treat the run as suspect and rerun export.
- Integrity warnings are non-blocking and intended as an audit aid.
