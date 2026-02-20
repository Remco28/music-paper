# Task Spec: BTT Phase 29 - Warning Category Filter and Selected-Run Digest

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Make warning triage more actionable by adding category-level filtering and a copyable warning digest for the selected run.

## Rationale
Phases 27-28 improved warning visibility, but maintainers still need focused filtering by warning type and a compact artifact for issue handoff.

## User Stories
1. As a maintainer, I can filter Recent Runs by warning category token.
2. As a maintainer, I can copy a warning digest for the selected run without manually assembling context.
3. As a reviewer, warning category context is visible in the run table.

## In Scope
- Add warning category query filter in Recent Runs.
- Add warning categories column in Recent Runs table.
- Add copyable selected-run warning digest block.

## Out of Scope
- Any warning generation/persistence changes.
- External export/reporting formats beyond existing CSV.

## Required File Changes
- `app.py`
- `docs/run-history.md`

## Required Functional Changes
1. Add `Warning Category Filter` text query applied to normalized warning category tokens.
2. Show warning categories in Recent Runs table rows.
3. In selected run details, show copyable warning digest when warnings exist.

## Constraints
- No new dependencies.
- Preserve existing filters and backward compatibility for legacy manifests.

## Acceptance Criteria
1. Category query narrows filtered set as expected.
2. Selected run with warnings exposes a copyable digest block.
3. No regressions in existing run-history/export workflows.
4. Existing validations pass.
