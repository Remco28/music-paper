# Task Spec: BTT Phase 13 - History Search and Limit Controls

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Improve Recent Runs usability by adding a run-id search filter and configurable history limit while preserving existing lightweight local behavior.

## Rationale
History now supports filters, detail inspection, settings reapply, and cleanup. The next simple productivity gain is finding a specific run quickly when many runs exist.

## User Stories
1. As a teacher, I can locate a run by partial run ID without scanning the full table.
2. As a maintainer, I can expand history beyond the fixed top-5 view when needed.
3. As a maintainer, I can keep the UI responsive with bounded history loading.

## In Scope
- Add run-id search text filter in Recent Runs.
- Add configurable history row limit (for example 5/10/20).
- Keep existing input/status filters and selected-run details behavior.
- Update docs for new controls.

## Out of Scope
- Full pagination framework.
- Sorting customization beyond newest-first default.
- Database/storage layer changes.

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/run-history.md`

## Required Functional Changes
1. **Run-ID Search Filter**
   - Add case-insensitive substring filter against `run_id`.
   - Apply after input/status filters.

2. **History Limit Control**
   - Add small control for number of recent manifests to load (bounded set values).
   - Pass chosen limit into history summary loader.

3. **Selection Resilience**
   - Keep selected run stable when still present after filtering.
   - If filtered out, automatically select first available result.

4. **Docs Update**
   - Document search + limit controls and expected behavior.

## Constraints
- No new dependencies.
- Preserve deterministic newest-first ordering.
- Keep non-blocking behavior for missing/corrupt manifests.

## Acceptance Criteria
1. Users can filter runs by partial run ID.
2. Users can choose history load size from bounded options.
3. Selected-run details continue working across filter changes.
4. Existing flows (export, cleanup, run details, apply settings) remain unaffected.

## Review Notes for Developer
- Keep controls compact to avoid clutter.
- Reuse existing session state patterns for filter values.
- Avoid expensive operations beyond current local manifest scan scope.
