# Task Spec: BTT Phase 5 - Output Quality and Failure Clarity

**Date:** 2026-02-19  
**Owner:** Architect  
**Status:** SPEC READY

## Objective
Improve practical output quality controls and failure clarity in the UI so teacher runs are more predictable and faster to troubleshoot.

## Rationale
Pipeline reliability foundations are in place. The next highest-value step is reducing ambiguity when outputs are weak or a stage fails, without introducing heavy new features.

## User Stories
1. As a teacher, I can quickly understand why a part was skipped or thin and what to adjust next.
2. As a teacher, I can tune simplification with confidence using clearer labels and guardrails.
3. As a maintainer, I can diagnose stage failures from concise structured context.

## In Scope
- Improve part report messaging with actionable guidance.
- Add lightweight warnings when simplification settings are unusually aggressive/conservative.
- Standardize stage-level error surface with short context blocks.
- Add small docs update for troubleshooting patterns.

## Out of Scope
- New transcription models.
- Auto-arrangement or instrument inference.
- Authentication/cloud/multi-user.

## Required File Changes
- `app.py`
- `pipeline.py`
- `README_for_teacher.md`
- `docs/` (new troubleshooting note)

## Required Functional Changes
1. **Actionable Part Report**
   - For skipped parts, include reason-specific guidance in UI:
     - unassigned -> assign stem and rerun
     - no_notes -> try less aggressive simplification or different profile
   - Keep report concise and readable.

2. **Simplification Guardrails**
   - Show non-blocking warnings when settings imply likely note loss (for example `1/4` grid + high min duration).
   - Warnings should not block export.

3. **Stage Error Clarity**
   - When a stage fails, show:
     - stage name
     - short error summary
     - next-step hint
   - Do not expose noisy full tracebacks in default UI.

4. **Troubleshooting Doc**
   - Add `docs/troubleshooting.md` with common failures and direct fixes:
     - missing executables
     - YouTube URL validation issues
     - empty or sparse parts

## Constraints
- Preserve current workflow and no-auth scope.
- Avoid heavy dependencies.
- Keep UI simple for non-technical users.

## Acceptance Criteria
1. Part report includes actionable suggestions for skipped outcomes.
2. Simplification warnings appear for risky settings but do not block runs.
3. Stage failures are presented with concise context and guidance.
4. Troubleshooting doc exists and maps common issues to concrete actions.
5. Existing pipeline behavior remains intact.

## Review Notes for Developer
- Favor low-risk additive UI messaging.
- Keep error text deterministic and short.
- Avoid broad exception swallowing; preserve stage boundaries.
