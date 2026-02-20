# Task Spec: BTT Phase 21 - History Table Clarity Polish

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Improve Recent Runs table readability by polishing column presentation and status labels for faster scanning by non-technical users.

## Rationale
History capabilities are now strong (filters, details, health, summaries, CSV). The next high-value refinement is clarity: cleaner labels and compact values reduce cognitive load during teacher workflows.

## User Stories
1. As a teacher, I can quickly scan run rows without decoding technical shorthand.
2. As a maintainer, I can distinguish manifest status and run outcome status at a glance.
3. As a user, I can read long values without table clutter.

## In Scope
- Improve column labels and value formatting in Recent Runs table.
- Normalize status wording for consistency.
- Add safe truncation/formatting for long values where needed.
- Keep existing data and behaviors unchanged.

## Out of Scope
- New data fields.
- Sorting/pagination redesign.
- Backend/storage changes.

## Required File Changes
- `app.py`
- `README_for_teacher.md` (brief note if user-visible wording changes significantly)

## Required Functional Changes
1. **Column Clarity**
   - Use clearer headers (for example `Input Source`, `Run Outcome`, `Manifest`, `ZIP`).
   - Keep deterministic column order.

2. **Status Wording**
   - Normalize display values to teacher-friendly labels (for example `Success`, `Unknown`, `Missing`, `Corrupt`).

3. **Compact Value Formatting**
   - Ensure long fields remain readable (truncate with existing helper where appropriate).
   - Preserve access to full details via selected-run panel.

4. **Behavior Preservation**
   - Do not alter filtering/search/selection/export semantics.

## Constraints
- No new dependencies.
- Keep table rendering lightweight.
- Maintain backward compatibility with legacy manifests.

## Acceptance Criteria
1. Table is more readable with clearer headers and statuses.
2. No functional regressions in Recent Runs controls/details/CSV export.
3. Existing validations and workflows remain unaffected.

## Review Notes for Developer
- Prefer presentation-layer changes only.
- Keep status mappings explicit and deterministic.
- Avoid introducing additional complexity beyond formatting improvements.
