# Task Spec: BTT Phase 14 - Manifest and ZIP Presence Health Surface

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add a lightweight health summary that reports manifest and ZIP artifact presence across the currently loaded recent runs.

## Rationale
The app now supports history browsing, detail inspection, and artifact reopen. A compact health rollup helps maintainers quickly detect cleanup drift (for example, manifests present but ZIP files missing) without inspecting runs one-by-one.

## User Stories
1. As a maintainer, I can see how many recent runs still have recoverable ZIP artifacts.
2. As a teacher, I can quickly tell whether a missing download is an isolated case or widespread.
3. As a maintainer, I can identify missing/corrupt manifest scenarios earlier.

## In Scope
- Add a small health summary within Recent Runs panel using currently loaded rows.
- Compute counts for:
  - runs loaded
  - manifests readable
  - manifests missing/corrupt (within selected set)
  - ZIP present vs missing
- Keep behavior non-blocking and local-only.
- Update docs.

## Out of Scope
- Full filesystem audit beyond current bounded history limit.
- Auto-repair or ZIP regeneration.
- Background monitoring jobs.

## Required File Changes
- `app.py`
- `utils.py` (only if helper extraction improves clarity)
- `docs/run-history.md`
- `README_for_teacher.md`

## Required Functional Changes
1. **Health Summary Block**
   - Add concise metrics in Recent Runs panel based on currently loaded/filtered run set.
   - Keep computation cheap and deterministic.

2. **ZIP Presence Check**
   - Use manifest `outcome.zip_filename` to test file existence in `downloads/`.
   - Treat missing filename as ZIP missing.

3. **Manifest Readability Accounting**
   - Include selected-set count of unreadable manifests where detectable.
   - Maintain existing graceful skip behavior for table rendering.

4. **Docs Update**
   - Document what the health block measures and what it does not.

## Constraints
- No new dependencies.
- Preserve existing history filters, search, limit, details, apply-settings, and maintenance controls.
- Avoid expensive full-disk scans.

## Acceptance Criteria
1. Recent Runs displays a compact health summary.
2. ZIP presence/missing counts reflect current loaded set.
3. UI remains responsive with bounded limits.
4. Existing flows remain unchanged.

## Review Notes for Developer
- Prefer additive helper logic over broad restructuring.
- Be explicit that the summary is scoped to loaded/filtered runs, not all historical runs.
- Keep terminology teacher-friendly.
