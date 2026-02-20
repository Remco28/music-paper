# Task Spec: BTT Phase 12 - Manifest Versioning and Compatibility Guards

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add explicit manifest schema versioning and compatibility handling so run-history/detail features remain stable as manifest fields evolve.

## Rationale
Recent phases increased reliance on persisted manifests (history filters, detail view, settings reapply, artifact reopen). The simplest way to keep this maintainable is to version the manifest format and centralize compatibility decisions.

## User Stories
1. As a maintainer, I can tell which schema version produced a run manifest.
2. As a user, I still see safe run summaries when older manifests lack newer fields.
3. As a developer, I can add future manifest fields without breaking current UI flows.

## In Scope
- Add `schema_version` to newly written manifests.
- Add compatibility helper(s) for reading manifests with missing/unknown versions.
- Surface manifest version in selected run details.
- Update docs and smoke checks for version handling.

## Out of Scope
- Backfilling/re-writing existing manifests on disk.
- Multi-step migration scripts.
- Any remote synchronization.

## Required File Changes
- `utils.py`
- `app.py`
- `docs/manifest-schema.md`
- `docs/run-history.md`
- `scripts/smoke_test.py`

## Required Functional Changes
1. **Manifest Version Write Path**
   - Include top-level `schema_version` in `write_run_manifest` output.
   - Use a named constant for current schema version.

2. **Compatibility Read Helpers**
   - Add helper that normalizes loaded manifest blocks (`input`, `options`, `outcome`, `pipeline`, `parts`) with safe defaults.
   - Unknown/newer schema versions should be treated as readable best-effort (non-blocking).

3. **UI Exposure**
   - In selected run details, show schema version (`n/a` if absent).
   - If manifest is missing version, keep behavior functional and mark as legacy.

4. **Docs + Smoke**
   - Document schema version field and compatibility expectations.
   - Add smoke checks for legacy (no version) and current version manifests.

## Constraints
- No new dependencies.
- Preserve existing run-history filters, selected-run details, and apply-settings behavior.
- Do not require migration of existing local manifests.

## Acceptance Criteria
1. New manifests include explicit `schema_version`.
2. Legacy manifests remain readable in history/detail panels.
3. Selected-run details show version info without crashing on absent/unknown versions.
4. Smoke checks cover versioned and legacy compatibility paths.

## Review Notes for Developer
- Keep compatibility logic centralized and deterministic.
- Favor additive changes; avoid broad refactors.
- Ensure helper outputs are plain dict/list primitives suitable for UI rendering.
