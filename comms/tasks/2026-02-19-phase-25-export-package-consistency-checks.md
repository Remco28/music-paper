# Task Spec: BTT Phase 25 - Export Package Consistency Checks

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add lightweight consistency checks for ZIP package contents so exported bundles reliably contain the expected core artifacts.

## Rationale
Export flow is stable, but packaging trust can be improved with explicit post-build checks. Verifying expected files reduces silent packaging drift and improves teacher confidence.

## User Stories
1. As a teacher, I can trust that each ZIP includes required core files.
2. As a maintainer, I get clear warnings when package contents are incomplete.
3. As a maintainer, checks remain lightweight and non-destructive.

## In Scope
- Verify ZIP contains manifest and full score MusicXML at minimum.
- Verify exported part PDF presence count aligns with in-memory part report expectations.
- Surface non-blocking warnings when mismatches are found.
- Update docs around export verification.

## Out of Scope
- Cryptographic signing/checksums.
- Automatic re-packaging retries.
- Deep content validation of individual PDFs.

## Required File Changes
- `app.py`
- `utils.py` (if helper extraction needed)
- `docs/export-verification.md`
- `scripts/smoke_test.py` (if helper added)

## Required Functional Changes
1. **ZIP Content Inspection**
   - Inspect generated ZIP entries immediately after packaging.
   - Confirm presence of:
     - `manifest.json`
     - full score MusicXML file

2. **Part Artifact Count Check**
   - Compare expected exported-part count vs packaged part-PDF count.
   - Show concise warning on mismatch.

3. **Warning Surface**
   - Reuse existing non-blocking export integrity warning patterns.
   - Keep export available even if warning appears.

4. **Docs/Test Updates**
   - Update export verification doc with new checks.
   - Add smoke coverage if utility helper is introduced.

## Constraints
- No new dependencies.
- Preserve existing export success behavior.
- Keep checks fast and deterministic.

## Acceptance Criteria
1. Core ZIP artifact presence checks run after export.
2. Mismatches produce clear non-blocking warnings.
3. Normal exports remain unchanged when checks pass.
4. Existing validations continue to pass.

## Review Notes for Developer
- Keep check logic readable and audit-friendly.
- Minimize duplicate file-system reads.
- Avoid false positives where possible by aligning checks with current export contract.
