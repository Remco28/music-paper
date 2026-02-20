# Task Spec: BTT Phase 18 - Preflight Staleness and Reminder Surface

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Show a lightweight preflight freshness indicator so users can quickly tell how old the current preflight result is and when rerunning it is recommended.

## Rationale
Phase 17 added change detection between preflight runs. The next simple reliability improvement is time-based context: even unchanged results can become stale after long sessions.

## User Stories
1. As a teacher, I can see whether preflight checks were run recently.
2. As a maintainer, I can get a clear reminder to rerun preflight after longer sessions.
3. As a maintainer, this remains non-blocking and local.

## In Scope
- Store preflight run timestamp in session state.
- Display human-readable age (for example, "2m ago") in preflight panel.
- Show gentle reminder when preflight age exceeds threshold (for example 30 minutes).
- Include timestamp/age in copyable diagnostics snapshot.
- Update docs.

## Out of Scope
- Background timers or auto-refresh.
- Automatic preflight reruns.
- Persistent storage across app restarts.

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/troubleshooting.md`

## Required Functional Changes
1. **Capture Timestamp**
   - On each preflight run, save timestamp in session.

2. **Freshness Display**
   - Show last preflight timestamp and age in preflight panel.
   - If age exceeds threshold, show non-blocking reminder to rerun preflight.

3. **Diagnostics Integration**
   - Add preflight freshness lines to `Copyable Diagnostics Summary`.

4. **Docs Update**
   - Mention preflight freshness guidance in troubleshooting/setup notes.

## Constraints
- No new dependencies.
- Session-only behavior.
- Preserve current preflight gating and change-indicator semantics.

## Acceptance Criteria
1. Preflight panel shows last-run time context after checks are run.
2. Users get a clear stale-check reminder after threshold.
3. Diagnostics snapshot includes freshness info.
4. Existing workflows and validations remain unaffected.

## Review Notes for Developer
- Keep age formatting simple and deterministic.
- Reminder should be advisory, not blocking.
- Reuse current datetime handling in app.
