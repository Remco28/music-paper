# Task Spec: BTT Phase 16 - Diagnostics Copyable Environment Snapshot

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add a copyable diagnostics snapshot so users can quickly share environment/tool status when troubleshooting run issues.

## Rationale
Run-history summaries now support operational handoff. The next practical support improvement is a parallel environment snapshot from Diagnostics, reducing back-and-forth when setup problems occur.

## User Stories
1. As a teacher, I can copy environment status to share setup issues.
2. As a maintainer, I can quickly see Python/app/tool path context from one pasted block.
3. As a maintainer, I can gather this without modifying app state or artifacts.

## In Scope
- Add copyable diagnostics summary block in Diagnostics panel.
- Include key fields already shown in UI (python/app/model/latest run/tool availability/tool paths).
- Keep session-local and read-only.
- Update docs.

## Out of Scope
- Auto-uploading diagnostics.
- Redacting/path anonymization framework.
- Additional deep system probes.

## Required File Changes
- `app.py`
- `README_for_teacher.md`
- `docs/troubleshooting.md`

## Required Functional Changes
1. **Diagnostics Summary Generation**
   - Build deterministic text summary from current Diagnostics data.
   - Include timestamp and core status lines.

2. **Copy-Friendly Surface**
   - Render summary in text area for manual copy.
   - Keep behavior non-destructive and local.

3. **Docs Update**
   - Add brief troubleshooting guidance for using the diagnostics summary.

## Constraints
- No new dependencies.
- Reuse existing diagnostics data collection.
- No behavior regressions in pipeline/history features.

## Acceptance Criteria
1. User can copy a concise diagnostics snapshot from UI.
2. Snapshot reflects current displayed diagnostics values.
3. No manifest/artifact writes occur from this feature.
4. Existing checks and workflows remain unaffected.

## Review Notes for Developer
- Keep output plain text and support-oriented.
- Avoid duplicating heavy checks; use already-resolved values.
- Ensure summary remains readable for non-technical users.
