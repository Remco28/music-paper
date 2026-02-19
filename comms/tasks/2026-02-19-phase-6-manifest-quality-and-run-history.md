# Task Spec: BTT Phase 6 - Manifest Quality and Run History

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Make run outputs easier to audit and compare by improving manifest completeness and adding a lightweight in-app run history view.

## Rationale
Core pipeline, diagnostics, and failure clarity are now in place. The next pragmatic step is better operational traceability so teacher and maintainer can compare recent runs without digging through folders manually.

## User Stories
1. As a teacher, I can quickly see recent runs and open the right ZIP.
2. As a maintainer, I can inspect simplified run metadata without manually opening each manifest file.
3. As a maintainer, I can verify run outcomes and settings consistency across reruns.

## In Scope
- Add run outcome summary fields in manifest.
- Add in-app recent run history panel (read-only).
- Add minimal helper utilities for listing/parsing recent manifests.
- Update docs to explain run history usage.

## Out of Scope
- Database/storage backends.
- Cross-machine sync.
- Authentication or permissions.

## Required File Changes
- `app.py`
- `utils.py`
- `README_for_teacher.md`
- `docs/` (small run-history note)

## Required Functional Changes
1. **Manifest Outcome Summary**
   - Include compact summary fields in manifest:
     - exported part count
     - skipped part count
     - output ZIP filename
   - Keep schema additive/backward-compatible.

2. **Recent Run History Panel**
   - Add read-only panel showing recent run records (for example latest 5):
     - run_id
     - timestamp
     - input type/value (shortened)
     - profile/simplify setting
     - exported/skipped counts
     - zip filename
   - If manifest parsing fails for a record, skip it safely.

3. **Helper Utilities**
   - Add utility function(s) to scan run directories for manifests and return normalized summary rows.
   - Avoid heavy I/O; cap results and sort newest-first.

4. **Docs**
   - Add/update docs explaining where run history data comes from and how to use it.

## Constraints
- Keep UI simple and non-intrusive.
- No new dependencies.
- Preserve existing export and quick rerun behavior.

## Acceptance Criteria
1. Manifests include additive outcome summary fields.
2. Recent run history panel renders without blocking pipeline usage.
3. History panel handles missing/corrupt manifest files gracefully.
4. Existing workflow behavior remains intact.
5. `py_compile` and `scripts/smoke_test.py` pass.

## Review Notes for Developer
- Keep parsing logic defensive and deterministic.
- Do not couple history rendering to successful preflight.
- Prefer concise table/rows over complex widgets.
