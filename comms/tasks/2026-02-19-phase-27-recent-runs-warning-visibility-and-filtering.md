# Task Spec: BTT Phase 27 - Recent Runs Warning Visibility and Filtering

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Expose manifested export integrity warning state in Recent Runs so warning-bearing runs are easy to spot and filter.

## Rationale
Phase 26 persisted warnings into manifests, but run-history surfaces do not yet make warning state first-class for scanning/reporting.

## User Stories
1. As a maintainer, I can quickly identify runs with export/package warnings.
2. As a maintainer, I can filter Recent Runs by warning presence.
3. As a reviewer, CSV exports include warning counts for offline triage.

## In Scope
- Add warning-state filter in Recent Runs.
- Include warning count in run table/copy summary/CSV.
- Keep behavior additive and non-destructive.

## Out of Scope
- Any new warning generation logic.
- Blocking or changing export success criteria.

## Required File Changes
- `app.py`
- `docs/run-history.md`

## Required Functional Changes
1. Add `Warning State` filter with options: `all`, `with_warnings`, `no_warnings`.
2. Track warning count per run from manifest `outcome.integrity_warnings`.
3. Include warning count in:
   - Recent Runs table
   - copyable summary lines
   - CSV export columns

## Constraints
- No new dependencies.
- Preserve existing filter semantics.
- Legacy manifests must default to zero warnings.

## Acceptance Criteria
1. Warning-state filter works with existing input/status/search/limit filters.
2. Runs with warnings are visibly distinguishable in table and summaries.
3. CSV includes warning fields and remains deterministic.
4. Existing validations continue to pass.
