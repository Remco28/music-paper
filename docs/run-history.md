# Run History (MVP)

The app includes a read-only **Recent Runs** panel that summarizes the latest run manifests found under:

- `temp/runs/<run_id>/manifest.json`

## What it shows
- Run ID
- Timestamp
- Input type and shortened source value
- Simplification profile + on/off
- Status (`success` or `unknown`)
- Exported/skipped part counts
- ZIP filename

## Filters
- `Input Type`: `all`, `local`, `youtube`
- `Status`: `all`, `success`, `unknown`

`unknown` usually means an older manifest format or incomplete run metadata.

## Notes
- The panel reads only local manifests and skips missing/corrupt files safely.
- It is non-blocking and does not depend on preflight pass/fail status.
- It is intended for quick comparison, not long-term archival.
