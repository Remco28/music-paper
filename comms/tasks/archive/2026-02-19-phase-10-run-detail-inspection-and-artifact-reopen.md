# Task Spec: BTT Phase 10 - Run Detail Inspection and Artifact Reopen

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add a lightweight run-detail inspector so maintainers can review a prior run's manifest and re-download its ZIP artifact (when still present) without rerunning the pipeline.

## Rationale
The app already writes deterministic run artifacts and shows a compact history list. The next fundamental step is operational recoverability: if a session resets, users should still be able to inspect what happened and recover existing outputs directly from stored run metadata.

## User Stories
1. As a teacher, I can select a recent run and verify what settings/input produced it.
2. As a maintainer, I can confirm whether a run's ZIP artifact still exists.
3. As a maintainer, I can re-download a previous ZIP without rerunning transcription.

## In Scope
- Add a run-detail section tied to Recent Runs selection.
- Add utility helper(s) to read a selected run manifest safely.
- Add optional download button for prior ZIP artifacts if file exists.
- Update docs for this workflow.

## Out of Scope
- Restoring full in-memory app state from manifest.
- Automatic artifact regeneration when files are missing.
- Any remote/cloud persistence.

## Required File Changes
- `app.py`
- `utils.py`
- `README_for_teacher.md`
- `docs/run-history.md`
- `scripts/smoke_test.py`

## Required Functional Changes
1. **Run Selection in Recent Runs**
   - Add simple run selector (run_id) for currently listed rows.
   - Keep existing filters unchanged.

2. **Run Detail Inspector**
   - Read selected manifest and display:
     - run_id, timestamp, input summary
     - simplification settings block
     - exported/skipped counts + success status
     - pipeline metadata (app/model)
   - If manifest is missing/corrupt, show non-blocking message.

3. **Artifact Reopen**
   - Resolve expected ZIP path from manifest (`downloads/<zip_filename>`).
   - If ZIP exists, expose download button.
   - If ZIP missing, display clear guidance (non-blocking).

4. **Utility Helper(s)**
   - Add deterministic helper in `utils.py` for safe manifest loading by run_id.
   - Return structured data with explicit status (`ok`, `missing`, `corrupt`).

5. **Docs + Smoke**
   - Document prior-run inspection and ZIP reopen behavior.
   - Add smoke coverage for new manifest-loader helper.

## Constraints
- No new dependencies.
- Keep UI local-only and minimal.
- Do not regress export flow, history filters, or cleanup controls.

## Acceptance Criteria
1. User can select a recent run and view manifest-backed details.
2. ZIP re-download appears only when artifact exists.
3. Missing/corrupt manifest or ZIP never crashes the app.
4. Existing smoke test and new helper coverage pass.

## Review Notes for Developer
- Treat all persisted files as potentially missing or stale.
- Keep details panel read-only and low-noise.
- Reuse existing formatting helpers where possible.
