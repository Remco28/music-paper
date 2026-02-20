# Task Spec: BTT Phase 15 - Recent Runs Copyable Summary and Session Note

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Provide a compact copyable text summary of the current Recent Runs filtered set and allow an optional short session note to be included in that summary.

## Rationale
The app now has strong local run observability. The next practical step is enabling quick human handoff (teacher-to-maintainer) without digging through files: one copy action should capture the current operational snapshot.

## User Stories
1. As a teacher, I can copy a concise recent-runs summary to share feedback.
2. As a maintainer, I can include a short note (for example setup context) with that summary.
3. As a maintainer, I can generate this without changing manifests or run artifacts.

## In Scope
- Add session-note input in Recent Runs panel (session-only, not persisted to manifests).
- Add generated text summary block for the current filtered/loaded set.
- Add one-click copy-friendly output (text area content easy to copy).
- Update docs.

## Out of Scope
- Writing notes into manifests.
- Multi-user/shared notes.
- External integrations (email/chat APIs).

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/run-history.md`

## Required Functional Changes
1. **Session Note**
   - Add optional short free-text note tied to session state.
   - Keep it local/session-only.

2. **Copyable Summary Block**
   - Build summary from current filtered bounded set, including:
     - timestamp generated
     - history filters/search/limit
     - health metrics line
     - up to first N run lines (run_id, status, exported/skipped, zip present/missing)
     - optional session note
   - Render in text area for easy copy.

3. **Non-Destructive Behavior**
   - No manifest writes.
   - No impact on export/history logic.

4. **Docs Update**
   - Briefly describe intended use of copyable summary.

## Constraints
- No new dependencies.
- Keep UI compact and local-only.
- Avoid large payload generation (bounded by existing history limit).

## Acceptance Criteria
1. User can produce and copy a concise operational summary from UI.
2. Summary reflects current filters/limit and health counts.
3. Optional note appears only in session and does not alter manifests.
4. Existing workflows remain unaffected.

## Review Notes for Developer
- Keep summary format plain and readable for non-technical users.
- Ensure summary generation is deterministic for a given filtered set.
- Reuse already-computed filtered records where possible.
