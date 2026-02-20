# Task Spec: BTT Phase 32 - Run Cache Auto-Refresh Toggle and Staleness Indicator

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Make Recent Runs cache behavior explicit by adding an auto-refresh toggle and stale/drift indicators.

## Rationale
Phase 31 added cache + manual refresh. Users still need clear control when they prefer stable snapshots and clear visibility when cache may be outdated.

## User Stories
1. As a maintainer, I can disable auto-refresh to keep a stable run-history snapshot while reviewing.
2. As a maintainer, I can see when the cache is stale or when run/manifest signature changed.
3. As a maintainer, I can manually refresh at any point.

## In Scope
- Add session toggle: `Auto Refresh Run Cache`.
- Show cache age and stale reminder.
- Show signature drift note when auto-refresh is off and source data changed.

## Out of Scope
- Any changes to filter/sort logic.
- Any schema/export behavior changes.

## Required File Changes
- `app.py`
- `docs/run-history.md`

## Required Functional Changes
1. Add auto-refresh toggle defaulting enabled.
2. If auto-refresh disabled and source signature changes, keep cached snapshot and show non-blocking drift note.
3. Show cache freshness context (last refresh + age) and stale reminder threshold.

## Constraints
- No new dependencies.
- Preserve existing refresh button behavior.

## Acceptance Criteria
1. Toggle clearly controls signature-triggered auto-refresh behavior.
2. Drift/stale indicators are visible and non-blocking.
3. Existing Recent Runs workflows remain intact.
4. Existing validations pass.
