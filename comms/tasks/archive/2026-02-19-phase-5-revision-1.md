# Task Spec: BTT Phase 5 Revision 1 - Export Failure State Integrity

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** REVISION REQUIRED

## Why Revision Is Needed
Phase 5 introduced stage-level error clarity, but current control flow can leave stale success artifacts visible after a failed run. This can mislead the teacher into downloading old outputs that do not correspond to the latest attempted run.

## Defect Summary
- `_run_export()` handles stage failures internally and returns early.
- `_render_export_stage()` continues to render summary/part report/download blocks regardless of whether the latest export attempt failed.
- Session state fields (`pdf_paths`, `part_report`, `zip_path`, etc.) are not explicitly invalidated at export start/failure boundaries.

## Required File Changes
- `app.py`

## Required Functional Changes
1. **Explicit Export Result Contract**
   - Change `_run_export(...)` to return `bool` success status (or structured result with `ok` flag).
   - Return `False` for any failed stage.

2. **Failure-State Reset / Invalidation**
   - At the start of each export attempt (regular and quick rerun), clear run-result fields that represent completed output:
     - `pdf_paths`
     - `part_report`
     - `musicxml_path`
     - `zip_path`
   - Ensure failed attempts do not leave prior-success artifacts presented as current.

3. **Render Gating by Attempt Outcome**
   - In `_render_export_stage()`, gate success-surface rendering (`_render_run_summary`, part list, download button) to only show data from successful completion.
   - On failure, show only stage error messaging and no stale download button.

4. **Quick Rerun Consistency**
   - Apply the same success/failure handling rules to quick rerun path.
   - Ensure failed quick rerun does not appear as successful output for new run ID.

## Constraints
- Preserve phase-5 stage error clarity UX.
- Keep non-blocking simplification warnings unchanged.
- Keep code changes localized and low-risk.

## Acceptance Criteria
1. After a failed export attempt, no stale ZIP download is shown for that failed attempt context.
2. After a failed export attempt, summary/part report do not present prior run as current run result.
3. Successful export behavior remains unchanged.
4. Quick rerun obeys the same state integrity rules.
5. `py_compile` and `scripts/smoke_test.py` continue to pass.

## Review Notes for Developer
- Prefer a small explicit state machine over implicit side effects.
- Keep existing stage-specific hints/messages intact.
