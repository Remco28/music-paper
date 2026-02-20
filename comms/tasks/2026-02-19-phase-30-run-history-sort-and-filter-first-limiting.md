# Task Spec: BTT Phase 30 - Run History Sort and Filter-First Limiting

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Improve Recent Runs discoverability by adding explicit sort mode and applying filters before history limit truncation.

## Rationale
Current behavior bounds run directories before filters, which can hide matching runs. This weakens warning triage and targeted run lookup.

## User Stories
1. As a maintainer, my filters search across all local runs before UI limiting.
2. As a maintainer, I can sort displayed runs by newest or warning density.
3. As a reviewer, copy summary reflects sort mode and matched/displayed counts.

## In Scope
- Add `Sort` control for Recent Runs.
- Apply filter logic across all run directories first.
- Apply history limit after filtering/sorting.
- Update copy summary and health captions with matched/displayed context.

## Out of Scope
- New manifest schema changes.
- Any change to export pipeline behavior.

## Required File Changes
- `app.py`
- `docs/run-history.md`

## Required Functional Changes
1. Add sort options: `newest_first`, `warning_count_desc`, `warning_count_asc`.
2. Evaluate filters across full run set, then apply selected sort and limit.
3. Display concise matched/displayed counts in Recent Runs health/copy summary.

## Constraints
- No new dependencies.
- Preserve existing filter semantics and warning fields.

## Acceptance Criteria
1. Filter queries are not silently excluded by pre-limit truncation.
2. Sort mode deterministically changes result ordering.
3. Copy summary documents sort mode and matched/displayed counts.
4. Existing validations pass.
