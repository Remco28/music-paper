# Task Spec: BTT Phase 20 - Run History Export CSV (Lite)

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add a lightweight CSV export of the current Recent Runs filtered set for offline review and record-keeping.

## Rationale
The app now provides rich on-screen history and copyable summaries. The next pragmatic step is structured export of the visible history subset for spreadsheet review without introducing persistence complexity.

## User Stories
1. As a teacher, I can export visible run history to a spreadsheet-friendly file.
2. As a maintainer, I can share filtered run metadata with stakeholders quickly.
3. As a maintainer, export remains scoped to current filters/limit and does not alter manifests.

## In Scope
- Add `Download CSV` action in Recent Runs panel.
- Export currently filtered set (including unreadable/missing manifest cases where represented).
- Include core columns: run_id, timestamp, input_type, status, exported_parts, skipped_parts, zip_filename, zip_present, manifest_status.
- Keep export local/session-only.

## Out of Scope
- Full historical export beyond current bounded set.
- Scheduled reporting.
- Additional file formats.

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/run-history.md`

## Required Functional Changes
1. **CSV Build**
   - Generate CSV from existing filtered records in Recent Runs panel.
   - Use deterministic column order.

2. **Download Control**
   - Provide download button with timestamped filename.
   - No writes to manifests or run artifacts.

3. **Scope Clarity**
   - Label export as scoped to current filters/search/limit.

4. **Docs Update**
   - Document CSV export purpose and scope.

## Constraints
- No new dependencies.
- Reuse existing in-memory filtered record set.
- Preserve existing panel behavior and performance.

## Acceptance Criteria
1. User can download CSV of current filtered run set.
2. CSV columns are stable and complete for operational review.
3. Export scope matches UI filters/search/limit.
4. Existing validations/workflows remain unaffected.

## Review Notes for Developer
- Keep encoding straightforward (`utf-8`).
- Ensure missing fields serialize safely (empty strings/zeros as appropriate).
- Keep UI wording explicit about scoped export.
