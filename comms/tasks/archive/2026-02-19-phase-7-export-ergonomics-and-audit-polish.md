# Task Spec: BTT Phase 7 - Export Ergonomics and Audit Polish

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Improve day-to-day export usability while tightening audit consistency between UI, ZIP artifacts, and manifest fields.

## Rationale
Manifest quality and run history are now in place. Next leverage is reducing operator friction when identifying the correct output package and validating what was exported.

## User Stories
1. As a teacher, I can immediately identify the right ZIP from the app and disk without confusion.
2. As a maintainer, I can verify UI summary counts match manifest and files.
3. As a maintainer, I can quickly detect mismatch issues in packaging.

## In Scope
- Improve ZIP naming consistency and collision handling.
- Add UI-side export artifact summary details (filename + size).
- Add small integrity checks between manifest outcome fields and exported file list.
- Update docs with export naming and verification notes.

## Out of Scope
- Cloud backup/sync.
- Multi-user workflow.
- Model-level transcription changes.

## Required File Changes
- `app.py`
- `utils.py`
- `README_for_teacher.md`
- `docs/` (small export-note update)

## Required Functional Changes
1. **ZIP Naming Ergonomics**
   - Ensure predictable ZIP naming with run ID suffix to avoid accidental overwrite ambiguity.
   - Reflect final ZIP filename consistently in manifest `outcome.zip_filename` and UI download label.

2. **Export Artifact Summary**
   - After successful export, show:
     - ZIP filename
     - ZIP size (human-readable)
     - run ID

3. **Light Integrity Check**
   - Add non-blocking check ensuring manifest outcome counts align with current part report counts.
   - If mismatch detected, show warning in diagnostics/review surface.

4. **Docs Update**
   - Document ZIP naming convention and quick verification steps.

## Constraints
- Keep existing workflow unchanged.
- Keep checks non-blocking.
- No new third-party dependencies.

## Acceptance Criteria
1. ZIP naming is deterministic and collision-resistant per run.
2. UI displays ZIP filename and size after successful export.
3. Manifest/UI count mismatches produce a warning, not a hard failure.
4. Existing flow remains intact and `smoke_test` passes.

## Review Notes for Developer
- Keep implementation additive.
- Do not duplicate expensive file scans.
- Prefer clear user labels over technical wording.
