# Task Spec: BTT Phase 31 - Recent Runs Manifest Cache and Refresh Control

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Reduce rerender overhead in Recent Runs by caching manifest-derived records in session state with explicit refresh visibility/control.

## Rationale
Recent Runs now supports richer filtering and warning analysis. Re-reading all manifests on every rerender can become expensive as run count grows.

## User Stories
1. As a maintainer, Recent Runs remains responsive with many local runs.
2. As a maintainer, I can manually refresh run-history cache after external file changes.
3. As a reviewer, I can see when Recent Runs data was last refreshed.

## In Scope
- Add session-scoped cache for manifest-derived run records.
- Auto-refresh cache when run/manifest signature changes.
- Add manual `Refresh Run Cache` action and last-refresh timestamp surface.

## Out of Scope
- Any schema changes.
- Changes to filtering/sorting semantics from Phase 30.

## Required File Changes
- `app.py`
- `docs/run-history.md`

## Required Functional Changes
1. Cache base run records (manifest load results + normalized run metadata) in session state.
2. Rebuild cache when detected run/manifest signature differs or refresh button is used.
3. Keep downstream filters/sort/limit operating on cached records.

## Constraints
- No new dependencies.
- Preserve existing output behavior.

## Acceptance Criteria
1. Recent Runs avoids repeated manifest file reads on every simple rerender.
2. Manual refresh control updates cache and refresh timestamp.
3. Filters/sort/CSV/detail behavior remains intact.
4. Existing validations pass.
