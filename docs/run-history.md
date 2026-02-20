# Run History (MVP)

The app includes a read-only **Recent Runs** panel that summarizes the latest run manifests found under:

- `temp/runs/<run_id>/manifest.json`

## What it shows
- Run ID
- Timestamp
- Input type and shortened source value
- Simplification profile + on/off
- Status (`success`, `failed`, or `unknown`)
- Export integrity warning count (from manifest `outcome.integrity_warnings`)
- Warning preview snippet (first warning, truncated)
- Exported/skipped part counts
- ZIP filename
- Run detail inspector for a selected run (settings/outcome/pipeline metadata)
- Part-level summary snippet (exported/skipped and common skip reasons)
- Manifest schema version (`legacy` marker for unversioned manifests)
- Re-download button for prior ZIP artifacts when still present in `downloads/`
- `Apply Settings to Current Options` action for copying valid simplification settings into current controls
- Health summary for current filtered set: runs loaded, readable manifests, missing/corrupt manifests, ZIP present, ZIP missing
- Warning category rollup for current filtered set (derived from warning message prefixes)
- Copyable summary text block (includes filters, health metrics, and up to five runs)
- Optional session note included in copyable summary (session-only, not persisted)
- CSV download for the current filtered set (spreadsheet-friendly operational snapshot)

## Filters
- `Input Type`: `all`, `local`, `youtube`
- `Status`: `all`, `success`, `failed`, `unknown`
- `Warning State`: `all`, `with_warnings`, `no_warnings`
- `Warning Category Filter`: case-insensitive token match against normalized warning categories
- `Sort`: `newest_first`, `warning_count_desc`, `warning_count_asc`
- `Run ID Search`: case-insensitive partial match on run ID
- `History Limit`: bounded recent-manifest load size (`5`, `10`, `20`)

- `failed` means manifest explicitly recorded `outcome.success = false`.
- `unknown` usually means an older manifest format or incomplete run metadata.

## Notes
- The panel reads only local manifests and skips missing/corrupt files safely.
- It is non-blocking and does not depend on preflight pass/fail status.
- It is intended for quick comparison, not long-term archival.
- Related cleanup actions are available in `Run Artifact Maintenance` (keep latest N + confirmed prune).
- If a selected run's manifest is missing/corrupt or ZIP is unavailable, the app shows a non-blocking message.
- Legacy (unversioned) manifests remain readable with compatibility defaults.
- Health summary scope is bounded by the selected `History Limit` and current filters/search.
- Session note and copyable summary do not write to manifests or run artifacts.
- CSV export is scoped to current filters/sort/limit (displayed set) and does not modify run artifacts.
- CSV export includes warning fields (`warning_count`, `has_warnings`) for offline triage.
- CSV export also includes `warning_preview` and `warning_categories`.
- Selected run details include a copyable warning digest when warnings are present.
- Filters are evaluated before limit truncation; the UI then shows the top N results based on selected sort mode.
- Recent Runs uses a session cache for manifest-derived rows and exposes `Refresh Run Cache` plus last-refresh timestamp.
- `Auto Refresh Run Cache` controls whether on-disk run/manifest changes refresh cache automatically.
- If auto refresh is off, the app shows a non-blocking drift reminder when cache differs from disk state.
- A stale reminder appears when run-cache freshness exceeds ~15 minutes.
