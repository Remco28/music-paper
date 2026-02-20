# Task Spec: BTT Phase 19 - Reset Workspace Safety Confirmation

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add explicit confirmation and impact preview for `Reset Temp Workspace` to prevent accidental loss of in-session working artifacts.

## Rationale
Operational surfaces have expanded (history, diagnostics, copyable summaries). The remaining high-risk action is workspace reset; users should see what will be cleared and confirm intent before execution.

## User Stories
1. As a teacher, I can understand what reset does before clicking it.
2. As a maintainer, I can avoid accidental reset during active troubleshooting/export iterations.
3. As a maintainer, reset remains fast and local when intentionally used.

## In Scope
- Add confirmation gate for `Reset Temp Workspace`.
- Show compact impact preview (active run ID, stems present, generated outputs present).
- Keep reset behavior itself unchanged after confirmation.
- Update docs.

## Out of Scope
- Undo/restore after reset.
- Soft-delete/trash behavior.
- Cleanup of `downloads/` artifacts.

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/troubleshooting.md`

## Required Functional Changes
1. **Impact Preview**
   - Before reset action executes, show current in-session indicators:
     - active run ID
     - whether stems exist
     - whether current export outputs exist

2. **Confirmation Gate**
   - Require checkbox confirmation before reset executes.
   - If not confirmed, show non-blocking warning and skip reset.

3. **Post-Reset UX**
   - Keep existing reset state-clearing semantics.
   - Clear reset confirmation checkbox after successful reset.

4. **Docs Update**
   - Clarify that reset clears temp workspace/session pointers but not downloaded ZIP files.

## Constraints
- No new dependencies.
- Preserve existing pipeline/history/diagnostics behavior.
- Keep UI concise.

## Acceptance Criteria
1. Reset cannot execute without explicit confirmation.
2. User sees clear preview of what will be affected.
3. Existing reset semantics remain intact once confirmed.
4. Existing validations pass.

## Review Notes for Developer
- Keep reset logic deterministic and easy to audit.
- Reuse current session-state keys for preview values.
- Ensure warning text is clear for non-technical users.
