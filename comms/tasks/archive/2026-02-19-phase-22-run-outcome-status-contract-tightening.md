# Task Spec: BTT Phase 22 - Run Outcome Status Contract Tightening

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Strengthen run outcome status semantics so history and details can clearly distinguish successful, failed, and unknown runs without ambiguity.

## Rationale
Current status uses `success`/`unknown`, which is safe but coarse. As history tooling matures, a tighter status contract improves operational confidence and debugging clarity.

## User Stories
1. As a teacher, I can tell whether a run truly succeeded or failed.
2. As a maintainer, I can filter and review failed runs without conflating them with legacy/unknown data.
3. As a maintainer, this remains backward-compatible with older manifests.

## In Scope
- Define explicit normalized status categories: `success`, `failed`, `unknown`.
- Ensure write path marks failed packaging scenarios deterministically.
- Ensure read path derives status safely for legacy manifests.
- Update history filters and display labels to include `failed`.
- Update docs and smoke coverage where applicable.

## Out of Scope
- Full failure taxonomy per stage in manifest (single status only in this phase).
- Migration/backfill of existing manifests.
- Analytics/reporting layer.

## Required File Changes
- `utils.py`
- `app.py`
- `docs/manifest-schema.md`
- `docs/run-history.md`
- `scripts/smoke_test.py`

## Required Functional Changes
1. **Manifest Contract**
   - Preserve `outcome.success` boolean for compatibility.
   - Add/normalize derived status logic that maps to:
     - `success` when `outcome.success == True`
     - `failed` when `outcome.success == False`
     - `unknown` when absent/invalid

2. **Read Path Normalization**
   - Centralize status derivation in manifest normalization helper.
   - Ensure history/detail panels consume normalized status field.

3. **UI Updates**
   - Update status filter options to include `failed`.
   - Update table/detail labels accordingly.

4. **Docs + Smoke**
   - Document status semantics clearly.
   - Add smoke assertion covering `failed` derivation.

## Constraints
- No new dependencies.
- Backward-compatible behavior for unversioned/legacy manifests.
- Preserve existing flows and performance.

## Acceptance Criteria
1. UI can show/filter `success`, `failed`, `unknown`.
2. Failed runs are distinguishable from unknown legacy runs.
3. Legacy manifests without success flag remain `unknown`.
4. Existing validations pass with added status coverage.

## Review Notes for Developer
- Keep status mapping explicit and deterministic.
- Avoid broad schema churn; additive/derived field is preferred.
- Ensure CSV/exported summaries remain coherent with new status vocabulary.
