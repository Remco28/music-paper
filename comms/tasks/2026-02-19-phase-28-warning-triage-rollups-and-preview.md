# Task Spec: BTT Phase 28 - Warning Triage Rollups and Preview

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Improve warning triage speed in Recent Runs by surfacing concise warning previews and category rollups.

## Rationale
Phase 27 added warning filtering/counts, but maintainers still need quick context on warning type without drilling into each run.

## User Stories
1. As a maintainer, I can see a short warning preview per run in the table/CSV.
2. As a maintainer, I can see aggregate warning categories for the filtered set.
3. As a reviewer, copy summaries include warning-category context for handoff.

## In Scope
- Derive warning category labels from manifest warning strings.
- Show filtered-set category rollup in Recent Runs panel.
- Include warning preview text in table/copy summary/CSV.

## Out of Scope
- Any new warning generation logic.
- Changes to warning persistence schema.

## Required File Changes
- `app.py`
- `docs/run-history.md`

## Required Functional Changes
1. Add per-run warning preview (first warning line, truncated).
2. Add filtered-set warning category rollup summary.
3. Include warning preview/category context in copy summary and CSV export.

## Constraints
- No new dependencies.
- Preserve existing filter and warning-count behavior.
- Keep logic deterministic and lightweight.

## Acceptance Criteria
1. Recent Runs displays warning preview context without requiring run-detail drilldown.
2. Filtered-set rollup reports warning categories deterministically.
3. CSV includes warning preview/category fields.
4. Existing validations pass.
