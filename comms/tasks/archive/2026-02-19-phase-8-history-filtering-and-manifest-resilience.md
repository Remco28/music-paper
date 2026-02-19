# Task Spec: BTT Phase 8 - History Filtering and Manifest Resilience

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Improve run-history usability and strengthen manifest handling for mixed-version or partially written run artifacts.

## Rationale
Run history and export audit metadata now exist. Next practical improvement is making history easier to scan and making manifest parsing more tolerant when older or interrupted runs are present.

## User Stories
1. As a teacher, I can quickly find runs by input type and recent success status.
2. As a maintainer, I can load history even when some manifests are incomplete/corrupt.
3. As a maintainer, I can distinguish successful exports from failed/incomplete runs at a glance.

## In Scope
- Add lightweight run-history filters in UI.
- Add resilient fallback handling for missing outcome fields.
- Add explicit success flag in manifest outcome.
- Update docs for history interpretation.

## Out of Scope
- Full-text search across runs.
- External database or indexing service.
- Authentication and access controls.

## Required File Changes
- `app.py`
- `utils.py`
- `scripts/smoke_test.py`
- `README_for_teacher.md`

## Required Functional Changes
1. **Manifest Success Flag**
   - Add additive `outcome.success` boolean in manifest.
   - Set true only on successful export packaging.

2. **History Filter Controls**
   - Add simple controls in `Recent Runs` panel:
     - input type filter (`all/local/youtube`)
     - status filter (`all/success/unknown`)
   - Keep defaults as `all`.

3. **Resilient Summary Parsing**
   - If `outcome` or subfields are missing, infer safe defaults without crashing.
   - Keep newest-first order and current result cap.

4. **Docs Update**
   - Briefly explain filter usage and meaning of `success`/`unknown` statuses.

## Constraints
- Preserve current pipeline behavior.
- Keep UI compact and non-intrusive.
- No new third-party dependencies.

## Acceptance Criteria
1. Manifests include `outcome.success` for new successful runs.
2. Recent Runs panel filters work and do not break rendering.
3. Missing/partial manifests are skipped or defaulted safely.
4. `py_compile` and `scripts/smoke_test.py` pass.

## Review Notes for Developer
- Keep changes additive and backward-compatible.
- Avoid repeated expensive scans when filters change.
- Prefer explicit fallback defaults over implicit exceptions.
