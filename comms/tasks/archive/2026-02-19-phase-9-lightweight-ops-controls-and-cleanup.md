# Task Spec: BTT Phase 9 - Lightweight Ops Controls and Cleanup

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add minimal operational controls for managing local run artifacts and keeping the workspace clean without manual file navigation.

## Rationale
History and manifest resilience are in place. Next pragmatic step is basic local operations: quick cleanup actions and safer management of accumulated run artifacts.

## User Stories
1. As a teacher, I can clear old runs from the UI without touching folders manually.
2. As a maintainer, I can keep disk usage manageable while preserving recent runs.
3. As a maintainer, I can perform cleanup without breaking active run state.

## In Scope
- Add a small run-artifact maintenance panel.
- Add utility helpers for pruning old run directories.
- Add confirmation safeguards for destructive cleanup actions.
- Update docs for cleanup behavior.

## Out of Scope
- Scheduled background jobs.
- Cloud/off-device retention policies.
- Complex backup/restore flows.

## Required File Changes
- `app.py`
- `utils.py`
- `README_for_teacher.md`

## Required Functional Changes
1. **Maintenance Panel**
   - Show run-directory count and approximate disk usage.
   - Add action to remove runs older than a selected keep-count (for example keep latest N).

2. **Safe Cleanup Controls**
   - Require explicit confirmation checkbox/button pairing before prune action.
   - Never delete current active run directory.

3. **Utility Helper(s)**
   - Add deterministic pruning function in `utils.py`:
     - sort run dirs newest-first
     - keep latest N
     - skip active run ID
     - return deleted count and reclaimed bytes

4. **Docs Update**
   - Brief note on cleanup controls and caution around temporary artifacts.

## Constraints
- Keep UI simple and local-only.
- No new dependencies.
- Preserve existing pipeline and run-history behavior.

## Acceptance Criteria
1. User can prune old runs while keeping latest N and active run intact.
2. Cleanup action requires explicit confirmation.
3. UI shows deleted count and reclaimed size after prune.
4. Existing app flow remains unchanged and validation scripts still pass.

## Review Notes for Developer
- Treat cleanup as potentially destructive: be conservative.
- Ensure byte-size calculations are best-effort and fast.
- Keep behavior deterministic for reviewability.
