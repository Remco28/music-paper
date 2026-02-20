# Task Spec: BTT Phase 11 - Run Config Reapply and Manifest Detail Polish

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Make prior-run inspection more actionable by allowing users to re-apply a selected run's simplification settings to the current session and view a compact part-level outcome summary from that run.

## Rationale
Phase 10 made prior runs inspectable and downloadable. The next simplest leverage point is reducing setup friction for reruns: users should be able to take known-good settings from history and apply them directly, without manual re-entry.

## User Stories
1. As a teacher, I can apply settings from a successful past run to current controls in one click.
2. As a maintainer, I can inspect part-level export/skip outcomes from a selected run without opening JSON files.
3. As a maintainer, I can do this safely even when manifests are partial.

## In Scope
- Add a read-only part summary snippet in selected run details.
- Add `Apply Settings to Current Options` action for selected run manifest options.
- Handle missing/partial option keys safely.
- Update docs and smoke coverage for any new helper logic.

## Out of Scope
- Full session restore (audio/stems/assignments).
- Automatic rerun triggers after applying settings.
- Any changes to export pipeline semantics.

## Required File Changes
- `app.py`
- `utils.py` (only if a helper is needed)
- `README_for_teacher.md`
- `docs/run-history.md`
- `scripts/smoke_test.py` (if helper added)

## Required Functional Changes
1. **Part-Level Detail**
   - In selected run details, show a concise breakdown from manifest `parts`:
     - exported count
     - skipped count
     - up to first few skipped reasons (for example, `unassigned`, `no_notes`).

2. **Re-Apply Settings**
   - Add button in selected run details to apply manifest options to current session option keys:
     - `opt_profile`
     - `opt_simplify_enabled`
     - `opt_quantize_grid`
     - `opt_min_duration`
     - `opt_density_threshold`
   - Only apply fields that are present and valid.
   - Show clear success message and avoid mutating unrelated state.

3. **Safety Behavior**
   - If selected manifest lacks options or contains invalid values, show non-blocking guidance.
   - Never crash on malformed `parts` or option blocks.

4. **Docs Update**
   - Add short usage note for applying settings from history.

## Constraints
- No new dependencies.
- Keep local-only behavior.
- Preserve existing filter/maintenance/export behavior.

## Acceptance Criteria
1. User can apply selected run settings with one click.
2. UI reflects applied options in current controls.
3. Selected-run details include part-level summary without requiring file access.
4. Partial/malformed manifests are handled gracefully.

## Review Notes for Developer
- Keep behavior deterministic and explicit.
- Prefer minimal helper functions if logic grows beyond readability.
- Reuse existing state keys and guardrail ranges.
