# Task Spec: BTT Phase 24 - Assignment Safety Guards

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Add lightweight assignment-stage safety guards that prevent ambiguous or risky assignment states before export.

## Rationale
Input and history reliability are stronger now; the next common failure point is assignment quality. Guarding obvious assignment issues upfront reduces wasted export attempts and skipped outputs.

## User Stories
1. As a teacher, I get a clear warning if I forgot to assign enough stems.
2. As a maintainer, I can detect suspicious assignment patterns before transcription/export.
3. As a user, normal valid assignment workflows remain quick and unchanged.

## In Scope
- Add assignment quality checks in stage 2/4 boundaries.
- Surface non-blocking warnings for suspicious states and blocking checks for invalid minimums.
- Keep current flexibility (allow intentional multi-stem-to-one-instrument mappings).
- Update troubleshooting docs.

## Out of Scope
- Hard musical heuristics per instrument family.
- Automatic assignment suggestions.
- Changes to core render/transcription logic.

## Required File Changes
- `app.py`
- `docs/troubleshooting.md`

## Required Functional Changes
1. **Minimum Assignment Guard**
   - Keep/strengthen requirement that at least one stem must be assigned before export.

2. **Assignment Quality Warnings**
   - Show non-blocking warnings for patterns such as:
     - high unassigned ratio
     - all assigned stems mapped to a single instrument
   - Warnings should be concise and actionable.

3. **Export Stage Integration**
   - Ensure blocking validation happens before starting transcription.
   - Preserve intentional advanced use cases (warnings, not hard blocks, for suspicious but valid patterns).

4. **Docs Update**
   - Add troubleshooting guidance for assignment guard messages.

## Constraints
- No new dependencies.
- Keep UI guidance concise.
- Preserve existing assignment flexibility and run flow.

## Acceptance Criteria
1. Invalid minimum assignment states are blocked with clear message.
2. Suspicious assignment patterns are surfaced as non-blocking warnings.
3. Existing successful assignment flows remain unaffected.
4. Existing validation checks pass.

## Review Notes for Developer
- Keep checks deterministic and explainable.
- Avoid over-constraining valid teaching workflows.
- Prefer simple ratio/count checks over complex heuristics.
