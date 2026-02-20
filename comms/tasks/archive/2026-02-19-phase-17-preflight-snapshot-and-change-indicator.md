# Task Spec: BTT Phase 17 - Preflight Snapshot and Change Indicator

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add a lightweight preflight snapshot indicator so users can quickly tell whether tool availability changed since the last preflight run.

## Rationale
Diagnostics and copyable summaries are now in place. The next practical reliability aid is highlighting environment drift (for example PATH/tool changes) without requiring users to manually compare outputs.

## User Stories
1. As a teacher, I can see whether preflight results are still current.
2. As a maintainer, I can detect when tool paths/status changed after setup tweaks.
3. As a maintainer, I can capture this status in troubleshooting context quickly.

## In Scope
- Store last preflight snapshot in session state.
- Add non-blocking indicator showing `unchanged` vs `changed` since last run.
- Include a concise delta line for changed tools.
- Update docs.

## Out of Scope
- Automatic re-running preflight.
- Persistent storage of snapshots across app restarts.
- Any install/repair automation.

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/troubleshooting.md`

## Required Functional Changes
1. **Snapshot Capture**
   - On `Run Preflight Checks`, store tool status/path snapshot in session.

2. **Change Indicator**
   - If a prior snapshot exists, compare current snapshot and show:
     - `No change since last preflight` OR
     - `Changed since last preflight` with affected tool names.

3. **User Guidance**
   - Keep messaging concise and non-blocking.
   - Encourage rerun preflight when environment changes are suspected.

4. **Docs Update**
   - Mention how to interpret preflight change indicator.

## Constraints
- No new dependencies.
- Session-only behavior.
- Preserve existing preflight gating semantics.

## Acceptance Criteria
1. Users see clear unchanged/changed feedback after repeated preflight runs.
2. Changed tools are identified by name.
3. Feature remains non-blocking and does not alter pipeline behavior.
4. Existing validations continue to pass.

## Review Notes for Developer
- Keep comparison deterministic and simple.
- Reuse existing preflight/path resolution logic where possible.
- Avoid cluttering the preflight panel with verbose output.
