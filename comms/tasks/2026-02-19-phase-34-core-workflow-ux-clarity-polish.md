# Task Spec: BTT Phase 34 - Core Workflow UX Clarity Polish

**Date:** 2026-02-19
**Owner:** Architect
**Status:** SPEC READY

## Objective
Reduce first-run friction in the core pipeline workflow by clarifying stage state and action intent.

## Rationale
MVP behavior is stable, but action labels and stage readiness cues can be clearer for teacher-led local use.

## User Stories
1. As a teacher, I can quickly tell which workflow stages are complete.
2. As a teacher, action buttons clearly communicate what happens next.
3. As a maintainer, UX polish remains non-invasive and behavior-preserving.

## In Scope
- Add compact workflow snapshot (read-only stage state).
- Clarify key action labels in Input/Stem/Export stages.
- Add brief helper captions where intent is ambiguous.

## Out of Scope
- Any pipeline logic changes.
- New data persistence or schema updates.

## Required File Changes
- `app.py`
- `README_for_teacher.md`

## Required Functional Changes
1. Add a stage-state summary block near top-level controls.
2. Update action labels for clearer intent (start-run, export ZIP, quick rerun semantics).
3. Preserve all existing gating and behavior.

## Constraints
- No new dependencies.
- UI/wording-only refinements.

## Acceptance Criteria
1. Stage readiness is visible without scrolling through all sections.
2. Button labels are clearer while triggering the same behavior.
3. Existing validations pass.
