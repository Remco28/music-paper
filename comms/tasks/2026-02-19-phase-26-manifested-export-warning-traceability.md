# Task Spec: BTT Phase 26 - Manifested Export Warning Traceability

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Persist non-blocking export integrity/consistency warnings into each run manifest so warning context remains auditable after app reruns.

## Rationale
Current warning surfaces are session-scoped. Persisting warnings in `manifest.json` improves post-run diagnostics and reviewer confidence when inspecting historical runs.

## User Stories
1. As a maintainer, I can inspect prior run manifests and see whether export warnings occurred.
2. As a teacher, I can reopen a prior run and understand if any non-blocking packaging concerns were detected.
3. As a developer, I can keep warning persistence backward-compatible and lightweight.

## In Scope
- Add additive manifest field under `outcome` for warning list.
- Write warning list after post-package integrity checks complete.
- Surface warning summary in selected-run details.
- Update schema/docs and smoke coverage.

## Out of Scope
- Blocking export on warnings.
- Retroactive migration of old manifests.
- Any change to core export pipeline success criteria.

## Required File Changes
- `app.py`
- `utils.py`
- `docs/manifest-schema.md`
- `docs/export-verification.md`
- `scripts/smoke_test.py`

## Required Functional Changes
1. **Manifest Persistence**
   - Persist warning list at `outcome.integrity_warnings` (array of strings).
   - Keep empty list when no warnings are present.

2. **Run Detail Visibility**
   - In selected run details, show warning count and concise warning text when present.

3. **Compatibility**
   - Keep legacy manifests readable by defaulting missing warning field to empty list.

4. **Validation**
   - Extend smoke checks for manifest normalization/defaulting and warning persistence helper behavior.

## Constraints
- No new dependencies.
- Additive/backward-compatible schema only.
- Preserve existing non-blocking warning UX.

## Acceptance Criteria
1. New manifests include `outcome.integrity_warnings`.
2. Warning list accurately reflects post-package checks for the run.
3. Selected-run detail UI exposes warning presence without breaking legacy manifests.
4. Compile + smoke checks pass.
