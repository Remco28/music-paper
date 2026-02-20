# Task Spec: BTT Phase 35 - Failure Traceability and Failed-Run Manifest Hardening

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Ensure failed export attempts leave manifest-backed traceability instead of appearing as missing-manifest runs.

## Rationale
Current failures before manifest write can leave run folders without outcome metadata, reducing run-history observability and complicating debugging.

## User Stories
1. As a maintainer, failed runs appear as explicit failed outcomes in Recent Runs.
2. As a maintainer, I can see failure stage and concise failure summary in run details.
3. As a reviewer, failure metadata remains backward-compatible for legacy manifests.

## In Scope
- Add additive failure context fields under `outcome`.
- Persist failure context for stage failures in export pipeline.
- Surface failure context in selected-run details.
- Update schema and troubleshooting docs; extend smoke checks.

## Out of Scope
- New retry/orchestration behavior.
- Stack-trace persistence.

## Required File Changes
- `app.py`
- `utils.py`
- `docs/manifest-schema.md`
- `docs/troubleshooting.md`
- `scripts/smoke_test.py`

## Required Functional Changes
1. Add `outcome.failure_stage` and `outcome.failure_summary` (additive fields).
2. Persist failure context for failed export attempts where possible.
3. Keep `status` derivation (`success`/`failed`/`unknown`) unchanged and backward-compatible.

## Constraints
- No new dependencies.
- Preserve current successful export behavior.

## Acceptance Criteria
1. Failed runs are manifest-visible with `success=false` and failure context when writable.
2. Selected-run details show failure context when present.
3. Existing validations pass.
